/**
 * Extension Manager - Wrapper for extension-module.js
 * This file provides compatibility with the refactored architecture
 */

// Import the extension module functionality
// Note: extension-module.js already exists and contains the full implementation
// This file serves as a compatibility layer for the new architecture

class ExtensionManager {
    constructor() {
        this.extensions = [];
        this.activeExtensions = new Set();
        this.initialized = false;
    }

    /**
     * Initialize the extension manager
     */
    async initialize() {
        if (this.initialized) {
            console.log('[ExtensionManager] Already initialized');
            return;
        }

        console.log('[ExtensionManager] Initializing...');
        
        try {
            // Load extensions from backend
            await this.loadExtensions();
            this.initialized = true;
            console.log('[ExtensionManager] Initialized successfully');
        } catch (error) {
            console.error('[ExtensionManager] Initialization failed:', error);
            throw error;
        }
    }

    /**
     * Load extensions from backend
     */
    async loadExtensions() {
        try {
            const response = await fetch('/api/extensions');
            if (!response.ok) {
                throw new Error(`Failed to load extensions: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.extensions = data.extensions || [];
            
            console.log(`[ExtensionManager] Loaded ${this.extensions.length} extensions`);
            return this.extensions;
        } catch (error) {
            console.error('[ExtensionManager] Failed to load extensions:', error);
            this.extensions = [];
            return [];
        }
    }

    /**
     * Show manage extensions modal
     */
    showManageModal() {
        console.log('[ExtensionManager] Opening manage extensions modal');
        
        const modal = document.getElementById('manageExtensionsModal');
        if (!modal) {
            console.error('[ExtensionManager] Manage extensions modal not found');
            return;
        }

        // Create modal content
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Manage Extensions</h2>
                    <button class="modal-close" onclick="this.closest('.modal').style.display='none'">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="extensions-list">
                        ${this.renderExtensionsList()}
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
    }

    /**
     * Show get extensions modal
     */
    showGetModal() {
        console.log('[ExtensionManager] Opening get extensions modal');
        
        const modal = document.getElementById('getExtensionsModal');
        if (!modal) {
            console.error('[ExtensionManager] Get extensions modal not found');
            return;
        }

        // Create modal content
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Get Extensions</h2>
                    <button class="modal-close" onclick="this.closest('.modal').style.display='none'">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="extensions-marketplace">
                        <p>Extension marketplace coming soon!</p>
                        <p>Available extensions will be displayed here.</p>
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
    }

    /**
     * Render extensions list HTML
     */
    renderExtensionsList() {
        if (this.extensions.length === 0) {
            return '<p class="no-extensions">No extensions installed</p>';
        }

        return this.extensions.map(ext => `
            <div class="extension-item">
                <div class="extension-info">
                    <h3>${ext.name}</h3>
                    <p>${ext.description || 'No description'}</p>
                    <span class="extension-version">v${ext.version || '1.0.0'}</span>
                </div>
                <div class="extension-actions">
                    <button class="btn btn-sm ${ext.enabled ? 'btn-danger' : 'btn-primary'}" 
                            onclick="window.extensionManager.toggleExtension('${ext.id}')">
                        ${ext.enabled ? 'Disable' : 'Enable'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Toggle extension enabled state
     */
    async toggleExtension(extensionId) {
        try {
            const extension = this.extensions.find(ext => ext.id === extensionId);
            if (!extension) {
                throw new Error(`Extension ${extensionId} not found`);
            }

            const newState = !extension.enabled;
            
            const response = await fetch(`/api/extensions/${extensionId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ enabled: newState })
            });

            if (!response.ok) {
                throw new Error(`Failed to toggle extension: ${response.statusText}`);
            }

            extension.enabled = newState;
            console.log(`[ExtensionManager] Extension ${extensionId} ${newState ? 'enabled' : 'disabled'}`);
            
            // Refresh the modal
            this.showManageModal();
        } catch (error) {
            console.error('[ExtensionManager] Failed to toggle extension:', error);
            alert(`Failed to toggle extension: ${error.message}`);
        }
    }

    /**
     * Install extension
     */
    async installExtension(extensionId) {
        try {
            const response = await fetch('/api/extensions/install', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ extensionId })
            });

            if (!response.ok) {
                throw new Error(`Failed to install extension: ${response.statusText}`);
            }

            await this.loadExtensions();
            console.log(`[ExtensionManager] Extension ${extensionId} installed`);
        } catch (error) {
            console.error('[ExtensionManager] Failed to install extension:', error);
            throw error;
        }
    }

    /**
     * Uninstall extension
     */
    async uninstallExtension(extensionId) {
        try {
            const response = await fetch(`/api/extensions/${extensionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`Failed to uninstall extension: ${response.statusText}`);
            }

            this.extensions = this.extensions.filter(ext => ext.id !== extensionId);
            console.log(`[ExtensionManager] Extension ${extensionId} uninstalled`);
        } catch (error) {
            console.error('[ExtensionManager] Failed to uninstall extension:', error);
            throw error;
        }
    }
}

// Create global instance
window.extensionManager = new ExtensionManager();

console.log('[ExtensionManager] Module loaded');
