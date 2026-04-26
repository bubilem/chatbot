(function() {
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    // Assume widget.css is in the same directory as this script
    // We can infer the script's path
    const scripts = document.getElementsByTagName('script');
    let scriptPath = '';
    for (let i = 0; i < scripts.length; i++) {
        if (scripts[i].src && scripts[i].src.includes('widget.js')) {
            scriptPath = scripts[i].src.substring(0, scripts[i].src.lastIndexOf('/'));
            break;
        }
    }
    link.href = (scriptPath ? scriptPath + '/' : '') + 'widget.css';
    document.head.appendChild(link);

    // Create Widget Container
    const container = document.createElement('div');
    container.id = 'chatbot-widget-container';

    // Widget HTML Structure
    container.innerHTML = `
        <div id="chatbot-widget-window" class="hidden">
            <div id="chatbot-widget-header">
                <h3>Agent</h3>
                <button id="chatbot-widget-close">&times;</button>
            </div>
            <div id="chatbot-widget-messages">
                <div class="chatbot-message agent">Dobrý den, jak vám mohu pomoci?</div>
            </div>
            <div id="chatbot-widget-input-area">
                <input type="text" id="chatbot-widget-input" placeholder="Napište zprávu..." maxlength="500">
                <button id="chatbot-widget-send" aria-label="Odeslat zprávu">
                    <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                </button>
            </div>
        </div>
        <div id="chatbot-widget-launcher">
            <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"></path></svg>
        </div>
    `;

    document.body.appendChild(container);

    // DOM Elements
    const windowEl = document.getElementById('chatbot-widget-window');
    const launcherEl = document.getElementById('chatbot-widget-launcher');
    const closeBtn = document.getElementById('chatbot-widget-close');
    const inputEl = document.getElementById('chatbot-widget-input');
    const sendBtn = document.getElementById('chatbot-widget-send');
    const messagesEl = document.getElementById('chatbot-widget-messages');

    // API URL - modify this to point to the correct absolute URL if needed
    // Assuming relative path for now: ../server/api.php
    // If the client is hosted on a different domain, provide full URL
    const API_URL = '../server/api.php';

    // Event Listeners
    launcherEl.addEventListener('click', () => {
        windowEl.classList.remove('hidden');
        launcherEl.classList.add('hidden');
        inputEl.focus();
    });

    closeBtn.addEventListener('click', () => {
        windowEl.classList.add('hidden');
        launcherEl.classList.remove('hidden');
    });

    sendBtn.addEventListener('click', sendMessage);
    inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chatbot-message ${sender}`;
        msgDiv.textContent = text;
        messagesEl.appendChild(msgDiv);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    let isSending = false;

    function sendMessage() {
        if (isSending) return; // Prevent double submission
        const text = inputEl.value.trim();
        if (!text) return;

        // Lock form
        isSending = true;
        inputEl.disabled = true;
        sendBtn.style.opacity = '0.5';
        sendBtn.style.cursor = 'not-allowed';

        // Add user message to UI
        appendMessage(text, 'user');
        inputEl.value = '';

        // Add a temporary typing indicator (optional, but good for UX)
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chatbot-message agent';
        loadingDiv.textContent = '...';
        loadingDiv.id = 'chatbot-loading';
        messagesEl.appendChild(loadingDiv);
        messagesEl.scrollTop = messagesEl.scrollHeight;

        // Send to server
        fetch(API_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 429) throw new Error('Příliš mnoho požadavků. Zpomalte prosím.');
                if (response.status === 400) throw new Error('Neplatný požadavek. Zpráva je možná příliš dlouhá.');
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading
            const loading = document.getElementById('chatbot-loading');
            if (loading) loading.remove();

            // Add agent response
            if (data && data.response) {
                appendMessage(data.response, 'agent');
            } else {
                appendMessage('Omlouváme se, došlo k chybě při zpracování odpovědi.', 'agent');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Remove loading
            const loading = document.getElementById('chatbot-loading');
            if (loading) loading.remove();
            
            appendMessage(error.message || 'Chyba připojení k serveru.', 'agent');
        })
        .finally(() => {
            // Unlock form
            isSending = false;
            inputEl.disabled = false;
            sendBtn.style.opacity = '1';
            sendBtn.style.cursor = 'pointer';
            
            // Focus back on input if window is not hidden
            if (!windowEl.classList.contains('hidden')) {
                inputEl.focus();
            }
        });
    }
})();
