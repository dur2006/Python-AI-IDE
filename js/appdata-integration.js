/**
 * AppData Integration Layer
 * Non-breaking enhancement system for Python-AI-IDE
 * 
 * This module provides a compatibility bridge between the AppData backend
 * and the existing frontend systems. It gracefully falls back to existing
 * functionality when the backend is unavailable.
 * 
 * Load Order: MUST load after layout-manager.js and layout-fixes.js
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    apiBase: '/api',
    retryAttempts: 3,
    retryDelay: 1000,
    cacheTimeout: 5 * 60 * 1000, // 5 minutes
    enableLogging: true
  };

  // Cache storage
  const cache = {
    themes: null,
    layouts: null,
    extensions: null,
    projects: null,
    appDataInfo: null,
    timestamps: {}
  };

  // Logging utility
  const logger = {
    log: (msg, data) => {
      if (CONFIG.enableLogging) {
        console.log(`[AppDataIntegration] ${msg}`, data || '');
      }
    },
    warn: (msg, data) => {
      if (CONFIG.enableLogging) {
        console.warn(`[AppDataIntegration] ${msg}`, data || '');
      }
    },
    error: (msg, data) => {
      if (CONFIG.enableLogging) {
        console.error(`[AppDataIntegration] ${msg}`, data || '');
      }
    }
  };

  // API utilities
  const api = {
    async fetch(endpoint, options = {}) {
      const url = `${CONFIG.apiBase}${endpoint}`;
      let lastError;

      for (let attempt = 0; attempt < CONFIG.retryAttempts; attempt++) {
        try {
          const response = await fetch(url, {
            method: options.method || 'GET',
            headers: {
              'Content-Type': 'application/json',
              ...options.headers
            },
            body: options.body ? JSON.stringify(options.body) : undefined
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          return await response.json();
        } catch (error) {
          lastError = error;
          if (attempt < CONFIG.retryAttempts - 1) {
            await new Promise(resolve => setTimeout(resolve, CONFIG.retryDelay));
          }
        }
      }

      throw lastError;
    },

    async checkAvailability() {
      try {
        const info = await this.fetch('/appdata/info');
        return info;
      } catch (error) {
        logger.warn('Backend not available:', error.message);
        return null;
      }
    }
  };

  // Cache management
  const cacheManager = {
    set(key, value) {
      cache[key] = value;
      cache.timestamps[key] = Date.now();
    },

    get(key) {
      if (!cache[key]) return null;

      const age = Date.now() - cache.timestamps[key];
      if (age > CONFIG.cacheTimeout) {
        cache[key] = null;
        cache.timestamps[key] = null;
        return null;
      }

      return cache[key];
    },

    clear() {
      Object.keys(cache).forEach(key => {
        if (key !== 'timestamps') {
          cache[key] = null;
        }
      });
      cache.timestamps = {};
    }
  };

  // Theme integration
  const themeIntegration = {
    async loadThemes() {
      const cached = cacheManager.get('themes');
      if (cached) return cached;

      try {
        const themes = await api.fetch('/appdata/themes');
        cacheManager.set('themes', themes);
        logger.log('Loaded themes from backend:', themes.length);
        return themes;
      } catch (error) {
        logger.warn('Failed to load themes, using defaults');
        return this.getDefaultThemes();
      }
    },

    getDefaultThemes() {
      return [
        { id: 'dark', name: 'Dark', colors: { primary: '#1e1e1e' } },
        { id: 'light', name: 'Light', colors: { primary: '#ffffff' } }
      ];
    },

    async applyTheme(themeId) {
      try {
        const themes = await this.loadThemes();
        const theme = themes.find(t => t.id === themeId);

        if (!theme) {
          logger.warn('Theme not found:', themeId);
          return false;
        }

        // Apply theme via CSS custom properties
        if (theme.colors) {
          Object.entries(theme.colors).forEach(([key, value]) => {
            document.documentElement.style.setProperty(`--${key}`, value);
          });
        }

        logger.log('Applied theme:', themeId);
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: { themeId } }));
        return true;
      } catch (error) {
        logger.error('Error applying theme:', error);
        return false;
      }
    },

    enhanceThemeMenu() {
      const themeMenu = document.getElementById('themeMenu');
      if (!themeMenu) return;

      this.loadThemes().then(themes => {
        // Filter out default themes (already in menu)
        const customThemes = themes.filter(t => t.id !== 'dark' && t.id !== 'light');

        if (customThemes.length > 0) {
          // Add separator if not exists
          if (!themeMenu.querySelector('.dropdown-separator:last-of-type')) {
            const separator = document.createElement('div');
            separator.className = 'dropdown-separator';
            themeMenu.appendChild(separator);
          }

          // Add custom themes
          customThemes.forEach(theme => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.innerHTML = `
              <svg class="dropdown-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
              </svg>
              <span>${theme.name}</span>
            `;
            item.addEventListener('click', () => this.applyTheme(theme.id));
            themeMenu.appendChild(item);
          });

          logger.log('Enhanced theme menu with', customThemes.length, 'custom themes');
        }
      });
    }
  };

  // Layout integration
  const layoutIntegration = {
    async loadLayouts() {
      const cached = cacheManager.get('layouts');
      if (cached) return cached;

      try {
        const layouts = await api.fetch('/appdata/layouts');
        cacheManager.set('layouts', layouts);
        logger.log('Loaded layouts from backend:', layouts.length);
        return layouts;
      } catch (error) {
        logger.warn('Failed to load layouts');
        return [];
      }
    },

    enhanceLayoutMenu() {
      const layoutMenu = document.getElementById('layoutsMenu');
      if (!layoutMenu) return;

      this.loadLayouts().then(layouts => {
        if (layouts.length > 0) {
          // Add separator
          const separator = document.createElement('div');
          separator.className = 'dropdown-separator';
          layoutMenu.appendChild(separator);

          // Add custom layouts
          layouts.forEach(layout => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.innerHTML = `
              <svg class="dropdown-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
              </svg>
              <span>${layout.name}</span>
            `;
            item.addEventListener('click', () => {
              if (window.layoutManager) {
                window.layoutManager.applyLayout(layout.id);
              }
            });
            layoutMenu.appendChild(item);
          });

          logger.log('Enhanced layout menu with', layouts.length, 'custom layouts');
        }
      });
    }
  };

  // Extension integration
  const extensionIntegration = {
    async loadExtensions() {
      const cached = cacheManager.get('extensions');
      if (cached) return cached;

      try {
        const extensions = await api.fetch('/appdata/extensions');
        cacheManager.set('extensions', extensions);
        logger.log('Loaded extensions from backend:', extensions.length);
        return extensions;
      } catch (error) {
        logger.warn('Failed to load extensions');
        return [];
      }
    },

    async toggleExtension(extensionId) {
      try {
        await api.fetch(`/appdata/extensions/${extensionId}/toggle`, { method: 'POST' });
        cacheManager.set('extensions', null); // Invalidate cache
        document.dispatchEvent(new CustomEvent('extensionToggled', { detail: { extensionId } }));
        return true;
      } catch (error) {
        logger.error('Error toggling extension:', error);
        return false;
      }
    },

    async installExtension(extensionId) {
      try {
        await api.fetch(`/appdata/extensions/${extensionId}/install`, { method: 'POST' });
        cacheManager.set('extensions', null); // Invalidate cache
        document.dispatchEvent(new CustomEvent('extensionInstalled', { detail: { extensionId } }));
        return true;
      } catch (error) {
        logger.error('Error installing extension:', error);
        return false;
      }
    },

    mergeWithExisting() {
      this.loadExtensions().then(backendExtensions => {
        // Merge with existing mock arrays if they exist
        if (window.installedExtensions && Array.isArray(window.installedExtensions)) {
          const merged = [...window.installedExtensions];
          backendExtensions.forEach(ext => {
            if (!merged.find(e => e.id === ext.id)) {
              merged.push(ext);
            }
          });
          window.installedExtensions = merged;
        }

        document.dispatchEvent(new CustomEvent('extensionsLoaded', { detail: { extensions: backendExtensions } }));
        logger.log('Merged extensions with existing system');
      });
    }
  };

  // Project integration
  const projectIntegration = {
    async loadProjects() {
      const cached = cacheManager.get('projects');
      if (cached) return cached;

      try {
        const projects = await api.fetch('/appdata/projects');
        cacheManager.set('projects', projects);
        logger.log('Loaded projects from backend:', projects.length);
        return projects;
      } catch (error) {
        logger.warn('Failed to load projects');
        return [];
      }
    },

    notifyProjectsLoaded() {
      this.loadProjects().then(projects => {
        document.dispatchEvent(new CustomEvent('backendProjectsLoaded', { detail: { projects } }));
        logger.log('Notified systems of loaded projects');
      });
    }
  };

  // Public API
  const appDataIntegration = {
    // Availability
    isBackendAvailable() {
      return cache.appDataInfo !== null;
    },

    getBackendInfo() {
      return cache.appDataInfo;
    },

    // Themes
    loadThemes: () => themeIntegration.loadThemes(),
    applyTheme: (id) => themeIntegration.applyTheme(id),

    // Layouts
    loadLayouts: () => layoutIntegration.loadLayouts(),

    // Extensions
    loadExtensions: () => extensionIntegration.loadExtensions(),
    toggleExtension: (id) => extensionIntegration.toggleExtension(id),
    installExtension: (id) => extensionIntegration.installExtension(id),

    // Projects
    loadProjects: () => projectIntegration.loadProjects(),

    // Cache
    clearCache: () => cacheManager.clear(),

    // Initialization
    async refreshAll() {
      logger.log('Refreshing all data...');
      cacheManager.clear();
      await this.init();
    },

    async init() {
      logger.log('Initializing AppData integration...');

      try {
        // Check backend availability
        const info = await api.checkAvailability();
        if (info) {
          cache.appDataInfo = info;
          logger.log('Backend is available');

          // Enhance menus
          themeIntegration.enhanceThemeMenu();
          layoutIntegration.enhanceLayoutMenu();
          extensionIntegration.mergeWithExisting();
          projectIntegration.notifyProjectsLoaded();
        } else {
          logger.log('Backend is not available - using fallback mode');
        }
      } catch (error) {
        logger.error('Initialization error:', error);
      }

      // Dispatch ready event
      document.dispatchEvent(new CustomEvent('appDataIntegrationReady'));
      logger.log('AppData integration ready');
    }
  };

  // Expose public API
  window.appDataIntegration = appDataIntegration;

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => appDataIntegration.init());
  } else {
    appDataIntegration.init();
  }

  logger.log('AppData integration module loaded');
})();