document.addEventListener('DOMContentLoaded', () => {
    // --- Constants & State ---
    const API_URL = 'http://127.0.0.1:5000';
    const DB_NAME = 'KrishiMitrDB';
    const DB_VERSION = 1;
    const STORE_NAME = 'knowledge_base';
    let db;
    let isRecording = false;

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
    
    // --- Conversational & Language Detection Layer ---
    const CONVERSATIONAL_RESPONSES = {
        greetings: { keywords: ["hello", "hi", "hey", "namaste", "नमस्ते", "namaskar", "नमस्कार"], en: "Hello! I am KrishiMitr. How can I help you today?", hi: "नमस्ते! मैं कृषि मित्र हूँ। मैं आज आपकी कैसे मदद कर सकता हूँ?" },
        thanks: { keywords: ["thank you", "thanks", "dhanyavad", "धन्यवाद", "shukriya", "शुक्रिया"], en: "You're welcome!", hi: "आपका स्वागत है!" }
    };
    const HINGLISH_KEYWORDS = ['bhav', 'kya', 'kaise', 'kyu', 'mein', 'hai', 'kaha', 'tamatar', 'pyaz', 'gehu', 'kapas', 'ganna', 'mausam', 'yojana', 'dava'];
    
    function detectLanguageOffline(query) {
        if (/[\u0900-\u097F]/.test(query)) return 'hi';
        const words = query.toLowerCase().split(/\s+/);
        if (words.some(word => HINGLISH_KEYWORDS.includes(word))) return 'hi';
        return 'en';
    }

    // --- IndexedDB & Data Sync ---
    function initDB() {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onupgradeneeded = e => e.target.result.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
        request.onsuccess = e => { db = e.target.result; updateOnlineStatus(); };
        request.onerror = e => { console.error('DB error:', e.target.errorCode); syncStatus.textContent = 'Error: Offline data unavailable.'; };
    }

    async function syncKnowledgeBase() {
        if (!navigator.onLine || !db) return;
        syncStatus.textContent = 'Syncing data for offline use...';
        try {
            const response = await fetch(`${API_URL}/api/knowledge-base`);
            if (!response.ok) throw new Error('Failed to fetch data.');
            const data = await response.json();
            const transaction = db.transaction(STORE_NAME, 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            store.clear();
            data.forEach(item => store.add(item));
            transaction.oncomplete = () => syncStatus.textContent = 'Offline data is ready.';
        } catch (error) {
            syncStatus.textContent = 'Offline data sync failed.';
            console.error('Sync failed:', error);
        }
    }

    // --- Offline Search ---
    function performOfflineSearch(query, detectedLang) {
        if (!db) { addMessage("Offline database isn't ready.", 'error'); return; }
        
        let processedQuery = query.toLowerCase();
        const hindiToEnglishKeywords = { 'भाव': 'price', 'कीमत': 'price', 'दाम': 'price', 'मौसम': 'weather', 'योजना': 'scheme', 'दवा': 'pest control', 'कीट': 'pest', 'खाद': 'fertilizer', 'मिट्टी': 'soil', 'चावल': 'rice', 'गेहूं': 'wheat', 'कपास': 'cotton', 'गन्ना': 'sugarcane', 'क्या है': '' };
        for (const [hindi, english] of Object.entries(hindiToEnglishKeywords)) {
            processedQuery = processedQuery.replace(new RegExp(hindi, 'g'), english);
        }
        
        const transaction = db.transaction(STORE_NAME, 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        store.getAll().onsuccess = e => {
            const knowledgeBase = e.target.result;
            const queryWords = processedQuery.split(/\s+/).filter(w => w.length > 2);
            let bestMatch = null, maxScore = 0;

            knowledgeBase.forEach(item => {
                let score = 0;
                const content = item.content.toLowerCase();
                queryWords.forEach(word => { if (content.includes(word)) score++; });
                if (score > maxScore) { maxScore = score; bestMatch = item; }
            });

            if (bestMatch && maxScore > 0) {
                const answer = (detectedLang === 'hi' && bestMatch.content_hi) ? bestMatch.content_hi : bestMatch.content;
                updateBotMessage({ answer, sources: [bestMatch.source], offlineDisclaimer: `(Offline Result)` }, `offline-${Date.now()}`, true);
            } else {
                addMessage("I couldn't find an answer in your offline data.", 'bot');
            }
        };
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
        } catch (error) {
            updateBotMessage({ answer: `Error: ${error.message}` }, loadingId);
        }
    };
    
    // --- COMPLETE UI UPDATE FUNCTIONS (RESTORED) ---
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
        if (!el) {
            el = document.createElement('div');
            el.id = messageId;
            el.className = 'message bot';
            chatMessages.appendChild(el);
        }
        el.classList.remove('loading');
        el.innerHTML = `
            <p>${data.answer}</p>
            ${data.sources ? `<div class="sources"><strong>Sources:</strong> ${data.sources.join(', ')}</div>` : ''}
            ${data.evidence_hash ? `<div class="verification"><strong>Verified Hash:</strong> ${data.evidence_hash}</div>` : ''}
            ${isOffline ? `<span class="offline-disclaimer">${data.offlineDisclaimer}</span>` : ''}
        `;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    // --- COMPLETE EVENT LISTENERS & INITIALIZERS (RESTORED) ---
    const updateOnlineStatus = () => {
        const isOnline = navigator.onLine;
        statusDot.className = isOnline ? 'online' : 'offline';
        statusText.textContent = isOnline ? 'Online' : 'Offline';
        if (isOnline) { 
            syncKnowledgeBase(); 
        } else { 
            syncStatus.textContent = 'Offline mode. Answers are from local data.'; 
        }
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
        recognition.onerror = (e) => { isRecording = false; voiceStatus.textContent = 'Voice error. Please try again.'; console.error('Voice Error:', e.error); };
        recognition.onresult = (e) => { const transcript = e.results[0][0].transcript; sendQuery(transcript); };

        voiceButton.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                // Let browser auto-detect language for voice
                recognition.start();
            }
        });
    } else {
        voiceButton.style.display = 'none';
    }

    // --- Start the App ---
    initDB();
});