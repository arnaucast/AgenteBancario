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
from __init__ import BankingContext

'''
@function_tool
def get_ibans2() -> List[str]:
    """If a client doesn't specify the IBAN from which to send a transfer, call this tool to get it"""
    query = 'SELECT "IBAN" FROM "iban_titulares WHERE "CIF" = %s AND "Titular" = %s'
    cursor.execute(query, (cif_cliente, "SI"))
    results = cursor.fetchall()
    # Convert tuple results to a list of IBANs
    if results:
        return [row[0] for row in results]
    return []
'''

def get_all_distinct_cifs() -> List[str]:
    """Retrieve all distinct CIFs from the iban_titulares table."""
    query = 'SELECT DISTINCT "CIF" FROM "iban_titulares" where "Titular" = %s ORDER BY "CIF"'
    cursor.execute(query,("SI",))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []

@function_tool
def get_ibans(wrapper: RunContextWrapper['BankingContext']) -> List[str]:
    """If a client doesn't specify the IBAN from which to send a transfer, call this tool to get it"""
    # Use NIF from context if available, otherwise fallback to imported cif_cliente
    nif = wrapper.context.nif if wrapper and wrapper.context and wrapper.context.nif else ""
    if nif == "":
        return []
    
    query = 'SELECT DISTINCT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s AND "Titular" = %s'
    cursor.execute(query, (nif, "SI"))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []

def get_ibans_for_nif(nif) -> List[str]:
    """If a client doesn't specify the IBAN from which to send a transfer, call this tool to get it"""
    # Use NIF from context if available, otherwise fallback to imported cif_cliente
    if nif == "":
        return []
    
    query = 'SELECT DISTINCT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s'
    cursor.execute(query, (nif,))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []

def get_ibans_for_web(nif) -> List[str]:
    """If a client doesn't specify the IBAN from which to send a transfer, call this tool to get it"""
    # Use NIF from context if available, otherwise fallback to imported cif_cliente
    query = 'SELECT distinct "IBAN" FROM "iban_titulares" WHERE "CIF" = %s AND "Titular" = %s'
    cursor.execute(query, (nif, "SI"))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []

def get_name_for_web(nif) -> List[str]:
    """If a client doesn't specify the IBAN from which to send a transfer, call this tool to get it"""
    # Use NIF from context if available, otherwise fallback to imported cif_cliente
    query = 'SELECT distinct "Nombre", "Apellidos" FROM "iban_titulares" WHERE "CIF" = %s'
    cursor.execute(query, (nif, ))
    results = cursor.fetchall()
    if results:
        return [(row[0] + " " +  row[1]) for row in results]
    return []

@function_tool
def validate_iban_ft(iban: str) -> bool:
    """
    Validates an IBAN using the standard MOD-97 algorithm and country-specific format rules.
    
    Args:
        iban: The IBAN to validate (can include spaces)
    
    Returns:
        bool: True if IBAN is valid, False otherwise
    """
    # Remove spaces and convert to uppercase
    iban = iban.replace(" ", "").upper()
    
    # Basic format check
    if not all(c.isalnum() for c in iban):
        return False
    
    # Check if IBAN has at least the minimum required length
    if len(iban) < 15:  # Shortest valid IBAN (Norway)
        return False
    
    # Extract country code
    country_code = iban[:2]
    
    # Country-specific length validation
    country_lengths = {
        "AL": 28, "AD": 24, "AT": 20, "AZ": 28, "BH": 22, "BY": 28, "BE": 16, "BA": 20,
        "BR": 29, "BG": 22, "BI": 27, "CR": 22, "HR": 21, "CY": 28, "CZ": 24, "DK": 18,
        "DJ": 27, "DO": 28, "EG": 29, "SV": 28, "EE": 20, "FK": 18, "FO": 18, "FI": 18,
        "FR": 27, "GE": 22, "DE": 22, "GI": 23, "GR": 27, "GL": 18, "GT": 28, "VA": 22,
        "HN": 28, "HU": 28, "IS": 26, "IQ": 23, "IE": 22, "IL": 23, "IT": 27, "JO": 30,
        "KZ": 20, "XK": 20, "KW": 30, "LV": 21, "LB": 28, "LY": 25, "LI": 21, "LT": 20,
        "LU": 20, "MT": 31, "MR": 27, "MU": 30, "MD": 24, "MC": 27, "MN": 20, "ME": 22,
        "NL": 18, "NI": 28, "MK": 19, "NO": 15, "PK": 24, "PS": 29, "PL": 28, "PT": 25,
        "QA": 29, "RO": 24, "RU": 33, "LC": 32, "SM": 27, "ST": 25, "SA": 24, "RS": 22,
        "SC": 31, "SK": 24, "SI": 19, "SO": 23, "ES": 24, "SD": 18, "OM": 23, "SE": 24,
        "CH": 21, "TL": 23, "TN": 24, "TR": 26, "UA": 29, "AE": 23, "GB": 22, "VG": 24,
        "YE": 30
    }
    
    # Check if country code exists in our database
    if country_code not in country_lengths:
        return False
    
    # Check if IBAN length matches expected length for that country
    if len(iban) != country_lengths[country_code]:
        return False
    
    return True
    
    '''
    # SEPA countries (for additional context if needed)
    sepa_countries = {
        "AD", "AT", "BE", "BG", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GI", "GR", "VA",
        "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", "NL", "NO", "PL", "PT", "RO",
        "SK", "SI", "ES", "SE", "CH", "GB"
    }
    
    # Move first 4 characters to the end
    rearranged_iban = iban[4:] + iban[:4]
    
    # Convert letters to numbers (A=10, B=11, ..., Z=35)
    numerical_iban = ""
    for char in rearranged_iban:
        if char.isalpha():
            numerical_iban += str(ord(char) - ord('A') + 10)
        else:
            numerical_iban += char
    
    # Check if mod 97 equals 1 (international standard validation)
    try:
        return int(numerical_iban) % 97 == 1
    except ValueError:
        # In case numerical_iban is too large for int conversion
        # Process in chunks
        remainder = 0
        chunk_size = 9  # Process 9 digits at a time
        
        for i in range(0, len(numerical_iban), chunk_size):
            chunk = numerical_iban[i:i+chunk_size]
            remainder = (remainder * (10 ** len(chunk)) + int(chunk)) % 97
        
        return remainder == 1
    '''

