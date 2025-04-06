import asyncio
from dotenv import load_dotenv
import os 
from agents import set_tracing_export_api_key
import logfire
from pydantic import BaseModel
from agents import function_tool, RunContextWrapper
from agents import (
    Agent,ModelSettings,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from typing import Sequence
import os
from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings

# Comment these lines out if you don't want Logfire tracing
from dotenv import load_dotenv
import os 
load_dotenv()
# Comment these lines out if you don't want Logfire tracing
logfire.configure(send_to_logfire=os.getenv("CONEXION_LOG_FIRE"))
logfire.instrument_openai_agents()
load_dotenv()
from .utilities.rag_utilities import *

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(client)
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace

@function_tool
async def DealWithRAGAgentic(text: str) -> str:

    categories_found = await FindType(text)
    print(categories_found.category)

    best3 = get_top3_matches(text,categories_found.category)
    print(best3)

    return best3

class CategoryFound(BaseModel):
    category: str
    """Exact name of category found"""

async def FindType(text: str) -> CategoryFound:
    result = await Runner.run(category_detector, f"text to analyze: {text}")
    return result.final_output_as(CategoryFound)

class OutputRAG(BaseModel):
    message_to_client: str
    """Information you need to tell the client. Return empty string "" if you can't help him"""
    operation_success: bool
    """Return always True"""

rag_agent = Agent(
    name="rag_agent",
    handoff_description="Handles rag",
    instructions="""You are an agent that deals with bank clients question. You need to call  and return result to client
    in message_to_client the message to send the client in html syntax and operation_success allways to True.Use  the info given by the toolDealWithRAGAgentic. 
    """,
    model=model,  # Adjust model as needed
    model_settings = ModelSettings(temperature=0),
    tools=[DealWithRAGAgentic],
    output_type =OutputRAG
)

async def main():
    topic = "Como bloqueo mi tarjeta"
    summary = await Runner.run(rag_agent, topic)
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())