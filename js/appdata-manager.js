/**
 * AppData Manager Module (Frontend)
 * Handles communication with backend AppData system
 * Manages themes, extensions, layouts, and projects
 */

const AppDataManager = (function() {
    'use strict';

    const API_BASE = '/api';
    
    // Cache for loaded data
    const cache = {
        themes: null,
        layouts: null,
        extensions: null,
        projects: null,
        appdata_info: null
    };

    /**
     * Initialize AppData system
     */
    async function init() {
        console.log('[AppDataManager] Initializing...');
        
        try {
            // Initialize AppData on backend
            const initResult = await fetch(`${API_BASE}/appdata/init`, {
                method: 'POST'
            }).then(r => r.json());
            
            console.log('[AppDataManager] Init result:', initResult);
            
            // Load all data
            await Promise.all([
                loadThemes(),
                loadLayouts(),
                loadExtensions(),
                loadProjects(),
                getAppDataInfo()
            ]);
            
            console.log('[AppDataManager] Initialized successfully');
            return true;
        } catch (error) {
            console.error('[AppDataManager] Initialization error:', error);
            return false;
        }
    }

    /**
     * Get AppData folder information
     */
    async function getAppDataInfo() {
        try {
            const response = await fetch(`${API_BASE}/appdata/info`);
            const data = await response.json();
            cache.appdata_info = data;
            console.log('[AppDataManager] AppData info:', data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error getting AppData info:', error);
            return null;
        }
    }

    /**
     * Load all themes
     */
    async function loadThemes() {
        try {
            const response = await fetch(`${API_BASE}/themes`);
            const data = await response.json();
            cache.themes = data;
            console.log('[AppDataManager] Themes loaded:', data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error loading themes:', error);
            return null;
        }
    }

    /**
     * Get a specific theme
     */
    async function getTheme(themeId) {
        try {
            const response = await fetch(`${API_BASE}/themes/${themeId}`);
            const data = await response.json();
            console.log('[AppDataManager] Theme loaded:', themeId, data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error loading theme:', error);
            return null;
        }
    }

    /**
     * Apply a theme
     */
    async function applyTheme(themeId) {
        try {
            const theme = await getTheme(themeId);
            
            if (!theme || theme.status === 'error') {
                console.error('[AppDataManager] Theme not found:', themeId);
                return false;
            }

            // Apply theme colors to CSS variables
            const root = document.documentElement;
            Object.entries(theme.colors).forEach(([key, value]) => {
                root.style.setProperty(`--${key}`, value);
            });

            // Save active theme
            localStorage.setItem('active-theme', themeId);
            
            console.log('[AppDataManager] Theme applied:', themeId);
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: themeId } }));
            
            return true;
        } catch (error) {
            console.error('[AppDataManager] Error applying theme:', error);
            return false;
        }
    }

    /**
     * Load all layouts
     */
    async function loadLayouts() {
        try {
            const response = await fetch(`${API_BASE}/layouts`);
            const data = await response.json();
            cache.layouts = data;
            console.log('[AppDataManager] Layouts loaded:', data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error loading layouts:', error);
            return null;
        }
    }

    /**
     * Get available layouts
     */
    function getLayouts() {
        return cache.layouts;
    }

    /**
     * Load all extensions
     */
    async function loadExtensions() {
        try {
            const response = await fetch(`${API_BASE}/extensions`);
            const data = await response.json();
            cache.extensions = data;
            console.log('[AppDataManager] Extensions loaded:', data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error loading extensions:', error);
            return null;
        }
    }

    /**
     * Get extensions
     */
    function getExtensions() {
        return cache.extensions;
    }

    /**
     * Toggle extension
     */
    async function toggleExtension(extId) {
        try {
            const response = await fetch(`${API_BASE}/extensions/${extId}/toggle`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reload extensions
                await loadExtensions();
                window.dispatchEvent(new CustomEvent('extensionToggled', { 
                    detail: { extension: data.extension } 
                }));
            }
            
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error toggling extension:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Install extension
     */
    async function installExtension(extId) {
        try {
            const response = await fetch(`${API_BASE}/extensions/${extId}/install`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reload extensions
                await loadExtensions();
                window.dispatchEvent(new CustomEvent('extensionInstalled', { 
                    detail: { extension: data.extension } 
                }));
            }
            
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error installing extension:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Uninstall extension
     */
    async function uninstallExtension(extId) {
        try {
            const response = await fetch(`${API_BASE}/extensions/${extId}/uninstall`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reload extensions
                await loadExtensions();
                window.dispatchEvent(new CustomEvent('extensionUninstalled', { 
                    detail: { extensionId: extId } 
                }));
            }
            
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error uninstalling extension:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Load all projects
     */
    async function loadProjects() {
        try {
            const response = await fetch(`${API_BASE}/projects`);
            const data = await response.json();
            cache.projects = data;
            console.log('[AppDataManager] Projects loaded:', data);
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error loading projects:', error);
            return null;
        }
    }

    /**
     * Get projects
     */
    function getProjects() {
        return cache.projects;
    }

    /**
     * Create new project
     */
    async function createProject(projectData) {
        try {
            const response = await fetch(`${API_BASE}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reload projects
                await loadProjects();
                window.dispatchEvent(new CustomEvent('projectCreated', { 
                    detail: { project: data.project } 
                }));
            }
            
            return data;
        } catch (error) {
            console.error('[AppDataManager] Error creating project:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Get cached data
     */
    function getCachedData(type) {
        return cache[type] || null;
    }

    /**
     * Refresh all data
     */
    async function refreshAll() {
        console.log('[AppDataManager] Refreshing all data...');
        return Promise.all([
            loadThemes(),
            loadLayouts(),
            loadExtensions(),
            loadProjects()
        ]);
    }

    // Public API
    const api = {
        init,
        getAppDataInfo,
        loadThemes,
        getTheme,
        applyTheme,
        loadLayouts,
        getLayouts,
        loadExtensions,
        getExtensions,
        toggleExtension,
        installExtension,
        uninstallExtension,
        loadProjects,
        getProjects,
        createProject,
        getCachedData,
        refreshAll
    };

    // Expose to window
    window.appDataManager = api;

    return api;
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AppDataManager.init());
} else {
    AppDataManager.init();
}
