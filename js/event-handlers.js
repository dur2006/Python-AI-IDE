/**
 * Event Handlers - Centralized event listener management
 */

const EventHandlers = (() => {
    const handlers = {};

    const init = () => {
        console.log('[EventHandlers] Initializing...');
        
        // Menu dropdown handlers
        setupMenuHandlers();
        
        // Modal close handlers
        setupModalHandlers();
        
        // Global click handler to close dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.menu-tab-wrapper')) {
                UIModule.closeAllDropdowns();
            }
        });

        console.log('[EventHandlers] All event handlers registered');
    };

    const setupMenuHandlers = () => {
        // File menu
        const fileMenu = document.querySelector('[onclick*="toggleDropdown"]');
        if (fileMenu) {
            console.log('[EventHandlers] File menu handler registered');
        }

        // Edit menu
        // View menu
        // Help menu
        // (These would be set up similarly)
    };

    const setupModalHandlers = () => {
        // Manage Extensions modal close
        const manageModal = document.getElementById('manageExtensionsModal');
        if (manageModal) {
            manageModal.addEventListener('click', (e) => {
                if (e.target === manageModal) {
                    UIModule.hideModal('manageExtensionsModal');
                }
            });
        }

        // Get Extensions modal close
        const getModal = document.getElementById('getExtensionsModal');
        if (getModal) {
            getModal.addEventListener('click', (e) => {
                if (e.target === getModal) {
                    UIModule.hideModal('getExtensionsModal');
                }
            });
        }

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    modal.classList.remove('show');
                }
            });
        });
    };

    const registerHandler = (name, handler) => {
        handlers[name] = handler;
        console.log(`[EventHandlers] Registered handler: ${name}`);
    };

    const getHandler = (name) => {
        return handlers[name];
    };

    return {
        init,
        registerHandler,
        getHandler,
        handlers
    };
})();
