import os
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms.fake import FakeListLLM

class LangChainRAG:
    def __init__(self):
        """
        Initializes the LangChain-powered RAG pipeline.
        """
        self.search = SerpAPIWrapper()
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = FakeListLLM(responses=["retrieved context placeholder"])

    def search_and_build_retriever(self, query: str):
        """
        Performs a web search, loads the content of the top result,
        chunks the content, and builds a retriever object for similarity search.
        """
        print(f"\n[LangChain] Performing web search for: '{query}'")
        try:
            # --- THIS IS THE CRITICAL FIX ---
            # The 'num_results' argument has been removed as it is no longer supported.
            # The function will now correctly return a dictionary of results.
            results = self.search.results(query)
            # --- END OF FIX ---
        except Exception as e:
            print(f"[LangChain] SerpAPI search failed: {e}")
            return None, []
        
        if not results or "organic_results" not in results or not results["organic_results"]:
            print("[LangChain] Web search returned no organic results.")
            return None, []

        top_result = results["organic_results"][0]
        url = top_result.get("link")
        source = top_result.get("source", "Web Search")
        
        if not url:
            print("[LangChain] No URL found in the top search result.")
            return None, []

        print(f"[LangChain] Loading content from URL: {url}")
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
        except Exception as e:
            print(f"[LangChain] Error loading URL content: {e}")
            return None, []

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)
        
        print(f"[LangChain] Creating vector store from {len(docs)} document chunks.")
        vector_store = FAISS.from_documents(docs, self.embeddings)
        
        return vector_store.as_retriever(), [source]

    def get_context(self, query: str):
        """
        The main public method to get relevant context for a given query.
        """
        retriever, sources = self.search_and_build_retriever(query)
        
        if not retriever:
            return None, []

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        result = qa_chain.invoke({"query": query})
        context = " ".join([doc.page_content for doc in result["source_documents"]])
        
        print(f"[LangChain] Retrieved context: '{context[:200]}...'")
        return context, sources