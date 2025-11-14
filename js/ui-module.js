/**
 * UI Module - Handles UI interactions and updates
 */

const UIModule = (() => {
    const modals = {};
    let notificationTimeout = null;

    const init = () => {
        console.log('[UIModule] Initializing...');
        
        // Register modals
        const modalIds = ['manageExtensionsModal', 'getExtensionsModal'];
        modalIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                modals[id] = el;
            } else {
                console.warn(`[UIModule] Modal not found: ${id}`);
            }
        });
    };

    const showModal = (modalId) => {
        const modal = modals[modalId] || document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            console.log(`[UIModule] Showing modal: ${modalId}`);
        } else {
            console.warn(`[UIModule] Modal not found: ${modalId}`);
        }
    };

    const hideModal = (modalId) => {
        const modal = modals[modalId] || document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            console.log(`[UIModule] Hiding modal: ${modalId}`);
        } else {
            console.warn(`[UIModule] Modal not found: ${modalId}`);
        }
    };

    const showNotification = (message, type = 'info') => {
        clearTimeout(notificationTimeout);
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#f48771' : type === 'success' ? '#89d185' : '#667eea'};
            color: white;
            border-radius: 6px;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        notificationTimeout = setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };

    const updateStatus = (message, type = 'info') => {
        const statusLeft = document.querySelector('.status-left');
        if (statusLeft) {
            const statusItem = statusLeft.querySelector('.status-item');
            if (statusItem) {
                statusItem.textContent = `🌐 ${message}`;
                statusItem.style.color = type === 'error' ? '#f48771' : type === 'success' ? '#89d185' : '#d4d4d4';
            }
        }
    };

    const toggleDropdown = (menuId, event) => {
        if (event) event.stopPropagation();
        
        const menu = document.getElementById(menuId);
        if (!menu) {
            console.warn(`[UIModule] Dropdown menu not found: ${menuId}`);
            return;
        }

        // Close other dropdowns
        document.querySelectorAll('.dropdown-menu.show').forEach(m => {
            if (m.id !== menuId) {
                m.classList.remove('show');
            }
        });

        menu.classList.toggle('show');
    };

    const closeAllDropdowns = () => {
        document.querySelectorAll('.dropdown-menu.show').forEach(m => {
            m.classList.remove('show');
        });
    };

    const setLoading = (elementId, isLoading) => {
        const el = document.getElementById(elementId);
        if (el) {
            if (isLoading) {
                el.disabled = true;
                el.style.opacity = '0.6';
            } else {
                el.disabled = false;
                el.style.opacity = '1';
            }
        }
    };

    return {
        init,
        showModal,
        hideModal,
        showNotification,
        updateStatus,
        toggleDropdown,
        closeAllDropdowns,
        setLoading,
        modals
    };
})();
