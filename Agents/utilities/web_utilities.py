
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

# Wrapper to run process_single_task in a thread and capture the result
def run_task_in_thread(current_agent, current_task, chat_history, context_summary, banking_context, result_queue):
    conversation_history, response, _ = process_single_task(
        current_agent,
        current_task,
        chat_history,
        context_summary,
        banking_context
    )
    result_queue.put((conversation_history, response))

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
    status_messages = [
        "Getting data...",
        "Appending data...",
        "Processing task...",
        "Finalizing..."
    ]
    
    # Update progress while the task runs
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(1.25)  # Adjust this to approximate task duration / steps
    
    # Wait for the thread to finish and get the result
    task_thread.join()
    conversation_history, response = result_queue.get()

    # Final UI update
    status_container.text("Done!")
    progress_bar.progress(1.0)
    
    return conversation_history, response

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
        "Analyzing input...",
        "Separating tasks...",
        "Processing results..."
    ]
    
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(0.75)  # Shorter duration since this might be faster
    
    separator_thread.join()
    separator_result = result_queue.get()

    status_container.text("Done!")
    progress_bar.progress(1.0)
    
    return separator_result

# Wrapper to run process_single_task in a thread and capture the result
def run_task_in_thread(current_agent, current_task, chat_history, context_summary, banking_context, result_queue):
    conversation_history, response, _ = process_single_task(
        current_agent,
        current_task,
        chat_history,
        context_summary,
        banking_context
    )
    result_queue.put((conversation_history, response))


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
        "Checking input...",
        "Applying guardrails...",
        "Validating content..."
    ]
    
    for i, status in enumerate(status_messages):
        status_container.text(status)
        progress_bar.progress((i + 1) / len(status_messages))
        time.sleep(0.5)  # Even shorter duration for guardrail check
    
    guardrail_thread.join()
    guardrail_result = result_queue.get()

    status_container.text("Done!")
    progress_bar.progress(1.0)
    
    return guardrail_result