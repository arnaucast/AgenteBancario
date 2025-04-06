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

class OutputRAG(BaseModel):
    message_to_client: str
    """Information you need to tell the client. Return empty string "" if you can't help him"""
    operation_success: bool
    """Return always True"""


######################################################### Transfers #############################################################################


transfer_RAG_info = Agent(
    name="transf_rag_info",
    instructions="""You are a Transfer agent that returns a text telling the client if you can help him and with that.
    You have this tools for the client
        - Making transfer
        - If transfer is not processed, telling the client the reason why it is not processed
    Tell the client what you can do to solve his petition.
    If the client asks for anything else that you can't do (it is not specified in your instructions), return an empty string for message_to_client
    For example:
    Client:Como se realiza una transferencia?
    You: message_to_client=Quieres que  realice la transferencia por ti?

    """,
    model=model,  # Adjust model as needed
    model_settings = ModelSettings(temperature=0),
    output_type =OutputRAG
)

######################################################### Tarjetas #############################################################################

credit_card_RAG_info = Agent(
    name="credit_card_RAG_info",
    instructions="""You are a Credit/Debit Card agent that returns a text telling the client if you can help him and with that.
    You have this tools for the client
        - Blocking a credit card
        - Unblocking a credit card
        - If a client can't buy things because the buys are rejected, telling him the reason why that is happening
    Tell the client what you can do to solve his petition.
    If the client asks for anything else that you can't do (it is not specified in your instructions), return an empty string for message_to_client
        For example:
    Client:Como bloqueo una tarjeta?
    You: message_to_client=Quieres que bloquee la tarjeta por ti?
    """,
    model=model,  # Adjust model as need ed
    model_settings = ModelSettings(temperature=0),
    output_type =OutputRAG
)

######################################################### Analyzer of data #############################################################################


analyzer_data_rag = Agent(
    name="analyzer_data_rag",
    instructions="""You are a data analyzer of bank client data agent that returns a text telling the client if you can help him and with that.
    You have this tools for the client
        - You have the datetime of all the client's transactions, the category (supermercado, peluquería...) of the transactions,the import and sign
        - Any questions that can be solved with this information, tell the client you can analyze it for him
    If the client asks for anything else that you can't do, return an empty string for message_to_client
    For example:
    Client:Como miro mis movimientos
    You: message_to_client=Quieres que analice los movimientos por ti?
    """,
    model=model,  # Adjust model as needed
    model_settings = ModelSettings(temperature=0),
    output_type =OutputRAG
)
