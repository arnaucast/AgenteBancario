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
from queue import Queue
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
from Agents.utilities.web_utilities import process_task_with_threading,process_separator_with_threading,process_guardrail_with_threading,AddContextToAgent
from Agents.utilities.change_get_data_db import BankingContext,get_all_distinct_cifs,get_ibans_for_web,get_saldos_by_IBAN,get_pan_by_cif,get_name_for_web
from __init__ import unique_contr_mov,unique_type_clie,unique_cifs_with_mov,get_tipo_cliente_iban
# Tracing and environment configuration (you might want to remove or modify these)
import logfire
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
    
    # Container to hold IBANs
    for iban in ibans:
        st.text_input(
            label="IBAN", 
            value=iban.replace(' ', ''),  # Remove all spaces
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

def main():
    initialize_session_state()
    st.set_page_config(page_title="Banking Assistant", page_icon="💼")

    # Custom CSS
    st.markdown("""
    <style>
        .chat-message {
            padding: 1.5rem; 
            border-radius: 0.5rem; 
            margin-bottom: 1rem; 
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #e6f7ff;
            border-left: 5px solid #2196F3;
        }
        .chat-message.assistant {
            background-color: #f0f0f0;
            border-left: 5px solid #4CAF50;
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
            # Create a container for CIF and nombre display
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
            st.session_state.chat_enabled = True

                # Display IBANs and PANs for Primary CIF
        # Modify the IBANs display section for Primary CIF to filter by unique_contr_mov
        if st.session_state.banking_context.nif:
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
            print("Ibandd")
            print(main_ibans[0])
            tipo_cli = get_tipo_cliente_iban(IBAN= main_ibans[0])
            st.markdown(f"*Tipo de cliente:* {tipo_cli[0]}", unsafe_allow_html=True)

            # Display PANs for Primary CIF with rounded numbers
            pans = get_pan_by_cif(st.session_state.banking_context.nif)
            if pans:
                with st.container():
                    for pan, limite, gasto, bloqueada in pans:
                        # Round limite and gasto to 2 decimal places
                        limite_display = f"{int(round(limite, 0))} €" if limite is not None else "N/A"
                        gasto_display = f"{int(round(gasto, 0))} €" if gasto is not None else "0 €"
                        bloqueada_display = "Yes" if bloqueada =="SI" else "No"
                        
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
            # Create a container for Test CIF and nombre display
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
            nombre_test = get_name_for_web(selected_test_cif)

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

    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.task_solved = True
        print("DEBUG: agent gets reset here 3 - New conversation")
        st.session_state.current_agent = None
        st.session_state.current_task = None
        st.session_state.context_summary = ""
        st.success("New conversation started!")
        st.rerun()

    st.caption("Ask me about banking tasks and I'll assist you step-by-step!")

    for message in st.session_state.chat_history:
        if not message.get("hidden", False):
            with st.container():
                if message["role"] == "user":

           
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="content">
                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.thread_id}" class="avatar" />
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

    # Add Yes/No buttons only for the last message, outside the loop
    if st.session_state.chat_history:  # Ensure chat history is not empty
        last_message = st.session_state.chat_history[-1]  # Get the last message
        if last_message["role"] == "assistant" and "Would you like to proceed with the next task" in last_message["content"]:
            # Only show buttons if the user hasn't responded with "yes" or "no" yet
            last_user_message = next((msg for msg in reversed(st.session_state.chat_history) if msg["role"] == "user"), None)
            if not last_user_message or (last_user_message["content"].lower() not in ["yes", "no"]):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key=f"yes_button_{st.session_state.thread_id}"):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": "yes",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.Usuario_click = "SI"
                        print("DEBUG: Yes button clicked, Usuario_click set to SI")
                        st.rerun()
                with col2:
                    if st.button("No", key=f"no_button_{st.session_state.thread_id}"):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": "no",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.Usuario_click = "NO"
                        print("DEBUG: No button clicked, Usuario_click set to NO")
                        st.rerun()

    # User input handling
    print("analisis")
    print(st.session_state.chat_enabled)
    print(st.session_state.task_solved)
    print(st.session_state.processing_message)
    if st.session_state.chat_enabled:
        if st.session_state.task_solved:
            print("1uicoee")
            user_input = st.chat_input("Ask about banking tasks...")
            if user_input:
                st.session_state.processing_message = user_input
                st.session_state.task_solved = False
                print("DEBUG: agent gets reset here 1 - New task input")
                st.session_state.current_agent = None
                st.rerun()
        else:
            if st.session_state.Usuario_click != "":
                feedback= st.session_state.Usuario_click 
            else:
                feedback = st.chat_input("Continue with the current task...")

            if feedback or st.session_state.task_success == True:
                if feedback:
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": feedback,
                        "timestamp": timestamp
                    })
                    print("DEBUG: appending because feedback")

                # Replace the existing "yes, solved" block with this:
                # Replace the entire "yes, solved" block with this:
                if st.session_state.task_success == True:
                    st.session_state.task_success = False
                    clean_history = prepare_clean_history(st.session_state.chat_history)
                    print("DEBUG: clean_conversation_history before summarization:", clean_history)
                    summary_result = Runner.run_sync(context_summarizer_agent, clean_history)
                    st.session_state.context_summary = summary_result.final_output_as(context_summarizer_agent).summary
                    
                    # Check if there are more tasks in separated_tasks
                    if (hasattr(st.session_state, 'separated_tasks') and 
                        st.session_state.separated_tasks and 
                        len(st.session_state.separated_tasks) > 1):
                        # Remove the completed task (first one)
                        completed_task = st.session_state.separated_tasks.pop(0)
                        
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Task completed. Summary: {st.session_state.context_summary}",
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "hidden": True
                        })
                        
                        # Store that we're waiting for confirmation on next task
                        next_task = st.session_state.separated_tasks[0] if st.session_state.separated_tasks else None
                        if next_task:
                            st.session_state.waiting_for_task_confirmation = True
                            st.session_state.next_task = next_task.order
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": f"First task completed. Would you like to proceed with the next task: '{next_task.order}'? (Yes/No)",
                                "timestamp": datetime.now().strftime("%I:%M %p")
                            })

                            st.session_state.task_solved = False
                    else:
                        # Original behavior when there were no separated tasks or only one task
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Task completed. Summary: {st.session_state.context_summary}",
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "hidden": True
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Do you want anything else?",
                            "timestamp": datetime.now().strftime("%I:%M %p")
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
                    
                    print("DEBUG: agent gets reset here 2 - Task solved")
                    print(f"DEBUG: current_agent before reset2: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
                    print(f"DEBUG: current_agent after reset2: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
                    st.rerun()

                # Add this new else-if block right after the "yes, solved" block but before the "else" block:
                elif (hasattr(st.session_state, 'waiting_for_task_confirmation') and 
                    st.session_state.waiting_for_task_confirmation):
                    print("quico0")
                    if st.session_state.Usuario_click == "SI":
                        print("quico1")
                        st.session_state.Usuario_click = ""
                        # User wants to proceed with next task
                        st.session_state.current_task = st.session_state.next_task
                        st.session_state.current_agent = configure_agent_coordinator(st.session_state.current_task)
                        if st.session_state.current_agent is None:
                            st.session_state.current_agent = define_default_agent()
                            
                        context_adicional = AddContextToAgent(st.session_state.current_agent.name, st.session_state.banking_context.nif)
                        if hasattr(st.session_state.current_agent, 'instructions'):
                            st.session_state.current_agent.instructions += "\nUse the conversation history or provided context summary to infer details unless specified otherwise."
                        if context_adicional != "":
                            st.session_state.current_agent.instructions += context_adicional

                        new_conversation_history = [
                            {"content": f"First task completed. Would you like to proceed with the next task: '{st.session_state.current_task}'? (Yes/No)", "role": "system"},
                            {"content": feedback.lower(), "role": "user", "timestamp": datetime.now().strftime("%I:%M %p")}
                        ]

                        # Assign the updated list to st.session_state.chat_history
                        st.session_state.chat_history = new_conversation_history
                        # Process the task immediately
                        conversation_history, response,task_success= process_task_with_threading(
                            st.session_state.current_agent,
                            st.session_state.current_task,
                            prepare_clean_history(st.session_state.chat_history) ,
                            st.session_state.context_summary,
                            st.session_state.banking_context
                        )
                        st.session_state.task_success = task_success
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.waiting_for_task_confirmation = False
                        del st.session_state.next_task
                        
                    elif st.session_state.Usuario_click == "NO":
                        print("quico2")
                        st.session_state.Usuario_click = ""
                        # User doesn't want to continue
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Okay, I won't proceed with the remaining tasks. Do you want anything else?",
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state.task_solved = True
                        st.session_state.current_agent = None
                        st.session_state.current_task = None
                        st.session_state.separated_tasks = None
                        st.session_state.waiting_for_task_confirmation = False
                        del st.session_state.next_task
                    
                    st.rerun()
                else:
                    print(f"DEBUG: continuing task, current agent: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
                    current_agent = st.session_state.current_agent
                    if isinstance(current_agent, dict):
                        current_agent = current_agent.get('handler', define_default_agent())
                    
                    conversation_history, response,task_success = process_task_with_threading(
                        current_agent,
                        st.session_state.current_task,
                        prepare_clean_history(st.session_state.chat_history)  ,
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
                    print("DEBUG: Appended agent response to chat_history:", response)
                    st.rerun()

    # Process message
    if st.session_state.processing_message and st.session_state.chat_enabled:
        user_input = st.session_state.processing_message
        st.session_state.processing_message = None

        try:
            print("DEBUG: Processing message")
            print(f"DEBUG: current_agent at start: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
            if st.session_state.current_agent is not None:
                current_agent = st.session_state.current_agent
                
                if isinstance(current_agent, dict):
                    current_agent = current_agent.get('handler', define_default_agent())

                print("DEBUG: passing info to the agent")
                print(st.session_state.context_summary)
                
                conversation_history, response,task_success = process_task_with_threading(
                    current_agent,
                    st.session_state.current_task,
                    prepare_clean_history( st.session_state.chat_history),
                    st.session_state.context_summary,
                    st.session_state.banking_context
                )
                st.session_state.task_success = task_success

                print("Agent response")
                print(response)
                
                st.session_state.chat_history = conversation_history
                print(f"DEBUG: After process_single_task, current_agent: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
            
            else:
                guardrail_result = process_guardrail_with_threading(banking_guardrail_agent, user_input)
                guardrail_output = guardrail_result.final_output_as(banking_guardrail_agent)
                filtered_input = guardrail_output.filtered_text
                
                if guardrail_output.non_banking_content_removed:
                    response = "Non-banking content removed. Processing only banking-related requests."
                    st.session_state.task_solved = True
                else:
                    separator_result = process_separator_with_threading(task_separator_agent, filtered_input)
                    separated_tasks = separator_result.final_output_as(task_separator_agent).items_found
                    st.session_state.separated_tasks = separated_tasks  # Store all tasks
                    
                    if not separated_tasks:
                        agent = define_default_agent()
                        new_conversation_history = [
                            {"content": f"Context from previous tasks: {st.session_state.context_summary}", "role": "system"},
                            {"content": user_input, "role": "user", "timestamp": datetime.now().strftime("%I:%M %p")}
                        ]
                        result = Runner.run_sync(agent, new_conversation_history, context=st.session_state.banking_context)
                        response = result.final_output_as(agent)
                        st.session_state.chat_history.extend(new_conversation_history[1:])
                        print("Appending chat if not separated")
                    else:
                        print("####################################### SEPARATED TASKS ##############################################")
                        print(separated_tasks)
                        st.session_state.current_task = separated_tasks[0].order
                        
                        current_agent = configure_agent_coordinator(st.session_state.current_task)
                        print(f"DEBUG: Setting current_agent not separated tasks:  {current_agent.name if current_agent is not None else 'None'}")
                        current_agent = current_agent if current_agent is not None else define_default_agent()
                        print(f"DEBUG: Setting current_agent not separated tasks2:  {current_agent.name if current_agent is not None else 'None'}")
                        context_adicional = AddContextToAgent(current_agent.name,st.session_state.banking_context.nif)
                        if hasattr(current_agent, 'instructions'):
                            current_agent.instructions += "\nUse the conversation history or provided context summary to infer details unless specified otherwise."
                        if context_adicional != "":
                            current_agent.instructions += context_adicional
                        print("Contexto_final")
                        print(current_agent.instructions)
                        new_conversation_history = [
                            {"content": f"Context from previous tasks: {st.session_state.context_summary}", "role": "system"},
                            {"content": st.session_state.current_task, "role": "user", "timestamp": datetime.now().strftime("%I:%M %p")}
                        ]
                        conversation_history, response,task_success = process_task_with_threading(
                            current_agent,
                            st.session_state.current_task,
                            prepare_clean_history(new_conversation_history) ,
                            st.session_state.context_summary,
                            st.session_state.banking_context
                        )
                        st.session_state.task_success = task_success
                        print("Agent response")
                        print(response)
                        st.session_state.chat_history.extend(new_conversation_history[1:])
                        print("DEBUG. appending when separated tasks")
                        print(f"DEBUG: Setting current_agent to:  {current_agent.name if current_agent is not None else 'None'}")
                        st.session_state.current_agent = current_agent

                timestamp = datetime.now().strftime("%I:%M %p")
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response, 
                    "timestamp": timestamp
                })
                print("DEBUG: appending here when not none")
            print(f"DEBUG: After appending response, current_agent: {st.session_state.current_agent.name if st.session_state.current_agent is not None else 'None'}")
        
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            timestamp = datetime.now().strftime("%I:%M %p")
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": error_message, 
                "timestamp": timestamp
            })
            print("DEBUG: appending exception")
        
        st.rerun()

    # Footer
    st.divider()

if __name__ == "__main__":
    main()