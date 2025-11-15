/**
 * Theme Manager - Manages IDE themes and appearance
 * Handles theme loading, switching, and customization
 */

class ThemeManager {
    constructor() {
        this.themes = [];
        this.currentTheme = null;
        this.initialized = false;
    }

    /**
     * Initialize the theme manager
     */
    async initialize() {
        if (this.initialized) {
            console.log('[ThemeManager] Already initialized');
            return;
        }

        console.log('[ThemeManager] Initializing...');
        
        try {
            // Load available themes
            await this.loadThemes();
            
            // Load saved theme preference or use default
            const savedTheme = localStorage.getItem('selectedTheme') || 'dark';
            await this.applyTheme(savedTheme);
            
            this.initialized = true;
            console.log('[ThemeManager] Initialized successfully');
        } catch (error) {
            console.error('[ThemeManager] Initialization failed:', error);
            // Apply default theme on error
            this.applyDefaultTheme();
        }
    }

    /**
     * Load available themes from backend
     */
    async loadThemes() {
        try {
            const response = await fetch('/api/themes');
            if (!response.ok) {
                throw new Error(`Failed to load themes: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.themes = data.themes || this.getDefaultThemes();
            
            console.log(`[ThemeManager] Loaded ${this.themes.length} themes`);
            return this.themes;
        } catch (error) {
            console.error('[ThemeManager] Failed to load themes from backend:', error);
            // Use default themes as fallback
            this.themes = this.getDefaultThemes();
            return this.themes;
        }
    }

    /**
     * Get default themes (fallback)
     */
    getDefaultThemes() {
        return [
            {
                id: 'dark',
                name: 'Dark',
                description: 'Default dark theme',
                colors: {
                    background: '#1e1e1e',
                    foreground: '#d4d4d4',
                    accent: '#007acc',
                    sidebar: '#252526',
                    editor: '#1e1e1e',
                    terminal: '#1e1e1e'
                }
            },
            {
                id: 'light',
                name: 'Light',
                description: 'Light theme',
                colors: {
                    background: '#ffffff',
                    foreground: '#000000',
                    accent: '#0066cc',
                    sidebar: '#f3f3f3',
                    editor: '#ffffff',
                    terminal: '#ffffff'
                }
            },
            {
                id: 'monokai',
                name: 'Monokai',
                description: 'Monokai color scheme',
                colors: {
                    background: '#272822',
                    foreground: '#f8f8f2',
                    accent: '#66d9ef',
                    sidebar: '#1e1f1c',
                    editor: '#272822',
                    terminal: '#272822'
                }
            }
        ];
    }

    /**
     * Apply a theme
     */
    async applyTheme(themeId) {
        try {
            const theme = this.themes.find(t => t.id === themeId);
            if (!theme) {
                console.warn(`[ThemeManager] Theme ${themeId} not found, using default`);
                this.applyDefaultTheme();
                return;
            }

            console.log(`[ThemeManager] Applying theme: ${theme.name}`);
            
            // Apply theme colors to CSS variables
            const root = document.documentElement;
            if (theme.colors) {
                Object.entries(theme.colors).forEach(([key, value]) => {
                    root.style.setProperty(`--theme-${key}`, value);
                });
            }

            // Update body class for theme-specific styles
            document.body.className = document.body.className.replace(/theme-\w+/g, '');
            document.body.classList.add(`theme-${themeId}`);

            this.currentTheme = theme;
            
            // Save preference
            localStorage.setItem('selectedTheme', themeId);
            
            console.log(`[ThemeManager] Theme ${theme.name} applied successfully`);
        } catch (error) {
            console.error('[ThemeManager] Failed to apply theme:', error);
            this.applyDefaultTheme();
        }
    }

    /**
     * Apply default theme
     */
    applyDefaultTheme() {
        console.log('[ThemeManager] Applying default dark theme');
        document.body.classList.add('theme-dark');
        this.currentTheme = this.themes.find(t => t.id === 'dark') || this.getDefaultThemes()[0];
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Get all available themes
     */
    getThemes() {
        return this.themes;
    }

    /**
     * Switch to next theme (for quick theme cycling)
     */
    cycleTheme() {
        if (this.themes.length === 0) return;
        
        const currentIndex = this.themes.findIndex(t => t.id === this.currentTheme?.id);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        const nextTheme = this.themes[nextIndex];
        
        this.applyTheme(nextTheme.id);
    }

    /**
     * Show theme selector modal
     */
    showThemeSelector() {
        console.log('[ThemeManager] Opening theme selector');
        
        // Create modal if it doesn't exist
        let modal = document.getElementById('themeSelectorModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'themeSelectorModal';
            modal.className = 'modal';
            document.body.appendChild(modal);
        }

        // Create modal content
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Select Theme</h2>
                    <button class="modal-close" onclick="document.getElementById('themeSelectorModal').style.display='none'">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="theme-grid">
                        ${this.renderThemeGrid()}
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
    }

    /**
     * Render theme grid HTML
     */
    renderThemeGrid() {
        return this.themes.map(theme => `
            <div class="theme-card ${theme.id === this.currentTheme?.id ? 'active' : ''}" 
                 onclick="window.themeManager.applyTheme('${theme.id}'); document.getElementById('themeSelectorModal').style.display='none'">
                <div class="theme-preview" style="background: ${theme.colors?.background || '#1e1e1e'}">
                    <div class="theme-preview-sidebar" style="background: ${theme.colors?.sidebar || '#252526'}"></div>
                    <div class="theme-preview-editor" style="background: ${theme.colors?.editor || '#1e1e1e'}; color: ${theme.colors?.foreground || '#d4d4d4'}">
                        <div class="theme-preview-line" style="color: ${theme.colors?.accent || '#007acc'}">function</div>
                        <div class="theme-preview-line">code</div>
                    </div>
                </div>
                <div class="theme-info">
                    <h3>${theme.name}</h3>
                    <p>${theme.description || ''}</p>
                </div>
                ${theme.id === this.currentTheme?.id ? '<div class="theme-active-badge">✓ Active</div>' : ''}
            </div>
        `).join('');
    }

    /**
     * Create custom theme
     */
    async createCustomTheme(themeData) {
        try {
            const response = await fetch('/api/themes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(themeData)
            });

            if (!response.ok) {
                throw new Error(`Failed to create theme: ${response.statusText}`);
            }

            await this.loadThemes();
            console.log(`[ThemeManager] Custom theme created: ${themeData.name}`);
        } catch (error) {
            console.error('[ThemeManager] Failed to create custom theme:', error);
            throw error;
        }
    }

    /**
     * Delete custom theme
     */
    async deleteTheme(themeId) {
        try {
            const response = await fetch(`/api/themes/${themeId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`Failed to delete theme: ${response.statusText}`);
            }

            this.themes = this.themes.filter(t => t.id !== themeId);
            
            // If deleted theme was active, switch to default
            if (this.currentTheme?.id === themeId) {
                this.applyTheme('dark');
            }
            
            console.log(`[ThemeManager] Theme ${themeId} deleted`);
        } catch (error) {
            console.error('[ThemeManager] Failed to delete theme:', error);
            throw error;
        }
    }

    /**
     * Export current theme
     */
    exportTheme() {
        if (!this.currentTheme) {
            console.warn('[ThemeManager] No theme to export');
            return;
        }

        const themeJson = JSON.stringify(this.currentTheme, null, 2);
        const blob = new Blob([themeJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentTheme.id}-theme.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        console.log(`[ThemeManager] Theme exported: ${this.currentTheme.name}`);
    }

    /**
     * Import theme from file
     */
    async importTheme(file) {
        try {
            const text = await file.text();
            const themeData = JSON.parse(text);
            
            await this.createCustomTheme(themeData);
            console.log(`[ThemeManager] Theme imported: ${themeData.name}`);
        } catch (error) {
            console.error('[ThemeManager] Failed to import theme:', error);
            throw error;
        }
    }
}

// Create global instance
window.themeManager = new ThemeManager();

console.log('[ThemeManager] Module loaded');
