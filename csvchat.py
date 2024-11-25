import os
import time
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import google.generativeai as genai

# Step 1: Load environment variables and configure API key
def load_api_key():
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)

# Step 2: Define functions for uploading and processing files
def upload_to_gemini(path, mime_type="text/csv"):
    """Uploads the given file to Gemini and returns the file object."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_files_active(files):
    """Waits for files to be ready for use after uploading."""
    st.info("Processing your file...")
    for file in files:
        while file.state.name == "PROCESSING":
            time.sleep(5)
            file = genai.get_file(file.name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process.")
    st.success("Your file is ready!")

# Define function to handle user questions with chat memory
def ask_question(chat_session, question):
    """Sends a question to the chat session and returns the response with memory and content checking."""
    # Gather chat history from session state
    chat_history = [{"role": "user", "content": msg["content"]} for msg in st.session_state.messages]
    chat_history.append({"role": "user", "content": question})

    response = chat_session.send_message(question)

    # Handle cases where the response does not contain relevant information
    if "not in the CSV file" in response.text.lower() or not response.text.strip():
        return (
            "The document you provided does not contain information on this topic.\n\n"
            f"To answer your question, '{question}':\n"
            f"{response.text.strip() or 'This information is not included in the CSV file.'}"
        )
    return response.text

# Main function for the Streamlit app
def main():
    load_api_key()  # Initialize API key
    #st.set_page_config(page_title="CSV Chatbot")
    st.title("Query Your CSV File")

    # Sidebar instructions
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("1. Upload a CSV file containing events.")
    st.sidebar.markdown("2. Wait for the file to be processed.")
    st.sidebar.markdown("3. Ask questions based on the events in the file.")

    # File upload and chat session initialization
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_file.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload the CSV file and check if it’s ready
        files = [upload_to_gemini("temp_file.csv")]
        wait_for_files_active(files)

        # Chat configuration
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 50,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
        
        # Start the chat session with CSV-specific instructions
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                        "Only answer questions based on the events in this CSV file. If a question is outside the scope of this CSV, respond with a polite message stating the content is not included.",
                    ],
                }
            ]
        )

        # Step 4: User input and chat display
        user_question = st.chat_input("Ask a question about the events:")

        if user_question:
            # Append user's question to chat history
            st.session_state.messages.append({"content": user_question, "is_user": True})
            
            # Generate and display response
            with st.spinner("Thinking..."):
                response_text = ask_question(chat_session, user_question)
            
            # Append model's response to chat history
            st.session_state.messages.append({"content": response_text, "is_user": False})

        # Display chat history
        for i, msg in enumerate(st.session_state.messages):
            if msg["is_user"]:
                message(msg["content"], is_user=True, key=f"{i}_user")
            else:
                message(msg["content"], is_user=False, key=f"{i}_ai")

# Run the app
if __name__ == "__main__":
    main()
