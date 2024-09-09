import streamlit as st
import threading
from caller import rag,colpali
import time

# Example methods that generate responses based on the user query
def method_1(query, result):
    start_time = time.time()
    response = rag("Normal",query)
    # time.sleep(1)  # Simulate delay
    end_time = time.time()
    result["response_1"] = {
        "response": response,
        "time_taken": end_time - start_time
    }

def method_2(query, result):
    start_time = time.time()
    response = rag("RAPTOR",query)
    # time.sleep(2)  # Simulate delay
    end_time = time.time()
    result["response_2"] = {
        "response": response,
        "time_taken": end_time - start_time
    }

def method_3(query, result):
    start_time = time.time()
    response =colpali(query)
    # time.sleep(0.5)  # Simulate delay
    end_time = time.time()
    result["response_3"] = {
        "response": response,
        "time_taken": end_time - start_time
    }

# Initialize session state for query and chat history if not already present
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Set the page layout to be wide
st.set_page_config(layout="wide")

# Title of the app
st.title("Compare Chat Responses from Three Methods with Execution Time")

# Iterate over the session history and display it using st.chat_message
# Display the chat history
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        # Display the user's query
        with st.chat_message("user"):
            st.write(chat["query"])

        # Create three columns for method 1, method 2, and method 3 responses
        col1, col2, col3 = st.columns(3)

        # Display Method 1 response in the first column
        with col1:
            with st.chat_message("assistant"):
                st.write(chat["response_1"]["response"])
                st.write(f"Execution time: {chat['response_1']['time_taken']:.2f} seconds")

        # Display Method 2 response in the second column
        with col2:
            with st.chat_message("assistant"):
                st.write(chat["response_2"]["response"])
                st.write(f"Execution time: {chat['response_2']['time_taken']:.2f} seconds")

        # Display Method 3 response in the third column
        with col3:
            with st.chat_message("assistant"):
                st.write(chat["response_3"]["response"])
                st.write(f"Execution time: {chat['response_3']['time_taken']:.2f} seconds")

# Input for user query using st.chat_input
query = st.chat_input("What is up?")

# When the user enters a query
if query:
    # Dictionary to store results from the threads
    result = {}

    # Create threads for each method
    t1 = threading.Thread(target=method_1, args=(query, result))
    t2 = threading.Thread(target=method_2, args=(query, result))
    t3 = threading.Thread(target=method_3, args=(query, result))

    # Start all threads at the same time
    t1.start()
    t2.start()
    t3.start()

    # Wait for all threads to finish
    t1.join()
    t2.join()
    t3.join()

    # Store the conversation in session state
    st.session_state.chat_history.append({
        "query": query,
        "response_1": result.get("response_1", {"response": "", "time_taken": 0}),
        "response_2": result.get("response_2", {"response": "", "time_taken": 0}),
        "response_3": result.get("response_3", {"response": "", "time_taken": 0})
    })

    # Display the new chat entries immediately after input
    with st.chat_message("user"):
        st.write(query)

    # Display responses side by side in three columns with execution time
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.chat_message("assistant"):
            st.write(result["response_1"]["response"])
            st.write(f"Execution time: {result['response_1']['time_taken']:.2f} seconds")
    with col2:
        with st.chat_message("assistant"):
            st.write(result["response_2"]["response"])
            st.write(f"Execution time: {result['response_2']['time_taken']:.2f} seconds")
    with col3:
        with st.chat_message("assistant"):
            st.write(result["response_3"]["response"])
            st.write(f"Execution time: {result['response_3']['time_taken']:.2f} seconds")
