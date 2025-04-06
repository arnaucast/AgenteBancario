# Imports and Dependencies
import os
from datetime import datetime
import uuid
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
import sys
# Set up project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from datetime import datetime
import time
import threading
import io
from queue import Queue
import markdown
import soundfile
# Custom imports (assuming these are in your project)
from agents import Runner
from manager import (
    main_banking, 
    process_single_task, 
    Runner, 
    configure_agent_coordinator, 
    define_default_agent, 
    banking_guardrail_agent, 
    task_separator_agent, 
    context_summarizer_agent
)
from Agents.utilities.web_utilities2 import process_task_with_threading,process_separator_with_threading,process_guardrail_with_threading,AddContextToAgent,process_task_with_threading_concurrent
from Agents.utilities.change_get_data_db import BankingContext,get_all_distinct_cifs,get_ibans_for_web,get_saldos_by_IBAN,get_pan_by_cif,get_name_for_web
from Agents.utilities.preferencias import check_and_update_language,ActualizaIdioma,get_language
from __init__ import unique_contr_mov,unique_type_clie,unique_cifs_with_mov,get_tipo_cliente_iban
from Agents.utilities.traductor_textos import get_translated_messages
# Tracing and environment configuration (you might want to remove or modify these)
import logfire

import logging
import speech_recognition as sr
# Suppress Streamlit's missing ScriptRunContext warnings
logging.getLogger("streamlit.runtime.scriptrunner.script_runner").setLevel(logging.ERROR)
from dotenv import load_dotenv
import os 
load_dotenv()
# Comment these lines out if you don't want Logfire tracing
logfire.configure(
    send_to_logfire=True,  # Ensure this is set to True
    token=os.getenv("CONEXION_LOG_FIRE"),
                    scrubbing=False)  # Use the token directly

logfire.instrument_openai_agents()

logfire.instrument_openai_agents()

# Patch the event loop to allow nested use of asyncio
nest_asyncio.apply()

import asyncio
import random

import numpy as np

from agents import Agent, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)
import time
import whisper
import numpy as np
import numpy.typing as npt


import numpy as np
import numpy as np
import streamlit as st
import threading
from datetime import datetime
import uuid
from dotenv import load_dotenv
import openai  # For transcription
import wavio
from gtts import gTTS  # For text-to-speech
from pydub import AudioSegment
# First, you'll need to install speech_recognition: pip install SpeechRecognition
# You'll also need PyAudio for microphone input: pip install PyAudio

import whisper
import streamlit as st
import wavio
import os
import speech_recognition as sr
from datetime import datetime
import uuid
import streamlit as st
from dotenv import load_dotenv

# Custom imports
# Custom imports
def display_ibans(ibans):
    """
    Display IBANs without spaces.
    
    Args:
        ibans (List[str]): List of IBAN numbers to display
    """
    if not ibans:
        st.warning("No IBANs found for this CIF.")
        return

    st.subheader("Your Bank Accounts")
    
    for iban in ibans:
        st.text_input(
            label="IBAN", 
            value=iban.replace(' ', ''),
            key=f"iban_{iban}",
            help="Click to select and copy"
        )

def format_iban(iban):
    """
    Format IBAN for better readability if needed.
    
    Args:
        iban (str): IBAN number to format
    
    Returns:
        str: Formatted IBAN with spaces every 4 characters
    """
    iban = iban.replace(' ', '')
    return ' '.join(iban[i:i+4] for i in range(0, len(iban), 4))

def prepare_clean_history(chat_history):
    """Remove timestamp and hidden fields from chat history before processing."""
    return [
        {k: v for k, v in message.items() if k not in ['timestamp', 'hidden']} 
        for message in chat_history
    ]

# Load environment variables
load_dotenv()

