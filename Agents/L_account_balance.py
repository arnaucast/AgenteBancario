from pydantic import BaseModel
from agents import Agent,ModelSettings
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
from context import BankingContext


class AccountBalance(BaseModel):
    message_to_client: str
    """Balance Of the account"""
    operation_success: bool
    """Indicates with True if you have managed to get a balance"""

account_balance_agent = Agent[BankingContext](
    name="Account_Balance",
    instructions="""
You assist banking clients telling them their balance.
If you are given multiple IBANs for the client, then ask the client for which one he wants the balance
    """,
    model=model,
    model_settings = ModelSettings(temperature=0),
    tools=[
       # get_ibans,  # Now expects a RunContextWrapper[BankingContext]
        #c,
        get_saldos_by_IBAN_ft
    ],
    output_type =AccountBalance
)