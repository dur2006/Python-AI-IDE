/**
 * UI Handlers Module
 * Handles all UI interactions and events
 * Extracted from inline code in index.html
 */

class UIHandlers {
    constructor() {
        this.currentDropdown = null;
        this.initialized = false;
    }

    /**
     * Initialize all UI handlers
     */
    init() {
        if (this.initialized) {
            console.warn('[UIHandlers] Already initialized');
            return;
        }

        console.log('[UIHandlers] Initializing UI handlers...');

        this.setupMenuHandlers();
        this.setupTerminalHandlers();
        this.setupAIHandlers();
        this.setupModalHandlers();
        this.setupFileTreeHandlers();
        this.setupTabHandlers();

        this.initialized = true;
        console.log('[UIHandlers] UI handlers initialized');
    }

    /**
     * Setup menu dropdown handlers
     */
    setupMenuHandlers() {
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (this.currentDropdown && !e.target.closest('.menu-tab-wrapper')) {
                this.currentDropdown.classList.remove('show');
                this.currentDropdown = null;
            }
        });

        console.log('[UIHandlers] Menu handlers setup');
    }

    /**
     * Toggle dropdown menu
     * @param {string} menuId - Menu element ID
     * @param {Event} event - Click event
     */
    toggleDropdown(menuId, event) {
        event.stopPropagation();
        const menu = document.getElementById(menuId);
        
        if (!menu) {
            console.error('[UIHandlers] Menu not found:', menuId);
            return;
        }
        
        if (this.currentDropdown === menu && menu.classList.contains('show')) {
            menu.classList.remove('show');
            this.currentDropdown = null;
            return;
        }
        
        if (this.currentDropdown) {
            this.currentDropdown.classList.remove('show');
        }
        
        menu.classList.add('show');
        this.currentDropdown = menu;
    }

    /**
     * Setup terminal handlers
     */
    setupTerminalHandlers() {
        // Terminal input handler
        const terminalInput = document.getElementById('terminalInput');
        if (terminalInput) {
            terminalInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const command = terminalInput.value.trim();
                    if (command && window.socketClient) {
                        // Add command to terminal display
                        window.socketClient.addTerminalOutput(`user@autopilot:~/project$ ${command}`, 'command');
                        
                        // Send command via socket client
                        window.socketClient.sendTerminalCommand(command);
                        
                        terminalInput.value = '';
                    }
                }
            });
        }

        // Terminal toggle button
        const toggleTerminalBtn = document.getElementById('toggleTerminalBtn');
        if (toggleTerminalBtn) {
            toggleTerminalBtn.addEventListener('click', () => {
                const terminal = document.getElementById('terminalSection');
                const content = document.getElementById('terminalContent');
                
                if (terminal && content) {
                    terminal.classList.toggle('collapsed');
                    content.classList.toggle('collapsed');
                    
                    const svg = toggleTerminalBtn.querySelector('svg polyline');
                    if (svg) {
                        if (terminal.classList.contains('collapsed')) {
                            svg.setAttribute('points', '6 9 12 15 18 9');
                        } else {
                            svg.setAttribute('points', '18 15 12 9 6 15');
                        }
                    }
                }
            });
        }

        console.log('[UIHandlers] Terminal handlers setup');
    }

    /**
     * Setup AI panel handlers
     */
    setupAIHandlers() {
        // AI input auto-resize
        const aiInput = document.getElementById('aiInput');
        if (aiInput) {
            aiInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });

            // AI input enter key handler
            aiInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendAIMessage();
                }
            });
        }

        // AI send button
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendAIMessage();
            });
        }

        // AI mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        console.log('[UIHandlers] AI handlers setup');
    }

    /**
     * Send AI message
     */
    sendAIMessage() {
        const input = document.getElementById('aiInput');
        if (!input) return;

        const message = input.value.trim();
        if (!message) return;

        // Add user message to chat
        if (window.socketClient) {
            window.socketClient.addAIMessage(message, true);
            
            // Get active mode
            const activeMode = document.querySelector('.mode-btn.active');
            const mode = activeMode ? activeMode.textContent.trim().split(' ')[1].toLowerCase() : 'chat';
            
            // Send to backend
            window.socketClient.sendAIMessage(message, mode);
        }

        // Clear input
        input.value = '';
        input.style.height = 'auto';
    }

    /**
     * Setup modal handlers
     */
    setupModalHandlers() {
        // Close modals when clicking outside
        window.addEventListener('click', (event) => {
            const manageModal = document.getElementById('manageExtensionsModal');
            const getModal = document.getElementById('getExtensionsModal');
            const projectModal = document.getElementById('projectModal');
            
            if (event.target === manageModal) {
                manageModal.classList.remove('show');
            }
            if (event.target === getModal) {
                getModal.classList.remove('show');
            }
            if (event.target === projectModal) {
                projectModal.style.display = 'none';
            }
        });

        console.log('[UIHandlers] Modal handlers setup');
    }

    /**
     * Setup file tree handlers
     */
    setupFileTreeHandlers() {
        const fileTree = document.getElementById('fileTree');
        if (!fileTree) return;

        // Delegate click events to file items
        fileTree.addEventListener('click', (e) => {
            const fileItem = e.target.closest('.file-item');
            if (fileItem) {
                this.selectFile(fileItem);
            }
        });

        console.log('[UIHandlers] File tree handlers setup');
    }

    /**
     * Select file in tree
     * @param {HTMLElement} element - File item element
     */
    selectFile(element) {
        // Remove active class from all items
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected item
        element.classList.add('active');
        
        // Get file name
        const fileName = element.textContent.trim();
        
        // Update editor tab
        const editorTabs = document.querySelector('.tabs');
        if (editorTabs) {
            const existingTab = editorTabs.querySelector('.tab');
            if (existingTab) {
                const fileIcon = element.querySelector('.file-icon');
                const icon = fileIcon ? fileIcon.textContent : '📄';
                
                existingTab.innerHTML = `
                    <span class="file-icon">${icon}</span>
                    <span>${fileName}</span>
                    <div class="tab-close" onclick="event.stopPropagation();">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </div>
                `;
            }
        }
        
        console.log('[UIHandlers] Selected file:', fileName);
    }

    /**
     * Setup tab handlers
     */
    setupTabHandlers() {
        // Tab close buttons
        document.addEventListener('click', (e) => {
            const tabClose = e.target.closest('.tab-close');
            if (tabClose) {
                e.stopPropagation();
                const tab = tabClose.closest('.tab');
                if (tab) {
                    this.closeTab(tab);
                }
            }
        });

        console.log('[UIHandlers] Tab handlers setup');
    }

    /**
     * Close tab
     * @param {HTMLElement} tab - Tab element
     */
    closeTab(tab) {
        const fileName = tab.textContent.trim();
        console.log('[UIHandlers] Closing tab:', fileName);
        
        // If this is the only tab, just clear it
        const tabs = document.querySelectorAll('.tab');
        if (tabs.length === 1) {
            tab.innerHTML = `
                <span class="file-icon">📄</span>
                <span>Untitled</span>
            `;
        } else {
            tab.remove();
        }
    }

    /**
     * Update window menu checkmarks
     */
    updateWindowMenuCheckmarks() {
        if (!window.layoutManager) return;
        
        const state = window.layoutManager.getState();
        
        const explorerCheck = document.getElementById('explorerCheck');
        const editorCheck = document.getElementById('editorCheck');
        const terminalCheck = document.getElementById('terminalCheck');
        const aiPanelCheck = document.getElementById('aiPanelCheck');
        
        if (explorerCheck) explorerCheck.style.display = state.sidebar.visible ? 'inline' : 'none';
        if (editorCheck) editorCheck.style.display = state.editor.visible ? 'inline' : 'none';
        if (terminalCheck) terminalCheck.style.display = state.terminal.visible ? 'inline' : 'none';
        if (aiPanelCheck) aiPanelCheck.style.display = state.aiPanel.visible ? 'inline' : 'none';
    }
}

// Create global instance
window.uiHandlers = new UIHandlers();

// Global functions for onclick handlers in HTML
window.toggleDropdown = (menuId, event) => {
    window.uiHandlers.toggleDropdown(menuId, event);
};

window.selectFile = (element, fileName) => {
    window.uiHandlers.selectFile(element);
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIHandlers;
}

console.log('[UIHandlers] Module loaded');
