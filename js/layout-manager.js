/**
 * Layout Manager Module
 * Manages window layouts, panel visibility, and resizing functionality
 */

const LayoutManager = (function() {
    'use strict';

    // Layout state
    const state = {
        currentLayout: 'default',
        panels: {
            sidebar: { visible: true, width: 250, minWidth: 200, maxWidth: 500 },
            editorArea: { visible: true, flex: 1 },
            terminal: { visible: true, height: 250, minHeight: 150, maxHeight: 500 },
            aiPanel: { visible: true, width: 380, minWidth: 300, maxWidth: 600 }
        },
        isResizing: false,
        resizingPanel: null,
        initialized: false
    };

    // Predefined layouts
    const layouts = {
        default: {
            name: 'Default',
            description: 'Standard IDE layout with all panels visible',
            panels: {
                sidebar: { visible: true, width: 250 },
                editorArea: { visible: true },
                terminal: { visible: true, height: 250 },
                aiPanel: { visible: true, width: 380 }
            }
        },
        focus: {
            name: 'Focus Mode',
            description: 'Editor only - minimize distractions',
            panels: {
                sidebar: { visible: false },
                editorArea: { visible: true },
                terminal: { visible: false },
                aiPanel: { visible: false }
            }
        },
        coding: {
            name: 'Coding',
            description: 'Editor with sidebar and terminal',
            panels: {
                sidebar: { visible: true, width: 250 },
                editorArea: { visible: true },
                terminal: { visible: true, height: 250 },
                aiPanel: { visible: false }
            }
        },
        debugging: {
            name: 'Debugging',
            description: 'Full layout with larger terminal',
            panels: {
                sidebar: { visible: true, width: 250 },
                editorArea: { visible: true },
                terminal: { visible: true, height: 350 },
                aiPanel: { visible: true, width: 380 }
            }
        },
        aiAssist: {
            name: 'AI Assist',
            description: 'Editor with AI panel, no terminal',
            panels: {
                sidebar: { visible: true, width: 250 },
                editorArea: { visible: true },
                terminal: { visible: false },
                aiPanel: { visible: true, width: 450 }
            }
        },
        minimal: {
            name: 'Minimal',
            description: 'Editor and terminal only',
            panels: {
                sidebar: { visible: false },
                editorArea: { visible: true },
                terminal: { visible: true, height: 200 },
                aiPanel: { visible: false }
            }
        }
    };

    /**
     * Initialize the layout manager
     */
    function init() {
        if (state.initialized) {
            console.log('[LayoutManager] Already initialized, skipping');
            return;
        }

        console.log('[LayoutManager] Initializing...');
        
        // Load saved layout from localStorage
        loadLayoutFromStorage();
        
        // Apply current layout
        applyLayout(state.currentLayout, false);
        
        // Setup resize handlers
        setupResizeHandlers();
        
        // Setup window resize listener
        window.addEventListener('resize', handleWindowResize);
        
        state.initialized = true;
        console.log('[LayoutManager] Initialized successfully');
    }

    /**
     * Apply a layout by name
     */
    function applyLayout(layoutName, shouldSave = true) {
        console.log('[LayoutManager] Applying layout:', layoutName);
        
        const layout = layouts[layoutName];
        if (!layout) {
            console.error('[LayoutManager] Layout not found:', layoutName);
            return false;
        }

        // Update state
        state.currentLayout = layoutName;
        
        // Apply panel configurations
        Object.keys(layout.panels).forEach(panelName => {
            const panelConfig = layout.panels[panelName];
            state.panels[panelName] = { ...state.panels[panelName], ...panelConfig };
        });

        // Update DOM
        updatePanelVisibility();
        updatePanelSizes();
        
        // Save to localStorage
        if (shouldSave) {
            saveLayoutToStorage();
        }
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('layoutChanged', { 
            detail: { layout: layoutName } 
        }));
        
        console.log('[LayoutManager] Layout applied:', layoutName);
        return true;
    }

    /**
     * Toggle panel visibility
     */
    function togglePanel(panelName) {
        console.log('[LayoutManager] Toggling panel:', panelName);
        
        if (!state.panels[panelName]) {
            console.error('[LayoutManager] Panel not found:', panelName);
            return false;
        }

        state.panels[panelName].visible = !state.panels[panelName].visible;
        updatePanelVisibility();
        saveLayoutToStorage();
        
        // Dispatch event
        window.dispatchEvent(new CustomEvent('panelToggled', { 
            detail: { panel: panelName, visible: state.panels[panelName].visible } 
        }));
        
        return state.panels[panelName].visible;
    }

    /**
     * Update panel visibility in DOM
     */
    function updatePanelVisibility() {
        // Sidebar
        const sidebar = document.querySelector('.sidebar');
        const sidebarResizer = document.getElementById('sidebarResizer');
        if (sidebar) {
            sidebar.style.display = state.panels.sidebar.visible ? 'flex' : 'none';
        }
        if (sidebarResizer) {
            sidebarResizer.style.display = state.panels.sidebar.visible ? 'block' : 'none';
        }

        // Editor Area
        const editorArea = document.getElementById('editorArea');
        if (editorArea) {
            editorArea.style.display = state.panels.editorArea.visible ? 'flex' : 'none';
        }

        // Terminal
        const terminal = document.getElementById('terminalSection');
        const terminalResizer = document.getElementById('terminalResizer');
        if (terminal) {
            terminal.style.display = state.panels.terminal.visible ? 'flex' : 'none';
        }
        if (terminalResizer) {
            terminalResizer.style.display = state.panels.terminal.visible ? 'block' : 'none';
        }

        // AI Panel
        const aiPanel = document.querySelector('.ai-panel');
        const aiPanelResizer = document.getElementById('aiPanelResizer');
        if (aiPanel) {
            aiPanel.style.display = state.panels.aiPanel.visible ? 'flex' : 'none';
        }
        if (aiPanelResizer) {
            aiPanelResizer.style.display = state.panels.aiPanel.visible ? 'block' : 'none';
        }
    }

    /**
     * Update panel sizes in DOM
     */
    function updatePanelSizes() {
        // Sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && state.panels.sidebar.visible) {
            sidebar.style.width = state.panels.sidebar.width + 'px';
        }

        // Terminal
        const terminal = document.getElementById('terminalSection');
        if (terminal && state.panels.terminal.visible) {
            terminal.style.height = state.panels.terminal.height + 'px';
        }

        // AI Panel
        const aiPanel = document.querySelector('.ai-panel');
        if (aiPanel && state.panels.aiPanel.visible) {
            aiPanel.style.width = state.panels.aiPanel.width + 'px';
        }
    }

    /**
     * Setup resize handlers for panels
     */
    function setupResizeHandlers() {
        console.log('[LayoutManager] Setting up resize handlers...');

        // Sidebar resizer (use existing HTML element)
        const sidebarResizer = document.getElementById('sidebarResizer');
        if (sidebarResizer) {
            sidebarResizer.addEventListener('mousedown', (e) => {
                e.preventDefault();
                state.isResizing = true;
                state.resizingPanel = 'sidebar';
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                console.log('[LayoutManager] Started resizing sidebar');
            });
        } else {
            console.warn('[LayoutManager] Sidebar resizer not found in HTML');
        }

        // Terminal resizer (use existing HTML element)
        const terminalResizer = document.getElementById('terminalResizer');
        if (terminalResizer) {
            terminalResizer.addEventListener('mousedown', (e) => {
                e.preventDefault();
                state.isResizing = true;
                state.resizingPanel = 'terminal';
                document.body.style.cursor = 'ns-resize';
                document.body.style.userSelect = 'none';
                console.log('[LayoutManager] Started resizing terminal');
            });
        } else {
            console.warn('[LayoutManager] Terminal resizer not found in HTML');
        }

        // AI Panel resizer (use existing HTML element)
        const aiPanelResizer = document.getElementById('aiPanelResizer');
        if (aiPanelResizer) {
            aiPanelResizer.addEventListener('mousedown', (e) => {
                e.preventDefault();
                state.isResizing = true;
                state.resizingPanel = 'aiPanel';
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                console.log('[LayoutManager] Started resizing AI panel');
            });
        } else {
            console.warn('[LayoutManager] AI panel resizer not found in HTML');
        }

        // Global mouse handlers
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        console.log('[LayoutManager] Resize handlers setup complete');
    }

    /**
     * Handle mouse move during resize
     */
    function handleMouseMove(e) {
        if (!state.isResizing) return;

        switch (state.resizingPanel) {
            case 'terminal':
                resizeTerminal(e);
                break;
            case 'sidebar':
                resizeSidebar(e);
                break;
            case 'aiPanel':
                resizeAIPanel(e);
                break;
        }
    }

    /**
     * Handle mouse up (end resize)
     */
    function handleMouseUp() {
        if (state.isResizing) {
            console.log('[LayoutManager] Stopped resizing:', state.resizingPanel);
            state.isResizing = false;
            state.resizingPanel = null;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            saveLayoutToStorage();
        }
    }

    /**
     * Resize terminal panel
     */
    function resizeTerminal(e) {
        const terminal = document.getElementById('terminalSection');
        if (!terminal) return;

        const containerRect = terminal.parentElement.getBoundingClientRect();
        const newHeight = containerRect.bottom - e.clientY;
        
        const { minHeight, maxHeight } = state.panels.terminal;
        if (newHeight >= minHeight && newHeight <= maxHeight) {
            state.panels.terminal.height = newHeight;
            terminal.style.height = newHeight + 'px';
        }
    }

    /**
     * Resize sidebar panel
     */
    function resizeSidebar(e) {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        const sidebarRect = sidebar.getBoundingClientRect();
        const newWidth = e.clientX - sidebarRect.left;
        
        const { minWidth, maxWidth } = state.panels.sidebar;
        if (newWidth >= minWidth && newWidth <= maxWidth) {
            state.panels.sidebar.width = newWidth;
            sidebar.style.width = newWidth + 'px';
        }
    }

    /**
     * Resize AI panel
     */
    function resizeAIPanel(e) {
        const aiPanel = document.querySelector('.ai-panel');
        if (!aiPanel) return;

        const panelRect = aiPanel.getBoundingClientRect();
        const newWidth = panelRect.right - e.clientX;
        
        const { minWidth, maxWidth } = state.panels.aiPanel;
        if (newWidth >= minWidth && newWidth <= maxWidth) {
            state.panels.aiPanel.width = newWidth;
            aiPanel.style.width = newWidth + 'px';
        }
    }

    /**
     * Handle window resize
     */
    function handleWindowResize() {
        // Ensure panels stay within bounds
        updatePanelSizes();
    }

    /**
     * Save layout to localStorage
     */
    function saveLayoutToStorage() {
        try {
            const layoutData = {
                currentLayout: state.currentLayout,
                panels: state.panels
            };
            localStorage.setItem('autopilot-layout', JSON.stringify(layoutData));
            console.log('[LayoutManager] Layout saved to storage');
        } catch (error) {
            console.error('[LayoutManager] Error saving layout:', error);
        }
    }

    /**
     * Load layout from localStorage
     */
    function loadLayoutFromStorage() {
        try {
            const saved = localStorage.getItem('autopilot-layout');
            if (saved) {
                const layoutData = JSON.parse(saved);
                state.currentLayout = layoutData.currentLayout || 'default';
                state.panels = { ...state.panels, ...layoutData.panels };
                console.log('[LayoutManager] Layout loaded from storage');
            }
        } catch (error) {
            console.error('[LayoutManager] Error loading layout:', error);
        }
    }

    /**
     * Get available layouts
     */
    function getLayouts() {
        return Object.keys(layouts).map(key => ({
            id: key,
            ...layouts[key]
        }));
    }

    /**
     * Get current layout
     */
    function getCurrentLayout() {
        return state.currentLayout;
    }

    /**
     * Get panel state
     */
    function getPanelState(panelName) {
        return state.panels[panelName];
    }

    /**
     * Get complete state
     */
    function getState() {
        return {
            currentLayout: state.currentLayout,
            sidebar: state.panels.sidebar,
            editorArea: state.panels.editorArea,
            terminal: state.panels.terminal,
            aiPanel: state.panels.aiPanel
        };
    }

    /**
     * Reset to default layout
     */
    function resetLayout() {
        console.log('[LayoutManager] Resetting to default layout');
        applyLayout('default');
    }

    // Public API
    const api = {
        init,
        applyLayout,
        togglePanel,
        getLayouts,
        getCurrentLayout,
        getPanelState,
        getState,
        resetLayout
    };

    // Expose to window for external access
    window.layoutManager = api;

    return api;
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => LayoutManager.init());
} else {
    LayoutManager.init();
}
