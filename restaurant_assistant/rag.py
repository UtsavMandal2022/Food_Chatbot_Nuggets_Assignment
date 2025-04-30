import json
from time import time
from openai import OpenAI
import ingest
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

import os
from sklearn.feature_extraction.text import CountVectorizer
from tqdm.auto import tqdm

# Setup the OpenAI client to use either Groq, OpenAI.com, or Ollama API
API_HOST = os.getenv("API_HOST")


if API_HOST == "groq":
    client = client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    )
    MODEL_NAME = os.getenv("GROQ_MODEL")

elif API_HOST == "ollama":
    client = openai.OpenAI(
        base_url=os.getenv("OLLAMA_ENDPOINT"),
        api_key="nokeyneeded",
    )
    MODEL_NAME = os.getenv("OLLAMA_MODEL")

elif API_HOST == "openai":
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL_NAME = os.getenv("OPENAI_MODEL")
else:
    
    MODEL_NAME = "llama3-8b-8192"  # Set a default model if none selected
    print("groq Selected")


# to run in streamlit cloud, i am hard coding the MODEL_NAME to groq, you can change the model as required
index = ingest.load_index()


def minsearch_search(query):
    boost = {

    'question': 2.5,       # High priority: users are searching questions
    'dish_name': 1.7,      # Important for matching specific dishes
    'section': 1.2,        # Moderate boost: helps in filtering by category
    'text': 1.3        # Slight boost: could help match answer content}
    }

    results = index.search(
        query=query,
        filter_dict={'question': query},
        boost_dict=boost,
        num_results=10
    )

    return results


entry_template = """
question: {question}
dish_name: {dish_name}
section: {section}
text: {text}
""".strip()



prompt_template = """
You're an AI assistant helping with menu queries. Answer the QUESTION based on the CONTEXT from our database.
Use only the facts from the CONTEXT when answering the QUESTION.
QUESTION: {question}
CONTEXT: 
{context}
""".strip()


def build_prompt(query, search_results):
    context = ""
    
    for doc in search_results:
        #context += f"Section: {doc['section']}\nQuestion: {doc['question']}\nAnswer: {doc['text']}\n\n"
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt



def llm(prompt, model=MODEL_NAME):
    response = client.chat.completions.create(
        model= MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    
    #return response.choices[0].message.content
    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats

#def llm(prompt, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()


def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model=MODEL_NAME)

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == MODEL_NAME:
        openai_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost


def rag(query, model=MODEL_NAME):
    t0 = time()

    search_results = minsearch_search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt, model=model)

    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

    openai_cost = openai_cost_rag + openai_cost_eval

    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    return answer_data