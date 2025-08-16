# KrishiMitr: An Agentic AI Solution for Agriculture

Welcome to the KrishiMitr project. This repository contains the end-to-end code for a multilingual, blockchain-anchored agricultural advisor designed for India’s diverse farming ecosystem.

## Table of Contents

1.  [Theme Overview](#theme-overview)
2.  [Solution Synopsis](#solution-synopsis)
3.  [Technical Architecture](#technical-architecture)
4.  [Project Structure](#project-structure)
5.  [Prerequisites](#prerequisites)
6.  [Setup and Installation](#setup-and-installation)
7.  [Running the Application](#running-the-application)
8.  [How It Works](#how-it-works)
9.  [Troubleshooting]

---

### 1. Theme Overview

**The Challenge:** Exploring and Building Agentic AI Solutions for a High-Impact Area of Society: Agriculture.

**Benefits:**
- Real-time, hyperlocal farm advice.
- Multilingual, low-connectivity access.
- Unified weather, soil, finance, and policy insights.
- Reduced climate and market risks.
- Inclusive support for all agri stakeholders.

---

### 2. Solution Synopsis

KrishiMitr provides real-time, evidence-backed recommendations on irrigation, crop choice, pest control, and more. It combines agentic AI reasoning with blockchain-based data anchoring to ensure trust and transparency. The system is designed to be accessible even in low-connectivity environments through a voice-first interface and offline capabilities.

---

### 3. Technical Architecture

The architecture is composed of five layers:

1.  **Data Ingestion & ETL Layer:** Fetches and processes data from sources like IMD (weather) and Agmarknet (market prices).
2.  **Knowledge Base & Blockchain Anchoring Layer:** Stores curated data and anchors its cryptographic hash on a permissioned blockchain (Hyperledger Fabric simulated) for tamper-proof verification. Large files are stored on IPFS (simulated).
3.  **AI Reasoning & RAG Layer:** A Retrieval-Augmented Generation (RAG) pipeline uses fine-tuned LLMs (e.g., LLaMA 3) to generate answers grounded in verified data, reducing hallucinations.
4.  **Delivery & Interaction Layer:** A Progressive Web App (PWA) with a voice-first UI provides the primary interface.
5.  **Offline Sync & P2P Mesh Layer:** A store-and-forward mechanism ensures that queries made offline are synced when connectivity is restored.

---

### 4. Project Structure
KrishiMitr/
├── README.md
├── backend/
├── frontend/
├── blockchain/
├── ai_model/
├── data_ingestion/
└── offline_sync/
code
Code
(A detailed description of each file is provided in the code sections below).

---

### 5. Prerequisites

- **Python 3.8+**: For backend, AI, and data ingestion.
- **Node.js and npm**: For serving the frontend.
- **Go 1.18+**: For the Hyperledger Fabric chaincode.
- **A modern web browser** (like Chrome or Firefox) that supports the Web Speech API and Service Workers.

---

### 6. Setup and Installation

**1. Clone the repository:**

git clone <repository_url>
cd KrishiMitr
2. Backend & AI Setup:
code
Bash
cd backend
pip install -r requirements.txt
cd ../ai_model
pip install -r requirements.txt
(Note: requirements.txt for the AI model is consolidated into the backend's for this project).

3. Data Ingestion (One-time setup):
Run the ETL script to process raw data and create the knowledge base for the RAG pipeline.
code
Bash
cd data_ingestion
python etl.py
This will create a knowledge_base.csv file in the ai_model/data directory.
4. Frontend Setup:
This project uses a simple Node.js server to serve the frontend files.
code
Bash
cd frontend
npm install -g http-server # Install a simple server

### 7. Running the Application
1. Start the Backend Server:
Open a terminal and run the Flask app.
code
Bash
cd backend
python app.py
The backend will be running at http://127.0.0.1:5000.
2. Start the Frontend Server:
Open a second terminal and run the HTTP server.
code
Bash
cd frontend
http-server .
The frontend will be accessible at http://127.0.0.1:8080.
3. Access KrishiMitr:
Open your web browser and navigate to http://127.0.0.1:8080. You can now ask agricultural questions via text or voice.

### 8. How It Works
The user asks a question on the Frontend PWA (e.g., "What is the market price for tomatoes in Delhi?").
The request is sent to the Backend Flask server.
The backend calls the AI RAG Pipeline, which retrieves relevant information from the knowledge_base.csv.
The RAG pipeline generates a precise, evidence-backed answer.
The backend creates an "evidence package" (query + answer + sources), generates its SHA256 hash, and simulates storing it on IPFS and anchoring the hash on the Blockchain.
The backend returns the answer, sources, and the transaction hash to the frontend.
The frontend displays the information. If the user is offline, the Service Worker serves the cached app, and the offline_sync logic (conceptual) would queue the request.

### 9. Troubleshooting

**Problem: The web page loads, but every query responds with "Sorry, I am having trouble connecting. Please try again later."**

This is the most common issue and it means the frontend cannot communicate with the backend. Here's how to fix it:

1.  **Check the Backend Terminal:** Look at the terminal where you ran `python backend/app.py`.
    *   If you see an error like `FileNotFoundError: [Errno 2] No such file or directory: 'ai_model/data/knowledge_base.csv'`, it means the AI's data file is missing.
    *   **Solution:** Make sure the file `ai_model/data/knowledge_base.csv` exists. The corrected code in this guide now includes this file directly. Alternatively, you can generate it by running `python data_ingestion/etl.py`.

2.  **Is the Backend Running?** Ensure you have two separate terminals open: one for the backend (`python backend/app.py`) and one for the frontend (`http-server .`). The backend must be running for the frontend to work.

3.  **Check for Other Errors:** The backend terminal will show any other Python errors that might be causing it to crash. A common one is missing libraries. Make sure you have installed all requirements by running `pip install -r backend/requirements.txt`.