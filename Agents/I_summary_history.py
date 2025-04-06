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

# New Context Summarizer Agent
CONTEXT_SUMMARIZER_PROMPT = (
    """You are an agent that summarizes the conversation history to extract key banking-related details (what he ordered, account numbers, import, user preferences) 
    for use in subsequent tasks. Provide a concise summary of 30 words of relevant information, ignoring non-banking content."""
)

class ContextSummary(BaseModel):
    summary: str
    """A concise summary of relevant banking details from the conversation history."""

context_summarizer_agent = Agent(
    name="ContextSummarizer",
    instructions=CONTEXT_SUMMARIZER_PROMPT,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=ContextSummary
)