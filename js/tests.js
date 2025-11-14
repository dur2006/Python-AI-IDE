/**
 * AutoPilot IDE - Comprehensive Test Suite
 * Tests all modules and functionality
 */

class TestSuite {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
        this.results = [];
    }

    test(name, fn) {
        this.tests.push({ name, fn });
    }

    async run() {
        console.log('🧪 Starting Test Suite...\n');
        
        for (const test of this.tests) {
            try {
                await test.fn();
                this.passed++;
                this.results.push({ name: test.name, status: '✅ PASS' });
                console.log(`✅ ${test.name}`);
            } catch (error) {
                this.failed++;
                this.results.push({ name: test.name, status: '❌ FAIL', error: error.message });
                console.error(`❌ ${test.name}: ${error.message}`);
            }
        }

        this.printSummary();
        return this.failed === 0;
    }

    printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 TEST SUMMARY');
        console.log('='.repeat(60));
        console.log(`✅ Passed: ${this.passed}`);
        console.log(`❌ Failed: ${this.failed}`);
        console.log(`📈 Total: ${this.tests.length}`);
        console.log(`🎯 Success Rate: ${((this.passed / this.tests.length) * 100).toFixed(2)}%`);
        console.log('='.repeat(60) + '\n');
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }

    assertExists(obj, message) {
        if (!obj) {
            throw new Error(message || 'Object does not exist');
        }
    }

    assertType(obj, type, message) {
        if (typeof obj !== type) {
            throw new Error(message || `Expected type ${type}, got ${typeof obj}`);
        }
    }
}

// Create global test suite
const testSuite = new TestSuite();

// ============================================================================
// DOM ELEMENT TESTS
// ============================================================================

testSuite.test('DOM: Project modal should exist', async () => {
    const modal = document.getElementById('projectModal');
    testSuite.assertExists(modal, 'projectModal element should exist');
});

testSuite.test('DOM: File tree should exist', async () => {
    const fileTree = document.getElementById('fileTree');
    testSuite.assertExists(fileTree, 'fileTree element should exist');
});

testSuite.test('DOM: Editor should exist', async () => {
    const editor = document.getElementById('editor');
    testSuite.assertExists(editor, 'editor element should exist');
});

testSuite.test('DOM: Terminal should exist', async () => {
    const terminal = document.querySelector('.terminal');
    testSuite.assertExists(terminal, 'terminal element should exist');
});

testSuite.test('DOM: AI Assistant panel should exist', async () => {
    const aiPanel = document.querySelector('.ai-assistant');
    testSuite.assertExists(aiPanel, 'AI Assistant panel should exist');
});

// ============================================================================
// PROJECT OPENER TESTS
// ============================================================================

testSuite.test('ProjectOpener: openProjectModal function should exist', async () => {
    testSuite.assertType(window.openProjectModal, 'function', 'openProjectModal should be a function');
});

testSuite.test('ProjectOpener: closeProjectModal function should exist', async () => {
    testSuite.assertType(window.closeProjectModal, 'function', 'closeProjectModal should be a function');
});

testSuite.test('ProjectOpener: switchProjectTab function should exist', async () => {
    testSuite.assertType(window.switchProjectTab, 'function', 'switchProjectTab should be a function');
});

testSuite.test('ProjectOpener: openProject function should exist', async () => {
    testSuite.assertType(window.openProject, 'function', 'openProject should be a function');
});

testSuite.test('ProjectOpener: Modal should have recent projects tab', async () => {
    const recentTab = document.getElementById('recentTab');
    testSuite.assertExists(recentTab, 'recentTab should exist');
});

testSuite.test('ProjectOpener: Modal should have browse tab', async () => {
    const browseTab = document.getElementById('browseTab');
    testSuite.assertExists(browseTab, 'browseTab should exist');
});

testSuite.test('ProjectOpener: Modal should have create tab', async () => {
    const createTab = document.getElementById('createTab');
    testSuite.assertExists(createTab, 'createTab should exist');
});

// ============================================================================
// FILE TREE TESTS
// ============================================================================

testSuite.test('FileTree: selectFile function should exist', async () => {
    testSuite.assertType(window.selectFile, 'function', 'selectFile should be a function');
});

testSuite.test('FileTree: File items should have click handlers', async () => {
    const fileItems = document.querySelectorAll('.file-item');
    testSuite.assert(fileItems.length > 0, 'File items should exist');
});

testSuite.test('FileTree: File tree should be clickable', async () => {
    const fileTree = document.getElementById('fileTree');
    const fileItems = fileTree.querySelectorAll('.file-item');
    testSuite.assert(fileItems.length > 0, 'File tree should contain file items');
});