def get_timestamp(message):
    """Safely get timestamp from message, using current time as fallback."""
    return message.get('timestamp', datetime.now().strftime("%I:%M %p"))

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_history_agent" not in st.session_state:
        st.session_state.chat_history_agent = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "banking_context" not in st.session_state:
        st.session_state.banking_context = BankingContext(nif=None)
    if "chat_enabled" not in st.session_state:
        st.session_state.chat_enabled = False
    if "processing_message" not in st.session_state:
        st.session_state.processing_message = None
    if "task_solved" not in st.session_state:
        st.session_state.task_solved = True
    if "current_agent" not in st.session_state:
        print("DEBUG: agent gets reset here 4 - Initial setup")
        st.session_state.current_agent = None
    if "current_rag_info" not in st.session_state:
        st.session_state.current_rag_info = None
    if "current_rag_research" not in st.session_state:
        st.session_state.current_rag_research = None
    if "is_question_rag" not in st.session_state:
        st.session_state.is_question_rag = False
    if "current_task" not in st.session_state:
        st.session_state.current_task = None
    if "context_summary" not in st.session_state:
        st.session_state.context_summary = ""
    if 'spinner_text' not in st.session_state:
        st.session_state.spinner_text = ''
    if 'separated_tasks' not in st.session_state:
        st.session_state.separated_tasks = ''
    if 'Usuario_click' not in st.session_state:
        st.session_state.Usuario_click = ''
    if "task_success" not in st.session_state:
        st.session_state.task_success = False
    if "waiting_for_task_confirmation" not in st.session_state:
        st.session_state.waiting_for_task_confirmation = False
    if "waiting_for_rag_confirmation" not in st.session_state:
        st.session_state.waiting_for_rag_confirmation = False
    if "idioma" not in st.session_state:
        st.session_state.idioma = ""
    if "traducciones" not in st.session_state:
        st.session_state.traducciones = {}

