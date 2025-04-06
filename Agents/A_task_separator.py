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
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
# Define the banking guardrail agent
BANKING_GUARDRAIL_PROMPT = (
    """You are an agent that filters client input to keep only banking-related requests that a banking agent can handle.
    
    Examples of banking-related requests include:
    - Things related to transfers
    - Things related to credit or debit cards
    - Things related to News related to Banc Sabadell. Any other topic not.
    - Analytics on the client's bank movements, client spending, client earnings
    """
)

class BankingFilterOutput(BaseModel):
    filtered_text: str
    """The input text with non-banking-related content removed"""
    non_banking_content_removed: bool
    """Indicates if any non-banking content was removed"""

banking_guardrail_agent = Agent(
    name="BankingFilterGuardrail",
    instructions=BANKING_GUARDRAIL_PROMPT,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=BankingFilterOutput,
)
# Fixed Task Separator Agent to ONLY separate tasks without filtering
TASK_SEPARATOR_PROMPT = (
    """You are an agent that processes a set of orders from a banking client. Your job is to:
    1. Identify individual tasks or questions in the input.
    2. Return each task as a separate item in a list so the next agent can handle each one separately.
    
    IMPORTANT: Do NOT filter any content,use the full text of the task, don't do a summary- your only job is to separate multiple requests into individual items.
    
    Examples of tasks might include:
    - 'check my account balance'
    - 'transfer €200 to Maria'
    - 'show my last 5 transactions'
    - 'what are the news about Banc Sabadell?'
    - 'tell me today's weather'
    - 'what's happening in sports today'
    
    All of these should be included in your output, regardless of whether they are banking-related or not.
    The filtering will be handled by a different agent."""
)

class TaskSeparatorStr(BaseModel):
    order: str
    """The individual task or question you have found in the message"""

class TaskSeparatorLists(BaseModel):
    items_found: list[TaskSeparatorStr]
    """A list of all tasks found in the message."""

task_separator_agent = Agent(
    name="TaskSeparator",
    instructions=TASK_SEPARATOR_PROMPT,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=TaskSeparatorLists
)