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

import asyncio

@function_tool
async def DealWithAnalyticsTask(text: str) -> str:
    # Step 1: Plan the searches
    print("Text received")
    print(text)
    print("A1")
    categories_found = await find_categories(text)
    
    # Step 2: Perform the searches sequentially
    print("A2")
    print(categories_found.items_found)
    print("bbb")
    categories_found = [item.category for item in categories_found.items_found]
    print(categories_found)
    if categories_found:
        categories_real_found = await Given_List_categ_find_names(categories_found,5)
        print("B")
        print(categories_real_found)
        categ_found = str(categories_real_found)
        categories_found = await find_filtered_categories(f"User question: {text} and the categories names you need to filter {categ_found} ")
        print("C")
        print(categories_found)
        categories_found = [item.category for item in categories_found.items_found]
        print("D")
        print(categories_found)
       
    
    # Step 3: Summarize the results
    print("A3")
    
    if categories_found:
        final_result = await execute_code_agent(f"User question: {text}. Filter for the categories that solve the user question. You can choose from these: {categories_found}")
    else:
        final_result = await execute_code_agent(f"User question: {text}")
    
    print("Final response")
    print(final_result)
    
    return final_result

async def find_categories(text: str) -> CategorySeparatorLists:
    result = await Runner.run(category_separator_agent, f"text to analyze: {text}")
    return result.final_output_as(CategorySeparatorLists)

async def find_filtered_categories(text: str) -> CategorySeparatorLists:
    result = await Runner.run(category_filterer, f"Categories to filter : {text}")
    return result.final_output_as(Categories_FilteredList)

async def execute_code_agent(text: str) -> str:
    print("Final text")
    print(text)
    result = await Runner.run(bank_query_agent, text)
    print("Text222")
    print(result)
    return result.final_output_as(str)

analyzer_of_data = Agent(
    name="Analytics",
    handoff_description="Handles analytics",
    instructions="""1. Use DealWithAnalyticsTask to perform the analysis. Send only the user's exact text to the tool. Try using this tool a maximum of 3 times.
2. When processing the returned data, follow these guidelines:
   - If data includes a table, display the table in a markdown or formatted layout
   - Use clear, concise language for explanations
   - Highlight key insights
   - Organize information with headings or bullet points if appropriate
   - Limit response to 200 words maximum
3. Formatting priorities:
   - Clarity
   - Readability
   - Use always thre ### for titles
   - Visual structure
   - Concise explanations of key findings
4. Include a brief summary or interpretation of the data
    """,
    model="o3-mini",  # Adjust model as needed
    tools=[DealWithAnalyticsTask]
)

async def main():
    topic = "news about Banco Sabadell"
    summary = await Runner.run(analyzer_of_data, topic)
    print(summary.final_output)

if __name__ == "__main__":
    asyncio.run(main())

