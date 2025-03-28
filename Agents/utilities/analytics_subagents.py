import psycopg2
import unidecode
import textdistance
from agents import Agent, Runner, function_tool
from typing import List
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel
# Connect to Supabase PostgreSQL (Session Pooler)
from dotenv import load_dotenv
import os 
load_dotenv()
conn = psycopg2.connect(
    dsn=os.getenv("CONEXION_BBDD")
)
from typing import List, Tuple
from openai import OpenAI
import numpy as np
cursor = conn.cursor()
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from typing import List, Union, Dict, Any
import re
from typing import Optional
from typing import List
from context import BankingContext
import os 
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
from .bank_movements_dealers import *


data = get_iban_data(["ES0081123456789012345678"])
print(data.info())
data = data[["fechahora","categoria","id_signo","importe"]]
############################################################# categories in text finder ######################################################################
CATEGORY_SEPARATOR_PROMPT = (
    """You are a precise agent that processes a user request for category analysis with the following specific instructions:
    1. Carefully identify the most relevant and directly requested category from the input.
    2. Prioritize the user's primary focus or main intent.
    3. If multiple categories are present, select ONLY the most specific or primary category that directly matches the user's core request.
    4. Return ONLY the most relevant category as a single-item list.
    5. If no clear primary category exists, return an empty list.

    Specific Matching Guidelines:
    - Look for the most explicit and central category in the user's request
    - Ignore peripheral or supplementary categories
    - Focus on the user's primary analytical intent

    Example 1:
    Input: "Quiero que me analices las compras de supermercado y los gastos que hago en medicación"
    Output: ["compras de supermercado"]

    Example 2:
    Input: "I want to analyze my salary payments and bank movements"
    Output: ["nomina (pagos de salario)"]

    Example 3:
    Input: "Give me an overview of everything"
    Output: []"""
)

class CategorySeparatorStr(BaseModel):
    category: str
    """The individual category or topic found in the message that the user wants analyzed"""

class CategorySeparatorLists(BaseModel):
    items_found: list[CategorySeparatorStr]
    """A list of all analysis categories found in the message."""

category_separator_agent = Agent(
    name="CategorySeparator",
    instructions=CATEGORY_SEPARATOR_PROMPT,
    model=model,
    output_type=CategorySeparatorLists
)

############################################################# Given categories, find the ones closer ######################################################################


