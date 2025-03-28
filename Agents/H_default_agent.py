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

def define_default_agent():
    """A fallback agent when no specific agent is selected."""
    return Agent(
        name="Default Banking Assistant",
        instructions="""
        You are a general banking assistant. Since no specific task was identified in your request,
        please clarify what you need help with (e.g., transfers, credit card issues, account details).
        You don't answer anything not related to banking.
        """,
        model=model
    )