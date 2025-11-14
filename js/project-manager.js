/**
 * AutoPilot IDE - Project Manager Module
 * Handles project creation, loading, switching, and persistence
 * Integrates with AppData backend when available
 */

class ProjectManager {
    constructor() {
        this.projects = [];
        this.currentProject = null;
        this.storageKey = 'autopilot_projects';
        this.currentProjectKey = 'autopilot_current_project';
        this.backendAvailable = false;
        this.init();
    }

    async init() {
        console.log('[ProjectManager] Initializing...');
        
        // Check if AppData backend is available
        await this.checkBackendAvailability();
        
        if (this.backendAvailable) {
            console.log('[ProjectManager] Backend available - loading projects from AppData');
            await this.loadProjectsFromBackend();
        } else {
            console.log('[ProjectManager] Backend unavailable - using localStorage');
            this.loadProjects();
        }
        
        this.loadCurrentProject();
        
        if (!this.currentProject && this.projects.length > 0) {
            this.setCurrentProject(this.projects[0].id);
        }
        
        if (!this.currentProject) {
            this.createDefaultProjects();
        }
        
        // Listen for backend project updates
        document.addEventListener('backendProjectsLoaded', (e) => {
            console.log('[ProjectManager] Backend projects loaded event received');
            this.handleBackendProjects(e.detail.projects);
        });
    }

    async checkBackendAvailability() {
        try {
            const response = await fetch('/api/appdata/info', {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.backendAvailable = data.available === true;
                console.log('[ProjectManager] Backend availability:', this.backendAvailable);
            }
        } catch (error) {
            console.log('[ProjectManager] Backend not available:', error.message);
            this.backendAvailable = false;
        }
    }

    async loadProjectsFromBackend() {
        try {
            const response = await fetch('/api/appdata/projects', {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (Array.isArray(data)) {
                this.projects = data.map(project => this.normalizeProject(project));
                console.log('[ProjectManager] Loaded', this.projects.length, 'projects from backend');
                
                // Also save to localStorage as backup
                this.saveProjects();
            }
        } catch (error) {
            console.error('[ProjectManager] Error loading projects from backend:', error);
            // Fallback to localStorage
            this.loadProjects();
        }
    }

    normalizeProject(project) {
        // Normalize backend project format to match our internal format
        return {
            id: project.id || `project-${Date.now()}`,
            name: project.name || 'Untitled Project',
            path: project.path || `/home/user/projects/${project.name}`,
            type: project.type || project.language || 'Python',
            createdAt: project.createdAt || project.created_at || new Date().toISOString(),
            lastOpened: project.lastOpened || project.last_opened || new Date().toISOString(),
            files: this.normalizeFiles(project.files || [])
        };
    }

    normalizeFiles(files) {
        if (!Array.isArray(files)) return [];
        
        return files.map(file => ({
            name: file.name || file.filename || 'untitled',
            type: file.type || 'file',
            icon: this.getFileIcon(file.name || file.filename || '')
        }));
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'py': '📄',
            'js': '📄',
            'ts': '📄',
            'html': '🌐',
            'css': '🎨',
            'json': '📦',
            'md': '📄',
            'txt': '📄'
        };
        return iconMap[ext] || '📄';
    }

    handleBackendProjects(backendProjects) {
        if (!Array.isArray(backendProjects)) return;
        
        this.projects = backendProjects.map(project => this.normalizeProject(project));
        this.saveProjects();
        
        // Update UI if current project changed
        if (this.currentProject) {
            const updatedCurrent = this.projects.find(p => p.id === this.currentProject.id);
            if (updatedCurrent) {
                this.currentProject = updatedCurrent;
            }
        }
        
        // Dispatch event for UI updates
        document.dispatchEvent(new CustomEvent('projectsUpdated', {
            detail: { projects: this.projects }
        }));
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
            
            // Dispatch event for UI updates
            document.dispatchEvent(new CustomEvent('currentProjectChanged', {
                detail: { project: project }
            }));
            
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

    async createProject(name, type, path) {
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
        
        // Try to sync with backend if available
        if (this.backendAvailable) {
            try {
                await fetch('/api/appdata/projects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(project)
                });
                console.log('[ProjectManager] Project synced to backend');
            } catch (error) {
                console.warn('[ProjectManager] Could not sync project to backend:', error);
            }
        }
        
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

    async deleteProject(projectId) {
        const index = this.projects.findIndex(p => p.id === projectId);
        if (index !== -1) {
            const project = this.projects[index];
            this.projects.splice(index, 1);
            this.saveProjects();
            
            if (this.currentProject?.id === projectId) {
                this.setCurrentProject(this.projects[0]?.id || null);
            }
            
            // Try to delete from backend if available
            if (this.backendAvailable) {
                try {
                    await fetch(`/api/appdata/projects/${projectId}`, {
                        method: 'DELETE'
                    });
                    console.log('[ProjectManager] Project deleted from backend');
                } catch (error) {
                    console.warn('[ProjectManager] Could not delete project from backend:', error);
                }
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
