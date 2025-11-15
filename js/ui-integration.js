/**
 * AutoPilot IDE - UI Integration Layer
 * Connects UI components with backend services via socketManager and projectManager
 */

class UIIntegration {
    constructor() {
        this.initialized = false;
        this.init();
    }

    init() {
        console.log('[UIIntegration] Initializing UI integration...');
        
        // Wait for DOM and dependencies to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Wait for dependencies
        const checkDependencies = setInterval(() => {
            if (window.socketManager && window.projectManager) {
                clearInterval(checkDependencies);
                this.initializeComponents();
            }
        }, 100);
    }

    initializeComponents() {
        console.log('[UIIntegration] Setting up UI components...');
        
        this.setupTerminalInput();
        this.setupAIInput();
        this.setupFileTree();
        this.setupProjectModal();
        this.setupExtensionModals();
        
        this.initialized = true;
        console.log('[UIIntegration] UI integration complete');
    }

    setupTerminalInput() {
        const terminalInput = document.getElementById('terminalInput');
        if (!terminalInput) return;

        terminalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = terminalInput.value.trim();
                if (command && window.socketManager) {
                    // Add command to terminal display
                    this.addTerminalLine(`user@autopilot:~/project$ ${command}`, 'command');
                    
                    // Execute via socket manager with CORRECT event name
                    window.socketManager.executeTerminalCommand(command);
                    
                    terminalInput.value = '';
                }
            }
        });

        console.log('[UIIntegration] Terminal input configured');
    }

    setupAIInput() {
        const aiInput = document.getElementById('aiInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (!aiInput || !sendBtn) return;

        // Auto-resize textarea
        aiInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Send message on button click
        sendBtn.addEventListener('click', () => {
            this.sendAIMessage();
        });

        // Send message on Enter (Shift+Enter for new line)
        aiInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendAIMessage();
            }
        });

        console.log('[UIIntegration] AI input configured');
    }

    sendAIMessage() {
        const aiInput = document.getElementById('aiInput');
        if (!aiInput) return;

        const message = aiInput.value.trim();
        if (!message) return;

        // Get active mode
        const activeMode = document.querySelector('.mode-btn.active');
        const mode = activeMode ? activeMode.textContent.trim() : 'Chat';

        // Get current project context
        const currentProject = window.projectManager ? window.projectManager.getCurrentProject() : null;
        const context = {
            mode: mode,
            project: currentProject ? {
                id: currentProject.id,
                name: currentProject.name,
                path: currentProject.path
            } : null
        };

        // Add user message to chat
        if (window.socketManager) {
            window.socketManager.addAIMessage(message, true);
            
            // Send to backend with CORRECT event name
            window.socketManager.sendAIMessage(message, context);
        }

        // Clear input
        aiInput.value = '';
        aiInput.style.height = 'auto';
    }

    setupFileTree() {
        const fileTree = document.getElementById('fileTree');
        if (!fileTree) return;

        // File tree will be populated by projectManager.loadProjectFiles()
        // This just sets up the click handlers
        fileTree.addEventListener('click', (e) => {
            const fileItem = e.target.closest('.file-item');
            if (!fileItem) return;

            // Remove active class from all items
            fileTree.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('active');
            });

            // Add active class to clicked item
            fileItem.classList.add('active');

            // Get file name
            const fileName = fileItem.textContent.trim();
            console.log('[UIIntegration] File selected:', fileName);

            // Update editor tab
            this.updateEditorTab(fileName);
        });

        console.log('[UIIntegration] File tree configured');
    }

    updateEditorTab(fileName) {
        const tabs = document.querySelector('.tabs');
        if (!tabs) return;

        let tab = tabs.querySelector('.tab');
        if (!tab) {
            // Create new tab if none exists
            tab = document.createElement('div');
            tab.className = 'tab active';
            tabs.appendChild(tab);
        }

        tab.innerHTML = `
            <span class="file-icon">📄</span>
            <span>${fileName}</span>
            <div class="tab-close" onclick="event.stopPropagation();">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
            </div>
        `;
    }

    setupProjectModal() {
        const modal = document.getElementById('projectModal');
        if (!modal) return;

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeProjectModal();
            }
        });

        console.log('[UIIntegration] Project modal configured');
    }

    setupExtensionModals() {
        const manageModal = document.getElementById('manageExtensionsModal');
        const getModal = document.getElementById('getExtensionsModal');

        if (manageModal) {
            manageModal.addEventListener('click', (e) => {
                if (e.target === manageModal) {
                    manageModal.classList.remove('show');
                }
            });
        }

        if (getModal) {
            getModal.addEventListener('click', (e) => {
                if (e.target === getModal) {
                    getModal.classList.remove('show');
                }
            });
        }

        console.log('[UIIntegration] Extension modals configured');
    }

    addTerminalLine(text, type = 'output') {
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

    closeProjectModal() {
        const modal = document.getElementById('projectModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // Helper method to update file tree from project files
    updateFileTreeDisplay(files) {
        const fileTree = document.getElementById('fileTree');
        if (!fileTree || !files || files.length === 0) {
            if (fileTree) {
                fileTree.innerHTML = '<div style="padding: 16px; color: var(--text-secondary); text-align: center;">No files in project</div>';
            }
            return;
        }

        fileTree.innerHTML = files.map(file => {
            const icon = this.getFileIcon(file.name || file.path);
            const name = file.name || file.path.split('/').pop();
            
            return `
                <div class="file-item" data-file-path="${file.path || name}">
                    <span class="file-icon">${icon}</span>
                    <span>${name}</span>
                </div>
            `;
        }).join('');

        console.log('[UIIntegration] File tree updated with', files.length, 'files');
    }

    getFileIcon(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        const iconMap = {
            'py': '🐍',
            'js': '📜',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            'md': '📝',
            'txt': '📄',
            'yml': '⚙️',
            'yaml': '⚙️',
            'xml': '📰',
            'sql': '🗄️',
            'sh': '⚡',
            'bat': '⚡',
            'exe': '⚙️',
            'zip': '📦',
            'tar': '📦',
            'gz': '📦'
        };
        
        return iconMap[ext] || '📄';
    }
}

// Create global instance
const uiIntegration = new UIIntegration();

// Export for use in other scripts
window.uiIntegration = uiIntegration;

// Helper function to update file tree (called by projectManager)
window.updateFileExplorer = function(files) {
    if (window.uiIntegration) {
        window.uiIntegration.updateFileTreeDisplay(files);
    }
};
