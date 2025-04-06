import psycopg2
from agents import Agent, Runner, function_tool
from typing import List
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel
# Connect to Supabase PostgreSQL (Session Pooler)
from dotenv import load_dotenv
import os 
load_dotenv()
'''
conn = psycopg2.connect(
    dsn=os.getenv("CONEXION_BBDD")
)
cursor = conn.cursor()
'''
from __init__ import conn,cursor 

import pandas as pd
import re
from typing import Optional

from typing import List
from context import BankingContext

def get_iban_data(ibans: List[str]) -> pd.DataFrame:
    """
    Retrieve contract data for specified IBANs from Supabase and convert to DataFrame.
    
    Parameters:
    -----------
    ibans : List[str]
        List of IBAN numbers to retrieve data for
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing contract data with datetime conversion
    """
    
    try:
        # Create cursor
        with conn.cursor() as cursor:
            # Prepare the query with parameterized input for IBANs
            query = '''
            SELECT 
                identificador_contrato, 
                fechahora, 
                categoria, 
                id_signo, 
                importe, 
                client_type
            FROM movements
            WHERE identificador_contrato IN %s
            '''
            
            # Execute query
            cursor.execute(query, (tuple(ibans),))
            
            # Fetch results
            columns = [
                'identificador_contrato', 
                'fechahora', 
                'categoria', 
                'id_signo', 
                'importe', 
                'client_type'
            ]
            
            # Fetch data and convert to DataFrame
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            
            # Convert fechahora to datetime
            df['fechahora'] = pd.to_datetime(df['fechahora'], format='%Y-%m-%d %H:%M:%S')
            
            return df
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    

def get_unique_ibans_by_client_type(client_type: str) -> List[str]:
    """
    Retrieve unique IBANs for a specific client type from the database.
    
    Parameters:
    -----------
    client_type : str
        The client type to filter by
    
    Returns:
    --------
    List[str]
        A list of unique IBAN numbers for the specified client type
    """

    try:
        # Create cursor
        with conn.cursor() as cursor:
            # Prepare the query to get unique IBANs for the specified client type
            query = '''
            SELECT DISTINCT identificador_contrato
            FROM movements
            WHERE client_type = %s
            ORDER BY identificador_contrato
            '''
            
            # Execute query
            cursor.execute(query, (client_type,))
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of IBANs
            unique_ibans = [row[0] for row in results]
            
            return unique_ibans
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    
# Example usage
# unique_corporate_ibans = get_unique_ibans_by_client_type('corporate')
# print(unique_corporate_ibans)

