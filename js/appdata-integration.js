/**
 * AppData Integration Layer
 * Provides centralized access to application data with caching and event system
 */

class AppDataIntegration {
    constructor() {
        this.baseUrl = '/api';
        this.cache = {
            projects: null,
            themes: null,
            extensions: null,
            layouts: null,
            settings: null
        };
        this.listeners = {};
        this.initialized = false;
        
        console.log('🔧 AppData Integration initialized');
    }

    /**
     * Initialize AppData integration
     */
    async initialize() {
        try {
            console.log('🚀 Initializing AppData...');
            
            // Load all data from backend
            await Promise.all([
                this.loadProjects(),
                this.loadThemes(),
                this.loadExtensions(),
                this.loadLayouts(),
                this.loadSettings()
            ]);
            
            this.initialized = true;
            this.emit('initialized', { status: 'success' });
            console.log('✅ AppData initialized successfully');
            
            return true;
        } catch (error) {
            console.error('❌ AppData initialization failed:', error);
            this.emit('error', { message: 'Initialization failed', error });
            return false;
        }
    }

    /**
     * Get AppData status
     */
    async getStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/appdata/status`);
            if (!response.ok) throw new Error('Failed to get status');
            const status = await response.json();
            return status;
        } catch (error) {
            console.error('Error getting AppData status:', error);
            throw error;
        }
    }

    // ==================== PROJECTS ====================

    async loadProjects() {
        try {
            const response = await fetch(`${this.baseUrl}/projects`);
            if (!response.ok) throw new Error('Failed to load projects');
            this.cache.projects = await response.json();
            this.emit('projects:loaded', this.cache.projects);
            return this.cache.projects;
        } catch (error) {
            console.error('Error loading projects:', error);
            throw error;
        }
    }

    getProjects() {
        return this.cache.projects || [];
    }

    async getProject(projectId) {
        try {
            const response = await fetch(`${this.baseUrl}/projects/${projectId}`);
            if (!response.ok) throw new Error('Project not found');
            return await response.json();
        } catch (error) {
            console.error('Error getting project:', error);
            throw error;
        }
    }

    async createProject(name, type = 'Python', description = '') {
        try {
            const response = await fetch(`${this.baseUrl}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, type, description })
            });
            
            if (!response.ok) throw new Error('Failed to create project');
            const project = await response.json();
            
            // Update cache
            await this.loadProjects();
            this.emit('project:created', project);
            
            return project;
        } catch (error) {
            console.error('Error creating project:', error);
            throw error;
        }
    }

    async deleteProject(projectId) {
        try {
            const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete project');
            
            // Update cache
            await this.loadProjects();
            this.emit('project:deleted', { id: projectId });
            
            return true;
        } catch (error) {
            console.error('Error deleting project:', error);
            throw error;
        }
    }

    // ==================== THEMES ====================

    async loadThemes() {
        try {
            const response = await fetch(`${this.baseUrl}/themes`);
            if (!response.ok) throw new Error('Failed to load themes');
            this.cache.themes = await response.json();
            this.emit('themes:loaded', this.cache.themes);
            return this.cache.themes;
        } catch (error) {
            console.error('Error loading themes:', error);
            throw error;
        }
    }

    getThemes() {
        return this.cache.themes || [];
    }

    getActiveTheme() {
        const themes = this.getThemes();
        return themes.find(t => t.active) || null;
    }

    async activateTheme(themeId) {
        try {
            const response = await fetch(`${this.baseUrl}/themes/${themeId}/activate`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to activate theme');
            const result = await response.json();
            
            // Update cache
            await this.loadThemes();
            this.emit('theme:activated', result.theme);
            
            return result.theme;
        } catch (error) {
            console.error('Error activating theme:', error);
            throw error;
        }
    }

    // ==================== EXTENSIONS ====================

    async loadExtensions() {
        try {
            const response = await fetch(`${this.baseUrl}/extensions`);
            if (!response.ok) throw new Error('Failed to load extensions');
            this.cache.extensions = await response.json();
            this.emit('extensions:loaded', this.cache.extensions);
            return this.cache.extensions;
        } catch (error) {
            console.error('Error loading extensions:', error);
            throw error;
        }
    }

    getExtensions() {
        return this.cache.extensions || [];
    }

    getInstalledExtensions() {
        return this.getExtensions().filter(e => e.installed);
    }

    getAvailableExtensions() {
        return this.getExtensions().filter(e => !e.installed);
    }

    async toggleExtension(extensionId) {
        try {
            const response = await fetch(`${this.baseUrl}/extensions/${extensionId}/toggle`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to toggle extension');
            const result = await response.json();
            
            // Update cache
            await this.loadExtensions();
            this.emit('extension:toggled', result.extension);
            
            return result.extension;
        } catch (error) {
            console.error('Error toggling extension:', error);
            throw error;
        }
    }

    async installExtension(extensionId) {
        try {
            const response = await fetch(`${this.baseUrl}/extensions/${extensionId}/install`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to install extension');
            const result = await response.json();
            
            // Update cache
            await this.loadExtensions();
            this.emit('extension:installed', result.extension);
            
            return result.extension;
        } catch (error) {
            console.error('Error installing extension:', error);
            throw error;
        }
    }

    async uninstallExtension(extensionId) {
        try {
            const response = await fetch(`${this.baseUrl}/extensions/${extensionId}/uninstall`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to uninstall extension');
            
            // Update cache
            await this.loadExtensions();
            this.emit('extension:uninstalled', { id: extensionId });
            
            return true;
        } catch (error) {
            console.error('Error uninstalling extension:', error);
            throw error;
        }
    }

    // ==================== LAYOUTS ====================

    async loadLayouts() {
        try {
            const response = await fetch(`${this.baseUrl}/layouts`);
            if (!response.ok) throw new Error('Failed to load layouts');
            this.cache.layouts = await response.json();
            this.emit('layouts:loaded', this.cache.layouts);
            return this.cache.layouts;
        } catch (error) {
            console.error('Error loading layouts:', error);
            throw error;
        }
    }

    getLayouts() {
        return this.cache.layouts || [];
    }

    getActiveLayout() {
        const layouts = this.getLayouts();
        return layouts.find(l => l.active) || null;
    }

    async activateLayout(layoutId) {
        try {
            const response = await fetch(`${this.baseUrl}/layouts/${layoutId}/activate`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to activate layout');
            const result = await response.json();
            
            // Update cache
            await this.loadLayouts();
            this.emit('layout:activated', result.layout);
            
            return result.layout;
        } catch (error) {
            console.error('Error activating layout:', error);
            throw error;
        }
    }

    async saveLayout(layoutId, config) {
        try {
            const response = await fetch(`${this.baseUrl}/layouts/${layoutId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config })
            });
            
            if (!response.ok) throw new Error('Failed to save layout');
            const result = await response.json();
            
            // Update cache
            await this.loadLayouts();
            this.emit('layout:saved', result.layout);
            
            return result.layout;
        } catch (error) {
            console.error('Error saving layout:', error);
            throw error;
        }
    }

    // ==================== SETTINGS ====================

    async loadSettings() {
        try {
            const response = await fetch(`${this.baseUrl}/settings`);
            if (!response.ok) throw new Error('Failed to load settings');
            this.cache.settings = await response.json();
            this.emit('settings:loaded', this.cache.settings);
            return this.cache.settings;
        } catch (error) {
            console.error('Error loading settings:', error);
            throw error;
        }
    }

    getSettings() {
        return this.cache.settings || {};
    }

    getSetting(key) {
        return this.getSettings()[key];
    }

    async setSetting(key, value) {
        try {
            const response = await fetch(`${this.baseUrl}/settings/${key}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value })
            });
            
            if (!response.ok) throw new Error('Failed to set setting');
            
            // Update cache
            await this.loadSettings();
            this.emit('setting:updated', { key, value });
            
            return true;
        } catch (error) {
            console.error('Error setting value:', error);
            throw error;
        }
    }

    async updateSettings(updates) {
        try {
            const response = await fetch(`${this.baseUrl}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) throw new Error('Failed to update settings');
            const result = await response.json();
            
            // Update cache
            this.cache.settings = result.settings;
            this.emit('settings:updated', result.settings);
            
            return result.settings;
        } catch (error) {
            console.error('Error updating settings:', error);
            throw error;
        }
    }

    // ==================== EVENT SYSTEM ====================

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for ${event}:`, error);
            }
        });
    }

    // ==================== UTILITY METHODS ====================

    clearCache() {
        this.cache = {
            projects: null,
            themes: null,
            extensions: null,
            layouts: null,
            settings: null
        };
        console.log('🗑️ Cache cleared');
    }

    async refresh() {
        console.log('🔄 Refreshing AppData...');
        this.clearCache();
        await this.initialize();
    }

    isInitialized() {
        return this.initialized;
    }
}

// Create global instance
window.appDataIntegration = new AppDataIntegration();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.appDataIntegration.initialize();
    });
} else {
    window.appDataIntegration.initialize();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AppDataIntegration;
}

// Global helper function
function getAppDataIntegration() {
    return window.appDataIntegration;
}

console.log('✅ AppData Integration layer loaded');