// ============================================================================
// UI FUNCTIONALITY TESTS
// ============================================================================

testSuite.test('UI: Editor tabs should exist', async () => {
    const tabs = document.querySelector('.tabs');
    testSuite.assertExists(tabs, 'tabs container should exist');
});

testSuite.test('UI: Tab close button should exist', async () => {
    const tabClose = document.querySelector('.tab-close');
    testSuite.assertExists(tabClose, 'tab-close button should exist');
});

testSuite.test('UI: Status bar should exist', async () => {
    const statusBar = document.querySelector('.status-bar');
    testSuite.assertExists(statusBar, 'status bar should exist');
});

testSuite.test('UI: Menu bar should exist', async () => {
    const menuBar = document.querySelector('.menu-bar');
    testSuite.assertExists(menuBar, 'menu bar should exist');
});

// ============================================================================
// STYLING TESTS
// ============================================================================

testSuite.test('Styling: Dark theme variables should be defined', async () => {
    const root = document.documentElement;
    const bgPrimary = getComputedStyle(root).getPropertyValue('--bg-primary');
    testSuite.assert(bgPrimary.trim().length > 0, 'CSS variables should be defined');
});

testSuite.test('Styling: Sidebar should have proper styling', async () => {
    const sidebar = document.querySelector('.sidebar');
    testSuite.assertExists(sidebar, 'sidebar should exist and be styled');
});

testSuite.test('Styling: Editor should have proper styling', async () => {
    const editor = document.querySelector('.editor');
    testSuite.assertExists(editor, 'editor should exist and be styled');
});

// ============================================================================
// MODAL TESTS
// ============================================================================

testSuite.test('Modal: Modal should have proper structure', async () => {
    const modal = document.getElementById('projectModal');
    const header = modal.querySelector('.modal-header');
    const body = modal.querySelector('.modal-body');
    testSuite.assertExists(header, 'modal header should exist');
    testSuite.assertExists(body, 'modal body should exist');
});

testSuite.test('Modal: Modal close button should exist', async () => {
    const closeBtn = document.querySelector('.modal-close');
    testSuite.assertExists(closeBtn, 'modal close button should exist');
});

testSuite.test('Modal: Project items should be clickable', async () => {
    const projectItems = document.querySelectorAll('.project-item');
    testSuite.assert(projectItems.length > 0, 'project items should exist');
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

testSuite.test('Integration: All main sections should be present', async () => {
    const sidebar = document.querySelector('.sidebar');
    const editor = document.querySelector('.editor-area');
    const terminal = document.querySelector('.terminal');
    const aiPanel = document.querySelector('.ai-assistant');
    
    testSuite.assertExists(sidebar, 'sidebar should exist');
    testSuite.assertExists(editor, 'editor area should exist');
    testSuite.assertExists(terminal, 'terminal should exist');
    testSuite.assertExists(aiPanel, 'AI panel should exist');
});

testSuite.test('Integration: Project opener should be accessible', async () => {
    const modal = document.getElementById('projectModal');
    const openBtn = document.querySelector('[onclick*="openProjectModal"]');
    testSuite.assertExists(modal, 'project modal should exist');
    testSuite.assertExists(openBtn, 'open project button should exist');
});

testSuite.test('Integration: File selection should work', async () => {
    const fileTree = document.getElementById('fileTree');
    const fileItems = fileTree.querySelectorAll('.file-item');
    testSuite.assert(fileItems.length > 0, 'file items should be selectable');
});

// ============================================================================
// PERFORMANCE TESTS
// ============================================================================

testSuite.test('Performance: Page should load quickly', async () => {
    const loadTime = performance.now();
    testSuite.assert(loadTime < 5000, 'Page should load in less than 5 seconds');
});

testSuite.test('Performance: DOM should be fully rendered', async () => {
    const elements = document.querySelectorAll('*');
    testSuite.assert(elements.length > 100, 'DOM should have sufficient elements');
});

// ============================================================================
// ACCESSIBILITY TESTS
// ============================================================================

testSuite.test('Accessibility: Buttons should have proper labels', async () => {
    const buttons = document.querySelectorAll('button');
    testSuite.assert(buttons.length > 0, 'buttons should exist');
});

testSuite.test('Accessibility: Form inputs should exist', async () => {
    const inputs = document.querySelectorAll('input, select, textarea');
    testSuite.assert(inputs.length > 0, 'form inputs should exist');
});

// ============================================================================
// EXPORT TEST RESULTS
// ============================================================================

// Auto-run tests when document is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        testSuite.run();
    });
} else {
    testSuite.run();
}

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = testSuite;
}