def validate_iban(iban: str) -> bool:
    """
    Validates an IBAN using the standard MOD-97 algorithm and country-specific format rules.
    
    Args:
        iban: The IBAN to validate (can include spaces)
    
    Returns:
        bool: True if IBAN is valid, False otherwise
    """
    # Remove spaces and convert to uppercase
    iban = iban.replace(" ", "").upper()
    
    # Basic format check
    if not all(c.isalnum() for c in iban):
        return False
    
    # Check if IBAN has at least the minimum required length
    if len(iban) < 15:  # Shortest valid IBAN (Norway)
        return False
    
    # Extract country code
    country_code = iban[:2]
    
    # Country-specific length validation
    country_lengths = {
        "AL": 28, "AD": 24, "AT": 20, "AZ": 28, "BH": 22, "BY": 28, "BE": 16, "BA": 20,
        "BR": 29, "BG": 22, "BI": 27, "CR": 22, "HR": 21, "CY": 28, "CZ": 24, "DK": 18,
        "DJ": 27, "DO": 28, "EG": 29, "SV": 28, "EE": 20, "FK": 18, "FO": 18, "FI": 18,
        "FR": 27, "GE": 22, "DE": 22, "GI": 23, "GR": 27, "GL": 18, "GT": 28, "VA": 22,
        "HN": 28, "HU": 28, "IS": 26, "IQ": 23, "IE": 22, "IL": 23, "IT": 27, "JO": 30,
        "KZ": 20, "XK": 20, "KW": 30, "LV": 21, "LB": 28, "LY": 25, "LI": 21, "LT": 20,
        "LU": 20, "MT": 31, "MR": 27, "MU": 30, "MD": 24, "MC": 27, "MN": 20, "ME": 22,
        "NL": 18, "NI": 28, "MK": 19, "NO": 15, "PK": 24, "PS": 29, "PL": 28, "PT": 25,
        "QA": 29, "RO": 24, "RU": 33, "LC": 32, "SM": 27, "ST": 25, "SA": 24, "RS": 22,
        "SC": 31, "SK": 24, "SI": 19, "SO": 23, "ES": 24, "SD": 18, "OM": 23, "SE": 24,
        "CH": 21, "TL": 23, "TN": 24, "TR": 26, "UA": 29, "AE": 23, "GB": 22, "VG": 24,
        "YE": 30
    }
    
    # Check if country code exists in our database
    if country_code not in country_lengths:
        return False
    
    # Check if IBAN length matches expected length for that country
    if len(iban) != country_lengths[country_code]:
        return False
    
    return True
    
    '''
    # SEPA countries (for additional context if needed)
    sepa_countries = {
        "AD", "AT", "BE", "BG", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GI", "GR", "VA",
        "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", "NL", "NO", "PL", "PT", "RO",
        "SK", "SI", "ES", "SE", "CH", "GB"
    }
    
    # Move first 4 characters to the end
    rearranged_iban = iban[4:] + iban[:4]
    
    # Convert letters to numbers (A=10, B=11, ..., Z=35)
    numerical_iban = ""
    for char in rearranged_iban:
        if char.isalpha():
            numerical_iban += str(ord(char) - ord('A') + 10)
        else:
            numerical_iban += char
    
    # Check if mod 97 equals 1 (international standard validation)
    try:
        return int(numerical_iban) % 97 == 1
    except ValueError:
        # In case numerical_iban is too large for int conversion
        # Process in chunks
        remainder = 0
        chunk_size = 9  # Process 9 digits at a time
        
        for i in range(0, len(numerical_iban), chunk_size):
            chunk = numerical_iban[i:i+chunk_size]
            remainder = (remainder * (10 ** len(chunk)) + int(chunk)) % 97
        
        return remainder == 1
    '''
    
class CheckIfIBANCorrect(BaseModel):
    IBAN_correct_format: bool = Field(
        description="Whether the IBAN passes validation through the validate_iban function"
    )
    detected_iban_emisor: Optional[str] = Field(
        default=None, 
        description="The detected IBAN if found, or None"
    )
    country: Optional[str] = Field(
        default=None,
        description="The country associated with the IBAN if detected"
    )

guardrail_agent = Agent(
    name="Check_IBAN_correct",
    instructions="""
    Analyze user input to detect IBAN emsisor information and determine:

    1. Does the input contain an IBAN emsior?
    2. Is the IBAN emisor valid? (Use the validate_iban_ft function.)
    3. Does the IBAN emisor belong to the sender? (Look for phrases like "my IBAN", "from my account", or "transfer from".)

    Rules:
    - If no IBAN is found:
    - Return: IBAN_correct_format = false, detected_iban_emisor = null, country = null.
    - If an IBAN  emisor is found:
    - Set detected_iban_emisor to the IBAN of the emisor
    - Set country to the IBAN’s country (from validate_iban).
    - Set IBAN_correct_format to true if validate_iban says it’s valid, false if not.
    """,
    tools=[validate_iban_ft],
    output_type=CheckIfIBANCorrect,
)

