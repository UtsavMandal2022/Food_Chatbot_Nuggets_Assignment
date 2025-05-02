import streamlit as st
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
import json
import minsearch  # use relative import if needed
import rag
import requests

# Load environment variables
load_dotenv()

# Setup the model and client
API_HOST = os.getenv("API_HOST")
MODEL_NAME = "bitext/Mistral-7B-Restaurants"
HF_API_KEY = os.getenv("HF_API_KEY")

if API_HOST == "hf":
    def hf_llm(prompt):
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 512
            }
        }
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")
        
elif API_HOST == "groq":
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODEL_NAME = os.getenv("GROQ_MODEL")

elif API_HOST == "ollama":
    client = OpenAI(base_url=os.getenv("OLLAMA_ENDPOINT"), api_key="nokeyneeded")
    MODEL_NAME = os.getenv("OLLAMA_MODEL")

elif API_HOST == "openai":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL_NAME = os.getenv("OPENAI_MODEL")

else:
    MODEL_NAME = "llama3-8b-8192"
    st.write("Unknown or missing API_HOST.")
    st.stop()

# Initialize session state for Q&A history
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []  # list of dicts: {question: ..., answer: ...}

# App title and description
st.title("Restaurant Chatbot with RAG for Nugget Assignment")

st.write("""
Discover your perfect dining spot with this AI-powered chatbot!
This intelligent assistant helps users explore restaurant menus, compare features, and find food that fits their taste, budget, or dietary needs — all in natural language.

This app uses Retrieval-Augmented Generation (RAG) to provide accurate and relevant answers to your questions about the restaurant menu.

**Made By:** Utsav Mandal
""")

# Input for the user query
query = st.text_input("Ask thy doubts!", placeholder="What are some healthy food suggestions?")

# Button to handle submission
if st.button("Submit"):
    if not query:
        st.error("Please enter a question.")
    else:
        with st.spinner("Fetching answer..."):
            try:
                if API_HOST == "hf":
                    start = time.time()
                    answer = hf_llm(query)
                    end = time.time()
                    response_time = round(end - start, 2)
                else:
                    answer_data = rag.rag(query, model=MODEL_NAME)
                    answer = answer_data['answer']
                    response_time = answer_data['response_time']

                # Save to session state
                st.session_state.qa_history.append({
                    "question": query,
                    "answer": answer,
                    "response_time": response_time
                })

                # Display current answer
                st.write(f"**Answer:** {answer}")
                st.write(f"**Response Time:** {response_time} seconds")

            except Exception as e:
                st.error(f"Error occurred: {str(e)}")

# Show history
if st.session_state.qa_history:
    st.subheader("History")
    for i, qa in enumerate(reversed(st.session_state.qa_history), 1):
        with st.expander(f"{i}. {qa['question']}"):
            st.markdown(f"**Answer:** {qa['answer']}")
            st.markdown(f"**Response Time:** {qa['response_time']} seconds")
