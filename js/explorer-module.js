/**
 * Explorer Module - Handles file explorer operations
 */

const ExplorerModule = (() => {
    let files = [];

    const init = () => {
        console.log('[ExplorerModule] Initializing...');
        loadFiles();
    };

    const loadFiles = async () => {
        try {
            const data = await APIModule.get('/files');
            files = data.files || [];
            render();
        } catch (error) {
            console.error('[ExplorerModule] Failed to load files:', error);
        }
    };

    const expandFolder = (folderId) => {
        console.log(`[ExplorerModule] Expanded folder: ${folderId}`);
    };

    const selectFile = (filename) => {
        console.log(`[ExplorerModule] Selected file: ${filename}`);
        EditorModule.openFile(filename);
    };

    const render = () => {
        console.log('[ExplorerModule] Rendering file tree');
    };

    return {
        init,
        loadFiles,
        expandFolder,
        selectFile,
        render,
        files
    };
})();
