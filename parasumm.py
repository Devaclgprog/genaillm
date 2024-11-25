import streamlit as st
from transformers import pipeline
from dotenv import load_dotenv
import os

# Load environment variables and configure API key if required
load_dotenv()

# Initialize summarization and sentiment-analysis pipelines
summarizer = pipeline("summarization")
sentiment_analyzer = pipeline("sentiment-analysis")

def main():
    # Set up Streamlit app
    #st.set_page_config(page_title="Text Summarization & Sentiment Analysis")
    st.title("Text Summarization & Sentiment Analysis")

    # File upload or text input section
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    user_text = st.text_area("Or paste text here:", height=200)

    if uploaded_file is not None or user_text:
        # Read text from uploaded file or text input
        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")
        else:
            text = user_text

        # Summarize the text
        with st.spinner("Summarizing..."):
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

        # Perform sentiment analysis
        with st.spinner("Analyzing sentiment..."):
            sentiment = sentiment_analyzer(text[:512])[0]  # Analyze only first 512 tokens for faster results

        # Display results
        st.subheader("Summary:")
        st.write(summary)

        st.subheader("Sentiment Analysis:")
        st.write(f"Label: {sentiment['label']} | Confidence: {sentiment['score']:.2f}")

    # Instructions in sidebar
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("1. Upload a text file or paste text in the input area.")
    st.sidebar.markdown("2. Wait for the text to be summarized and analyzed.")

if __name__ == "__main__":
    main()
