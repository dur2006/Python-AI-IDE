/**
 * Extension Module - Handles extension management
 */

const ExtensionModule = (() => {
    let installed = [];
    let available = [];

    const init = () => {
        console.log('[ExtensionModule] Initializing...');
        fetch();
    };

    const fetch = async () => {
        try {
            const data = await APIModule.get('/extensions');
            installed = data.installed || [];
            available = data.available || [];
            console.log(`[ExtensionModule] Loaded ${installed.length} installed, ${available.length} available`);
        } catch (error) {
            console.error('[ExtensionModule] Failed to fetch extensions:', error);
        }
    };

    const install = async (extId) => {
        try {
            UIModule.setLoading(`install-btn-${extId}`, true);
            await APIModule.post(`/extensions/${extId}/install`);
            await fetch();
            renderAvailable();
            UIModule.showNotification('Extension installed successfully', 'success');
        } catch (error) {
            console.error('[ExtensionModule] Failed to install extension:', error);
            UIModule.showNotification('Failed to install extension', 'error');
        } finally {
            UIModule.setLoading(`install-btn-${extId}`, false);
        }
    };

    const uninstall = async (extId) => {
        try {
            UIModule.setLoading(`uninstall-btn-${extId}`, true);
            await APIModule.post(`/extensions/${extId}/uninstall`);
            await fetch();
            renderInstalled();
            UIModule.showNotification('Extension uninstalled successfully', 'success');
        } catch (error) {
            console.error('[ExtensionModule] Failed to uninstall extension:', error);
            UIModule.showNotification('Failed to uninstall extension', 'error');
        } finally {
            UIModule.setLoading(`uninstall-btn-${extId}`, false);
        }
    };

    const toggle = async (extId) => {
        try {
            UIModule.setLoading(`toggle-btn-${extId}`, true);
            await APIModule.post(`/extensions/${extId}/toggle`);
            await fetch();
            renderInstalled();
            UIModule.showNotification('Extension toggled successfully', 'success');
        } catch (error) {
            console.error('[ExtensionModule] Failed to toggle extension:', error);
            UIModule.showNotification('Failed to toggle extension', 'error');
        } finally {
            UIModule.setLoading(`toggle-btn-${extId}`, false);
        }
    };

    const renderInstalled = () => {
        const list = document.getElementById('extensionsList');
        if (!list) {
            console.warn('[ExtensionModule] Extensions list not found');
            return;
        }

        list.innerHTML = '';

        if (installed.length === 0) {
            list.innerHTML = '<div style="color: var(--text-secondary); text-align: center; padding: 20px;">No extensions installed</div>';
            return;
        }

        installed.forEach(ext => {
            const item = document.createElement('div');
            item.className = 'extension-item';
            item.innerHTML = `
                <div class="extension-info">
                    <div class="extension-status ${ext.enabled ? '' : 'disabled'}"></div>
                    <div class="extension-details">
                        <div class="extension-name">${ext.name}</div>
                        <div class="extension-version">v${ext.version} • ${ext.enabled ? 'Enabled' : 'Disabled'}</div>
                    </div>
                </div>
                <div class="extension-actions">
                    <button class="extension-btn" id="toggle-btn-${ext.id}" onclick="ExtensionModule.toggle(${ext.id})">
                        ${ext.enabled ? 'Disable' : 'Enable'}
                    </button>
                    <button class="extension-btn danger" id="uninstall-btn-${ext.id}" onclick="ExtensionModule.uninstall(${ext.id})">
                        Uninstall
                    </button>
                </div>
            `;
            list.appendChild(item);
        });
    };

    const renderAvailable = () => {
        const list = document.getElementById('availableExtensionsList');
        if (!list) {
            console.warn('[ExtensionModule] Available extensions list not found');
            return;
        }

        list.innerHTML = '';

        const notInstalled = available.filter(
            avail => !installed.some(inst => inst.id === avail.id)
        );

        if (notInstalled.length === 0) {
            list.innerHTML = '<div style="color: var(--text-secondary); text-align: center; padding: 20px;">All available extensions are already installed!</div>';
            return;
        }

        notInstalled.forEach(ext => {
            const item = document.createElement('div');
            item.className = 'extension-item';
            item.innerHTML = `
                <div class="extension-info">
                    <div class="extension-details">
                        <div class="extension-name">${ext.name}</div>
                        <div class="extension-version">v${ext.version} • ${ext.description}</div>
                    </div>
                </div>
                <div class="extension-actions">
                    <button class="extension-btn install" id="install-btn-${ext.id}" onclick="ExtensionModule.install(${ext.id})">
                        Install
                    </button>
                </div>
            `;
            list.appendChild(item);
        });
    };

    const openManage = () => {
        renderInstalled();
        UIModule.showModal('manageExtensionsModal');
    };

    const openGet = () => {
        renderAvailable();
        UIModule.showModal('getExtensionsModal');
    };

    return {
        init,
        fetch,
        install,
        uninstall,
        toggle,
        renderInstalled,
        renderAvailable,
        openManage,
        openGet,
        installed,
        available
    };
})();
