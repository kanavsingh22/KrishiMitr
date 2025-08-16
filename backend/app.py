from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import hashlib
import json
import time
from googletrans import Translator, LANGUAGES

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_model.rag_pipeline import RAGPipeline
from utils.ipfs_client import ipfs_client
from utils.blockchain_client import blockchain_client

app = Flask(__name__)
CORS(app)

# --- Service Initialization ---
try:
    rag_pipeline = RAGPipeline()
    translator = Translator()
    print("Backend services initialized successfully.")
except Exception as e:
    print(f"FATAL: Failed to initialize services: {e}")
    rag_pipeline = None
    translator = None

# --- NEW: Conversational Layer ---
CONVERSATIONAL_RESPONSES = {
    "greetings": {
        "keywords": ["hello", "hi", "hey", "namaste", "नमस्ते", "namaskar", "नमस्कार"],
        "en": "Hello! I am KrishiMitr, your AI agricultural assistant. How can I help you today?",
        "hi": "नमस्ते! मैं कृषि मित्र हूँ, आपका AI कृषि सहायक। मैं आज आपकी कैसे मदद कर सकता हूँ?"
    },
    "thanks": {
        "keywords": ["thank you", "thanks", "dhanyavad", "धन्यवाद", "shukriya", "शुक्रिया"],
        "en": "You're welcome! Feel free to ask if you have more questions.",
        "hi": "आपका स्वागत है! यदि आपके कोई और प्रश्न हैं तो बेझिझक पूछें।"
    }
}

@app.route('/api/ask', methods=['POST'])
def ask_question():
    if not rag_pipeline or not translator:
        return jsonify({"error": "Backend services are not available."}), 500
        
    data = request.get_json()
    query = data.get('query', '').lower()

    # --- Step 1: Check for Conversational Keywords ---
    detected_lang = 'en' # Default language
    try:
        detected_lang = translator.detect(query).lang
    except Exception:
        pass # Keep default if detection fails

    for intent, value in CONVERSATIONAL_RESPONSES.items():
        if any(keyword in query for keyword in value['keywords']):
            response_text = value.get(detected_lang, value['en'])
            # Return a simple response without blockchain anchoring
            return jsonify({"answer": response_text, "sources": ["Conversational"]})

    # --- Step 2: If not conversational, proceed with RAG pipeline ---
    query_for_rag = query
    if detected_lang == 'hi':
        try:
            translated_query = translator.translate(query, src='hi', dest='en')
            query_for_rag = translated_query.text
        except Exception as e:
            return jsonify({"error": f"Language translation failed: {e}"}), 500

    answer_en, sources = rag_pipeline.ask(query_for_rag)
    
    final_answer = answer_en
    if detected_lang == 'hi':
        try:
            translated_answer = translator.translate(answer_en, src='en', dest='hi')
            final_answer = translated_answer.text
        except Exception:
            final_answer = answer_en # Fallback to English

    # --- Step 3: Anchor evidence and send response ---
    evidence = { "timestamp": time.time(), "query": query, "answer": final_answer, "sources": sources }
    evidence_cid = ipfs_client.add_json(evidence)
    asset_id = hashlib.sha256(query.encode() + str(time.time()).encode()).hexdigest()
    tx_id = blockchain_client.submit_transaction(asset_id=asset_id, data_hash=evidence_cid, owner="KrishiMitrSystem")

    response = { "answer": final_answer, "sources": sources, "evidence_hash": evidence_cid, "blockchain_tx_id": tx_id }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)