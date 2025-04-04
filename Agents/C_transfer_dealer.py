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

class TargetTransfStr(BaseModel):
    IBAN_EMISOR: str
    NAME_RECEPTOR: str

# Define the Find_IBAN_of_transfer_receiver agent
find_target_of_transfer = Agent(
    name="Find_IBAN_of_transfer_receiver",
    instructions="""
Given a bank transfer request where the receiver’s IBAN is missing:
1. If both the sender’s IBAN (IBAN_EMISOR) and the receiver’s full or partial name (receptor_name) are provided, use available tools to find the receiver’s IBAN.
2. If either IBAN_EMISOR or receptor_name is missing, Please ask the user to provide the detailed IBAN of the receiver'
3. If no match is found for the receiver, return: 'The receiver’s IBAN could not be identified. Please ask the user to provide the detailed IBAN of the receiver.'
    """,
    model=model,
    tools=[find_closest_match],
    output_type=str  # Assuming it returns a string (IBAN or error message)
)

class TransferOutput(BaseModel):
    message_to_client: str
    """Information you need to tell the client"""
    operation_success: bool
    """Indicates with True if the transfer has been made with success"""

# Define the Send_Transfer_to_IBAN_receptor agent
send_transfer_to_iban_receptor = Agent(
    name="Send_Transfer_to_IBAN_receptor",
    instructions="""
If provided with both the IBAN of the emisor (IBAN_EMISOR) and the IBAN of the receptor (IBAN_RECEPTOR) for a transfer, use the available tool to execute the transfer.
If the order has been able to be processed, return the message and also operation_success to True
If the order hasn't been able to be processed, return the message and also operation_success to False
If not enough information, tell the agent to ask the client for the information
    """,
    model=model,
    tools=[transfer_money_and_log],
    output_type=TransferOutput  # Assuming it returns a confirmation message or error
)


class TransferOutput2(BaseModel):
    message_to_client: str
    """Information you need to tell the client"""
    operation_success: bool
    """Indicates with True if the transfer has been made with success"""


#3. If and only if the client provides the name or partial name of the receiver (e.g., "John Doe"), call `Find_IBAN_of_transfer_receiver` with the provided name. Example: {"IBAN_EMISOR": "ES9121000418450200051332", "receiver_name": "John Doe"}. If nothing is returned, ask: "I couldn’t find the receiver’s IBAN. Can you provide more details?"
# Define the Transfer Coordinator agent with BankingContext
''' find_target_of_transfer.as_tool(
            tool_name="Find_IBAN_of_transfer_receiver",
            tool_description="If you have the IBAN of the emisor and name or partial name of receptor, call this tool"
        ),'''
transfer_coordinator = Agent[BankingContext](
    name="Transfer Coordinator",
    instructions="""
You assist banking clients with transfers, requiring the sender’s IBAN (IBAN_EMISOR), receiver’s IBAN (IBAN_RECEPTOR), and transfer amount (import). Follow these steps:
. If multiple IBANs are returned, ask the client which one to use. If only one is returned, suggest it to the client for confirmation.
- If IBAN_EMISOR, IBAN_RECEPTOR, and import are all available: Present the details (IBAN_EMISOR, IBAN_RECEPTOR, import) to the client for confirmation. After confirmation, call `Send_Transfer_to_IBAN_receptor` with all three parameters.
- If `Send_Transfer_to_IBAN_receptor` returns operation_success = true, inform the client: "Transfer completed successfully!" and return operation_success = True.
- Do not call any tool unless all its required parameters are present.
- If client tells that he doesn't want to do this task, return operation_success = True and tell "Operación cancelada to the client"
Respond in the client's language
    """,

    model=model,
    tools=[
       # get_ibans,  # Now expects a RunContextWrapper[BankingContext]
        #c,
     
        send_transfer_to_iban_receptor.as_tool(
            tool_name="Send_Transfer_to_IBAN_receptor",
            tool_description="Executes a transfer using IBAN_EMISOR, IBAN_RECEPTOR, and import. Requires client confirmation and all three variables must be non empty."
        )
    ],
    output_type =TransferOutput2
    #input_guardrails=[iban_emisor_guardrail]  # Assuming this is defined elsewhere
)

'''
find_target_of_transfer.as_tool(
            tool_name="Find_IBAN_of_transfer_receiver",
            tool_description="Requires IBAN_EMISOR and receptor_name. Returns the receiver’s IBAN or an error message if not found.",
            params_json_schema=TargetTransfStr.model_json_schema()
        ),
'''