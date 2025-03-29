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
from agents import Runner
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

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

# List of 20 test examples in Spanish (mix of banking and non-banking)
test_examples = [
    "Quiero revisar mis transacciones de este mes"
]

# Process each example and print original text and result
for example in test_examples:
    prueba = Runner.run_sync(banking_guardrail_agent, example)
    guardrail_output = prueba.final_output_as(banking_guardrail_agent)
    
    print(f"Original text: {example}")
    print(f"Filtered text: {guardrail_output.filtered_text}")
    print(f"Non-banking content removed: {guardrail_output.non_banking_content_removed}")
    print("-" * 50)
