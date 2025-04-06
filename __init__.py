from dataclasses import dataclass,field
import pandas as pd

import psycopg2
from typing import List,Dict
from dotenv import load_dotenv
import os 
load_dotenv()
conn = psycopg2.connect(
    dsn=os.getenv("CONEXION_BBDD")
)
cursor = conn.cursor()

@dataclass
class BankingContext:
    nif: str = None  # The NIF will be set via Streamlit
    data: Dict = field(default_factory=dict) 
    traducciones: Dict = field(default_factory=dict) 

def get_unique_variable_mov(variable) -> List[str]:
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
            query = f'''
            SELECT DISTINCT "{variable}"
            FROM movements
            '''
            
            # Execute query
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of IBANs
            unique_valors = [row[0] for row in results]
            
            return unique_valors
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def get_tipo_cliente_iban(IBAN) -> List[str]:
    """
    Retrieve unique tipo_cli de IBAN
    
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
            query = f'''
            SELECT DISTINCT "client_type"
            FROM movements
            where "identificador_contrato" = %s
            '''
            
            # Execute query
            cursor.execute(query,(IBAN,))
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of IBANs
            unique_valors = [row[0] for row in results]
            
            return unique_valors
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []   
    
def get_distinct_cifs_by_ibans(ibans: List[str]) -> List[str]:
    """
    Retrieve distinct CIFs for given IBANs from the iban_titulares table.
    
    Parameters:
    -----------
    ibans : List[str]
        List of IBAN numbers to retrieve CIFs for
    
    Returns:
    --------
    List[str]
        List of distinct CIFs associated with the given IBANs
    """
    # Database connection parameters
    try:
        # Create cursor
        with conn.cursor() as cursor:
            # Prepare the query to get distinct CIFs for the given IBANs
            query = '''
            SELECT DISTINCT "CIF"
            FROM "iban_titulares"
            WHERE "IBAN" IN %s AND "Titular" = 'SI'
            ORDER BY "CIF"
            '''
            
            # Execute query
            cursor.execute(query, (tuple(ibans),))
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of CIFs
            distinct_cifs = [row[0] for row in results]
            
            return distinct_cifs
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    

unique_contr_mov = get_unique_variable_mov("identificador_contrato")
unique_type_clie = get_unique_variable_mov("client_type")
unique_cifs_with_mov = get_distinct_cifs_by_ibans(unique_contr_mov)