
import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from streamlit_chat import message  # To display chat history

# Step 1: Load environment variables and configure API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # Ensure your API key is set as an environment variable
genai.configure(api_key=API_KEY)

def main():
    # Step 2: Initialize Streamlit app
    #st.set_page_config(page_title="Code Summarization and Debugging Assistant")
    st.title("Code Summarization and Debugging Assistant")

    # Chat history stored in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Step 3: File upload and content reading
    uploaded_file = st.file_uploader("Upload your code file (Python, Java, or C)", type=["py", "java", "c", "cpp"])

    if uploaded_file is not None:
        # Read uploaded file content
        code_content = uploaded_file.read().decode("utf-8")
        st.code(code_content, language="python" if uploaded_file.type == "text/x-python" else "java" if uploaded_file.type == "text/x-java" else "c")  # Display code based on type

        # Chat configuration
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 1024,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

        # Step 4: Define function to analyze code
        def analyze_code(task):
            """Sends code and task (summarize/debug) to the model for analysis."""
            prompt = f"Here is some code:\n{code_content}\n\nTask: {task}\nProvide a detailed response."
            # Use send_message to get the model's response
            response = model.start_chat(history=[
                {
                    "role": "user",
                    "parts": [
                        prompt
                    ]
                }
            ])
            return response.send_message(prompt).text  # Corrected method to send message

        # Step 5: Summarize or Debug based on user choice
        task = st.radio("Choose what you want the assistant to do:", ("Summarize Code", "Debug Code"))

        if st.button("Run Analysis"):
            with st.spinner("Analyzing..."):
                if task == "Summarize Code":
                    # Summarize the code
                    response_text = analyze_code("Summarize what the code does in simple terms.")
                else:
                    # Debug the code
                    response_text = analyze_code("Identify any errors in the code and suggest potential fixes.")
                
                # Append user's question and model's response to chat history
                st.session_state.messages.append({"content": task, "is_user": True})
                st.session_state.messages.append({"content": response_text, "is_user": False})

        # Display chat history
        for i, msg in enumerate(st.session_state.messages):
            message(msg["content"], is_user=msg["is_user"], key=f"{i}_msg")

    # Additional Instructions
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("1. Upload a code file in Python (.py), Java (.java), or C (.c/.cpp).")
    st.sidebar.markdown("2. Choose to either summarize or debug the code.")
    st.sidebar.markdown("3. Click 'Run Analysis' to receive an explanation or debugging assistance.")

if __name__ == "__main__":
    main()
