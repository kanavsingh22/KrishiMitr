document.addEventListener('DOMContentLoaded', () => {
    // --- Constants & State ---
    const API_URL = 'http://127.0.0.1:5000';
    const DB_NAME = 'KrishiMitrDB', DB_VERSION = 1, STORE_NAME = 'knowledge_base';
    let db;
    let isRecording = false;
    let offlineIndex; // For FlexSearch

    // --- DOM Elements ---
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    const voiceButton = document.getElementById('voice-button');
    const chatWindow = document.getElementById('chat-window');
    const chatMessages = document.getElementById('chat-messages');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const syncStatus = document.getElementById('sync-status');
    const voiceStatus = document.getElementById('voice-status');
    
    // --- Conversational & Language Detection ---
    const CONVERSATIONAL_RESPONSES = {
        greetings: { keywords: ["hello", "hi", "hey", "namaste", "नमस्ते"], en: "Hello! How can I help?", hi: "नमस्ते! मैं कैसे मदद कर सकता हूँ?" },
    };
    const HINGLISH_KEYWORDS = ['bhav', 'kya', 'kaise', 'mein', 'hai', 'tamatar', 'pyaz', 'gehu', 'mausam', 'yojana', 'dava'];
    const OFFLINE_ERROR_MESSAGES = {
        en: "I couldn't find an answer in your offline data. Please connect to the internet for a live search.",
        hi: "मुझे आपके ऑफ़लाइन डेटा में कोई उत्तर नहीं मिला। कृपया लाइव खोज के लिए इंटरनेट से कनेक्ट करें।"
    };
    
    function detectLanguageOffline(query) {
        if (/[\u0900-\u097F]/.test(query)) return 'hi';
        const words = query.toLowerCase().split(/\s+/);
        if (words.some(word => HINGLISH_KEYWORDS.includes(word))) return 'hi';
        return 'en';
    }

    // --- IndexedDB & FlexSearch for the DYNAMIC "Learning" Database ---
    function initializeOfflineIndex() {
        offlineIndex = new FlexSearch.Document({
            document: { id: "id", index: ["query_en", "answer_en"] }, // Index both questions and answers
            tokenize: "forward"
        });
    }

    function initDB() {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onupgradeneeded = e => {
            const store = e.target.result.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            store.createIndex('query_en', 'query_en', { unique: true }); // Index queries for faster searching
        };
        request.onsuccess = e => {
            db = e.target.result;
            // Load existing data from DB into FlexSearch index on startup
            loadDBDataIntoIndex();
            updateOnlineStatus();
        };
        request.onerror = e => { console.error('DB error:', e.target.errorCode); };
    }
    
    async function loadDBDataIntoIndex() {
        if (!db) return;
        const transaction = db.transaction(STORE_NAME, 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        store.getAll().onsuccess = e => {
            const data = e.target.result;
            offlineIndex.clear();
            data.forEach(doc => offlineIndex.add(doc));
            console.log(`${data.length} offline records loaded into search index.`);
            syncStatus.textContent = `Offline data ready (${data.length} records).`;
        };
    }

    // --- NEW: Function to save online results to the learning database ---
    function cacheResponseToDB(response) {
        if (!db || !response.query_en || !response.answer_en) return;
        const transaction = db.transaction(STORE_NAME, 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const newRecord = {
            query_en: response.query_en,
            answer_en: response.answer_en,
            answer_hi: response.answer_hi,
            source: response.sources[0] || 'Web',
            hash: response.cache_hash
        };
        // Add the new record. The 'id' will be auto-incremented.
        const request = store.add(newRecord);
        request.onsuccess = () => {
            console.log("Successfully cached new response to IndexedDB.");
            // Add the new record to the live search index as well
            offlineIndex.add(newRecord);
        };
        request.onerror = (e) => {
            console.error("Error caching response to IndexedDB:", e.target.error);
        };
    }

    // --- Offline Search (now uses the dynamic learning database) ---
    function performOfflineSearch(query, detectedLang) {
        if (!offlineIndex) { addMessage("Offline data is not ready.", 'error'); return; }
        
        const searchResults = offlineIndex.search(query, { limit: 1, enrich: true });
        if (searchResults.length > 0 && searchResults[0].result.length > 0) {
            const bestMatch = searchResults[0].result[0].doc;
            const answer = (detectedLang === 'hi' && bestMatch.answer_hi) ? bestMatch.answer_hi : bestMatch.answer_en;
            updateBotMessage({ answer, sources: [bestMatch.source], offlineDisclaimer: `(From your device's data)` }, `offline-${Date.now()}`, true);
        } else {
            addMessage(OFFLINE_ERROR_MESSAGES[detectedLang], 'error');
        }
    }

    // --- Main Query Handler ---
    const sendQuery = async (query) => {
        if (!query.trim()) return;
        const queryLower = query.toLowerCase();
        addMessage(query, 'user');
        queryInput.value = '';

        const detectedLang = detectLanguageOffline(query);

        for (const intent in CONVERSATIONAL_RESPONSES) {
            if (CONVERSATIONAL_RESPONSES[intent].keywords.some(k => queryLower.includes(k))) {
                addMessage(CONVERSATIONAL_RESPONSES[intent][detectedLang], 'bot');
                return;
            }
        }
        
        if (!navigator.onLine) {
            performOfflineSearch(query, detectedLang);
            return;
        }
        
        const loadingId = `loading-${Date.now()}`;
        addMessage('Thinking...', 'bot', true, loadingId);
        try {
            const response = await fetch(`${API_URL}/api/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Server error');
            updateBotMessage(data, loadingId);
            cacheResponseToDB(data); // <-- Learn from the online response
        } catch (error) {
            updateBotMessage({ answer: `Error: ${error.message}` }, loadingId);
        }
    };
    
    // --- UI, Event Listeners & Helper Functions ---
    const addMessage = (text, sender, isLoading = false, messageId = null) => {
        const el = document.createElement('div');
        if (messageId) el.id = messageId;
        el.classList.add('message', sender);
        if (isLoading) el.classList.add('loading');
        if (sender === 'error') el.classList.add('error');
        el.textContent = text;
        chatMessages.appendChild(el);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const updateBotMessage = (data, messageId, isOffline = false) => {
        let el = document.getElementById(messageId);
        if (!el) { el = document.createElement('div'); el.id = messageId; el.className = 'message bot'; chatMessages.appendChild(el); }
        el.classList.remove('loading');
        // Use innerHTML to render bold tags from the backend
        el.innerHTML = `<p>${data.answer.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')}</p>${data.sources ? `<div class="sources"><strong>Sources:</strong> ${data.sources.join(', ')}</div>` : ''}${data.cache_hash ? `<div class="verification"><strong>Verified Hash:</strong> ${data.cache_hash.substring(0, 20)}...</div>` : ''}${isOffline ? `<span class="offline-disclaimer">${data.offlineDisclaimer}</span>` : ''}`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const updateOnlineStatus = () => {
        const isOnline = navigator.onLine;
        statusDot.className = isOnline ? 'online' : 'offline';
        statusText.textContent = isOnline ? 'Online' : 'Offline';
        if (!isOnline) { syncStatus.textContent = 'Offline mode.'; }
    };

    sendButton.addEventListener('click', () => sendQuery(queryInput.value));
    queryInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendQuery(queryInput.value); });
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onstart = () => { isRecording = true; voiceButton.classList.add('recording'); voiceStatus.textContent = 'Listening...'; };
        recognition.onend = () => { isRecording = false; voiceButton.classList.remove('recording'); voiceStatus.textContent = ''; };
        recognition.onerror = (e) => { isRecording = false; voiceStatus.textContent = 'Voice error.'; console.error('Voice Error:', e.error); };
        recognition.onresult = (e) => { const transcript = e.results[0][0].transcript; sendQuery(transcript); };
        voiceButton.addEventListener('click', () => {
            if (isRecording) { recognition.stop(); } 
            else { recognition.start(); }
        });
    } else {
        voiceButton.style.display = 'none';
    }

    // --- Start the App ---
    initializeOfflineIndex();
    initDB();
});