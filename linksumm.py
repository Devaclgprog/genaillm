import streamlit as st
from transformers import pipeline
from newspaper import Article
import validators

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")

def main():
    st.title("URL Summarization Tool")

    # User input for URL
    url = st.text_input("Enter the URL of the article you want to summarize:")

    # Check if URL is valid and process it
    if url:
        if validators.url(url):
            with st.spinner("Fetching and summarizing the article..."):
                try:
                    # Download and parse the article
                    article = Article(url)
                    article.download()
                    article.parse()
                    article_text = article.text

                    # Check if article_text is not empty
                    if article_text.strip():
                        # Limit text length for summarization
                        max_input_length = 1024  # Adjust based on model limits
                        article_text = article_text[:max_input_length]
                        
                        # Summarize the article text
                        summary_result = summarizer(
                            article_text, max_length=150, min_length=30, do_sample=False
                        )
                        
                        # Check if summarizer returned any output
                        if summary_result and "summary_text" in summary_result[0]:
                            summary = summary_result[0]["summary_text"]
                            st.subheader("Article Summary:")
                            st.write(summary)
                        else:
                            st.error("The summarization model did not return any summary.")
                    else:
                        st.error("Failed to extract content from the URL. Please try a different URL.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a valid URL.")

    # Instructions in the sidebar
    st.sidebar.markdown("### Instructions")
    st.sidebar.markdown("1. Enter the URL of an article.")
    st.sidebar.markdown("2. The tool will fetch, analyze, and summarize the content.")

if __name__ == "__main__":
    main()
