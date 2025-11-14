/**
 * Layout Fixes Script
 * Patches remaining bugs in index.html without modifying the entire file
 */

(function() {
    'use strict';

    console.log('[LayoutFixes] Applying patches...');

    // Fix 1: Update Window Menu onclick handlers to use correct panel IDs
    function fixWindowMenuHandlers() {
        const windowMenu = document.getElementById('windowMenu');
        if (!windowMenu) return;

        const dropdownItems = windowMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item, index) => {
            const span = item.querySelector('span');
            if (!span) return;

            const text = span.textContent.trim();
            
            // Remove old onclick and add new one with correct panel ID and stopPropagation
            item.removeAttribute('onclick');
            
            item.addEventListener('click', function(event) {
                event.stopPropagation(); // Prevent dropdown from closing
                
                let panelName;
                switch(text) {
                    case 'Explorer':
                        panelName = 'sidebar';
                        break;
                    case 'Editor':
                        panelName = 'editorArea'; // Fixed from 'editor'
                        break;
                    case 'Terminal':
                        panelName = 'terminal';
                        break;
                    case 'AI Assistant':
                        panelName = 'aiPanel';
                        break;
                }
                
                if (panelName && window.layoutManager) {
                    window.layoutManager.togglePanel(panelName);
                    updateWindowMenuCheckmarks();
                }
            });
        });
        
        console.log('[LayoutFixes] Fixed window menu handlers');
    }

    // Fix 2: Update checkmark function to use correct panel names
    function updateWindowMenuCheckmarks() {
        if (!window.layoutManager) return;
        
        const state = window.layoutManager.getState();
        
        // Fixed: Use editorArea instead of editor
        const explorerCheck = document.getElementById('explorerCheck');
        const editorCheck = document.getElementById('editorCheck');
        const terminalCheck = document.getElementById('terminalCheck');
        const aiPanelCheck = document.getElementById('aiPanelCheck');
        
        if (explorerCheck) explorerCheck.style.display = state.sidebar.visible ? 'inline' : 'none';
        if (editorCheck) editorCheck.style.display = state.editorArea.visible ? 'inline' : 'none';
        if (terminalCheck) terminalCheck.style.display = state.terminal.visible ? 'inline' : 'none';
        if (aiPanelCheck) aiPanelCheck.style.display = state.aiPanel.visible ? 'inline' : 'none';
    }

    // Fix 3: Add active layout indicators
    function updateLayoutMenuIndicators() {
        if (!window.layoutManager) return;
        
        const currentLayout = window.layoutManager.getCurrentLayout();
        const layoutsMenu = document.getElementById('layoutsMenu');
        if (!layoutsMenu) return;

        const dropdownItems = layoutsMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            // Remove existing checkmarks
            let checkmark = item.querySelector('.dropdown-item-check');
            if (checkmark) {
                checkmark.remove();
            }

            // Get layout name from onclick attribute
            const onclick = item.getAttribute('onclick');
            if (!onclick) return;

            const match = onclick.match(/applyLayout\('([^']+)'\)/);
            if (!match) return;

            const layoutName = match[1];

            // Add checkmark if this is the current layout
            if (layoutName === currentLayout) {
                checkmark = document.createElement('span');
                checkmark.className = 'dropdown-item-check';
                checkmark.textContent = '✓';
                item.appendChild(checkmark);
            }
        });
    }

    // Fix 4: Add smooth transitions to panels
    function addPanelTransitions() {
        const style = document.createElement('style');
        style.textContent = `
            #sidebar, #editorArea, #terminalSection, #aiPanel {
                transition: opacity 0.3s ease-out, transform 0.3s ease-out;
            }
            
            #sidebar.hidden, #editorArea.hidden, #terminalSection.hidden, #aiPanel.hidden {
                opacity: 0;
                transform: scale(0.98);
            }
            
            #sidebarResizer, #terminalResizer, #aiPanelResizer {
                transition: opacity 0.2s ease-out;
            }
        `;
        document.head.appendChild(style);
        console.log('[LayoutFixes] Added panel transitions');
    }

    // Fix 5: Enhance layout menu with stopPropagation
    function fixLayoutMenuHandlers() {
        const layoutsMenu = document.getElementById('layoutsMenu');
        if (!layoutsMenu) return;

        const dropdownItems = layoutsMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            const onclick = item.getAttribute('onclick');
            if (!onclick) return;

            const match = onclick.match(/applyLayout\('([^']+)'\)/);
            if (!match) return;

            const layoutName = match[1];

            // Remove old onclick and add new one with stopPropagation
            item.removeAttribute('onclick');
            
            item.addEventListener('click', function(event) {
                event.stopPropagation();
                
                if (window.layoutManager) {
                    window.layoutManager.applyLayout(layoutName);
                    updateLayoutMenuIndicators();
                    updateWindowMenuCheckmarks();
                }
            });
        });
        
        console.log('[LayoutFixes] Fixed layout menu handlers');
    }

    // Override the global updateWindowMenuCheckmarks function
    window.updateWindowMenuCheckmarks = updateWindowMenuCheckmarks;

    // Initialize fixes when DOM is ready
    function initFixes() {
        console.log('[LayoutFixes] Initializing fixes...');
        
        fixWindowMenuHandlers();
        fixLayoutMenuHandlers();
        addPanelTransitions();
        
        // Update indicators after a short delay to ensure layoutManager is ready
        setTimeout(() => {
            updateWindowMenuCheckmarks();
            updateLayoutMenuIndicators();
        }, 200);

        // Listen for layout changes
        window.addEventListener('layoutChanged', () => {
            updateLayoutMenuIndicators();
            updateWindowMenuCheckmarks();
        });

        window.addEventListener('panelToggled', () => {
            updateWindowMenuCheckmarks();
        });

        console.log('[LayoutFixes] All fixes applied successfully!');
    }

    // Run fixes when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFixes);
    } else {
        initFixes();
    }

})();