def get_embeddings_batch(texts: List[str], client: OpenAI, embedding_model: str = "text-embedding-3-small") -> np.ndarray:
    """
    Get embeddings for multiple texts in a single API call
    """
    response = client.embeddings.create(
        input=texts, 
        model=embedding_model
    )
    return np.array([item.embedding for item in response.data])

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def preprocess_text(text: str) -> str:
    """
    Preprocess input text to improve matching
    - Convert to lowercase
    - Remove special characters
    - Normalize whitespace
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

categories = [
    "RESTAURANTES COMIDA RAPIDA - Quick service dining options",
    "RESTAURANTES BARES Y CAFETERIAS - Casual dining and drinks",
    "SUPERMERCADOS, PEQUENO COMERCIO - Grocery and small retail",
    "RETIRADA EFECTIVO - Cash withdrawal transactions",
    "INGRESO EFECTIVO - Cash deposit transactions",
    "TRANSFERENCIA EMITIDA - Outgoing bank transfers",
    "TRANSFERENCIA RECIBIDA - Incoming bank transfers",
    "ASOCIACIONES Y ONGs - Charities and non-profits",
    "ESTANCO - Tobacco and stamp shops",
    "ELECTRODOMESTICOS, INFORMATICA Y ELECTRONICA - Appliances and tech purchases",
    "JOYAS Y COMPLEMENTOS - Jewelry and accessories",
    "LOTERIAS Y APUESTAS - Lottery and gambling expenses",
    "REGALOS - Gift-related purchases",
    "ROPA Y CALZADO - Clothing and footwear",
    "MATERIAL DEPORTIVO - Sports equipment purchases",
    "CENTROS DEPORTIVOS - Sports facility fees",
    "ASOCIACIONES DE PADRES Y MADRES - Parent-teacher association costs",
    "EDUCACION - School and learning expenses",
    "UNIVERSIDAD Y ESTUDIOS SUPERIORES - Higher education costs",
    "AGUA Y SANEAMIENTO - Water and sanitation bills",
    "ENERGIA Y GAS - Electricity and gas bills",
    "HOGAR - Household goods and services",
    "GASTOS DE ALQUILER - Rental payment expenses",
    "INGRESOS DE ALQUILER - Rental income received",
    "NOMINA - Salary or payroll income",
    "PENSION SS - Social security pension",
    "PENSION ALIMENTICIA - Child support payments",
    "FONDOS DE INVERSION - Investment fund transactions",
    "VALORES - Stock and securities trading",
    "CRIPTOMONEDAS - Cryptocurrency-related transactions",
    "AMAZON - Amazon online purchases",
    "ALIEXPRESS - AliExpress online purchases",
    "NEOBANCOS - Digital banking services",
    "MUSICA E INSTRUMENTOS - Music and instrument costs",
    "OCIO Y CULTURA - Leisure and cultural activities",
    "PRESTAMO - Loan-related payments",
    "HIPOTECA - Mortgage payment expenses",
    "RENTING/LEASING - Leasing or renting costs",
    "SEGUROS - Insurance policy payments",
    "COMBUSTIBLE Y RECARGA - Fuel and vehicle charging",
    "PARKING Y GARAJE - Parking and garage fees",
    "TRANSPORTE TREN - Train travel expenses",
    "TRANSPORTE AVION - Air travel expenses",
    "TRANSPORTE TAXI - Taxi service costs",
    "PEAJES - Toll road fees"
]
def create_transaction_categorizer(embedding_model: str = "text-embedding-3-small"):
    """
    Create a transaction categorizer with precomputed category embeddings
    """
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
    
    # Precompute category embeddings
    category_embeddings = get_embeddings_batch(categories, client, embedding_model)
    
    def classify_transaction(transaction_text: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Classify transaction using embedding-based similarity
        """
        # Preprocess input
        processed_text = preprocess_text(transaction_text)
        
        # Get embedding for input text
        input_embedding = get_embeddings_batch([processed_text], client, embedding_model)[0]
        
        # Compute similarities with all categories
        similarities = [
            cosine_similarity(input_embedding, cat_emb) 
            for cat_emb in category_embeddings
        ]
        
        # Get top candidates based on embedding similarity
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        # Prepare results with top candidates, stripping descriptions
        candidates = [
            (categories[idx].split(" - ")[0], similarities[idx])  # Take only the category name
            for idx in top_indices
        ]
        
        return candidates
    
    return classify_transaction

async def Given_List_categ_find_names(list_categ: List[str],top_to_show:int) -> List[Tuple[str, List[str]]]:
    """
    Return a list of tuples, each containing the transaction text and its top category names
    """
    categorize_transaction = create_transaction_categorizer()
    result = []
    
    for trans in list_categ:
        print("Transaction is")
        print(trans)
        candidates = categorize_transaction(trans, top_n=top_to_show)
        print("Transb")
        # Extract only the category names from the candidates
        category_names = [category for category, score in candidates]
        print(category_names)
        # Append tuple of (transaction_text, list_of_categories)
        result.append((trans, category_names))
    
    return result


#################################################### Given a user request and categories, select the top caategories ########################