def CheckIfIBANBelongs(IBAN,nif):
    try:
        query = 'SELECT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s  AND "IBAN" = %s'
        cursor.execute(query, (nif, IBAN))
        result = cursor.fetchone()
        
        if not result:
            return False
        else: 
            return True
    except:
        return False
    
   
class CheckTransferDetails(BaseModel):
    IBAN_receptor_defined: bool = Field(
        description="True if IBAN of the receptor of the transfer is defined"
    )
    IBAN_receptor_correct_format: bool = Field(
        description="True if IBAN receptor has correct format"
    )
    Importe_transfer_defined: bool = Field(
        description="True if importe of the transfer is defined"
    )


guardrail_agent_transf = Agent(
    name="Check_Transfer_Details",
    instructions="""
    Analyze user input to detect IBAN receptor information is correct and determine:

    1. Does the input contain an IBAN receptor of the transfer?
    2. Is the IBAN receptorsor valid? (Use the validate_iban function.)

    Rules:
    - If no IBAN  receptor is found and no Importe_transfer_defined found
    - Return: IBAN_receptor_defined = false,IBAN_receptor_correct_format=False Importe_transfer_defined = false
    - Make sure you don't confound the IBAN given in Este cliente tiene los siguientes IBAN... These IBANs are of the client that wants to make the transfer
    """,
    tools=[validate_iban_ft],
    output_type=CheckTransferDetails,
) 
@input_guardrail
async def iban_emisor_guardrail_v2(
    ctx: RunContextWrapper['BankingContext'], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Guardrail to check if an IBAN is provided, valid, and belongs to the client."""
    print("Processing input for IBAN validation")

    # Handle different input types
    if isinstance(input, str):
        input_str = input
    elif isinstance(input, list):
        # Handle dictionary inputs (common in conversation history)
        if all(isinstance(item, dict) for item in input):
            # Extract content from dictionaries
            input_str = " ".join([item.get('content', '') for item in input])
        else:
            # Fallback for other object types
            input_str = " ".join([str(item) for item in input])
    else:
        input_str = str(input)
    
    # Run the IBAN validation guardrail agent
    result = await Runner.run(guardrail_agent_transf, input_str, context=ctx.context)
    iban_check_result = result.final_output_as(CheckTransferDetails)
    
    if  not iban_check_result.IBAN_receptor_defined and not iban_check_result.Importe_transfer_defined:
        print("HOLA1")
        return GuardrailFunctionOutput(
            output_info={
                "message": f"{ctx.context.traducciones['IBAN_VALIDAR_MSG1']}"
            },
            tripwire_triggered=True
        )
    if  not iban_check_result.IBAN_receptor_defined and  iban_check_result.Importe_transfer_defined:
        print("HOLA1")
        return GuardrailFunctionOutput(
            output_info={
                "message": f"{ctx.context.traducciones['IBAN_VALIDAR_MSG2']}"
            },
            tripwire_triggered=True
        )
    # If no IBAN was detected or the IBAN is invalid
    if  iban_check_result.IBAN_receptor_defined and not iban_check_result.IBAN_receptor_correct_format:
        print("HOLA2")
        return GuardrailFunctionOutput(
            output_info={
                "message": f"{ctx.context.traducciones['IBAN_VALIDAR_MSG3']}"
            },
            tripwire_triggered=True
        )
    
        # If no IBAN was detected or the IBAN is invalid
    if  iban_check_result.IBAN_receptor_defined and  iban_check_result.IBAN_receptor_correct_format and not iban_check_result.Importe_transfer_defined:
        print("HOLA2")
        return GuardrailFunctionOutput(
            output_info={
                "message": f"{ctx.context.traducciones['IBAN_VALIDAR_MSG4']}"
            },
            tripwire_triggered=True
        )

    # IBAN is valid, belongs to the sender, and is registered to the client
    return GuardrailFunctionOutput(
        output_info={
            "message": f"{ctx.context.traducciones['IBAN_VALIDAR_MSG5']}"
        },
        tripwire_triggered=False
    )

@input_guardrail
async def iban_emisor_guardrail(
    ctx: RunContextWrapper['BankingContext'], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Guardrail to check if an IBAN is provided, valid, and belongs to the client."""
    print("Processing input for IBAN validation")

    # Handle different input types
    if isinstance(input, str):
        input_str = input
    elif isinstance(input, list):
        # Handle dictionary inputs (common in conversation history)
        if all(isinstance(item, dict) for item in input):
            # Extract content from dictionaries
            input_str = " ".join([item.get('content', '') for item in input])
        else:
            # Fallback for other object types
            input_str = " ".join([str(item) for item in input])
    else:
        input_str = str(input)
    
    # Run the IBAN validation guardrail agent
    result = await Runner.run(guardrail_agent, input_str, context=ctx.context)
    iban_check_result = result.final_output_as(CheckIfIBANCorrect)
    
    if  iban_check_result.detected_iban_emisor ==None:
        print("HOLA1")
        return GuardrailFunctionOutput(
            output_info={
                "message": "All correct"
            },
            tripwire_triggered=False
        )
    # If no IBAN was detected or the IBAN is invalid
    if   iban_check_result.detected_iban_emisor != None and not iban_check_result.IBAN_correct_format:
        print("HOLA2")
        return GuardrailFunctionOutput(
            output_info={
                "message": "Please provide a valid IBAN to proceed with the transfer. "
                           "For example ES0081122233445566778888"
            },
            tripwire_triggered=True
        )
    
    # Extract the detected IBAN (already validated by the guardrail agent)
    iban_emisor = iban_check_result.detected_iban_emisor.replace(" ", "")  # Remove spaces
    
    # Check if the IBAN belongs to the client using database lookup
    try:
        query = 'SELECT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s AND "Titular" = %s AND "IBAN" = %s'
        cursor.execute(query, (ctx.context.nif, 'SI', iban_emisor))
        result = cursor.fetchone()
        
        if not result:
            print("HOLA3")
            return GuardrailFunctionOutput(
                output_info={
                    "message": "The provided IBAN does not belong to you. Please provide a valid IBAN that is registered to your account."
                },
                tripwire_triggered=True
            )
        
    except Exception as e:
        print("HOLA4")
        # Handle database errors
        print(f"Database error: {e}")
        
        # Roll back the failed transaction
        try:
            conn.rollback()  # Assuming 'connection' is your database connection object
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")
        
        return GuardrailFunctionOutput(
            output_info={
                "message": "We're experiencing technical difficulties verifying your account. Please try again later."
            },
            tripwire_triggered=True
        )
    print("HOLA5")
    # IBAN is valid, belongs to the sender, and is registered to the client
    return GuardrailFunctionOutput(
        output_info={
            "message": "IBAN verification successful.",
            "iban_emisor": iban_emisor,
            "country": iban_check_result.country
        },
        tripwire_triggered=False
    )

@function_tool
def check_iban_ownership(wrapper: RunContextWrapper['BankingContext'],iban: str) -> str:
    """Checks if the provided IBAN belongs to the client (cif_cliente) as a titular"""
    query = 'SELECT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s AND "Titular" = "SI" AND "IBAN" = %s'
    cursor.execute(query, (wrapper.context.nif, iban))
    result = cursor.fetchone()
    if result:
        return "Este IBAN es del cliente"
    return "Este IBAN no es del cliente"

def get_saldos_by_IBAN(IBAN:str):
    """Con esta herramienta consigues el saldo del cliente para un IBAN"""
    query = 'SELECT "Saldo" FROM "saldos" WHERE "IBAN" = %s'
    cursor.execute(query, (IBAN,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

@function_tool
def get_saldos_by_IBAN_ft(IBAN:str):
    query = 'SELECT "Saldo" FROM "saldos" WHERE "IBAN" = %s'
    cursor.execute(query, (IBAN,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# Function to get the Titular de Gestión details by IBAN
def get_titular_de_gestion(iban):
    query = 'SELECT "Nombre", "Apellidos" FROM "iban_titulares" WHERE "IBAN" = %s AND "Titular de Gestion" = %s'
    cursor.execute(query, (iban, 'SI'))
    result = cursor.fetchone()
    if result:
        return result[0], result[1]  # Return Nombre, Apellidos
    return None, None

# Function to get phone number by IBAN
def get_phone_by_iban(iban):
    query = 'SELECT "Telefono" FROM "iban_telefono" WHERE "IBAN" = %s'
    cursor.execute(query, (iban,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def relationship_exists(iban_emisor, iban_receptor):
    query = 'SELECT 1 FROM "relaciones_bizums" WHERE "IBAN_EMISOR" = %s AND "IBAN_RECEPTOR" = %s'
    cursor.execute(query, (iban_emisor, iban_receptor))
    return cursor.fetchone() is not None

# Function to extract words of at least 5 letters from a name
def extract_significant_words(name):
    words = name.split()
    return {word for word in words if len(word) >= 5}

# Function to fetch IBAN by CIF and PAN
def get_iban_by_cif_and_pan(cif, pan):
    query = 'SELECT "IBAN" FROM "pan_limite_tarjeta" WHERE "CIF" = %s AND "PAN" = %s'
    cursor.execute(query, (cif, pan))
    result = cursor.fetchone()
    return result[0] if result else None

def get_pan_by_cif(cif):
    """
    Fetch all PANs and their details for a given CIF.
    
    Args:
        cif (str): The CIF to query
        
    Returns:
        List[Tuple]: List of tuples containing (PAN, limite_tarjeta, gasto_mes, tarjeta_bloqueada)
                     or None if no results
    """
    query = 'SELECT "PAN", "limite_tarjeta", "gasto_mes", "tarjeta_bloqueada" FROM "pan_limite_tarjeta" WHERE "CIF" = %s'
    cursor.execute(query, (cif,))
    results = cursor.fetchall()
    return results if results else None


@function_tool
def get_pans_function(wrapper: RunContextWrapper['BankingContext']) -> List[str]:
    """Returns all credit card PANs of a client"""
    nif = wrapper.context.nif if wrapper and wrapper.context and wrapper.context.nif else ""
    query = 'SELECT DISTINCT "PAN" FROM "pan_limite_tarjeta" WHERE "CIF" = %s'
    cursor.execute(query, (nif,))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []


def get_pans(nif) -> List[str]:
    """Returns all credit card PANs of a client"""
    query = 'SELECT DISTINCT "PAN" FROM "pan_limite_tarjeta" WHERE "CIF" = %s'
    cursor.execute(query, (nif,))
    results = cursor.fetchall()
    if results:
        return [row[0] for row in results]
    return []

@function_tool
def get_card_details_function(wrapper: RunContextWrapper['BankingContext'], pan:str)->str:
    """Get the the credit card limit, current monnth spending and wether the credit card is blocked for a pan given with format 5402********0001"""

    query = '''
        SELECT "limite_tarjeta", "gasto_mes", "tarjeta_bloqueada"
        FROM "pan_limite_tarjeta"
        WHERE "CIF" = %s AND "PAN" = %s
    '''
    cursor.execute(query, (wrapper.context.nif, pan))
    result = cursor.fetchone()
    if result:
        return {
            "limite_tarjeta": result[0],
            "gasto_mes": result[1],
            "tarjeta_bloqueada": result[2]
        }
    return None

def get_card_details(cif:str, pan:str)->str:
    """Get the the credit card limit, current monnth spending and wether the credit card is blocked"""

    query = '''
        SELECT "limite_tarjeta", "gasto_mes", "tarjeta_bloqueada"
        FROM "pan_limite_tarjeta"
        WHERE "CIF" = %s AND "PAN" = %s
    '''
    cursor.execute(query, (cif, pan))
    result = cursor.fetchone()
    if result:
        return {
            "limite_tarjeta": result[0],
            "gasto_mes": result[1],
            "tarjeta_bloqueada": result[2]
        }
    return None


class block_card(BaseModel):
    success_status: bool
    message: str

@function_tool
def block_card_function(wrapper: RunContextWrapper['BankingContext'], pan:str)->block_card:
    """
    Given a credit card that must be given in format 5402********0001, block the credit card
    """
    try:
        # Step 1: Check if the card exists for the given CIF and PAN
        card_details = get_card_details(wrapper.context.nif, pan)
        if not card_details:
            return block_card(success_status=False,message= f"No records found for {wrapper.context.nif} and PAN {pan}.")
        # Step 2: Check the current status of tarjeta_bloqueada
        if card_details["tarjeta_bloqueada"] == 'SI':
            return block_card(success_status=True,message= f"Card with PAN {pan} is already blocked.")

        # Step 3: Update tarjeta_bloqueada to 'SÍ'
        query = 'UPDATE "pan_limite_tarjeta" SET "tarjeta_bloqueada" = %s WHERE "CIF" = %s AND "PAN" = %s'
        cursor.execute(query, ('SI', wrapper.context.nif, pan))

        # Step 4: Commit the transaction
        conn.commit()

        return block_card(success_status=True,message= f"Card with PAN {pan} has been successfully blocked.")

    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        return block_card(success_status=False,message= f"Error blocking card: {str(e)}")


class unblock_card(BaseModel):
    success_status: bool
    message: str

@function_tool
def unblock_card_function(wrapper: RunContextWrapper['BankingContext'],pan:str)->unblock_card:
    """
    BGiven a credit card that must be given in format 5402********0001, unblock the credit card
    """
    try:
        # Step 1: Check if the card exists for the given CIF and PAN
        card_details = get_card_details(wrapper.context.nif, pan)
        if not card_details:
            return unblock_card(success_status=False,message= f"No record found in pan_limite_tarjeta for CIF {wrapper.context.nif} and PAN {pan}.")
        # Step 2: Check the current status of tarjeta_bloqueada
        if card_details["tarjeta_bloqueada"] == 'NO':
            return unblock_card(success_status=True,message= f"Card with PAN {pan} is already unblocked.")

        # Step 3: Update tarjeta_bloqueada to 'SÍ'
        query = 'UPDATE "pan_limite_tarjeta" SET "tarjeta_bloqueada" = %s WHERE "CIF" = %s AND "PAN" = %s'
        cursor.execute(query, ('NO', wrapper.context.nif, pan))

        # Step 4: Commit the transaction
        conn.commit()

        return unblock_card(success_status=True,message= f"Card with PAN {pan} has been successfully unblocked.")

    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        return unblock_card(success_status=False,message= f"Error unblocking card: {str(e)}")


def update_saldo_IBAN(IBAN, quantity, operation="add"):
    """
    Updates the Saldo for a given IBAN by adding or subtracting a quantity.
    
    Args:
        IBAN (str): The contract number to update.
        quantity (float): The amount to add or subtract.
        operation (str): "add" to add the quantity, "subtract" to subtract it.
    
    Returns:
        tuple: (bool, str, float) - (success status, message, new saldo if successful)
    """
    try:
        # Step 1: Get the current Saldo
        current_saldo = get_saldos_by_IBAN(IBAN)
        if current_saldo is None:
            return False, f"No record found for IBAN {IBAN}.", None

        # Step 2: Calculate the new Saldo
        if operation.lower() == "add":
            new_saldo = current_saldo + quantity
        elif operation.lower() == "subtract":
            new_saldo = current_saldo - quantity
            if new_saldo < 0:
                return False, "Insufficient balance for subtraction.", None
        else:
            return False, "Invalid operation. Use 'add' or 'subtract'.", None

        # Step 3: Update the Saldo in the database
        query = 'UPDATE "saldos" SET "Saldo" = %s WHERE "IBAN" = %s'
        cursor.execute(query, (new_saldo, IBAN))
        
        # Step 4: Commit the transaction
        conn.commit()

        # Step 5: Verify the update (optional)
        updated_saldo = get_saldos_by_IBAN(IBAN)
        if updated_saldo == new_saldo:
            return True, f"Saldo updated successfully for IBAN {IBAN}.", new_saldo
        else:
            return False, "Failed to verify the update.", None

    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        return False, f"Error updating Saldo: {str(e)}", None

class make_transfer_class(BaseModel):
    success_status: bool
    message: str

@function_tool
def transfer_money_and_log(wrapper: RunContextWrapper['BankingContext'],iban_emisor:str, iban_receptor:str, amount:float)->make_transfer_class:
    """
    Transfers money from iban_emisor to iban_receptor, updates Saldos, and logs the relationship in relaciones_bizums.
    """

    validate_iban_emisor = validate_iban(iban_emisor)
    validate_iban_receptor = validate_iban(iban_receptor)

    query = 'SELECT "IBAN" FROM "iban_titulares" WHERE "CIF" = %s AND  "IBAN" = %s'
    cursor.execute(query, (wrapper.context.nif, iban_emisor))
    result = cursor.fetchone()

    if validate_iban_emisor and validate_iban_receptor:
        if result:
            try:
                # Step 1: Get the current Saldo for both IBANs
                saldo_emisor = get_saldos_by_IBAN(iban_emisor)
                saldo_receptor = get_saldos_by_IBAN(iban_receptor)

                if saldo_emisor is None:
                    return make_transfer_class(success_status=False,message= f"IBAN {iban_emisor} not found in Saldos. Tell the client")
                if saldo_receptor is None:
                    return make_transfer_class(success_status=False,message= f"IBAN {iban_receptor} not found in Saldos. Tell the client")
                
                # Step 2: Verify sufficient balance in iban_emisor
                if saldo_emisor < amount:
                    return make_transfer_class(success_status=False,message= f"Insufficient balance in IBAN {iban_emisor}. Current Saldo: {saldo_emisor}, Required: {amount}. Tell the client")

                # Step 3: Calculate new Saldos
                new_saldo_emisor = saldo_emisor - amount
                new_saldo_receptor = saldo_receptor + amount

                # Step 4: Update both IBANs in Saldos
                query = 'UPDATE "saldos" SET "Saldo" = %s WHERE "IBAN" = %s'
                cursor.execute(query, (new_saldo_emisor, iban_emisor))
                cursor.execute(query, (new_saldo_receptor, iban_receptor))

                # Step 5: Fetch Titular de Gestión details for both IBANs
                nombre_emisor, apellidos_emisor = get_titular_de_gestion(iban_emisor)
                nombre_receptor, apellidos_receptor = get_titular_de_gestion(iban_receptor)

                if nombre_emisor is None:
                    return make_transfer_class(success_status=False,message= f"No Titular de Gestión found for IBAN {iban_emisor}. Tell the client")
                if nombre_receptor is None:
                    return make_transfer_class(success_status=False,message= f"No Titular de Gestión found for IBAN {iban_receptor}.Tell the client")
                
                # Step 6: Fetch phone numbers for both IBANs
                telefono_emisor = get_phone_by_iban(iban_emisor)
                telefono_receptor = get_phone_by_iban(iban_receptor)

                if telefono_emisor is None:
                    return make_transfer_class(success_status=False,message= f"No phone number found for IBAN {iban_emisor}. Tell the client")
                if telefono_receptor is None:
                    return make_transfer_class(success_status=False,message= f"No phone number found for IBAN {iban_receptor}. Tell the client")

                # Step 7: Check if the relationship already exists in relaciones_bizums
                if relationship_exists(iban_emisor, iban_receptor):
                    # If the relationship exists, commit the Saldo updates and return
                    conn.commit()
                    return make_transfer_class(success_status=True,message= f"Transfer of {amount} from IBAN {iban_emisor} to IBAN {iban_receptor} successful. Tell the client")

                # Step 8: Insert the new relationship into relaciones_bizums
                query = '''
                    INSERT INTO "relaciones_bizums" (
                        "IBAN_EMISOR", "IBAN_RECEPTOR", "TELEFONO_EMISOR", "TELEFONO_RECEPTOR",
                        "NOMBRE_EMISOR", "APELLIDO_EMISOR", "NOMBRE_RECEPTOR", "APELLIDO_RECEPTOR"
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query, (
                    iban_emisor, iban_receptor, telefono_emisor, telefono_receptor,
                    nombre_emisor, apellidos_emisor, nombre_receptor, apellidos_receptor
                ))

                # Step 9: Commit the transaction (Saldos updates + relaciones_bizums insert)
                conn.commit()

                return make_transfer_class(success_status=True,message= f"Transfer of {amount} from IBAN {iban_emisor} to IBAN {iban_receptor} successful. Tell the client")
            except Exception as e:
                # Rollback the transaction on error
                conn.rollback()
                return make_transfer_class(success_status=False,message= f"Error during transfer: {str(e)}")
        else:
            return  make_transfer_class(success_status=False,message= f"The IBAN {iban_emisor} doesn't belong to you. Tell the client")
    elif not validate_iban_emisor:
        return  make_transfer_class(success_status=False,message= f"The IBAN EMISOR doesn't have the correct format. Tell the client")
    else:
        return  make_transfer_class(success_status=False,message= f"The IBAN RECEPTOR doesn't have the correct format. Tell the client")
    

# Function to normalize a name (remove accents, convert to uppercase)
def normalize_name(name):
    # Remove accents using unidecode
    name = unidecode.unidecode(name)
    # Convert to uppercase and remove extra spaces
    return " ".join(name.upper().split())


class closest_match_transfer_class(BaseModel):
    closest_match: Optional[dict]  # Allows dict or None

@function_tool
# Function to find the closest match in relaciones_bizums
def find_closest_match(iban_emisor:str, target_name:str)->closest_match_transfer_class:
    """
    Only if receiver's name is not "", call this tool..
    """
    if not target_name or not target_name.strip():
        return "I don't have the name of the receptor. Ask the client for information." # Early return if no name provided
    # Normalize the target name
    target_name_normalized = normalize_name(target_name)
    # Extract significant words (≥ 5 letters) from the target name
    target_words = extract_significant_words(target_name_normalized)

    # Fetch all relationships for the given IBAN_EMISOR
    query = '''
        SELECT "NOMBRE_RECEPTOR", "APELLIDO_RECEPTOR", "IBAN_RECEPTOR", "TELEFONO_RECEPTOR"
        FROM "relaciones_bizums"
        WHERE "IBAN_EMISOR" = %s
    '''
    cursor.execute(query, (iban_emisor,))
    results = cursor.fetchall()

    if not results:
        return closest_match_transfer_class(closest_match=None)

    # Find the closest match using Levenshtein distance with the filter
    closest_match = None
    min_distance = float('inf')

    for result in results:
        nombre_receptor, apellido_receptor, iban_receptor, telefono_receptor = result
        # Concatenate NOMBRE_RECEPTOR and APELLIDO_RECEPTOR
        full_name = f"{nombre_receptor} {apellido_receptor}"
        # Normalize the full name
        full_name_normalized = normalize_name(full_name)

        # Compute Levenshtein distance
        distance = textdistance.levenshtein(target_name_normalized, full_name_normalized)

        # Extract significant words from NOMBRE_RECEPTOR and APELLIDO_RECEPTOR
        receptor_words = extract_significant_words(normalize_name(nombre_receptor))
        receptor_words.update(extract_significant_words(normalize_name(apellido_receptor)))

        # Check if any significant words match
        has_matching_word = bool(target_words & receptor_words)  # Intersection of sets

        # Apply the filter: exclude if distance > 10 and no matching words
        if distance > 10 and not has_matching_word:
            continue

        # Update the closest match if this distance is smaller
        if distance < min_distance:
            min_distance = distance
            closest_match = {
                "Nombre": nombre_receptor,
                "Apellidos": apellido_receptor,
                "IBAN": iban_receptor,
                "Telefono": telefono_receptor,
                "Distance": distance,
                "HasMatchingWord": has_matching_word
            }

    return closest_match_transfer_class(closest_match=closest_match)

class Check_Payment_Cond(BaseModel):
    conditions_passed: bool
    failed_conditions_list: List[str] 


@function_tool
def check_payment_conditions_function(wrapper: RunContextWrapper['BankingContext'], pan:str, import_amount:int)->Check_Payment_Cond:
    """
    Checks the payments conditions to know why a client can't buy things with a certain credit card.
    If the import of the buy is not given by the client, assign import_amount to 0
    The pan is given  to this tool with format 5402********0001
    """
    failed_conditions = []
    data = {}

    # Step 1: Get the IBAN associated with the CIF and PAN
    iban = get_iban_by_cif_and_pan(wrapper.context.nif, pan)
    if not iban:
        failed_conditions.append(f"No record found in pan_limite_tarjeta for CIF {wrapper.context.nif} and PAN {pan}.")
        return Check_Payment_Cond(conditions_passed=False, failed_conditions_list=failed_conditions)
    data["iban"] = iban

    # Step 2: Get the current Saldo for the IBAN
    saldo = get_saldos_by_IBAN(iban)
    if saldo is None:
        failed_conditions.append(f"IBAN {iban} not found in saldos.")
        return Check_Payment_Cond(conditions_passed=False, failed_conditions_list=failed_conditions)
    data["saldo"] = saldo

    # Step 3: Get card details (limite_tarjeta, gasto_mes, tarjeta_bloqueada)
    card_details = get_card_details(wrapper.context.nif, pan)
    if not card_details:
        failed_conditions.append(f"No record found in pan_limite_tarjeta for CIF {wrapper.context.nif} and PAN {pan}.")
        return Check_Payment_Cond(conditions_passed=False, failed_conditions_list=failed_conditions)

    data["limite_tarjeta"] = card_details["limite_tarjeta"]
    data["gasto_mes"] = card_details["gasto_mes"]
    data["tarjeta_bloqueada"] = card_details["tarjeta_bloqueada"]

    # Step 4: Check all conditions
    # Condition 1: Saldo - import_amount >= 0
    if saldo - import_amount < 0:
        failed_conditions.append(f"Insufficient balance in IBAN {iban}. Current Saldo: {saldo}, Required: {import_amount}")

    # Condition 2: gasto_mes + import_amount <= limite_tarjeta
    if data["gasto_mes"] + import_amount > data["limite_tarjeta"]:
        failed_conditions.append(f"Monthly spending limit exceeded. Current gasto_mes: {data['gasto_mes']}, Import: {import_amount}, Limit: {data['limite_tarjeta']}")

    # Condition 3: tarjeta_bloqueada = 'NO'
    if data["tarjeta_bloqueada"] != 'NO':
        failed_conditions.append(f"Card is blocked (tarjeta_bloqueada = '{data['tarjeta_bloqueada']}').")

    # Return the result
    conditions_passed = len(failed_conditions) == 0
    return Check_Payment_Cond(conditions_passed=conditions_passed, failed_conditions_list=failed_conditions)

# New function to check payment conditions
def check_payment_conditions(cif, pan, import_amount):
    """
    Checks the conditions for a payment using the given CIF, PAN, and import amount.
    
    Args:
        cif (str): The client identifier.
        pan (str): The card number (PAN).
        import_amount (float): The amount to spend.
    
    Returns:
        tuple: (bool, list, dict) - (conditions_passed, failed_conditions, data)
            - conditions_passed: True if all conditions pass, False otherwise.
            - failed_conditions: List of strings describing failed conditions.
            - data: Dictionary containing 'iban', 'saldo', 'limite_tarjeta', 'gasto_mes', 'tarjeta_bloqueada'.
    """
    failed_conditions = []
    data = {}

    # Step 1: Get the IBAN associated with the CIF and PAN
    iban = get_iban_by_cif_and_pan(cif, pan)
    if not iban:
        failed_conditions.append(f"No record found in pan_limite_tarjeta for CIF {cif} and PAN {pan}.")
        return False, failed_conditions, data
    data["iban"] = iban

    # Step 2: Get the current Saldo for the IBAN
    saldo = get_saldos_by_IBAN(iban)
    if saldo is None:
        failed_conditions.append(f"IBAN {iban} not found in saldos.")
        return False, failed_conditions, data
    data["saldo"] = saldo

    # Step 3: Get card details (limite_tarjeta, gasto_mes, tarjeta_bloqueada)
    card_details = get_card_details(cif, pan)
    if not card_details:
        failed_conditions.append(f"No record found in pan_limite_tarjeta for CIF {cif} and PAN {pan}.")
        return False, failed_conditions, data

    data["limite_tarjeta"] = card_details["limite_tarjeta"]
    data["gasto_mes"] = card_details["gasto_mes"]
    data["tarjeta_bloqueada"] = card_details["tarjeta_bloqueada"]

    # Step 4: Check all conditions
    # Condition 1: Saldo - import_amount >= 0
    if saldo - import_amount < 0:
        failed_conditions.append(f"Insufficient balance in IBAN {iban}. Current Saldo: {saldo}, Required: {import_amount}")

    # Condition 2: gasto_mes + import_amount <= limite_tarjeta
    if data["gasto_mes"] + import_amount > data["limite_tarjeta"]:
        failed_conditions.append(f"Monthly spending limit exceeded. Current gasto_mes: {data['gasto_mes']}, Import: {import_amount}, Limit: {data['limite_tarjeta']}")

    # Condition 3: tarjeta_bloqueada = 'NO'
    if data["tarjeta_bloqueada"] != 'NO':
        failed_conditions.append(f"Card is blocked (tarjeta_bloqueada = '{data['tarjeta_bloqueada']}').")

    # Return the result
    conditions_passed = len(failed_conditions) == 0
    return conditions_passed, failed_conditions, data

def process_payment(cif, pan, import_amount):
    """
    Processes a payment using the given CIF, PAN, and import amount.
    
    Args:
        cif (str): The client identifier.
        pan (str): The card number (PAN).
        import_amount (float): The amount to spend.
    
    Returns:
        tuple: (bool, str) - (success status, message with failed conditions if any)
    """
    try:
        # Step 1: Check payment conditions
        conditions_passed, failed_conditions, data = check_payment_conditions(cif, pan, import_amount)

        # Step 2: If conditions failed, return the failure message
        if not conditions_passed:
            return False, f"Transaction failed: {', '.join(failed_conditions)}"

        # Step 3: Extract data for updates
        iban = data["iban"]
        saldo = data["saldo"]
        gasto_mes = data["gasto_mes"]

        # Step 4: Update gasto_mes in pan_limite_tarjeta
        new_gasto_mes = gasto_mes + import_amount
        query_update_gasto = 'UPDATE "pan_limite_tarjeta" SET "gasto_mes" = %s WHERE "CIF" = %s AND "PAN" = %s'
        cursor.execute(query_update_gasto, (new_gasto_mes, cif, pan))

        # Step 5: Update Saldo in saldos
        new_saldo = saldo - import_amount
        query_update_saldo = 'UPDATE "saldos" SET "Saldo" = %s WHERE "IBAN" = %s'
        cursor.execute(query_update_saldo, (new_saldo, iban))

        # Step 6: Commit the transaction
        conn.commit()

        return True, "Transaction successful."

    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        return False, f"Transaction failed: Error occurred - {str(e)}"


# Function to change the card's spending limit
def change_card_limit(cif, pan, new_limit):
    """
    Changes the spending limit (limite_tarjeta) for the given CIF and PAN.
    The new limit must not exceed 6000.
    
    Args:
        cif (str): The client identifier.
        pan (str): The card number (PAN).
        new_limit (float): The new spending limit.
    
    Returns:
        tuple: (bool, str) - (success status, message)
    """
    try:
        # Step 1: Check if the card exists for the given CIF and PAN
        card_details = get_card_details(cif, pan)
        if not card_details:
            return False, f"No record found in pan_limite_tarjeta for CIF {cif} and PAN {pan}."

        # Step 2: Check if the new limit exceeds the maximum allowed (6000)
        if new_limit > 6000:
            return False, f"New limit ({new_limit}) exceeds the maximum allowed limit of 6000."

        # Step 3: Check if the new limit is less than the current gasto_mes
        current_gasto_mes = card_details["gasto_mes"]
        if new_limit < current_gasto_mes:
            return False, f"New limit ({new_limit}) cannot be less than the current gasto_mes ({current_gasto_mes})."

        # Step 4: Check if the new limit is the same as the current limit
        current_limit = card_details["limite_tarjeta"]
        if new_limit == current_limit:
            return True, f"Card with PAN {pan} already has a spending limit of {new_limit}."

        # Step 5: Update limite_tarjeta with the new value
        query = 'UPDATE "pan_limite_tarjeta" SET "limite_tarjeta" = %s WHERE "CIF" = %s AND "PAN" = %s'
        cursor.execute(query, (new_limit, cif, pan))

        # Step 6: Commit the transaction
        conn.commit()

        return True, f"Spending limit for card with PAN {pan} has been successfully updated to {new_limit}."

    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        return False, f"Error updating card limit: {str(e)}"
    


