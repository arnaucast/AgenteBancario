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
from .utilities.analytics_subagents import *
from .utilities.bank_movements_dealers import *
from .utilities.bank_movements_dealers import *
import asyncio
from __init__ import BankingContext

@function_tool
async def DealWithAnalyticsTask(ctx: RunContextWrapper['BankingContext'],text: str,iban_emisor:str) -> str:
    """Tool that must be given the petition of the user for the data he wants to analyze and the iban_emisor of the user"""
    # Step 1: Plan the searches
    print("Text received")
    print(text)
    IBAN_CORRECTO = CheckIfIBANBelongs(iban_emisor,ctx.context.nif)
    if IBAN_CORRECTO:
        data = get_iban_data([iban_emisor])
        print(f"Hemos sacado datos de {iban_emisor}")
        data = data[["fechahora","categoria","id_signo","importe"]].to_dict()
        categories_found = await find_categories(text)
        

        # Step 2: Perform the searches sequentially
        
        print(categories_found.items_found)
        
        categories_found = [item.category for item in categories_found.items_found]
        print(categories_found)
        if categories_found:
            categories_real_found = await Given_List_categ_find_names(categories_found,5)
            
            print(categories_real_found)
            categ_found = str(categories_real_found)
            categories_found = await find_filtered_categories(f"User question: {text} and the categories names you need to filter {categ_found} ")
            
            print(categories_found)
            categories_found = [item.category for item in categories_found.items_found]
            
            print(categories_found)
        
        
        # Step 3: Summarize the results
        
        if categories_found:
            final_result = await execute_code_agent(data,f"User question: {text}. Filter for the categories that solve the user question. You can choose from these: {categories_found}")
        else:
            final_result = await execute_code_agent(data,f"User question: {text}")
        
        final_result_v2 = await AnalyzeText(text,final_result)
        print("Final response")
        print(final_result_v2)
        
        return final_result_v2
    else:
        return "El IBAN proporcionado no es del usuario"

async def find_categories(text: str) -> CategorySeparatorLists:
    result = await Runner.run(category_separator_agent, f"text to analyze: {text}")
    return result.final_output_as(CategorySeparatorLists)

async def find_filtered_categories(text: str) -> CategorySeparatorLists:
    result = await Runner.run(category_filterer, f"Categories to filter : {text}")
    return result.final_output_as(Categories_FilteredList)

async def execute_code_agent(data,text: str) -> str:
    print("Final text")
    print(text)
    BankingContext.data = data
    result = await Runner.run(bank_query_agent, text,context=BankingContext)
    print("Text222")
    print(result)
    return result.final_output_as(str)

async def AnalyzeText(output_data: str,user_question) -> str:
    result = await Runner.run(analyze_user_data, f"The user question is {user_question} and the data you must use is {output_data}")
    return result.final_output_as(str)

class AnalyzerOutput(BaseModel):
    message_to_client: str
    """Analysis to send the client"""
    operation_success: bool
    """Allways return it to True, no matter what"""



analyzer_of_data = Agent[BankingContext](
    name="Analytics",
    handoff_description="Handles analytics",
    instructions="""1. Use DealWithAnalyticsTask to perform the analysis. 
    Send only the user's exact text to the tool and the IBAN emisor. Try using this tool a maximum of 3 times.
    IF there are several IBANs, asks the user which one he wants to analyze
    When returned the analysis by the tool DealWithAnalyticsTask, return the analysis to the client, without changing or adding anything, along the operation_success  = true
    """,
    model=model,  # Adjust model as needed
    tools=[DealWithAnalyticsTask],
    output_type =AnalyzerOutput
)

async def main():
    topic = "news about Banco Sabadell"
    summary = await Runner.run(analyzer_of_data, topic)
    print(summary.final_output)

if __name__ == "__main__":
    asyncio.run(main())

