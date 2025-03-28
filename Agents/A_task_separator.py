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

# Define the banking guardrail agent
BANKING_GUARDRAIL_PROMPT = (
    """You are an agent that filters client input to keep only banking-related requests that a banking agent can handle.
    
    Examples of banking-related requests include:
    - Checking transactions
    - Sending money
    - Account balance inquiries
    - Payment scheduling
    - Asking for news specifically about Banc Sabadell
    - Data Analysis of bank movements 
    
    IMPORTANT: Asking for news about Banc Sabadell is a valid request and should be kept.
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
    model="o3-mini",
    output_type=BankingFilterOutput,
)
# Fixed Task Separator Agent to ONLY separate tasks without filtering
TASK_SEPARATOR_PROMPT = (
    """You are an agent that processes a set of orders from a banking client. Your job is to:
    1. Identify individual tasks or questions in the input.
    2. Return each task as a separate item in a list so the next agent can handle each one separately.
    
    IMPORTANT: Do NOT filter any content - your only job is to separate multiple requests into individual items.
    
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
    model="o3-mini",
    output_type=TaskSeparatorLists
)