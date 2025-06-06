import psycopg2
import unidecode
import textdistance
from agents import Agent, Runner, function_tool,ModelSettings
from typing import List
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel
# Connect to Supabase PostgreSQL (Session Pooler)
from dotenv import load_dotenv
import os 
load_dotenv()
import os 
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')
'''
conn = psycopg2.connect(
    dsn=os.getenv("CONEXION_BBDD")
)
cursor = conn.cursor()
'''
from __init__ import conn,cursor 

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
import re
from typing import Optional

from typing import List
from context import BankingContext


def check_and_update_language( nif: str) -> dict:
    """
    Check if the NIF exists in preferencias_clientes table.
    If it doesn't exist, insert a new row with the NIF and idioma='spanish'.
    
    Args:
        wrapper: The context wrapper
        nif: The NIF to check and potentially insert
        
    Returns:
        Dictionary with operation status and result
    """
    # First, check if the NIF exists
    check_query = '''
        SELECT "NIF", "idioma" 
        FROM "preferencias_clientes"
        WHERE "NIF" = %s
    '''
    
    cursor.execute(check_query, (nif,))
    result = cursor.fetchone()

    print("ress")
    print(result)
    
    if result:
        # NIF exists, return the current preference
        return {
            "exists": True,
            "nif": result[0],
            "idioma": result[1]
        }
    else:
        # NIF doesn't exist, insert new row with spanish as idioma
        
        
        # Commit the transaction to save changes
        # Make sure to use the proper connection object
        # connection.commit()
        
        return {
            "exists": False,
            "nif": nif,
            "idioma": "",
            "message": "New preference created"
        }

import psycopg2

def ActualizaIdioma(nif, idioma):
    try:
        # Verificar si el NIF ya existe en la tabla
        check_query = '''
            SELECT COUNT(*) 
            FROM preferencias_clientes 
            WHERE "NIF" = %s
        '''
        cursor.execute(check_query, (nif,))
        exists = cursor.fetchone()[0] > 0

        if exists:
            # Si el NIF existe, actualizamos el idioma
            update_query = '''
                UPDATE preferencias_clientes 
                SET "idioma" = %s 
                WHERE "NIF" = %s
            '''
            cursor.execute(update_query, (idioma, nif))
        else:
            # Si el NIF no existe, obtenemos las columnas e insertamos un nuevo registro
            columns_query = '''
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'preferencias_clientes'
            '''
            cursor.execute(columns_query)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Preparar nombres de columnas y valores para la inserción
            column_names = []
            values = []
            placeholders = []
            
            for column in columns:
                column_names.append(f'"{column}"')
                placeholders.append('%s')
                
                if column.lower() == 'nif':
                    values.append(nif)
                elif column.lower() == 'idioma':
                    values.append(idioma)
                else:
                    values.append("")  # Otros campos vacíos
            
            # Crear y ejecutar la consulta de inserción
            insert_query = f'''
                INSERT INTO "preferencias_clientes" ({', '.join(column_names)})
                VALUES ({', '.join(placeholders)})
            '''
            cursor.execute(insert_query, values)
        
        # Confirmar los cambios
        conn.commit()

    except psycopg2.Error as e:
        print(f"Error en la base de datos: {e}")
        conn.rollback()  # Revertir cambios en caso de error

class Idioma_Cliente(BaseModel):
    idioma: str
    """El idioma utilizado por el cliente"""

############################################################# Language  ###########################################################33
# Define the Send_Transfer_to_IBAN_receptor agent
get_language = Agent(
    name="get_language",
    instructions="""
    Given a user message, return the language the user is giving: The values you can return are Spanish, English, French, German, Catalan
    """,
    model=model,
    model_settings = ModelSettings(temperature=0),
    output_type=Idioma_Cliente  # Assuming it returns a confirmation message or error
)
