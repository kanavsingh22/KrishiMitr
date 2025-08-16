import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import os
import sys

class RAGPipeline:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the RAG pipeline.
        - Loads a sentence transformer model.
        - Loads and encodes the knowledge base from a CSV file.
        """
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = None
        self.kb_embeddings = None
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Loads the knowledge base from the CSV file and pre-computes embeddings."""
        kb_path = os.path.join(os.path.dirname(__file__), 'data', 'knowledge_base.csv')
        try:
            self.knowledge_base = pd.read_csv(kb_path)
            # Ensure 'content' column is string type
            self.knowledge_base['content'] = self.knowledge_base['content'].astype(str)
            # Pre-compute embeddings for faster retrieval
            self.kb_embeddings = self.model.encode(self.knowledge_base['content'].tolist(), convert_to_tensor=True)
            print("Knowledge base loaded and embeddings computed successfully.")
        except FileNotFoundError:
            print("="*60)
            print(f"FATAL ERROR: Knowledge base file not found at {kb_path}.")
            print("Please create this file by running the ETL script:")
            print("python data_ingestion/etl.py")
            print("="*60)
            # Exit the application if the core data file is missing
            sys.exit(1) 
            
    def retrieve(self, query, top_k=3):
        """Retrieves the most relevant documents from the knowledge base."""
        if self.kb_embeddings is None or len(self.kb_embeddings) == 0:
            return pd.DataFrame() # Return empty if KB is not loaded
            
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        # Calculate cosine similarity
        cos_scores = util.pytorch_cos_sim(query_embedding, self.kb_embeddings)[0]
        
        # Get top_k scores and their indices
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.knowledge_base)))
        
        # Return the top N most similar documents
        retrieved_docs = self.knowledge_base.iloc[top_results.indices.cpu()]
        return retrieved_docs

    def generate_answer(self, query, retrieved_docs):
        """
        Generates a concise answer based on the query and retrieved documents.
        This is a simplified "generation" step. A real LLM would be used here.
        """
        if retrieved_docs.empty:
            return "I'm sorry, I could not find relevant information to answer your question.", []

        # Simple heuristic: if the query is about price, extract price info. Otherwise, return the most relevant doc.
        if "price" in query.lower() or "market" in query.lower():
            for content in retrieved_docs['content']:
                if "Rs." in content and any(word in content.lower() for word in query.lower().split()):
                    return content, retrieved_docs['source'].unique().tolist()
        
        # Default to returning the content of the single most relevant document
        answer = retrieved_docs.iloc[0]['content']
        sources = retrieved_docs['source'].unique().tolist()

        return answer, sources

    def ask(self, query):
        """
        End-to-end function to handle a user query.
        """
        retrieved_docs = self.retrieve(query)
        answer, sources = self.generate_answer(query, retrieved_docs)
        return answer, sources

# (The rest of the file `fine_tuning_placeholder.py` remains the same)