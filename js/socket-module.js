/**
 * Socket Module - Handles WebSocket communication
 */

const SocketModule = (() => {
    let socket = null;
    const handlers = {};

    const init = () => {
        console.log('[SocketModule] Initializing...');
        
        try {
            socket = io('http://localhost:5000', {
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 5
            });

            socket.on('connect', () => {
                console.log('[SocketModule] Connected to backend');
                UIModule.updateStatus('Backend Connected', 'success');
                TerminalModule.addOutput('✓ Connected to backend', 'success');
                emit('socket:connected');
            });

            socket.on('disconnect', () => {
                console.log('[SocketModule] Disconnected from backend');
                UIModule.updateStatus('Backend Disconnected', 'error');
                TerminalModule.addOutput('✗ Disconnected from backend', 'error');
                emit('socket:disconnected');
            });

            socket.on('terminal_output', (data) => {
                if (data.stdout) TerminalModule.addOutput(data.stdout, 'output');
                if (data.stderr) TerminalModule.addOutput(data.stderr, 'error');
            });

            socket.on('ai_response', (data) => {
                AIModule.addMessage(data.message, false);
            });

            socket.on('error', (error) => {
                console.error('[SocketModule] Error:', error);
                UIModule.showNotification('Connection error: ' + error, 'error');
            });

        } catch (error) {
            console.error('[SocketModule] Failed to initialize:', error);
            UIModule.showNotification('Failed to connect to backend', 'error');
        }
    };

    const emit = (event, data = {}) => {
        if (!socket) {
            console.warn('[SocketModule] Socket not initialized');
            return;
        }
        socket.emit(event, data);
    };

    const on = (event, callback) => {
        if (!socket) {
            console.warn('[SocketModule] Socket not initialized');
            return;
        }
        socket.on(event, callback);
        handlers[event] = callback;
    };

    const off = (event) => {
        if (!socket) return;
        socket.off(event);
        delete handlers[event];
    };

    const disconnect = () => {
        if (socket) {
            socket.disconnect();
            socket = null;
        }
    };

    const isConnected = () => {
        return socket && socket.connected;
    };

    return {
        init,
        emit,
        on,
        off,
        disconnect,
        isConnected,
        handlers,
        getSocket: () => socket
    };
})();
