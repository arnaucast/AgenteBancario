

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
from agents import Runner
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')


import pandas as pd
import numpy as np
from openai import OpenAI
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
conn = psycopg2.connect(
    dsn=os.getenv("CONEXION_BBDD")
)
cursor = conn.cursor()
#from __init__ import conn,cursor 

# Load environment variables
load_dotenv()
api_key =  os.getenv("OPENAI_API_KEY")
print(api_key)
# Initialize OpenAI client
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


print(client)
def get_embedding(text):
    """Generate embedding for a given text using OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def create_embeddings_df(df):
    """Add embeddings column to the dataframe"""
    df['respuesta_embedd'] = df['Respuestas'].apply(get_embedding)
    return df


def get_top3_matches(input_text,filter):
    """Find top 3 matching responses from Supabase based on cosine similarity"""
    try:
     
        # Get embedding for input text
        input_embedding = get_embedding(input_text)

        # Query to find top 3 matches using cosine similarity
        # Note: This assumes your Supabase has vector extension enabled
        query = '''
            SELECT respuesta_text, 
                   1 - (respuesta_embedd <=> %s::vector) as similarity
            FROM chatbot_responses
            WHERE  "tipo" = %s
            ORDER BY similarity DESC
            LIMIT 3;
        '''
        # Convert input embedding to string format
        embedding_str = f'[{",".join(map(str, input_embedding))}]'
             
        cursor.execute(query, (embedding_str,filter))
        results = cursor.fetchall()
      
        # Format results
        matches = [
            {"text": row[0], "similarity": row[1]}
            for row in results
        ]
        
        return matches

    except Exception as e:
        print(f"Error querying Supabase: {e}")
        return []
    
################################################# Agent Category Detector ##############################################
# Define the Send_Transfer_to_IBAN_receptor agent


class CategoryFound(BaseModel):
    category: str
    """Exact name of category found"""


category_detector  = Agent(
    name="category_detector",
    instructions="""
    Ypu are an agent that given a bank client request, you return 
    the exact name of the category most likely needed to respond the question or doubt.
    Choose from this categories names:
        Transferencias: for questions related to transfers
        Tarjetas: for questions related to credit cards
        "": if no category matches

    For example:
    Quiero saber como hacer una transferencia. You return Transferencias

    """,
    model=model,
    output_type=CategoryFound  # Assuming it returns a confirmation message or error
)