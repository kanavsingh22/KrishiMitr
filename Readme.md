# KrishiMitr: An Agentic AI Solution for Agriculture (v3.0 - Live & Decentralized)

This version represents a major architectural evolution, transforming KrishiMitr into a dynamic, live, and decentralized information agent.

### Core Upgrades

1.  **Live Public Data:** The app no longer uses a static CSV. It performs live web searches (via SerpApi) and queries a live news API (GNews) to provide up-to-the-minute answers.

2.  **Decentralized Offline Cache:** A peer-to-peer data sharing model is simulated. Online queries are cached locally with a blockchain hash. Offline users can access this shared cache, simulating getting data from a nearby device.

3.  **LangChain RAG Pipeline:** The backend is now powered by LangChain, using a sophisticated chain (Web Loader -> Text Splitter -> Embeddings -> FAISS Vector Store) to provide highly relevant context for generating intelligent answers.

### Required Setup

1.  **API Keys:** This version requires two free API keys.
    *   Go to `gnews.io` to get a news API key.
    *   Go to `serpapi.com` to get a web search API key.

2.  **Environment File:** Create a file named `.env` in the main `KrishiMitr/` project directory. Add your keys to it:
    ```
    SERPAPI_API_KEY="YOUR_SERPAPI_KEY_HERE"
    GNEWS_API_KEY="YOUR_GNEWS_API_KEY_HERE"
    ```

### How to Run

1.  **Install Dependencies:**
    ```bash
    # Navigate to the backend folder
    cd backend
    # Install all required libraries
    pip install -r requirements.txt
    cd ..
    ```

2.  **Run Backend (in Terminal 1):**
    ```bash
    cd backend
    python3 app.py
    ```

3.  **Run Frontend (in Terminal 2):**
    ```bash
    cd frontend
    http-server .
    ```

4.  **Access App:** Open your browser to `http://127.0.0.1:8080`
    *   **Crucial:** Perform a **Hard Refresh** (`Ctrl+Shift+R` or `Cmd+Shift+R`) to clear any old files from your browser's cache.

### How to Test

1.  **Online LangChain RAG:** Ask a specific question like "best irrigation method for sugarcane in sandy soil?". Observe the backend terminal to see the LangChain process (finding URLs, loading content). The answer will be freshly generated.
2.  **Online Live News:** Ask "latest news on agriculture in India". The backend will query the GNews API.
3.  **Offline P2P Simulation:**
    *   While online, ask a specific question like "how to control whitefly in vegetable crops?". The answer is saved to a shared cache simulation.
    *   Go offline. Ask the same question. The app will retrieve the answer instantly from the local cache, simulating a P2P exchange.


    # KrishiMitr: An Agentic AI Solution for Agriculture (v4.0 - Intelligent & Dynamic)

This version introduces the final major upgrades, focusing on response quality and creating a truly powerful and useful offline experience.

### Core Upgrades

1.  **Intelligent Summarization & Formatting:** The backend's LLM simulator no longer dumps raw text. It now intelligently summarizes the retrieved information, extracts key points, and formats the answer with bold titles and crisp sentences for excellent readability.

2.  **Dynamic "Learning" Offline Database:** The offline architecture has been completely redesigned. Every verified answer you receive online is now automatically saved to your device's permanent database (IndexedDB). Your app's offline knowledge grows with every use, making it an incredibly powerful, personalized tool over time.

3.  **Robust Multilingual Experience:** The app now guarantees responses in Hindi (Devanagari script) for any Hinglish or Hindi query. All offline messages, including errors, are now also displayed in the appropriate language.

### Required Setup

(Setup for API keys and `.env` file is the same as the previous version).

### How to Run

1.  **Install Dependencies:** `pip install -r backend/requirements.txt`
2.  **Run Backend:** `cd backend` -> `python3 app.py`
3.  **Run Frontend:** `cd frontend` -> `http-server .`
4.  **Access App:** `http://127.0.0.1:8080` (Hard Refresh: `Ctrl+Shift+R`)

### How to Test the New Features

1.  **Test Summarization:** Ask a question online like "how to use urea fertilizer for wheat". The response will be a well-formatted summary, not a wall of text.

2.  **Test the "Learning" Offline Mode:**
    *   **Step 1 (Learn):** While online, ask a specific question: `what is the market price for cotton in mumbai?`. You will get a live answer.
    *   **Step 2 (Recall):** Now, disconnect from the internet. The dot will turn red.
    *   **Step 3 (Verify):** Ask the same question again, or a similar one like `mumbai me kapas ka bhav`. The app will instantly retrieve the perfectly formatted answer you received earlier from its permanent offline database.