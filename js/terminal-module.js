/**
 * Terminal Module - Handles terminal operations
 */

const TerminalModule = (() => {
    let isCollapsed = false;
    const maxLines = 1000;

    const init = () => {
        console.log('[TerminalModule] Initializing...');
        
        const toggleBtn = document.getElementById('toggleTerminalBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggle);
        } else {
            console.warn('[TerminalModule] Toggle button not found');
        }

        const terminalInput = document.getElementById('terminalInput');
        if (terminalInput) {
            terminalInput.addEventListener('keypress', handleInput);
        } else {
            console.warn('[TerminalModule] Terminal input not found');
        }

        setupResizer();
    };

    const addOutput = (text, type = 'output') => {
        const content = document.getElementById('terminalContent');
        if (!content) {
            console.warn('[TerminalModule] Terminal content not found');
            return;
        }

        const line = document.createElement('div');
        line.className = 'terminal-line';
        
        const span = document.createElement('span');
        span.className = `terminal-${type}`;
        span.textContent = text;
        
        line.appendChild(span);
        content.appendChild(line);

        // Limit lines
        const lines = content.querySelectorAll('.terminal-line');
        if (lines.length > maxLines) {
            lines[0].remove();
        }

        content.scrollTop = content.scrollHeight;
    };

    const clear = () => {
        const content = document.getElementById('terminalContent');
        if (content) {
            content.innerHTML = '';
            addOutput('Terminal cleared', 'info');
        }
    };

    const toggle = () => {
        const terminal = document.getElementById('terminalSection');
        const content = document.getElementById('terminalContent');
        
        if (!terminal || !content) {
            console.warn('[TerminalModule] Terminal elements not found');
            return;
        }

        isCollapsed = !isCollapsed;
        terminal.classList.toggle('collapsed');
        content.classList.toggle('collapsed');
        
        const btn = document.getElementById('toggleTerminalBtn');
        if (btn) {
            const svg = btn.querySelector('svg polyline');
            if (svg) {
                if (isCollapsed) {
                    svg.setAttribute('points', '6 9 12 15 18 9');
                } else {
                    svg.setAttribute('points', '18 15 12 9 6 15');
                }
            }
        }
    };

    const handleInput = (e) => {
        if (e.key === 'Enter') {
            const input = e.target;
            const command = input.value.trim();
            
            if (command) {
                addOutput(`user@autopilot:~/project$ ${command}`, 'command');
                
                if (SocketModule.isConnected()) {
                    SocketModule.emit('terminal_execute', { command });
                } else {
                    addOutput('Error: Not connected to backend', 'error');
                }
                
                input.value = '';
            }
        }
    };

    const setupResizer = () => {
        const resizer = document.getElementById('terminalResizer');
        const terminal = document.getElementById('terminalSection');
        
        if (!resizer || !terminal) {
            console.warn('[TerminalModule] Resizer or terminal not found');
            return;
        }

        let isResizing = false;

        resizer.addEventListener('mousedown', () => {
            isResizing = true;
            document.body.style.cursor = 'ns-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            const containerRect = terminal.parentElement.getBoundingClientRect();
            const newHeight = containerRect.bottom - e.clientY;
            
            if (newHeight >= 150 && newHeight <= 500) {
                terminal.style.height = newHeight + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        });
    };

    return {
        init,
        addOutput,
        clear,
        toggle,
        isCollapsed
    };
})();
