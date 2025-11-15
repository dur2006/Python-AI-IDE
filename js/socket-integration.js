/**
 * AutoPilot IDE - Socket.IO Integration
 * Properly connects frontend to backend socket events
 */

class SocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        console.log('[SocketManager] Initializing Socket.IO connection...');
        
        this.socket = io('http://localhost:5000', {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: this.maxReconnectAttempts,
            transports: ['websocket', 'polling']
        });

        this.registerEventHandlers();
    }

    registerEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('[SocketManager] Connected to backend');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            this.addTerminalOutput('✓ Connected to backend', 'success');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('[SocketManager] Disconnected from backend:', reason);
            this.connected = false;
            this.updateConnectionStatus(false);
            this.addTerminalOutput('✗ Disconnected from backend', 'error');
        });

        this.socket.on('connect_error', (error) => {
            console.error('[SocketManager] Connection error:', error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.addTerminalOutput('✗ Failed to connect to backend after multiple attempts', 'error');
            }
        });

        this.socket.on('connection_response', (data) => {
            console.log('[SocketManager] Connection response:', data);
            if (data.message) {
                this.addTerminalOutput(data.message, 'success');
            }
        });

        // Terminal events - CORRECT EVENT NAME: terminal_output
        this.socket.on('terminal_output', (data) => {
            console.log('[SocketManager] Terminal output:', data);
            
            if (data.stdout) {
                this.addTerminalOutput(data.stdout, 'output');
            }
            
            if (data.stderr) {
                this.addTerminalOutput(data.stderr, 'error');
            }
            
            if (data.returncode !== undefined && data.returncode !== 0) {
                this.addTerminalOutput(`Process exited with code ${data.returncode}`, 'error');
            }
        });

        // AI events - CORRECT EVENT NAME: ai_response
        this.socket.on('ai_response', (data) => {
            console.log('[SocketManager] AI response:', data);
            
            if (data.error) {
                this.addAIMessage(`Error: ${data.message}`, false, true);
            } else {
                this.addAIMessage(data.message, false);
            }
        });

        // Ping/Pong for connection testing
        this.socket.on('pong', (data) => {
            console.log('[SocketManager] Pong received:', data);
        });

        // Error handling
        this.socket.on('error', (error) => {
            console.error('[SocketManager] Socket error:', error);
            this.addTerminalOutput(`Socket error: ${error}`, 'error');
        });
    }

    // CORRECT METHOD: Use terminal_command event
    executeTerminalCommand(command, cwd = null) {
        if (!this.connected) {
            console.error('[SocketManager] Not connected to backend');
            this.addTerminalOutput('✗ Not connected to backend', 'error');
            return;
        }

        console.log('[SocketManager] Executing terminal command:', command);
        
        this.socket.emit('terminal_command', {
            command: command,
            cwd: cwd
        });
    }

    // CORRECT METHOD: Use ai_message event
    sendAIMessage(message, context = {}) {
        if (!this.connected) {
            console.error('[SocketManager] Not connected to backend');
            this.addAIMessage('Error: Not connected to backend', false, true);
            return;
        }

        console.log('[SocketManager] Sending AI message:', message);
        
        this.socket.emit('ai_message', {
            message: message,
            context: context
        });
    }

    // Test connection
    ping() {
        if (this.socket) {
            this.socket.emit('ping');
        }
    }

    // Helper methods for UI updates
    updateConnectionStatus(connected) {
        const statusItems = document.querySelectorAll('.status-item');
        statusItems.forEach(item => {
            if (item.textContent.includes('Backend')) {
                item.textContent = connected ? '🌐 Backend Connected' : '🌐 Backend Disconnected';
                item.style.color = connected ? 'var(--success)' : 'var(--error)';
            }
        });

        const contextIndicator = document.querySelector('.context-indicator');
        if (contextIndicator) {
            contextIndicator.style.background = connected ? '#4caf50' : '#f44336';
        }

        const contextText = document.querySelector('.ai-context .context-left span');
        if (contextText) {
            contextText.textContent = connected ? 'Backend Connected' : 'Backend Disconnected';
        }
    }

    addTerminalOutput(text, type = 'output') {
        const content = document.getElementById('terminalContent');
        if (!content) return;

        const line = document.createElement('div');
        line.className = 'terminal-line';
        
        const span = document.createElement('span');
        span.className = `terminal-${type}`;
        span.textContent = text;
        
        line.appendChild(span);
        
        // Insert before the input line (last element)
        const inputLine = content.querySelector('.terminal-input-line');
        if (inputLine) {
            content.insertBefore(line, inputLine);
        } else {
            content.appendChild(line);
        }
        
        content.scrollTop = content.scrollHeight;
    }

    addAIMessage(message, isUser = false, isError = false) {
        const chat = document.getElementById('aiChat');
        if (!chat) return;

        const msg = document.createElement('div');
        msg.className = `ai-message ${isUser ? 'user' : ''}`;
        
        if (isError) {
            msg.style.borderLeft = '3px solid var(--error)';
            msg.style.background = 'rgba(244, 67, 54, 0.1)';
        }
        
        msg.textContent = message;
        chat.appendChild(msg);
        chat.scrollTop = chat.scrollHeight;
    }

    isConnected() {
        return this.connected;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Create global instance
const socketManager = new SocketManager();

// Export for use in other scripts
window.socketManager = socketManager;
