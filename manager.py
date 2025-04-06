import asyncio
from dotenv import load_dotenv
import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool
from Agents.A_task_separator import task_separator_agent, banking_guardrail_agent
from Agents.B_credit_card_dealer import credit_card_coordinator
from Agents.C_transfer_dealer import transfer_coordinator
from Agents.F_most_likely_agent import configure_agent_coordinator  # Assuming this is where configure_agent_coordinator lives
from Agents.H_default_agent import define_default_agent
from Agents.I_summary_history import context_summarizer_agent
# Agents/manager.py

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from context import BankingContext
import asyncio
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
import concurrent.futures

import streamlit as st
import uuid
from datetime import datetime
import asyncio
import nest_asyncio
import os
from dotenv import load_dotenv
import logfire
from dotenv import load_dotenv
import os 
load_dotenv()
# Comment these lines out if you don't want Logfire tracing
logfire.configure(send_to_logfire=os.getenv("CONEXION_LOG_FIRE"),scrubbing=False)
logfire.instrument_openai_agents()
logfire.instrument_openai_agents()

# Patch the event loop to allow nested use of asyncio
nest_asyncio.apply()

# Your existing imports and setup
load_dotenv()

def run_async_with_event_loop(coro):
    """
    Helper function to run async coroutines in a synchronous context
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)
def get_timestamp(message):
    """Safely get timestamp from message, using current time as fallback."""
    return message.get('timestamp', datetime.now().strftime("%I:%M %p"))
def process_single_task(agent, task, conversation_history, context_summary="", banking_context=None):
    """Process a single task with the given agent, using conversation history and context summary."""
    async def async_process():
        # Create a clean version of conversation history without timestamp
        clean_conversation_history = [
            {k: v for k, v in msg.items() if k != 'timestamp'} 
            for msg in conversation_history
        ]

        task_with_context = f"Task: {task}\nContext from previous tasks: {context_summary}" if context_summary else task

        # DEBUG: Print out the full context being sent to the agent
        print("\n--- DEBUG: Agent Processing ---")
        print("Task:", task)

        existing_tasks = [msg["content"] for msg in clean_conversation_history if msg["role"] == "user"]
        if task_with_context not in existing_tasks:
            clean_conversation_history.append({"content": task_with_context, "role": "user"})

        print("new_context")
        print(clean_conversation_history)
        
        try:
            result = await Runner.run(agent, clean_conversation_history, context=banking_context)
            agent_response = result.final_output_as(agent)
            print("Agent")
            clean_conversation_history.append({"content": agent_response.message_to_client, "role": "assistant"})
            print("conv")
            print(conversation_history)
            print(agent_response.message_to_client)
            print(agent_response.operation_success)
            print(False)
            return conversation_history, agent_response.message_to_client,agent_response.operation_success, False
        
        except Exception as e:
            print("Full Exception Type:", type(e))
            
            # Specifically for InputGuardrailTripwireTriggered
            if type(e).__name__ == 'InputGuardrailTripwireTriggered':
                # Extract the message from the guardrail result
                try:
                    guardrail_result = e.guardrail_result
                    output = guardrail_result.output
                    error_msg = f"{output.output_info['message']}"
                except Exception as extract_error:
                    # Fallback if extraction fails
                    print(f"Error extracting guardrail message: {extract_error}")
                    error_msg = f"Banking Assistant: I'm experiencing technical difficulties: {str(e)}"
                clean_conversation_history.append({"content": error_msg, "role": "assistant"})
                return conversation_history, error_msg,False, False
            else:
                # For other types of exceptions
                error_msg = f"Banking Assistant: I'm experiencing technical difficulties: {str(e)}"
                clean_conversation_history.append({"content": error_msg, "role": "assistant"})
            
            return conversation_history, error_msg,True, False
            

    return run_async_with_event_loop(async_process())

def main_banking(user_input, conversation_history=None, reset_history_between_tasks=False, banking_context=None):
    """Main function to handle banking requests with task separation and context summarization."""
    async def async_main_banking():
        if conversation_history is None:
            conversation_history = []

        # Create a clean version of conversation history without timestamp
        clean_conversation_history = [
            {k: v for k, v in msg.items() if k != 'timestamp'} 
            for msg in conversation_history
        ]

        guardrail_result = await Runner.run(banking_guardrail_agent, user_input)
        guardrail_output = guardrail_result.final_output_as(banking_guardrail_agent)
        filtered_input = guardrail_output.filtered_text

        if guardrail_output.non_banking_content_removed:
            return conversation_history, "Non-banking content was removed. Processing only banking-related requests.", False

        separator_result = await Runner.run(task_separator_agent, filtered_input)
        separated_tasks = separator_result.final_output_as(task_separator_agent).items_found

        if not separated_tasks:
            current_agent = define_default_agent()
            clean_conversation_history.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, clean_conversation_history, context=banking_context)
            response = result.final_output_as(current_agent)
            clean_conversation_history.append({"content": response, "role": "assistant"})
            return conversation_history, response, False

        context_summary = ""
        task_results = []
        for task in separated_tasks:
            task_text = task.order
            
            # Modify this part to work directly with agent
            selected_agent = configure_agent_coordinator(task_text)
            current_agent = selected_agent if selected_agent else define_default_agent()
            
            # Only modify instructions if it's an Agent type
            if hasattr(current_agent, 'instructions'):
                current_agent.instructions += "\nUse the conversation history or provided context summary to infer details like account numbers or user preferences when processing tasks, unless the user specifies otherwise."
            
            conversation_history, response, _ = process_single_task(current_agent, task_text, conversation_history, context_summary, banking_context)
            task_results.append(response)
            
            summary_result = await Runner.run(context_summarizer_agent, clean_conversation_history)
            context_summary = summary_result.final_output_as(context_summarizer_agent).summary

        return conversation_history, "\n".join(task_results), False