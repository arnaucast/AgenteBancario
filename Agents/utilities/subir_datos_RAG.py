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
from __init__ import conn,cursor 

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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

def upload_to_supabase(df):
    """Upload dataframe with embeddings to Supabase"""
    try:
        # Connect to Supabase

        drop_table_query = '''
            DROP TABLE IF EXISTS chatbot_responses;
        '''
        cursor.execute(drop_table_query)

        # Create table if it doesn't exist
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS chatbot_responses (
                id SERIAL PRIMARY KEY,
                respuesta_text TEXT NOT NULL,
                Tipo TEXT NOT NULL,
                respuesta_embedd VECTOR(1536)  -- OpenAI embeddings are 1536-dimensional
            );
        '''
        cursor.execute(create_table_query)

        # Prepare data for insertion
        data_to_insert = [
            (row['Respuestas'],row['Tipo'],row['respuesta_embedd'])
            for _, row in df.iterrows()
        ]

        # Insert data
        insert_query = '''
            INSERT INTO chatbot_responses (respuesta_text,Tipo, respuesta_embedd)
            VALUES %s
        '''
        # Convert embeddings to string format compatible with PostgreSQL vector type
        formatted_data = [
            (text, tipo,f'[{",".join(map(str, embedding))}]')
            for text,tipo, embedding in data_to_insert
        ]
        
        execute_values(cursor, insert_query, formatted_data)
        
        # Commit the transaction
        conn.commit()
        print("Data successfully uploaded to Supabase")

    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        conn.rollback()





if __name__ == "__main__":
    # Create fake banking explanations
    explicaciones_tarjetas = [
        "Para bloquear tu tarjeta en caso de robo tienes que ir a la pestaña de tarjetas, buscar tu tarjeta y bloquearla",
        "Para desbloquear tu tarjeta tienes que ir a la pestaña de tarjetas, buscar tu tarjeta y desbloquearla",
        "Si no puedes realizar compras, tienes que ir a mis tarjetas y analizar que no hayas superado el límite mensual de gasto o que la tarjeta no esté apagada o bloqueada",
        "Para aumentar el límite de tu tarjeta tienes que ir a tus tarjetas y aumentar el límite de la tarjeta que quieras",
        "El límite máximo mensual de una tarjeta es de 6000€",
        "Para apagar una  tarjeta puedes ir a mis tarjetas y apagarla"]

    explicaciones_transferencias = [
        "Para realizar una transferencia tienes que ir a la sección de transferencias, seleccionar la cuenta de origen, ingresar el destinatario y el importe, y confirmarla",
        "Si una transferencia no se ha procesado, verifica en el historial de movimientos que el saldo sea suficiente y que los datos del destinatario sean correctos",
        "Para cancelar una transferencia pendiente puedes ir a la sección de transferencias, buscar la operación en estado pendiente y seleccionar la opción de cancelar",
        "El límite diario para transferencias es de 10,000€, pero puedes ajustarlo en la configuración de límites si necesitas modificarlo",
        "Para programar una transferencia recurrente debes ir a transferencias, elegir la opción de programar, definir la frecuencia y confirmar los detalles",
        "Si necesitas comprobar el estado de una transferencia, ve a la sección de historial, busca la operación y revisa los detalles del movimiento"]

    datos_tarjetas = pd.DataFrame({"Respuestas": explicaciones_tarjetas,"Tipo":"Tarjetas"})
    datos_transferencias = pd.DataFrame({"Respuestas": explicaciones_transferencias,"Tipo":"Transferencias"})
    datos_unidos = pd.concat([datos_tarjetas, datos_transferencias],axis=0)
    print(datos_unidos.shape)
    # Assuming 'datos' is your dataframe
    # Example usage:
    # datos = pd.DataFrame({'respuesta BOT': ['response1', 'response2', ...]})
    
    # Step 1: Create embeddings
    datos_with_embeddings = create_embeddings_df(datos_unidos)
    print(datos_with_embeddings)
    # Step 2: Upload to Supabase
    upload_to_supabase(datos_with_embeddings)
