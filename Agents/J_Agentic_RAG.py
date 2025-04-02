import asyncio
from dotenv import load_dotenv
import os 
from agents import set_tracing_export_api_key
import logfire
from pydantic import BaseModel
from agents import function_tool, RunContextWrapper
from agents import (
    Agent,
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
from .utilities.bank_movements_dealers import *
from .utilities.bank_movements_dealers import *
from .utilities.rag_utilities import *

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace

@function_tool
async def DealWithRAGAgentic(text: str) -> str:

    categories_found = await FindType(text)
    print(categories_found.category)




class CategoryFound(BaseModel):
    category: str
    """Exact name of category found"""

async def FindType(text: str) -> CategoryFound:
    result = await Runner.run(category_detector, f"text to analyze: {text}")
    return result.final_output_as(CategoryFound)

rag_agent = Agent(
    name="Analytics",
    handoff_description="Handles analytics",
    instructions="""You are an agent that deals with bank clients question. You need to call  and return result to client
    """,
    model=model,  # Adjust model as needed
    tools=[DealWithRAGAgentic],
    output_type =str
)


async def main():
    topic = "Como bloqueo mi tarjeta"
    summary = await Runner.run(rag_agent, topic)
    print(summary.final_output)

if __name__ == "__main__":
    asyncio.run(main())