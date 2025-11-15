/**
 * Socket Client Module
 * Unified socket.io client with correct event names matching backend
 * Fixes: terminal_execute -> terminal_command
 */

class SocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.listeners = new Map();
    }

    /**
     * Initialize socket connection
     * Uses dynamic URL based on current page origin
     */
    init(url = null) {
        // Use provided URL or default to current origin
        const socketUrl = url || window.location.origin;
        console.log('[SocketClient] Initializing connection to:', socketUrl);
        
        this.socket = io(socketUrl, {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: this.maxReconnectAttempts
        });

        this.setupEventHandlers();
        return this.socket;
    }

    /**
     * Setup core socket event handlers
     */
    setupEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('[SocketClient] Connected to backend');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.emit('status', { connected: true });
            this.addTerminalOutput('✓ Connected to backend', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('[SocketClient] Disconnected from backend');
            this.connected = false;
            this.emit('status', { connected: false });
            this.addTerminalOutput('✗ Disconnected from backend', 'error');
        });

        this.socket.on('connect_error', (error) => {
            console.error('[SocketClient] Connection error:', error);
            this.reconnectAttempts++;
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.addTerminalOutput('✗ Failed to connect to backend', 'error');
            }
        });

        // Terminal output handler - CORRECT EVENT NAME
        this.socket.on('terminal_output', (data) => {
            console.log('[SocketClient] Terminal output received:', data);
            if (data.stdout) this.addTerminalOutput(data.stdout, 'output');
            if (data.stderr) this.addTerminalOutput(data.stderr, 'error');
            this.emit('terminal_output', data);
        });

        // AI response handler
        this.socket.on('ai_response', (data) => {
            console.log('[SocketClient] AI response received:', data);
            this.addAIMessage(data.message, false);
            this.emit('ai_response', data);
        });

        // Ping/pong for connection health
        this.socket.on('pong', (data) => {
            console.log('[SocketClient] Pong received:', data);
        });
    }

    /**
     * Send terminal command - USES CORRECT EVENT NAME
     * @param {string} command - Command to execute
     */
    sendTerminalCommand(command) {
        if (!this.connected) {
            console.error('[SocketClient] Cannot send command - not connected');
            this.addTerminalOutput('✗ Not connected to backend', 'error');
            return false;
        }

        console.log('[SocketClient] Sending terminal command:', command);
        
        // CORRECT EVENT NAME: terminal_command (not terminal_execute)
        this.socket.emit('terminal_command', {
            command: command,
            cwd: this.getCurrentWorkingDirectory()
        });

        return true;
    }

    /**
     * Send AI message
     * @param {string} message - Message to send
     * @param {string} mode - AI mode (chat, explain, debug, refactor)
     */
    sendAIMessage(message, mode = 'chat') {
        if (!this.connected) {
            console.error('[SocketClient] Cannot send AI message - not connected');
            return false;
        }

        console.log('[SocketClient] Sending AI message:', { message, mode });
        
        this.socket.emit('ai_message', {
            message: message,
            mode: mode,
            context: this.getAIContext()
        });

        return true;
    }

    /**
     * Send ping to check connection
     */
    ping() {
        if (this.connected) {
            this.socket.emit('ping', { timestamp: Date.now() });
        }
    }

    /**
     * Register custom event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * Emit custom event to registered listeners
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[SocketClient] Error in listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Add terminal output to UI
     * @param {string} text - Output text
     * @param {string} type - Output type (output, error, success, command)
     */
    addTerminalOutput(text, type = 'output') {
        const content = document.getElementById('terminalContent');
        if (!content) return;

        const line = document.createElement('div');
        line.className = 'terminal-line';
        
        const span = document.createElement('span');
        span.className = `terminal-${type}`;
        span.textContent = text;
        
        line.appendChild(span);
        
        // Insert before the input line
        const inputLine = content.querySelector('.terminal-input-line');
        if (inputLine) {
            content.insertBefore(line, inputLine);
        } else {
            content.appendChild(line);
        }
        
        content.scrollTop = content.scrollHeight;
    }

    /**
     * Add AI message to chat
     * @param {string} message - Message text
     * @param {boolean} isUser - Whether message is from user
     */
    addAIMessage(message, isUser = false) {
        const chat = document.getElementById('aiChat');
        if (!chat) return;

        const msg = document.createElement('div');
        msg.className = `ai-message ${isUser ? 'user' : ''}`;
        msg.textContent = message;
        
        chat.appendChild(msg);
        chat.scrollTop = chat.scrollHeight;
    }

    /**
     * Get current working directory (from project manager if available)
     * @returns {string} Current working directory
     */
    getCurrentWorkingDirectory() {
        if (window.projectManager) {
            const currentProject = window.projectManager.getCurrentProject();
            if (currentProject && currentProject.path) {
                return currentProject.path;
            }
        }
        return process.cwd ? process.cwd() : '.';
    }

    /**
     * Get AI context (current file, project, etc.)
     * @returns {Object} Context object
     */
    getAIContext() {
        const context = {
            timestamp: Date.now()
        };

        // Add current project info
        if (window.projectManager) {
            const currentProject = window.projectManager.getCurrentProject();
            if (currentProject) {
                context.project = {
                    name: currentProject.name,
                    path: currentProject.path
                };
            }
        }

        // Add current file info
        const activeTab = document.querySelector('.tab.active');
        if (activeTab) {
            context.currentFile = activeTab.textContent.trim();
        }

        return context;
    }

    /**
     * Check if socket is connected
     * @returns {boolean} Connection status
     */
    isConnected() {
        return this.connected && this.socket && this.socket.connected;
    }

    /**
     * Disconnect socket
     */
    disconnect() {
        if (this.socket) {
            console.log('[SocketClient] Disconnecting...');
            this.socket.disconnect();
            this.connected = false;
        }
    }

    /**
     * Reconnect socket
     */
    reconnect() {
        if (this.socket) {
            console.log('[SocketClient] Reconnecting...');
            this.socket.connect();
        }
    }
}

// Create global instance
window.socketClient = new SocketClient();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocketClient;
}

console.log('[SocketClient] Module loaded');
