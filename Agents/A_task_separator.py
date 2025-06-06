from pydantic import BaseModel
from agents import Agent
from agents import (
    Agent,ModelSettings,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
import os
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
# Define the banking guardrail agent
BANKING_GUARDRAIL_PROMPT = (
    """You are an agent that filters client input to identify and retain only banking-related requests.
    Your task is to pass through the original request unchanged if it is banking-related, without adding explanations, 
    instructions, or modifications unless explicitly asked. If the input contains multiple questions, sentences, or parts, 
    evaluate each part independently and retain all parts that are banking-related, combining them into a single unchanged 
    output exactly as they were provided, preserving the original wording and structure.

    Examples of banking-related requests include:
    - Things related to transfers
    - Things related to credit or debit cards
    - Things related to News related to Banc Sabadell (no other topics)
    - Requests for bank movements, analysis of movements, spending, earnings, or breakdowns of spending (e.g., by category or time)
    - Questions about bank problems clients are having, even if they write ir really bad (buys are being blocked, stolen credit cards...)

    For example:
    - Input containing multiple banking-related parts: a request about transfers followed by a request about spending analysis.
    - Output: the full original input with both parts unchanged.
    - Input mixing banking and non-banking topics: a non-banking question followed by a banking-related request about transfers.
    - Output: only the banking-related request about transfers, unchanged.
    """
)

class BankingFilterOutput(BaseModel):
    filtered_text: str
    """The input text with non-banking-related content removed"""
    non_banking_content_removed: bool
    """Indicates if any non-banking content was removed"""

banking_guardrail_agent = Agent(
    name="BankingFilterGuardrail",
    instructions=BANKING_GUARDRAIL_PROMPT,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=BankingFilterOutput,
)
# Fixed Task Separator Agent to ONLY separate tasks without filtering
TASK_SEPARATOR_PROMPT = (
    """You are an agent that processes a set of orders from a banking client. Your job is to:
    1. Identify individual tasks or questions in the input.
    2. Return each task as a separate item in a list so the next agent can handle each one separately.
    
    IMPORTANT: Do NOT filter any content,use the full text of the task, don't do a summary- your only job is to separate multiple requests into individual items.
    
    Examples of tasks might include:
    - 'check my account balance'
    - 'transfer €200 to Maria'
    - 'show my last 5 transactions'
    - 'what are the news about Banc Sabadell?'
    - 'How has my salary evolved and how is my spending going this month?

    3. If it is an analytic task, return everything together as a task
    Really important: If the input is a single sentence or short statement with related parts (e.g., separated by commas or conjunctions), 
        treat it as one task unless the parts are clearly independent requests.


    
    All of these should be included in your output, regardless of whether they are banking-related or not.
    The filtering will be handled by a different agent."""
)

class TaskSeparatorStr(BaseModel):
    order: str
    """The individual task or question you have found in the message"""

class TaskSeparatorLists(BaseModel):
    items_found: list[TaskSeparatorStr]
    """A list of all tasks found in the message."""

task_separator_agent = Agent(
    name="TaskSeparator",
    instructions=TASK_SEPARATOR_PROMPT,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=TaskSeparatorLists
)


'''

File "F:\Escritorio\Sabadell\CURSOS\LLM\Agents OpenAI\Agente_Bancario_Github\agente_bancario_git\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 121, in exec_func_with_error_handling
    result = func()
             ^^^^^^
File "F:\Escritorio\Sabadell\CURSOS\LLM\Agents OpenAI\Agente_Bancario_Github\agente_bancario_git\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 593, in code_to_exec
    exec(code, module.__dict__)
File "F:\Escritorio\Sabadell\CURSOS\LLM\Agents OpenAI\Agente_Bancario_Github\create_website.py", line 911, in <module>
    main()
File "F:\Escritorio\Sabadell\CURSOS\LLM\Agents OpenAI\Agente_Bancario_Github\create_website.py", line 467, in main
    <h3 style="color: {primary_color}; margin-bottom: 10px;">{traducciones['WELCOME_MSG'].format(name=nombre[0])}</h3>
'''