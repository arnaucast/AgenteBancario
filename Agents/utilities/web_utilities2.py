
import streamlit as st
from queue import Queue
import threading
from manager import process_single_task
import time
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
import asyncio
from .change_get_data_db import get_ibans_for_nif,get_pans
def AddContextToAgent(agent_name,selected_nif):
    
    if agent_name in ("Transfer Coordinator","Account_Balance"):
        ibans = get_ibans_for_nif(selected_nif)
        if len(ibans) ==1:
            return f"Este cliente emisor tiene el siguiente IBAN, la transferencia realízala con él: {ibans}"
        if len(ibans) >1:
            return f"Este cliente  emisor tiene los siguientes IBANs, pregúntale con cual quiere realizar la transferencia: {ibans}"
        else: 
            return ""
    elif agent_name =="Analytics":
        ibans = get_ibans_for_nif(selected_nif)
        if len(ibans) ==1:
            return f"Este cliente emisor tiene el siguiente IBAN, haz el análisis con él: {ibans}"
        if len(ibans) >1:
            return f"Este cliente emisor tiene los siguientes IBANs, pregúntale al cliente cual utilizar para el análisis {ibans} y devuelve  operation_success  = false"
        else: 
            return ""
    elif agent_name =="Credit Card Cordinator":
        pans=  get_pans(selected_nif)
        if len(pans) ==1:
            return f"Este cliente tiene los siguientes PANs, resuelve con ellos su petición: {pans}"
        elif len(pans) >1:
            return f"Este cliente tiene el siguiente PANs, resuelve con el su petición: {pans}"
        else: 
            return ""
    else:
        return ""


# Wrapper to run process_single_task in a thread and capture the result
def run_task_in_thread(current_agent, current_task, chat_history, context_summary, banking_context, result_queue):
    conversation_history, response,success, _ = process_single_task(
        current_agent,
        current_task,
        chat_history,
        context_summary,
        banking_context
    )
    result_queue.put((conversation_history, response,success))


def process_task_with_threading(current_agent, current_task, chat_history, context_summary, banking_context):
    # Prepare threading components
    result_queue = Queue()
    task_thread = threading.Thread(
        target=run_task_in_thread,
        args=(current_agent, current_task, chat_history, context_summary, banking_context, result_queue)
    )
    task_thread.start()

    # Dynamic status updates with progress bar
    status_container = st.empty()
    progress_bar = st.progress(0)
    if current_agent.name == "Analytics":
        status_messages = [
            "Buscando categorías..",
            "Encontrando nombres categorías reales..",
            "Filtrando nombres categorías reales...",
            "Programando la consulta..."
        ]
        
        # Update progress while the task runs
        for i, status in enumerate(status_messages):
            status_container.text(status)
            progress_bar.progress((i + 1) / len(status_messages))
            time.sleep(4)  # Adjust this to approximate task duration / steps
    else:
        status_messages = [
            "Obteniendo datos..",
            "Procesando tarea...",
            "Finalizando..."
        ]
        
        # Update progress while the task runs
        for i, status in enumerate(status_messages):
            status_container.text(status)
            progress_bar.progress((i + 1) / len(status_messages))
            time.sleep(1.25)  # Adjust this to approximate task duration / steps
    
    # Wait for the thread to finish and get the result
    task_thread.join()
    conversation_history, response,task_success= result_queue.get()

    # Final UI update
    status_container.text("Hecho!")
    progress_bar.progress(1.0)
    
    return conversation_history, response,task_success

# New wrapper for task_separator_agent
def run_separator_in_thread(task_separator_agent, filtered_input, result_queue):
    separator_result = Runner.run_sync(task_separator_agent, filtered_input)
    result_queue.put(separator_result)

def process_separator_with_threading(task_separator_agent, filtered_input):
    result_queue = Queue()
    separator_thread = threading.Thread(
        target=run_separator_in_thread,
        args=(task_separator_agent, filtered_input, result_queue)
    )
    separator_thread.start()

    status_container = st.empty()
    progress_bar = st.progress(0)
    status_messages = [
        "Analizando mensaje...",
        "Separando tareas...",
        "Procesando resultados..."
    ]
    
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(0.75)  # Shorter duration since this might be faster
    
    separator_thread.join()
    separator_result = result_queue.get()

    status_container.text("Hecho!")
    progress_bar.progress(1.0)
    
    return separator_result


# New wrapper for banking_guardrail_agent
def run_guardrail_in_thread(banking_guardrail_agent, user_input, result_queue):
    guardrail_result = Runner.run_sync(banking_guardrail_agent, user_input)
    result_queue.put(guardrail_result)

def process_guardrail_with_threading(banking_guardrail_agent, user_input):
    result_queue = Queue()
    guardrail_thread = threading.Thread(
        target=run_guardrail_in_thread,
        args=(banking_guardrail_agent, user_input, result_queue)
    )
    guardrail_thread.start()

    status_container = st.empty()
    progress_bar = st.progress(0)
    status_messages = [
        "Analizando mensaje...",
        "Aplicando filtros...",
        "Validando el contenido..."
    ]
    
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(0.5)  # Even shorter duration for guardrail check
    
    guardrail_thread.join()
    guardrail_result = result_queue.get()

    status_container.text("Hecho!")
    progress_bar.progress(1.0)
    
    return guardrail_result


########################################################### Deal with RAG question ###############################################################################


def process_task_with_threading_concurrent(agent_get_info_rag, agent_rag_research, current_task, chat_history, context_summary, banking_context):
    # Prepare threading components for two agents
    result_queue1 = Queue()
    result_queue2 = Queue()
    
    # Create threads for both agents
    thread1 = threading.Thread(
        target=run_task_in_thread,
        args=(agent_get_info_rag, current_task, chat_history, context_summary, banking_context, result_queue1)
    )
    thread2 = threading.Thread(
        target=run_task_in_thread,
        args=(agent_rag_research, current_task, chat_history, context_summary, banking_context, result_queue2)
    )
    
    # Start both threads concurrently
    thread1.start()
    thread2.start()

    # Dynamic status updates with progress bar
    status_container = st.empty()
    progress_bar = st.progress(0)
    status_messages = [
        "Inicializando agentes...",
        "Procesando con Agent2 investigador...",
        "Procesando con Agente buscador de acciones...",
        "Combinando resultados..."
    ]
    
    # Update progress while tasks run
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(1.25)  # Adjust this to approximate task duration / steps
    
    # Wait for both threads to finish
    thread1.join()
    thread2.join()
    
    # Get results from both queues
    conversation_history_info_rag, response_info_rag, success1 = result_queue1.get()
    conversation_history_res_rag, response_research_rag, success2 = result_queue2.get()
    
    print("Task states:")
    print(f"Agent 1 success: {success1}")
    print(f"Agent 2 success: {success2}")

    # Final UI update
    status_container.text("Hecho!")
    progress_bar.progress(1.0)

    if response_info_rag  != "": 
        response_total = f"{response_research_rag}. <br><b>{response_info_rag}</b>"
        conversation_history_res_rag.append({"content": response_info_rag, "role": "assistant"})
    else: 
        response_total = response_research_rag 

    
    # Return results from both agents
    return conversation_history_res_rag, response_total,True,response_info_rag