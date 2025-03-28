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
                """,
    model=model,
    tools=[block_card_function, unblock_card_function]
)


credit_card_coordinator = Agent[BankingContext](
    name="Credit Card Cordinator",
    handoff_description="""Handles credit card requests and can block credit cards, unblock them, check details (monthly spending limit, current month spending)
                       and find the reason on why a client can't buy things with a credit card""",
    instructions="""
    You are an Agent responsible of helping banking clients with requests related to credit cards
    You have two tools at your disposal that you can use whenever you receive a request.
    If the client does not specify the PAN, use the `get_pans_function` to retrieve it and then ask the client which PAN to use, or if one, if use that one
    When the request is solved by the tools, then tell the client what you have achieved.
    If the tools tell you that it can't be solved, comunicate that to the client.
    You must pass the credit card pan with this format  5402********0001 to the tools
    Never assume things.
    """,
    model=model,
    tools=[
    get_pans_function,
    Check_Credit_Card_Data.as_tool(
        tool_name="Check_Credit_Card_Data",
        tool_description="An agent capable of checking data like credit card limit, money spent this month on credit card or why a client credit card doesn't work"
    ),
    Update_Credit_Card_Data.as_tool(
        tool_name="Update_Credit_Card_Data",
        tool_description="An agent capable of blocking or unblocking a credit card. You must give him the PAN and the order to do"
    )]
)


