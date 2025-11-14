/**
 * AutoPilot IDE - Main Application Initialization
 */

class App {
    constructor() {
        this.initialized = false;
        this.modules = [];
    }

    async init() {
        console.log('🚀 AutoPilot IDE - Initializing Application...\n');
        
        try {
            // Initialize modules in order
            this.modules = [
                { name: 'APIModule', module: APIModule },
                { name: 'SocketModule', module: SocketModule },
                { name: 'UIModule', module: UIModule },
                { name: 'TerminalModule', module: TerminalModule },
                { name: 'AIModule', module: AIModule },
                { name: 'EditorModule', module: EditorModule },
                { name: 'ExplorerModule', module: ExplorerModule },
                { name: 'ExtensionModule', module: ExtensionModule },
                { name: 'EventHandlers', module: EventHandlers }
            ];

            // Initialize each module
            for (const { name, module } of this.modules) {
                if (module && module.init) {
                    console.log(`[App] Initializing ${name}...`);
                    await module.init();
                } else {
                    console.warn(`[App] Module ${name} has no init method`);
                }
            }

            this.initialized = true;
            console.log('\n✅ Application initialized successfully!\n');
            UIModule.showNotification('AutoPilot IDE Ready', 'success');

            // Run tests if in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log('\n🧪 Running test suite...\n');
                await testSuite.run();
            }

        } catch (error) {
            console.error('[App] Initialization failed:', error);
            UIModule.showNotification('Failed to initialize application', 'error');
        }
    }

    isInitialized() {
        return this.initialized;
    }

    getModule(name) {
        const mod = this.modules.find(m => m.name === name);
        return mod ? mod.module : null;
    }
}

// Create global app instance
const app = new App();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = app;
}