CATEGORY_FILTRATOR = (
    """You are an agent that processes a user request and a list of tuples, where each tuple contains (text, possible categories in that text).
    Your task is to analyze the user message and return a new list of unique categories that match the user's intent, selected from the provided categories.
    
    - Focus on understanding the user's request and identify the key topics or terms they are asking about.
    - From the provided tuple list, extract only the categories that directly relate to the user's request.
    - One text may have multiple relevant categories; include all that make sense based on the context.
    - Ensure the output contains only unique categories (no duplicates).
    
    Example:
    - User message: "I want to know my salary for the last 12 months and also las salidas en efectivo"
    - Input categories: [('sueldo (salarios recibidos)', ['INGRESOS DE ALQUILER', 'NOMINA', 'TRANSFERENCIA RECIBIDA']),
                        ('Retiradas de efectivo'),['RETIRADA EFECTIVO', 'INGRESO EFECTIVO']]
    - Output: ['NOMINA', 'RETIRADA EFECTIVO']
    - Don't return the text, only categories
    """
)

class Categories_Filtered(BaseModel):
    category: str
    """The individual category or topic found in the message that the user wants analyzed"""

class Categories_FilteredList(BaseModel):
    items_found: list[Categories_Filtered]
    """A list of all analysis categories found in the message."""

category_filterer = Agent(
    name="CategoryFiltrator",
    instructions=CATEGORY_FILTRATOR,
    model=model,
    output_type=Categories_FilteredList
)


#################################################### Programmer #####################################################################################
@function_tool
def execute_complex_query2(code: str) -> any:
    """
    Execute a multi-line Python code snippet with robust result handling.

    Parameters:
    - code: Multi-line Python code string

    Returns:
    - Flexible result handling for various code patterns
    """
    print("################ CODE GENERATED BY THE AGENT ########################")
    print(code)
    
    # Create a local namespace with the dataframe
    local_namespace = {'table': data}  # 'data' assumed to be available globally or passed

    try:
        # Split the code into lines
        code_lines = code.strip().split('\n')
        
        # Execute all lines except the last one
        for line in code_lines[:-1]:
            exec(line, globals(), local_namespace)
        
        # Evaluate the last line
        last_line = code_lines[-1].strip()
        
        # Sophisticated result extraction
        try:
            # Try to evaluate the last line
            result = eval(last_line, globals(), local_namespace)
            
            # Handle different return types
            if isinstance(result, (list, tuple, dict)):
                return result
            
            # If it's a simple value, wrap it
            return result
        
        except Exception as e:
            # If evaluation fails, try execution
            try:
                exec(last_line, globals(), local_namespace)
                
                # Check for common variable assignment patterns
                if '=' in last_line:
                    # Handle chained assignments and multiple assignments
                    assigned_vars = [var.strip() for var in last_line.split('=')[0].split(',')]
                    result = {var: local_namespace.get(var) for var in assigned_vars if var in local_namespace}
                    return result
                
                return None
            
            except Exception as exec_error:
                print(f"\n!!! EXECUTION ERROR: {exec_error}")
                return {'error': str(exec_error)}
    
    except Exception as e:
        print(f"\n!!! OVERALL ERROR: {e}")
        return {'error': str(e)}
    
import traceback

