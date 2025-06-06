from pydantic import BaseModel
from agents import Agent
from agents import (
    Agent,ModelSettings,
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
from .J_Agentic_RAG import rag_agent
from .K_RAG_action_finder import transfer_RAG_info,credit_card_RAG_info,analyzer_data_rag
from .L_account_balance import account_balance_agent

class OutputModelSelector(BaseModel):
    agent_selected: str
    """Name of Agent Selected"""
    user_wants_information: bool
    """True if user wants informations"""

# Define the Agent Selector Agent
agent_selector_agent = Agent(
    name="Agent Selector",
    instructions="""
    You are an agent that selects the most likely agent for a user's request. You are given the request and a list of available agents with their names and descriptions.

    Your job is to:
    1. Analyze the request to identify the primary task involved (e.g., 'language translation', 'banking issue').
    2. Match the task to the most appropriate agent based on their names and descriptions.
    3. If multiple agents could apply, choose the one that best fits the request based on specificity and relevance.
    4. For user_wants_information return True only if the user wants to know how to do something or wants information about a product or bank service
    For example: "Quiero hacer una transferencia": False "Como se hace una transferencia" True "Por qué no puedo realizar transferencias" True

    """,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type= OutputModelSelector
)

# External tool registry (all are agents now)
agent_registry = {
    "Credit_Card_Coordinator": {
        "type": "agent",
        "agent": credit_card_coordinator,  # Assuming this is an Agent object
        "description": """Handles credit card requests and can block credit cards, unblock them, check why a client can't buy things with a credit card
                         (monthly spending limit, current month spending)""",
        "agent_rag_info":credit_card_RAG_info,
        "agent_rag_researcher":rag_agent
    },
    "Transfer_Coordinator": {
        "type": "agent",
        "agent": transfer_coordinator,  # Assuming this is an Agent object
        "description": "Handles transfers",
        "agent_rag_info": transfer_RAG_info,
        "agent_rag_researcher":rag_agent
    },
    "News_Coordinator": {
        "type": "agent",
        "agent": news_coordinator,  # Assuming this is an Agent object
        "description": "Does research on news related to Banc Sabadell",
        "agent_rag_info":None,
        "agent_rag_researcher":rag_agent
    },
        "Analyzer of data": {
        "type": "agent",
        "agent": analyzer_of_data,  # Assuming this is an Agent object
        "description": "Does analytics on bank movements, it has the movements categories of clients (salary, rent, etc... If you find the word analysis or analytics, it is the agent ",
        "agent_rag_info":analyzer_data_rag,
        "agent_rag_researcher":rag_agent
        
    },
        "Account Balance": {
        "type": "agent",
        "agent": account_balance_agent,  # Assuming this is an Agent object
        "description": "Gets the balance or saldo of a client's account ",
        "agent_rag_info":None,
        "agent_rag_researcher":rag_agent
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
        selected_agent_output = result.final_output_as(OutputModelSelector)
        selected_agent_name = selected_agent_output.agent_selected
        user_information = selected_agent_output.user_wants_information
        
        # Check if the agent name is valid
        if selected_agent_name not in agent_registry:
            retry_message = f"Invalid agent: {selected_agent_name}. Please return a valid agent name from: {list(agent_registry.keys())}"
            conversation_history.append({"content": retry_message, "role": "user"})
            continue
        
        # Valid output, proceed
        break
    else:
        # Max attempts reached
        return None, None
    # Return the selected agent directly since everything is an agent now
    return agent_registry[selected_agent_name]["agent"],user_information,agent_registry[selected_agent_name]["agent_rag_info"],agent_registry[selected_agent_name]["agent_rag_researcher"]
