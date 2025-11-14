/**
 * AI Module - Handles AI assistant functionality
 */

const AIModule = (() => {
    const modes = {
        'Chat': '💬',
        'Explain': '🔍',
        'Debug': '🐛',
        'Refactor': '✨'
    };

    let currentMode = 'Chat';

    const init = () => {
        console.log('[AIModule] Initializing...');
        
        // Setup mode buttons
        document.querySelectorAll('.mode-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => setMode(btn));
        });

        // Setup send button
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', send);
        } else {
            console.warn('[AIModule] Send button not found');
        }

        // Setup input
        const aiInput = document.getElementById('aiInput');
        if (aiInput) {
            aiInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                }
            });

            aiInput.addEventListener('input', () => {
                aiInput.style.height = 'auto';
                aiInput.style.height = Math.min(aiInput.scrollHeight, 120) + 'px';
            });
        } else {
            console.warn('[AIModule] AI input not found');
        }
    };

    const setMode = (btnElement) => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        btnElement.classList.add('active');
        
        const modeText = btnElement.textContent.trim();
        const mode = Object.keys(modes).find(m => modeText.includes(m));
        if (mode) {
            currentMode = mode;
            console.log(`[AIModule] Mode changed to: ${currentMode}`);
        }
    };

    const getMode = () => currentMode;

    const send = () => {
        const input = document.getElementById('aiInput');
        if (!input) {
            console.warn('[AIModule] AI input not found');
            return;
        }

        const message = input.value.trim();
        if (!message) return;

        addMessage(message, true);

        if (SocketModule.isConnected()) {
            SocketModule.emit('ai_message', {
                message: message,
                mode: currentMode
            });
        } else {
            addMessage('Error: Not connected to backend', false);
        }

        input.value = '';
        input.style.height = 'auto';
    };

    const addMessage = (message, isUser = false) => {
        const chat = document.getElementById('aiChat');
        if (!chat) {
            console.warn('[AIModule] AI chat not found');
            return;
        }

        const msg = document.createElement('div');
        msg.className = `ai-message ${isUser ? 'user' : ''}`;
        msg.textContent = message;
        msg.style.animation = 'fadeIn 0.3s ease-out';
        
        chat.appendChild(msg);
        chat.scrollTop = chat.scrollHeight;
    };

    const clear = () => {
        const chat = document.getElementById('aiChat');
        if (chat) {
            chat.innerHTML = '';
            addMessage('Chat cleared. How can I help you?', false);
        }
    };

    return {
        init,
        send,
        addMessage,
        setMode,
        getMode,
        clear,
        modes,
        currentMode
    };
})();
