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

from __init__ import conn,cursor 

import pandas as pd
import numpy as np
from openai import OpenAI
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))








import pandas as pd


# Optionally save to CSV if needed
# datos.to_csv("banking_explanations.csv", index=False)

# Main execution
if __name__ == "__main__":
    # Assuming 'datos' is your dataframe
    # Example usage:
    # datos = pd.DataFrame({'respuesta BOT': ['response1', 'response2', ...]})
    
    # Step 1: Create embeddings
    datos_with_embeddings = create_embeddings_df(datos)
    print("Embeddings created")
    print(len(datos_with_embeddings["respuesta_embedd"].iloc[0]))
    
    # Step 2: Upload to Supabase
    upload_to_supabase(datos_with_embeddings)
    print("Upload supabase")
    
    # Step 3: Test the matching function
    test_text = "SI want to know what is the credit score"
    top_matches = get_top3_matches(test_text)
    
    print("\nTop 3 matches:")
    for i, match in enumerate(top_matches, 1):
        print(f"{i}. Text: {match['text']}")
        print(f"   Similarity: {match['similarity']:.4f}")
        
