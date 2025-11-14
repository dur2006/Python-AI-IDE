/**
 * AutoPilot IDE - Project Manager Module
 * Handles project creation, loading, switching, and persistence
 */

class ProjectManager {
    constructor() {
        this.projects = [];
        this.currentProject = null;
        this.storageKey = 'autopilot_projects';
        this.currentProjectKey = 'autopilot_current_project';
        this.init();
    }

    init() {
        console.log('[ProjectManager] Initializing...');
        this.loadProjects();
        this.loadCurrentProject();
        
        if (!this.currentProject && this.projects.length > 0) {
            this.setCurrentProject(this.projects[0].id);
        }
        
        if (!this.currentProject) {
            this.createDefaultProjects();
        }
    }

    createDefaultProjects() {
        console.log('[ProjectManager] Creating default projects...');
        
        const defaultProjects = [
            {
                id: 'autopilot-project-1',
                name: 'AutoPilot-Project',
                path: '/home/user/projects/AutoPilot-Project',
                type: 'Python',
                createdAt: new Date(Date.now() - 0 * 24 * 60 * 60 * 1000).toISOString(),
                lastOpened: new Date().toISOString(),
                files: [
                    { name: 'main.py', type: 'file', icon: '📄' },
                    { name: 'config.json', type: 'file', icon: '📄' },
                    { name: 'README.md', type: 'file', icon: '📄' }
                ]
            },
            {
                id: 'webapp-demo-1',
                name: 'WebApp-Demo',
                path: '/home/user/projects/WebApp-Demo',
                type: 'JavaScript',
                createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                lastOpened: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                files: [
                    { name: 'index.html', type: 'file', icon: '🌐' },
                    { name: 'style.css', type: 'file', icon: '🎨' },
                    { name: 'app.js', type: 'file', icon: '📄' }
                ]
            },
            {
                id: 'python-utils-1',
                name: 'Python-Utils',
                path: '/home/user/projects/Python-Utils',
                type: 'Python',
                createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                lastOpened: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                files: [
                    { name: 'utils.py', type: 'file', icon: '📄' },
                    { name: 'helpers.py', type: 'file', icon: '📄' },
                    { name: 'tests.py', type: 'file', icon: '📄' }
                ]
            }
        ];

        this.projects = defaultProjects;
        this.saveProjects();
        this.setCurrentProject(defaultProjects[0].id);
    }

    saveProjects() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.projects));
            console.log('[ProjectManager] Projects saved to localStorage');
        } catch (error) {
            console.error('[ProjectManager] Error saving projects:', error);
        }
    }

    loadProjects() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                this.projects = JSON.parse(stored);
                console.log('[ProjectManager] Loaded', this.projects.length, 'projects from localStorage');
            }
        } catch (error) {
            console.error('[ProjectManager] Error loading projects:', error);
            this.projects = [];
        }
    }

    loadCurrentProject() {
        try {
            const projectId = localStorage.getItem(this.currentProjectKey);
            if (projectId) {
                const project = this.projects.find(p => p.id === projectId);
                if (project) {
                    this.currentProject = project;
                    console.log('[ProjectManager] Loaded current project:', project.name);
                }
            }
        } catch (error) {
            console.error('[ProjectManager] Error loading current project:', error);
        }
    }

    setCurrentProject(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        if (project) {
            this.currentProject = project;
            project.lastOpened = new Date().toISOString();
            this.saveProjects();
            localStorage.setItem(this.currentProjectKey, projectId);
            console.log('[ProjectManager] Current project set to:', project.name);
            return true;
        }
        return false;
    }

    getCurrentProject() {
        return this.currentProject;
    }

    getRecentProjects(limit = 10) {
        return this.projects
            .sort((a, b) => new Date(b.lastOpened) - new Date(a.lastOpened))
            .slice(0, limit);
    }

    createProject(name, type, path) {
        const id = `project-${Date.now()}`;
        const project = {
            id,
            name,
            type,
            path: path || `/home/user/projects/${name}`,
            createdAt: new Date().toISOString(),
            lastOpened: new Date().toISOString(),
            files: this.getDefaultFilesForType(type)
        };

        this.projects.push(project);
        this.saveProjects();
        this.setCurrentProject(id);
        console.log('[ProjectManager] Project created:', name);
        return project;
    }

    getDefaultFilesForType(type) {
        const fileMap = {
            'Python': [
                { name: 'main.py', type: 'file', icon: '📄' },
                { name: 'config.py', type: 'file', icon: '📄' },
                { name: 'README.md', type: 'file', icon: '📄' }
            ],
            'JavaScript': [
                { name: 'index.js', type: 'file', icon: '📄' },
                { name: 'package.json', type: 'file', icon: '📦' },
                { name: 'README.md', type: 'file', icon: '📄' }
            ],
            'Web App': [
                { name: 'index.html', type: 'file', icon: '🌐' },
                { name: 'style.css', type: 'file', icon: '🎨' },
                { name: 'script.js', type: 'file', icon: '📄' }
            ],
            'Empty': []
        };

        return fileMap[type] || [];
    }

    deleteProject(projectId) {
        const index = this.projects.findIndex(p => p.id === projectId);
        if (index !== -1) {
            const project = this.projects[index];
            this.projects.splice(index, 1);
            this.saveProjects();
            
            if (this.currentProject?.id === projectId) {
                this.setCurrentProject(this.projects[0]?.id || null);
            }
            
            console.log('[ProjectManager] Project deleted:', project.name);
            return true;
        }
        return false;
    }

    getProjectFiles(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        return project ? project.files : [];
    }

    formatDate(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Opened today';
        if (diffDays === 1) return 'Opened yesterday';
        if (diffDays < 7) return `Opened ${diffDays} days ago`;
        if (diffDays < 30) return `Opened ${Math.floor(diffDays / 7)} weeks ago`;
        return `Opened ${Math.floor(diffDays / 30)} months ago`;
    }
}

// Create global instance
const projectManager = new ProjectManager();
