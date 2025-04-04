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

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace

# Planner Agent: Generates a search plan for news about a topic
PLANNER_PROMPT = (
    "You are a research planner. Given a topic, produce a set of 2 web searches to gather recent news and updates. "
    "Focus on recent headlines, key events, and developments related to the topic."
)

class SearchItem(BaseModel):
    reason: str
    """Reasoning for why this search is relevant."""
    query: str
    """The search term to use."""

class SearchPlan(BaseModel):
    searches: list[SearchItem]
    """List of searches to perform."""

planner_agent = Agent(
    name="NewsPlannerAgent",
    instructions=PLANNER_PROMPT,
    model=model,
    output_type=SearchPlan,
)

# Search Agent: Performs web searches and returns concise summaries
SEARCH_INSTRUCTIONS = (
    "You are a research assistant focused on news. Given a search term, use web search to retrieve up-to-date information "
    "and produce a short summary of at most 200 words. Focus on key events, dates, and developments relevant to the topic."
)

search_agent = Agent(
    name="NewsSearchAgent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
)

# Summary Agent: Combines search results into a final news summary
SUMMARY_INSTRUCTIONS = (
    "You are a news summarizer. Given a list of news summaries, combine them into a single concise summary of 50 words. "
    "Focus on the most significant events and developments, avoiding financial analysis or speculation. Include key dates and details."
)

summary_agent = Agent(
    name="NewsSummaryAgent",
    instructions=SUMMARY_INSTRUCTIONS,
    model=model,
)

"""Functions for orchestrating planning, searching, and summarizing news about a topic."""
import asyncio
from typing import Sequence
from agents import Agent, Runner, function_tool, ModelSettings, WebSearchTool
from pydantic import BaseModel

# ... (keep your existing agent definitions unchanged)

@function_tool
async def run_news_research(topic: str) -> str:
    # Step 1: Plan the searches
    print("A1")
    search_plan = await _plan_searches(topic)
    
    # Step 2: Perform the searches sequentially
    print("A2")
    search_results = await _perform_searches(search_plan)
    
    # Step 3: Summarize the results
    print("A3")
    final_summary = await _summarize_results(search_results)
    
    return final_summary
'''
async def _plan_searches2(topic: str) -> SearchPlan:
    result = await Runner.run(planner_agent, f"Topic: {topic}")
    return result.final_output_as(SearchPlan)

async def _perform_searches(search_plan: SearchPlan) -> Sequence[str]:
    results: list[str] = []
    for item in search_plan.searches:
        result = await _search(item)
        if result is not None:
            results.append(result)
    return results


async def _search(item: SearchItem) -> str:
    result = await Runner.run(search_agent, item.query)
    return str(result.final_output)
'''

async def _plan_searches(topic: str) -> SearchPlan:
    result = await Runner.run(planner_agent, f"Topic: {topic}")
    return result.final_output_as(SearchPlan)

async def _perform_searches(search_plan) -> Sequence[str]:
    tasks = [asyncio.create_task(_search(item)) for item in search_plan.searches] #iy creates a list with all the searches strings to use
    #each element is a dictionary with reason and search item
    results: list[str] = []
    num_completed = 0
    for task in asyncio.as_completed(tasks): # iterates over the tasks as they complete. Each task in the loop 
                                            #is a Task object that has finished its execution (either successfully or with an exception).
        '''
        Even though asyncio.as_completed gives you completed tasks, you still need to await each one to retrieve its result (or exception). 
        This is because a Task is a wrapper around a coroutine, and await extracts the final value.
        '''
        result = await task
        if result is not None:
            results.append(result)
        num_completed += 1
    return results #append of results

async def _search(search_plan) -> str | None:
    try:
        result = await Runner.run(search_agent, search_plan.query) #we send  it the text
        return str(result.final_output)
    except Exception:
        return None 


async def _summarize_results(search_results: Sequence[str]) -> str:
    if not search_results:
        return "No news summaries available."
    input_text = "Summaries:\n" + "\n\n".join(search_results)
    result = await Runner.run(summary_agent, input_text)
    return str(result.final_output), True

class NoticiasOutput(BaseModel):
    message_to_client: str
    """Information you need to tell the client"""
    operation_success: bool
    """Allways return True"""


news_coordinator = Agent(
    name="News Coordinator",
    instructions="""
Given some news to search, use run_news_research and return the result to the user.
Return the message_to_client and also operation_success =True always
    """,
    model=model,  # Adjust model as needed
    tools=[run_news_research],
    output_type =NoticiasOutput
)
'''
async def main():
    topic = "news about Banco Sabadell"
    print("HOLA1")
    summary = await Runner.run(news_coordinator, topic)
    print(summary.final_output)

if __name__ == "__main__":
    asyncio.run(main())'''