@function_tool
def execute_complex_query(code: str) -> any:
    """
    Execute a multi-line Python code snippet with robust result handling.

    Parameters:
    - code: Multi-line Python code string

    Returns:
    - Flexible result handling for various code patterns
    """
    print("################ CODE GENERATED BY THE AGENT ########################")
    print(code)
    
    # Create a local namespace with the dataframe
    local_namespace = {'table': data}  # 'data' assumed to be available globally or passed

    try:
        # Preprocess the code to handle multiline dictionary and other complex declarations
        processed_code = preprocess_code(code)
        print("Processed code")
        print(processed_code)
        
        # Split the processed code into lines
        code_lines = processed_code.strip().split('\n')
        
        # Execute all lines except the last o
        # ne
        for line in code_lines[:-1]:
            exec(line, globals(), local_namespace)
        
        # Evaluate the last line
        last_line = code_lines[-1].strip()
        
        # Sophisticated result extraction
        try:
            # Try to evaluate the last line
            result = eval(last_line, globals(), local_namespace)
            
            # Handle different return types
            if isinstance(result, (list, tuple, dict)):
                return result
            
            # If it's a simple value, wrap it
            return result
        
        except Exception as e:
            # If evaluation fails, try execution
            try:
                exec(last_line, globals(), local_namespace)
                
                # Check for common variable assignment patterns
                if '=' in last_line:
                    # Handle chained assignments and multiple assignments
                    assigned_vars = [var.strip() for var in last_line.split('=')[0].split(',')]
                    result = {var: local_namespace.get(var) for var in assigned_vars if var in local_namespace}
                    return result
                
                return None
            
            except Exception as exec_error:
                print(f"\n!!! EXECUTION ERROR: {exec_error}")
                traceback.print_exc()
                return {'error': str(exec_error)}
    
    except Exception as e:
        print(f"\n!!! OVERALL ERROR: {e}")
        traceback.print_exc()
        return {'error': str(e)}

def preprocess_code(code: str) -> str:
    """
    Preprocess code to handle multiline dictionary, list, and complex declarations.

    Args:
        code (str): Original code string

    Returns:
        str: Processed code string
    """
    # Remove commented lines
    lines = [line for line in code.split('\n') if not line.strip().startswith('#')]

    # Handle multiline declarations
    processed_lines = []
    current_statement = []
    in_multiline = False
    paren_count = 0
    brace_count = 0
    bracket_count = 0

    for line in lines:
        stripped_line = line.strip()

        # Count opening and closing delimiters
        paren_count += stripped_line.count('(') - stripped_line.count(')')
        brace_count += stripped_line.count('{') - stripped_line.count('}')
        bracket_count += stripped_line.count('[') - stripped_line.count(']')

        # Check if we're in a multiline statement
        if (('(' in stripped_line and paren_count > 0) or 
            ('{' in stripped_line and brace_count > 0) or
            ('[' in stripped_line and bracket_count > 0)):
            if not in_multiline:
                in_multiline = True
            current_statement.append(stripped_line)
            continue

        # Continuing a multiline statement
        if in_multiline:
            current_statement.append(stripped_line)

            # Check if multiline statement is complete
            if paren_count == 0 and brace_count == 0 and bracket_count == 0:
                # Join without newlines and minimal whitespace
                combined = ' '.join(current_statement)
                # Remove any remaining newlines and extra spaces
                combined = ''.join(combined.splitlines())
                combined = ' '.join(combined.split())
                processed_lines.append(combined)
                current_statement = []
                in_multiline = False
            continue

        # Regular line
        if not in_multiline:
            processed_lines.append(line)

    # If statement was not closed, combine it
    if current_statement:
        combined = ' '.join(current_statement)
        combined = ''.join(combined.splitlines())
        combined = ' '.join(combined.split())
        processed_lines.append(combined)

    return '\n'.join(processed_lines)

bank_query_agent = Agent(
    name="Bank Movement Insight Agent",
    instructions="""
You are a data analysis expert for bank movement insights. Your goal is to:

1. Answer only the user's specific question, avoiding unrelated analysis
2. Use pandas for precise data manipulation
3. Return your finds to the agent so it can analyze them
4. Provide actionable insights based solely on relevant data

DataFrame columns:
- fechahora: Transaction date, dtype = datetime64[ns]
- categoria: Transaction category, dtype = object
- importe: Transaction amount, dtype = float64
- id_signo: Transaction sign (+1 income, -1 expense), dtype = int64

Rules:
- Use 'table' as the DataFrame name
- Filter data only for the user's request (e.g., specific categories or timeframes)
- Avoid computing or returning data beyond the question’s scope
- Last line must return a summary of key findings (e.g., totals, averages)
- Keep analysis focused, efficient, and insight-driven
    """,
    model=model,
    tools=[execute_complex_query]
)


