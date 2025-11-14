/**
 * Editor Module - Handles code editor operations
 */

const EditorModule = (() => {
    let files = {};
    let currentFile = null;

    const init = () => {
        console.log('[EditorModule] Initializing...');
        // Initialize editor functionality
    };

    const openFile = (filename) => {
        currentFile = filename;
        console.log(`[EditorModule] Opened file: ${filename}`);
    };

    const closeFile = (filename) => {
        if (currentFile === filename) {
            currentFile = null;
        }
        delete files[filename];
        console.log(`[EditorModule] Closed file: ${filename}`);
    };

    const saveFile = (filename, content) => {
        files[filename] = content;
        console.log(`[EditorModule] Saved file: ${filename}`);
    };

    const getContent = (filename) => {
        return files[filename] || '';
    };

    return {
        init,
        openFile,
        closeFile,
        saveFile,
        getContent,
        files,
        currentFile
    };
})();
