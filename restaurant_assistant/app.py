import streamlit as st
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
import json
import minsearch  # use relative import if needed
import rag

# Load environment variables
load_dotenv()

# Setup the OpenAI client to use either Groq, OpenAI.com, or Ollama API
API_HOST = os.getenv("API_HOST")

if API_HOST == "groq":
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
    MODEL_NAME = os.getenv("GROQ_MODEL")

elif API_HOST == "ollama":
    client = OpenAI(
        base_url=os.getenv("OLLAMA_ENDPOINT"),
        api_key="nokeyneeded"
    )
    MODEL_NAME = os.getenv("OLLAMA_MODEL")

elif API_HOST == "openai":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL_NAME = os.getenv("OPENAI_MODEL")
else:
    MODEL_NAME = "llama3-8b-8192"  # Set a default model if none selected
    st.write("groq Selected")
    st.stop()

# App Title
st.title("Restaurant Chatbot with RAG")


st.write(f"""
Enhance your dining experience with this chatbot! It helps waitstaff by making the menu more transparent and accessible to customers, saving time for everyone. Ask questions like:

- What ingredients are in this cake?
- Do you have a cake with XYZ?
- What's the price of this item?
- What is the cheapest cake available?
- Can you show me cakes under $10?
""")

# Input for the user query
query = st.text_input("Enter your question about the restaurant menu:")


# Button to handle question res
if st.button("Submit"):
    if not query:
        st.error("Please enter a question.")
    else:
        with st.spinner("Fetching answer..."):
            # Call the RAG pipeline
            answer_data = rag.rag(query, model=MODEL_NAME)

            # Display the result
            
            st.write(f"Answer: {answer_data['answer']}")
            st.write(f"Response Time: {answer_data['response_time']} seconds")
            st.write(f"Relevance: {answer_data['relevance']}")
            st.write(f"Cost: ${answer_data['openai_cost']:.6f}")
