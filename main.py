import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import hashlib
st.set_page_config(page_title="Multi-Function AI Bot", layout="centered")
# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Setup
client = MongoClient(MONGO_URI)
db = client["chatbot"]
user_collection = db["user_details"]

# Hashing password for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check for duplicate user
def user_exists(email):
    return user_collection.find_one({"email": email}) is not None

# Signup Function
def signup(name, email, password):
    if user_exists(email):
        st.warning("User already exists. Please login.")
        return False
    user_collection.insert_one({"name": name, "email": email, "password": hash_password(password)})
    st.success("Signup successful. Please login.")
    return True

# Login Function
def login(email, password):
    user = user_collection.find_one({"email": email, "password": hash_password(password)})
    if user:
        st.session_state["user"] = user
        return True
    else:
        st.warning("Incorrect email or password.")
        return False

# Sidebar for Account Management
st.sidebar.title("Account")
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    action = st.sidebar.radio("Choose Action", ["Signup", "Login"])
    if action == "Signup":
        name = st.sidebar.text_input("Name")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Signup"):
            signup(name, email, password)
    elif action == "Login":
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(email, password):
                st.sidebar.success("Login successful.")
else:
    st.sidebar.write(f"Welcome, {st.session_state['user']['name']}")
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None

# Home Page after login
st.title("Multi-Function AI Bot")
if st.session_state["user"]:
    module = st.selectbox("Choose a Module", [
        "PDF Question Answering Bot",
        "CSV Bot",
        "Link Summarizer",
        "Text Summarizer",
        "Code Summarizer"
    ])

    # Import and run the chosen module
    if module == "PDF Question Answering Bot":
        import pdfchat
        pdfchat.main()
        
    elif module == "CSV Bot":
        import csvchat
        csvchat.main()

    elif module == "Link Summarizer":
        import linksumm
        linksumm.main()

    elif module == "Text Summarizer":
        import parasumm
        parasumm.main()

    elif module == "Code Summarizer":
        import codesumm
        codesumm.main()
