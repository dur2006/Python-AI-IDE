/**
 * Initialization Module
 * Orchestrates the startup of the AutoPilot IDE
 * Ensures all modules are loaded and initialized in correct order
 */

class AppInitializer {
    constructor() {
        this.initialized = false;
        this.modules = {
            socketClient: false,
            projectManager: false,
            layoutManager: false,
            uiHandlers: false
        };
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.initialized) {
            console.warn('[AppInitializer] Already initialized');
            return;
        }

        console.log('[AppInitializer] Starting application initialization...');

        try {
            // Step 1: Initialize socket connection
            await this.initSocketClient();

            // Step 2: Initialize project manager
            await this.initProjectManager();

            // Step 3: Initialize layout manager
            await this.initLayoutManager();

            // Step 4: Initialize UI handlers
            await this.initUIHandlers();

            // Step 5: Load last project or show welcome
            await this.loadInitialState();

            // Step 6: Setup global error handlers
            this.setupErrorHandlers();

            this.initialized = true;
            console.log('[AppInitializer] ✓ Application initialized successfully');
            
            // Show success message in terminal
            if (window.socketClient) {
                window.socketClient.addTerminalOutput('✓ AutoPilot IDE initialized successfully', 'success');
                window.socketClient.addTerminalOutput('Type "help" for available commands', 'output');
            }

        } catch (error) {
            console.error('[AppInitializer] Initialization failed:', error);
            this.showInitializationError(error);
        }
    }

    /**
     * Initialize socket client
     */
    async initSocketClient() {
        console.log('[AppInitializer] Initializing socket client...');
        
        if (!window.socketClient) {
            throw new Error('SocketClient not loaded');
        }

        // Initialize connection to backend
        const backendUrl = this.getBackendUrl();
        window.socketClient.init(backendUrl);

        // Wait for connection (with timeout)
        await this.waitForConnection(5000);

        this.modules.socketClient = true;
        console.log('[AppInitializer] ✓ Socket client initialized');
    }

    /**
     * Wait for socket connection
     * @param {number} timeout - Timeout in milliseconds
     */
    waitForConnection(timeout = 5000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            const checkConnection = () => {
                if (window.socketClient.isConnected()) {
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    console.warn('[AppInitializer] Socket connection timeout - continuing anyway');
                    resolve(); // Don't fail initialization if backend is down
                } else {
                    setTimeout(checkConnection, 100);
                }
            };
            
            checkConnection();
        });
    }

    /**
     * Initialize project manager
     */
    async initProjectManager() {
        console.log('[AppInitializer] Initializing project manager...');
        
        if (!window.projectManager) {
            throw new Error('ProjectManager not loaded');
        }

        // Initialize project manager
        await window.projectManager.init();

        this.modules.projectManager = true;
        console.log('[AppInitializer] ✓ Project manager initialized');
    }

    /**
     * Initialize layout manager
     */
    async initLayoutManager() {
        console.log('[AppInitializer] Initializing layout manager...');
        
        if (!window.layoutManager) {
            console.warn('[AppInitializer] LayoutManager not found - skipping');
            return;
        }

        // Initialize layout manager
        window.layoutManager.init();

        this.modules.layoutManager = true;
        console.log('[AppInitializer] ✓ Layout manager initialized');
    }

    /**
     * Initialize UI handlers
     */
    async initUIHandlers() {
        console.log('[AppInitializer] Initializing UI handlers...');
        
        if (!window.uiHandlers) {
            throw new Error('UIHandlers not loaded');
        }

        // Initialize UI handlers
        window.uiHandlers.init();

        this.modules.uiHandlers = true;
        console.log('[AppInitializer] ✓ UI handlers initialized');
    }

    /**
     * Load initial state (last project or welcome screen)
     */
    async loadInitialState() {
        console.log('[AppInitializer] Loading initial state...');
        
        if (window.projectManager) {
            // Try to load last opened project
            const lastProject = window.projectManager.getLastProject();
            
            if (lastProject) {
                console.log('[AppInitializer] Loading last project:', lastProject.name);
                try {
                    await window.projectManager.loadProject(lastProject.id);
                } catch (error) {
                    console.error('[AppInitializer] Failed to load last project:', error);
                    this.showWelcomeScreen();
                }
            } else {
                this.showWelcomeScreen();
            }
        }
    }

    /**
     * Show welcome screen
     */
    showWelcomeScreen() {
        console.log('[AppInitializer] Showing welcome screen');
        
        // Update editor with welcome message
        const editor = document.getElementById('editor');
        if (editor) {
            editor.innerHTML = `
                <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                    <h1 style="color: var(--accent-primary); margin-bottom: 20px;">
                        🚀 Welcome to AutoPilot IDE
                    </h1>
                    <p style="font-size: 16px; margin-bottom: 30px;">
                        Your AI-powered Python development environment
                    </p>
                    <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                        <button onclick="window.projectManager.showProjectModal()" 
                                style="padding: 12px 24px; background: var(--accent-primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px;">
                            📁 Open Project
                        </button>
                        <button onclick="window.projectManager.createNewProject()" 
                                style="padding: 12px 24px; background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; font-size: 14px;">
                            ✨ Create New Project
                        </button>
                    </div>
                    <div style="margin-top: 40px; font-size: 14px;">
                        <p>💡 <strong>Quick Tips:</strong></p>
                        <ul style="list-style: none; padding: 0; margin-top: 10px;">
                            <li>• Use the AI panel on the right for code assistance</li>
                            <li>• Terminal is available at the bottom</li>
                            <li>• Press Ctrl+P to quickly open files</li>
                        </ul>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Setup global error handlers
     */
    setupErrorHandlers() {
        // Catch unhandled errors
        window.addEventListener('error', (event) => {
            console.error('[AppInitializer] Unhandled error:', event.error);
            this.showError('An unexpected error occurred', event.error.message);
        });

        // Catch unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('[AppInitializer] Unhandled promise rejection:', event.reason);
            this.showError('An unexpected error occurred', event.reason);
        });

        console.log('[AppInitializer] ✓ Error handlers setup');
    }

    /**
     * Get backend URL from environment or default
     * @returns {string} Backend URL
     */
    getBackendUrl() {
        // Check if running in development or production
        const isDevelopment = window.location.hostname === 'localhost' || 
                             window.location.hostname === '127.0.0.1';
        
        if (isDevelopment) {
            return 'http://localhost:5000';
        }
        
        // In production, use same origin
        return window.location.origin;
    }

    /**
     * Show initialization error
     * @param {Error} error - Error object
     */
    showInitializationError(error) {
        const editor = document.getElementById('editor');
        if (editor) {
            editor.innerHTML = `
                <div style="padding: 40px; text-align: center; color: var(--error);">
                    <h1 style="margin-bottom: 20px;">⚠️ Initialization Failed</h1>
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        Failed to initialize AutoPilot IDE
                    </p>
                    <div style="background: var(--bg-tertiary); padding: 20px; border-radius: 8px; text-align: left; max-width: 600px; margin: 0 auto;">
                        <strong>Error:</strong>
                        <pre style="margin-top: 10px; color: var(--text-primary);">${error.message}</pre>
                    </div>
                    <button onclick="location.reload()" 
                            style="margin-top: 30px; padding: 12px 24px; background: var(--accent-primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px;">
                        🔄 Reload Application
                    </button>
                </div>
            `;
        }
    }

    /**
     * Show error message
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        // Add error to terminal if available
        if (window.socketClient) {
            window.socketClient.addTerminalOutput(`✗ ${title}: ${message}`, 'error');
        }
        
        // Could also show a toast notification here
        console.error(`[AppInitializer] ${title}:`, message);
    }

    /**
     * Check if application is initialized
     * @returns {boolean} Initialization status
     */
    isInitialized() {
        return this.initialized;
    }

    /**
     * Get module status
     * @returns {Object} Module status object
     */
    getModuleStatus() {
        return { ...this.modules };
    }
}

// Create global instance
window.appInitializer = new AppInitializer();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.appInitializer.init();
    });
} else {
    // DOM already loaded
    window.appInitializer.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AppInitializer;
}

console.log('[AppInitializer] Module loaded');
