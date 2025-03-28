from pydantic import BaseModel
from agents import Agent
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
import os
from .utilities.change_get_data_db import *

from agents import Agent, Runner, function_tool
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

from .A_task_separator import task_separator_agent, banking_guardrail_agent
from .B_credit_card_dealer import credit_card_coordinator
from .C_transfer_dealer import transfer_coordinator
from .G_web_researcher import  news_coordinator
from .D_analytics_agent import analyzer_of_data
# Define the Agent Selector Agent
agent_selector_agent = Agent(
    name="Agent Selector",
    instructions="""
    You are an agent that selects the most likely agent for a user's request. You are given the request and a list of available agents with their names and descriptions.

    Your job is to:
    1. Analyze the request to identify the primary task involved (e.g., 'language translation', 'banking issue').
    2. Match the task to the most appropriate agent based on their names and descriptions.
    3. Return a JSON-formatted string containing a single agent name, e.g., "[\"Agent_Name\"]".
    4. If no agent matches, return an empty list as a JSON string: "[]".
    5. If multiple agents could apply, choose the one that best fits the request based on specificity and relevance.
    6. If asked to retry due to invalid output, ensure the output is a valid JSON string like "[\"Agent_Name\"]".
    """,
    model=model
)

# External tool registry (all are agents now)
agent_registry = {
    "Credit_Card_Coordinator": {
        "type": "agent",
        "agent": credit_card_coordinator,  # Assuming this is an Agent object
        "description": """Handles credit card requests and can block credit cards, unblock them, check why a client can't buy
                         (monthly spending limit, current month spending)
                       and find the reason on why a client can't buy things with a credit card"""
    },
    "Transfer_Coordinator": {
        "type": "agent",
        "agent": transfer_coordinator,  # Assuming this is an Agent object
        "description": "Handles transfers"
    },
    "News_Coordinator": {
        "type": "agent",
        "agent": news_coordinator,  # Assuming this is an Agent object
        "description": "Does research on news related to Banc Sabadell"
    },
        "Analyzer of data": {
        "type": "agent",
        "agent": analyzer_of_data,  # Assuming this is an Agent object
        "description": "Does analytics on bank movements. If you find the word analysis or analytics, it is the agent "
    }
    # Add 18+ more agents here
}

def configure_agent_coordinator(user_request):
    # Prepare input for agent_selector_agent
    agent_info = "\n".join([f"{name}: {info['description']}" for name, info in agent_registry.items()])
    selector_input = f"User request: {user_request}\nAvailable agents:\n{agent_info}"
    conversation_history = [{"content": selector_input, "role": "user"}]

    max_attempts = 3  # Prevent infinite loops
    for attempt in range(max_attempts):
        # Run the agent selector
        result = Runner.run_sync(agent_selector_agent, conversation_history)
        selected_agent_output = result.final_output_as(agent_selector_agent)
        print("Selected agent output:")
        print(selected_agent_output)
        
        # Clean up the output if it's a string
        if isinstance(selected_agent_output, str):
            # Remove Markdown code block syntax if present
            selected_agent_output = selected_agent_output.replace("```json", "").replace("```", "").strip()
            
            import json
            try:
                # Parse as JSON directly
                selected_agent_names = json.loads(selected_agent_output)
            except json.JSONDecodeError:
                # Handle common issues like single quotes
                try:
                    import ast
                    selected_agent_names = ast.literal_eval(selected_agent_output)
                except (SyntaxError, ValueError):
                    # If all attempts fail, try again
                    retry_message = f"Invalid output format: {selected_agent_output}. Return a valid JSON string like [\"Agent_Name\"]. No code blocks."
                    conversation_history.append({"content": retry_message, "role": "user"})
                    continue
        else:
            selected_agent_names = selected_agent_output  # Handle case where output is already a list
        
        # Validate output
        if not isinstance(selected_agent_names, list):
            retry_message = f"Output must be a list, got {type(selected_agent_names)}. Return a valid JSON string like [\"Agent_Name\"]."
            conversation_history.append({"content": retry_message, "role": "user"})
            continue
        
        # Check if the list is empty or has exactly one agent
        if len(selected_agent_names) > 1:
            retry_message = f"Output must contain exactly one agent, got {selected_agent_names}. Select the most likely agent."
            conversation_history.append({"content": retry_message, "role": "user"})
            continue
        elif not selected_agent_names:  # Empty list
            return None  # No matching agent found
        
        # Extract the single agent name
        selected_agent_name = selected_agent_names[0]
        
        # Check if the agent name is valid
        if selected_agent_name not in agent_registry:
            retry_message = f"Invalid agent: {selected_agent_name}. Please return a valid agent name from: {list(agent_registry.keys())}"
            conversation_history.append({"content": retry_message, "role": "user"})
            continue
        
        # Valid output, proceed
        break
    else:
        # Max attempts reached
        return None

    # Return the selected agent directly since everything is an agent now
    return agent_registry[selected_agent_name]["agent"]