def main():
    st.set_page_config(page_title="Banking Assistant", page_icon="💼")
    initialize_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
        .chat-message {
            padding: 1rem; 
            border-radius: 0.5rem; 
            margin-bottom: 1rem; 
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #e6f7ff;
            border-left: 5px solid #0079AD;
        }
        .chat-message.assistant {
            background-color: #f0f0f0;
            border-left: 5px solid #0079AD;
        }
        .chat-message .content {
            display: flex;
            margin-top: 0.5rem;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 1rem;
        }
        .message {
            flex: 1;
            color: #000000;
        }
        .timestamp {
            font-size: 0.8rem;
            color: #888;
            margin-top: 0.2rem;
        }
        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .markdown-content th, .markdown-content td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .markdown-content th {
            background-color: #f5f5f5;
        }
        .stMarkdown p {
            font-size: 14px;
            margin-bottom: 0.2rem;
            word-wrap: break-word;
        }
        .stTextInput > div > div > input {
            font-size: 14px;
        }
        [data-testid="stSidebar"] {
            width: 500px !important;
        }
        [data-testid="stAppViewContainer"] > .main {
            margin-left: 500px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Banking Setup")
        
        available_cifs = get_all_distinct_cifs()
        
        st.subheader("Primary Banking CIF")
        cif_disabled = not st.session_state.task_solved or len(st.session_state.chat_history) > 0
        
        if available_cifs:
            filtered_cifs = [cif for cif in available_cifs if cif in unique_cifs_with_mov]
            col1, col2 = st.columns([5, 5])
            with col1:
                selected_main_cif = st.selectbox(
                    "Select your Primary CIF (Required)",
                    options=filtered_cifs,
                    index=filtered_cifs.index(st.session_state.banking_context.nif) if st.session_state.banking_context.nif in filtered_cifs else 0,
                    placeholder="Choose a CIF...",
                    disabled=cif_disabled,
                    key="main_cif_select"
                )
            with col2:
                if selected_main_cif.strip():
                    nombre = get_name_for_web(selected_main_cif.strip())
                    st.markdown("**Nombre**")
                    st.text_input(
                        label="Name",
                        value=nombre[0] if nombre else "N/A",
                        key="primary_nombre_display",
                        label_visibility="collapsed",
                        disabled=True
                    )
        else:
            selected_main_cif = st.text_input(
                "Enter your Primary CIF (Required)", 
                value=st.session_state.banking_context.nif or "",
                disabled=cif_disabled,
                key="main_cif_input"
            )
        
        if selected_main_cif.strip():
            st.session_state.banking_context.nif = selected_main_cif.strip()
            st.session_state.idioma = ""
            st.session_state.chat_enabled = True

        if st.session_state.banking_context.nif:
            diccionario_idioma = check_and_update_language(st.session_state.banking_context.nif)
            if diccionario_idioma["exists"]:
                st.session_state.idioma = diccionario_idioma["idioma"]
                st.session_state.traducciones = get_translated_messages(diccionario_idioma["idioma"])
                st.session_state.banking_context.traducciones = st.session_state.traducciones
            # Mostrar el idioma del cliente
            st.markdown("**Idioma:**")
            idioma_display = st.session_state.idioma if st.session_state.idioma else "No registrado"
            st.text_input(
                label="Idioma del cliente",
                value=idioma_display,
                key="idioma_display",
                label_visibility="collapsed",
                disabled=True,
                help="Idioma registrado para este cliente"
            )
            
            nombre = get_name_for_web(st.session_state.banking_context.nif)
            main_ibans = [iban for iban in get_ibans_for_web(st.session_state.banking_context.nif) if iban in unique_contr_mov]
            if main_ibans:
                with st.container():
                    for iban in main_ibans:
                        saldo = get_saldos_by_IBAN(iban)
                        saldo_display = f"{saldo:.2f} €" if saldo is not None else "0.00 €"
                        col1, col2 = st.columns([7, 3])
                        with col1:
                            st.markdown("**IBAN**")
                            st.text_input(
                                label="IBAN Number",
                                value=iban.replace(' ', ''),
                                key=f"primary_main_iban_{iban}",
                                label_visibility="collapsed",
                                help="Click to select and copy"
                            )
                        with col2:
                            st.markdown("**Saldos**")
                            st.text_input(
                                label="Account Balance",
                                value=saldo_display,
                                key=f"primary_saldo_{iban}",
                                label_visibility="collapsed",
                                help="Current balance"
                            )
            else:
                st.warning("No IBANs found for Primary CIF.")
            
            tipo_cli = get_tipo_cliente_iban(IBAN=main_ibans[0])
            st.markdown(f"*Tipo de cliente:* {tipo_cli[0]}", unsafe_allow_html=True)

            pans = get_pan_by_cif(st.session_state.banking_context.nif)
            if pans:
                with st.container():
                    for pan, limite, gasto, bloqueada in pans:
                        limite_display = f"{int(round(limite, 0))} €" if limite is not None else "N/A"
                        gasto_display = f"{int(round(gasto, 0))} €" if gasto is not None else "0 €"
                        bloqueada_display = "Yes" if bloqueada == "SI" else "No"
                        
                        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])
                        with col1:
                            st.markdown("**PAN**")
                            st.text_input(
                                label="Card Number",
                                value=pan,
                                key=f"pan_{pan}",
                                label_visibility="collapsed",
                                help="Click to select and copy"
                            )
                        with col2:
                            st.markdown("**Limit**")
                            st.text_input(
                                label="Card Limit",
                                value=limite_display,
                                key=f"limite_{pan}",
                                label_visibility="collapsed",
                                help="Card spending limit"
                            )
                        with col3:
                            st.markdown("**Spent**")
                            st.text_input(
                                label="Monthly Spending",
                                value=gasto_display,
                                key=f"gasto_{pan}",
                                label_visibility="collapsed",
                                help="Current month spending"
                            )
                        with col4:
                            st.markdown("**Blocked**")
                            st.text_input(
                                label="Blocked Status",
                                value=bloqueada_display,
                                key=f"bloqueada_{pan}",
                                label_visibility="collapsed",
                                help="Is the card blocked?"
                            )
            else:
                st.warning("No PANs found for Primary CIF.")
            st.divider()

        st.divider()

        st.subheader("Test CIF (Optional)")
        if available_cifs:
            col1, col2 = st.columns([5, 5])
            with col1:
                selected_test_cif = st.selectbox(
                    "Select a Test CIF",
                    options=available_cifs,
                    index=0,
                    placeholder="Choose a CIF for testing...",
                    key="test_cif_select"
                )
            with col2:
                if selected_test_cif and selected_test_cif != "None":
                    nombre_test = get_name_for_web(selected_test_cif)
                    st.markdown("**Nombre**")
                    st.text_input(
                        label="Name",
                        value=nombre_test[0] if nombre_test else "N/A",
                        key="test_nombre_display",
                        label_visibility="collapsed",
                        disabled=True
                    )
        else:
            selected_test_cif = st.text_input(
                "Enter a Test CIF",
                value="",
                key="test_cif_input"
            )
        
        if selected_test_cif and selected_test_cif != "None":
            test_ibans = get_ibans_for_web(selected_test_cif)
            if test_ibans:
                with st.container():
                    for iban in test_ibans:
                        saldo = get_saldos_by_IBAN(iban)
                        saldo_display = f"{saldo:.2f} €" if saldo is not None else "0.00 €"
                        col1, col2 = st.columns([7, 3])
                        with col1:
                            st.markdown("**IBAN**")
                            st.text_input(
                                label="IBAN Number",
                                value=iban.replace(' ', ''),
                                key=f"main_iban_{iban}",
                                label_visibility="collapsed",
                                help="Click to select and copy"
                            )
                        with col2:
                            st.markdown("**Saldos**")
                            st.text_input(
                                label="Account Balance",
                                value=saldo_display,
                                key=f"saldo_{iban}",
                                label_visibility="collapsed",
                                help="Current balance"
                            )
            else:
                st.warning("No IBANs found for Test CIF.")
            st.divider()

    nombre = get_name_for_web(selected_main_cif.strip())
    # Obtener las traducciones según el idioma seleccionado
    #   # Esto puede venir de st.session_state.language o similar
    traducciones = get_translated_messages(st.session_state.idioma)

    # Construir el mensaje de bienvenida con las traducciones
    welcome_html = f"""
    <div class="chat-message assistant">
        <div class="content">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=banking-agent" class="avatar" />
            <div class="message">
                <h3 style="color: #0079AD; margin-bottom: 10px;">{traducciones['WELCOME_MSG'].format(name=nombre[0])}</h3>
                <p style="color: #000000; margin-bottom: 15px;">{traducciones['INTRO_TEXT']}</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #0079AD;">
                    <strong style="color: #0079AD; display: block; margin-bottom: 10px;">{traducciones['WHAT_CAN_I_DO']}</strong>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['TRANSFER_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['TRANSFER_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['BALANCE_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['BALANCE_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['CARDS_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['CARDS_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['MOVEMENTS_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['MOVEMENTS_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['DOUBTS_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['DOUBTS_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['NEWS_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['NEWS_TEXT']}</p>
                    </details>
                    <details style="margin-bottom: 10px;">
                        <summary style="color: #000000; cursor: pointer;">✅ {traducciones['PREFERENCES_SUMMARY']}</summary>
                        <p style="color: #000000; margin: 10px 0 0 20px;">{traducciones['PREFERENCES_TEXT']}</p>
                    </details>
                </div>
                <p style="color: #000000; margin-top: 15px;">{traducciones['HELP_TODAY']}</p>
            </div>
        </div>
    </div>
    """

    # Mostrar el mensaje en Streamlit
    st.markdown(welcome_html, unsafe_allow_html=True)

    if st.button(f"{st.session_state.banking_context.traducciones['NUEVA_CONV']}"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.task_solved = True
        st.session_state.current_agent = None
        st.session_state.current_task = None
        st.session_state.context_summary = ""
        st.success(f"{st.session_state.banking_context.traducciones['NUEVA_CONV_EMP']}")
        st.rerun()

    st.caption(f"{st.session_state.banking_context.traducciones['PREGUNTA_CUALQ']}")

    for message in st.session_state.chat_history:
        if not message.get("hidden", False):
            with st.container():
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="content">
                            <img src="https://api.dicebear.com/9.x/personas/svg?seed=Amaya" class="avatar" />
                            <div class="message">
                                {message["content"]}
                                <div class="timestamp">{get_timestamp(message)}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="content">
                            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=banking-agent" class="avatar" />
                            <div class="message">
                                {message["content"]}
                                <div class="timestamp">{get_timestamp(message)}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    if st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]
        if last_message["role"] == "assistant" and (st.session_state.banking_context.traducciones["TAREA_REALIZADA_PROS"] in last_message["content"]
                                                    or st.session_state.waiting_for_rag_confirmation == True):
            last_user_message = next((msg for msg in reversed(st.session_state.chat_history) if msg["role"] == "user"), None)
            if not last_user_message or (last_user_message["content"].lower() not in ["yes", "no"]):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"{st.session_state.banking_context.traducciones['SI']}", key=f"yes_button_{st.session_state.thread_id}"):
                        st.session_state.Usuario_click = "SI"
                        st.rerun()
                with col2:
                    if st.button(f"{st.session_state.banking_context.traducciones['NO']}", key=f"no_button_{st.session_state.thread_id}"):
                        st.session_state.Usuario_click = "NO"
                        st.rerun()

    # User input handling
    if st.session_state.chat_enabled:
        if st.session_state.task_solved:
            user_input = st.chat_input("Ask about banking tasks...")
            if user_input:
                if st.session_state.idioma == "":
                    summary_result = Runner.run_sync(get_language, user_input)
                    st.session_state.idioma = summary_result.final_output_as(get_language).idioma
                    ActualizaIdioma(st.session_state.banking_context.nif, st.session_state.idioma)
                    diccionario_idioma = check_and_update_language(st.session_state.banking_context.nif)
                    st.session_state.traducciones = get_translated_messages(diccionario_idioma["idioma"])
                    st.session_state.banking_context.traducciones = st.session_state.traducciones
                    

                timestamp = datetime.now().strftime("%I:%M %p")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": timestamp
                })
                st.markdown(f"""
                    <div class="chat-message user">
                        <div class="content">
                            <img src="https://api.dicebear.com/9.x/personas/svg?seed=Amaya" class="avatar" />
                            <div class="message">
                                {user_input}
                                <div class="timestamp">{get_timestamp(st.session_state.chat_history[-1])}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.session_state.processing_message = user_input
                st.session_state.task_solved = False
                st.session_state.current_agent = None
                st.rerun()
        else:
            if st.session_state.Usuario_click != "":
                feedback = st.session_state.Usuario_click
            else:
                feedback = st.chat_input("Continue with the current task...")

            if feedback or st.session_state.task_success:
                if feedback:
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": feedback,
                        "timestamp": timestamp
                    })
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="content">
                            <img src="https://api.dicebear.com/9.x/personas/svg?seed=Amaya" class="avatar" />
                            <div class="message">
                                {feedback}
                                <div class="timestamp">{get_timestamp(st.session_state.chat_history[-1])}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.chat_history_agent.append({
                        "role": "user",
                        "content": feedback
                    })

                if st.session_state.task_success:
                    st.session_state.task_success = False
                    clean_history = st.session_state.chat_history_agent
                    summary_result = Runner.run_sync(context_summarizer_agent, clean_history)
                    st.session_state.context_summary = summary_result.final_output_as(context_summarizer_agent).summary
                    
                    if (hasattr(st.session_state, 'separated_tasks') and 
                        st.session_state.separated_tasks and 
                        len(st.session_state.separated_tasks) > 1):
                        completed_task = st.session_state.separated_tasks.pop(0)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Task completed. Summary: {st.session_state.context_summary}",
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "hidden": True
                        })
                        st.session_state.chat_history_agent.append({
                            "role": "assistant",
                            "content": f"Task completed. Summary: {st.session_state.context_summary}"
                        })
                        next_task = st.session_state.separated_tasks[0] if st.session_state.separated_tasks else None
                        if next_task:
                            st.session_state.waiting_for_task_confirmation = True
                            st.session_state.next_task = next_task.order
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": f"{st.session_state.banking_context.traducciones['TAREA_REALIZADA_PROS']}  '{next_task.order}'? {st.session_state.banking_context.traducciones['SI_NO']}",
                                "timestamp": datetime.now().strftime("%I:%M %p")
                            })
                            st.session_state.chat_history_agent.append({
                                "role": "assistant",
                                "content": f"{st.session_state.banking_context.traducciones['TAREA_REALIZADA_PROS']} '{next_task.order}'? {st.session_state.banking_context.traducciones['SI_NO']}"
                            })
                            st.session_state.task_solved = False
                    else:
                        st.session_state.chat_history_agent.append({
                            "role": "assistant",
                            "content": f"Task completed. Summary: {st.session_state.context_summary}"
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"{st.session_state.banking_context.traducciones['ALGO_MAS']}",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.chat_history_agent.append({
                            "role": "assistant",
                            "content": f"{st.session_state.banking_context.traducciones['ALGO_MAS']}"
                        })

                        

                        st.session_state.task_solved = True
                        st.session_state.current_agent = None
                        st.session_state.current_task = None
                        if hasattr(st.session_state, 'separated_tasks'):
                            st.session_state.separated_tasks = None
                        if hasattr(st.session_state, 'waiting_for_task_confirmation'):
                            del st.session_state.waiting_for_task_confirmation
                        if hasattr(st.session_state, 'next_task'):
                            del st.session_state.next_task
                    st.rerun()

                elif (st.session_state.waiting_for_task_confirmation or st.session_state.waiting_for_rag_confirmation):
                    if st.session_state.Usuario_click == "SI":
                        st.session_state.Usuario_click = ""
                        st.session_state.current_task = st.session_state.next_task
                        st.session_state.current_agent, st.session_state.is_question_rag, st.session_state.current_rag_info, st.session_state.current_rag_research = configure_agent_coordinator(st.session_state.current_task)
                        if st.session_state.current_agent is None:
                            st.session_state.current_agent = define_default_agent()
                        context_adicional = AddContextToAgent(st.session_state.current_agent.name, st.session_state.banking_context.nif)
                        if hasattr(st.session_state.current_agent, 'instructions'):
                            st.session_state.current_agent.instructions += "\nUse the conversation history or provided context summary to infer details unless specified otherwise."
                        st.session_state.current_agent.instructions += f"\nAl usuario siempre le respondes en el idioma {st.session_state.idioma} "
                        print("INSTRUCT")
                        print(st.session_state.current_agent.instructions)
                        if context_adicional != "":
                            st.session_state.current_agent.instructions += context_adicional

                        new_conversation_history_agent = [
                            {"content": f"{st.session_state.banking_context.traducciones['TAREA_REALIZADA_PROS']} '{st.session_state.current_task}'?  {st.session_state.banking_context.traducciones['SI_NO']}", "role": "system"},
                            {"content": feedback.lower(), "role": "user"}
                        ]
                        st.session_state.chat_history_agent = new_conversation_history_agent
                        conversation_history, response, task_success = process_task_with_threading(
                            st.session_state.current_agent,
                            st.session_state.current_task,
                            st.session_state.chat_history_agent,
                            st.session_state.context_summary,
                            st.session_state.banking_context
                        )
                        st.session_state.task_success = task_success
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.chat_history_agent.append({
                            "role": "assistant",
                            "content": response
                        })
                        st.session_state.waiting_for_task_confirmation = False
                        st.session_state.waiting_for_rag_confirmation = False
                        del st.session_state.next_task
                    elif st.session_state.Usuario_click == "NO":
                        st.session_state.Usuario_click = ""
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"{st.session_state.banking_context.traducciones['NO_PROS_ALGO_MAS']}",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })

                        st.session_state.chat_history_agent.append({
                            "role": "assistant",
                            "content": f"{st.session_state.banking_context.traducciones['NO_PROS_ALGO_MAS']}"
                        })
                        st.session_state.task_solved = True
                        st.session_state.current_agent = None
                        st.session_state.current_task = None
                        st.session_state.separated_tasks = None
                        st.session_state.waiting_for_task_confirmation = False
                        del st.session_state.next_task
                    st.rerun()
                else:
                    current_agent = st.session_state.current_agent
                    if isinstance(current_agent, dict):
                        current_agent = current_agent.get('handler', define_default_agent())
                    conversation_history, response, task_success = process_task_with_threading(
                        current_agent,
                        st.session_state.current_task,
                        st.session_state.chat_history_agent,
                        st.session_state.context_summary,
                        st.session_state.banking_context
                    )
                    st.session_state.task_success = task_success
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": timestamp
                    })
                    st.session_state.chat_history_agent.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.rerun()

    if st.session_state.processing_message and st.session_state.chat_enabled:
        user_input = st.session_state.processing_message
        st.session_state.processing_message = None

        try:
            if st.session_state.current_agent is not None:
                current_agent = st.session_state.current_agent
                if isinstance(current_agent, dict):
                    current_agent = current_agent.get('handler', define_default_agent())
                conversation_history, response, task_success = process_task_with_threading(
                    current_agent,
                    st.session_state.current_task,
                    st.session_state.chat_history_agent,
                    st.session_state.context_summary,
                    st.session_state.banking_context
                )
                st.session_state.task_success = task_success
                st.session_state.chat_history = conversation_history
                st.session_state.chat_history_agent = conversation_history
            else:
                guardrail_result = process_guardrail_with_threading(banking_guardrail_agent, user_input)
                guardrail_output = guardrail_result.final_output_as(banking_guardrail_agent)
                filtered_input = guardrail_output.filtered_text
                
                if guardrail_output.non_banking_content_removed and filtered_input == "":
                    response = "Non-banking content removed. Processing only banking-related requests."
                    st.session_state.task_solved = True
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="content">
                            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=banking-agent" class="avatar" />
                            <div class="message">
                                f"{st.session_state.banking_context.traducciones['PROCESO_PREG_BANC']}"
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"{st.session_state.banking_context.traducciones['PROCESO_PREG_BANC']}"
                    })
                else:
                    separator_result = process_separator_with_threading(task_separator_agent, filtered_input)
                    separated_tasks = separator_result.final_output_as(task_separator_agent).items_found
                    st.session_state.separated_tasks = separated_tasks
                    
                    if not separated_tasks:
                        agent = define_default_agent()
                        new_conversation_history = [
                            {"content": f"Context from previous tasks: {st.session_state.context_summary}", "role": "system"},
                            {"content": user_input, "role": "user", "timestamp": datetime.now().strftime("%I:%M %p")}
                        ]
                        result = Runner.run_sync(agent, new_conversation_history, context=st.session_state.banking_context)
                        response = result.final_output_as(agent)
                    else:
                        st.session_state.current_task = separated_tasks[0].order
                        st.session_state.current_agent, st.session_state.is_question_rag, st.session_state.current_rag_info, st.session_state.current_rag_research = configure_agent_coordinator(st.session_state.current_task)
                        st.session_state.current_agent = st.session_state.current_agent if st.session_state.current_agent is not None else define_default_agent()
                        context_adicional = AddContextToAgent(st.session_state.current_agent.name, st.session_state.banking_context.nif)
                        if hasattr(st.session_state.current_agent, 'instructions'):
                            st.session_state.current_agent.instructions += "\nUse the conversation history or provided context summary to infer details unless specified otherwise."
                        st.session_state.current_agent.instructions += f"\nAl usuario siempre le respondes en el idioma {st.session_state.idioma} "
                        print("INSTRUCT")
                        print(st.session_state.current_agent.instructions)
                        if context_adicional != "":
                            st.session_state.current_agent.instructions += context_adicional
                        
                        new_conversation_history_chat = [
                            {"content": f"Context from previous tasks: {st.session_state.context_summary}", "role": "system"},
                            {"content": st.session_state.current_task, "role": "user", "timestamp": datetime.now().strftime("%I:%M %p")}
                        ]
                        new_conversation_history_agent = [
                            {"content": f"Context from previous tasks: {st.session_state.context_summary}", "role": "system"},
                            {"content": st.session_state.current_task, "role": "user"}
                        ]
                        if st.session_state.is_question_rag == True and st.session_state.current_agent.name not in ("News Coordinator", "Analytics", "Account_Balance"):
                            conversation_history, response, task_success, response_info_rag = process_task_with_threading_concurrent(
                                st.session_state.current_rag_info,
                                st.session_state.current_rag_research,
                                st.session_state.current_task,
                                new_conversation_history_agent,
                                st.session_state.context_summary,
                                st.session_state.banking_context
                            )
                            st.session_state.chat_history_agent.extend(new_conversation_history_agent[1:])
                            if response_info_rag != "":
                                st.session_state.waiting_for_rag_confirmation = True
                                st.session_state.task_success = False
                                st.session_state.next_task = st.session_state.current_task
                            else:
                                st.session_state.task_success = True
                            timestamp = datetime.now().strftime("%I:%M %p")
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": timestamp
                            })
                            st.session_state.chat_history_agent.append({
                                "role": "assistant",
                                "content": response
                            })
                        else:
                            conversation_history, response, st.session_state.task_success = process_task_with_threading(
                                st.session_state.current_agent,
                                st.session_state.current_task,
                                new_conversation_history_agent,
                                st.session_state.context_summary,
                                st.session_state.banking_context
                            )
                            st.session_state.chat_history_agent.extend(new_conversation_history_agent[1:])
                            timestamp = datetime.now().strftime("%I:%M %p")
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": timestamp
                            })
                            st.session_state.chat_history_agent.append({
                                "role": "assistant",
                                "content": response
                            })
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            timestamp = datetime.now().strftime("%I:%M %p")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": timestamp
            })
            st.session_state.chat_history_agent.append({
                "role": "assistant",
                "content": error_message
            })
        st.rerun()

    st.divider()

if __name__ == "__main__":
    main()