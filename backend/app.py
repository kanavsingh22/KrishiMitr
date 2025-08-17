from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import hashlib
import json
import time
from dotenv import load_dotenv
from gnews import GNews
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_model.rag_pipeline import LangChainRAG
from utils.ipfs_client import ipfs_client
from utils.blockchain_client import blockchain_client
from googletrans import Translator
import pandas as pd

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    rag_pipeline = LangChainRAG()
    translator = Translator()
    gnews_api_key = os.getenv("GNEWS_API_KEY")
    if not gnews_api_key:
        print("Warning: GNEWS_API_KEY not found. News functionality will be disabled.")
        gnews = None
    else:
        gnews = GNews()
        gnews.api_key = gnews_api_key
    print("Backend services initialized successfully.")
except Exception as e:
    print(f"FATAL: Failed to initialize services: {e}")
    rag_pipeline = None

CONVERSATIONAL_RESPONSES = {
    "greetings": {"keywords": ["hello", "hi", "hey", "namaste", "नमस्ते"], "en": "Hello! I am KrishiMitr. How can I assist you?", "hi": "नमस्ते! मैं कृषि मित्र हूँ। मैं आपकी कैसे सहायता कर सकता हूँ?"}
}

def generate_llm_style_response(query, context, lang='en'):
    """
    Simulates an LLM summarizing and formatting a response.
    This is the core of the "crisp and well-formatted response" feature.
    """
    print(f"\n---LLM SIMULATOR: Summarizing context for query '{query}'---")
    
    # Heuristics to extract the most important information
    sentences = re.split(r'(?<=[.!?])\s+', context)
    
    # If the query is about price, find the sentence with numbers.
    if "price" in query.lower() or "rate" in query.lower() or "भाव" in query:
        for sentence in sentences:
            if re.search(r'\d', sentence) and ("rs" in sentence.lower() or "price" in sentence.lower()):
                summary = f"**Market Price Information:** {sentence.strip()}"
                return summary
    
    # If the query is a "how-to", try to find instructive sentences.
    if "how to" in query.lower() or "kaise" in query:
         summary = f"**Guidance:** {sentences[0].strip()}"
         if len(sentences) > 1:
             summary += f" {sentences[1].strip()}"
         return summary

    # Default summarization: Return the first 2-3 sentences.
    summary = " ".join(sentences[:2]).strip()
    
    if not summary:
        return "Based on the information found, the details are available in the provided source."
        
    return f"**Key Information:** {summary}"

@app.route('/api/knowledge-base', methods=['GET'])
def get_knowledge_base():
    try:
        kb_path = os.path.join(os.path.dirname(__file__), '..', 'ai_model', 'data', 'knowledge_base.csv')
        df = pd.read_csv(kb_path)
        df['id'] = df.index
        records = df.to_dict('records')
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    if not rag_pipeline: return jsonify({"error": "Backend services unavailable."}), 500
        
    data = request.get_json()
    query = data.get('query', '').lower()

    detected_lang = 'en'
    try:
        if query.strip(): detected_lang = translator.detect(query).lang
        if 'hi' in detected_lang: detected_lang = 'hi' # Standardize to 'hi'
    except Exception: pass

    # Handle conversational queries
    for intent, value in CONVERSATIONAL_RESPONSES.items():
        if any(keyword in query for keyword in value['keywords']):
            return jsonify({"answer": value.get(detected_lang, value['en']), "sources": ["Conversational"]})

    # Main RAG logic
    query_for_rag = query
    if detected_lang == 'hi':
        query_for_rag = translator.translate(query, src='hi', dest='en').text

    context, sources = rag_pipeline.get_context(query_for_rag)
    
    if not context:
        answer_en = "I'm sorry, I could not find a relevant source on the web for your query. Please try rephrasing it."
    else:
        answer_en = generate_llm_style_response(query_for_rag, context, 'en')

    # Robust translation for the final answer
    final_answer = answer_en
    answer_hi = translator.translate(answer_en, src='en', dest='hi').text
    if detected_lang == 'hi':
        final_answer = answer_hi

    response = {
        "answer": final_answer,
        "sources": sources,
        "query_en": query_for_rag,
        "answer_en": answer_en,
        "answer_hi": answer_hi
    }
    
    cache_hash = hashlib.sha256(f"{query_for_rag}:{answer_en}".encode()).hexdigest()
    response["cache_hash"] = cache_hash
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)