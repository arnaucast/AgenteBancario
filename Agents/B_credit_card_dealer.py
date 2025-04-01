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
from context import BankingContext


class UpdateCreditCard(BaseModel):
    message_to_client: str
    """Information you need to tell the agent"""
    operation_success: bool
    """Indicates with True of operation success"""


Check_Credit_Card_Data = Agent[BankingContext](
    name="Check_Credit_Card_Data",
    instructions="""Given a set of tools you are responsible of checking data related to credit cards.
                    In case there is no data to return, return the message given by the tool.
                    If you find that the credit card is blocked, tell the credit card cordinator to propose
                    the client to unblock it if he wants""",
    model =model,
    tools=[get_card_details_function,check_payment_conditions_function]
)

Update_Credit_Card_Data = Agent[BankingContext](
    name="Update_Credit_Card_Data",
    instructions="""You are responsible for blocking or unblocking credit cards of clients and have two tools to do it
                    You need to pass the credit card in the format  5402********0001. 
                    If you get passed PAN without *, add them to fit the format 
                    As response return operation_success to True if you have managed to block the credit cards demanded or if the cards demanded were already un/blocked.
                    If any kind of error, return False to that variable
                """,
    model=model,
    tools=[block_card_function, unblock_card_function],
    output_type =UpdateCreditCard
)

class CreditCardOutput(BaseModel):
    message_to_client: str
    """Information you need to tell the client"""
    operation_success: bool
    """Indicates with True if Update_Credit_Card_Data called and client credit un/blocked or was already un/blocked. """


credit_card_coordinator = Agent[BankingContext](
    name="Credit Card Cordinator",
    handoff_description="""Handles credit card requests and can block credit cards, unblock them, check details (monthly spending limit, current month spending)
                       and find the reason on why a client can't buy things with a credit card""",
    instructions="""
    You are an Agent responsible of helping banking clients with requests related to credit cards
    If the client does not specify the PAN, ask the client which PAN to use.
    If operation_success returned by Update_Credit_Card_Data is True, return to the client the mssage + operation_success=True.
    If the tools tell you that it can't be solved, comunicate that to the client, setting operation_success to False
    If the client tells you that he is done with the petition, return "May I help you with something else" and return operation_success to True
    """,
    model=model,
    tools=[
    Check_Credit_Card_Data.as_tool(
        tool_name="Check_Credit_Card_Data",
        tool_description="An agent capable of checking data like credit card limit, money spent this month on credit card or why a client credit card doesn't work"
    ),
    Update_Credit_Card_Data.as_tool(
        tool_name="Update_Credit_Card_Data",
        tool_description="An agent capable of blocking or unblocking a credit card. You must give him the PAN and the order to do"
    )],
    output_type =CreditCardOutput
)


