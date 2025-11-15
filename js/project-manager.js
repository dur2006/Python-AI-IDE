/**
 * AutoPilot IDE - Project Manager Module
 * NOW PROPERLY INTEGRATED WITH BACKEND API
 */

class ProjectManager {
    constructor() {
        this.projects = [];
        this.currentProject = null;
        this.apiBase = 'http://localhost:5000/api';
        this.initialized = false;
    }

    async init() {
        if (this.initialized) {
            console.log('[ProjectManager] Already initialized');
            return;
        }

        console.log('[ProjectManager] Initializing with backend API...');
        try {
            await this.loadProjects();
            
            if (!this.currentProject && this.projects.length > 0) {
                await this.setCurrentProject(this.projects[0].id);
            }
            
            this.initialized = true;
            console.log('[ProjectManager] Initialized successfully');
        } catch (error) {
            console.error('[ProjectManager] Initialization failed:', error);
            this.showError('Failed to initialize project manager');
            throw error;
        }
    }

    async loadProjects() {
        try {
            const response = await fetch(`${this.apiBase}/projects`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.projects = data.data || [];
                console.log('[ProjectManager] Loaded', this.projects.length, 'projects from backend');
                
                // Load current project from localStorage (just the ID)
                const currentProjectId = localStorage.getItem('autopilot_current_project');
                if (currentProjectId) {
                    this.currentProject = this.projects.find(p => p.id === currentProjectId);
                }
            } else {
                throw new Error(data.error || 'Failed to load projects');
            }
        } catch (error) {
            console.error('[ProjectManager] Error loading projects:', error);
            throw error;
        }
    }

    async setCurrentProject(projectId) {
        try {
            const project = this.projects.find(p => p.id === projectId);
            if (!project) {
                console.error('[ProjectManager] Project not found:', projectId);
                return false;
            }

            // Update lastOpened on backend
            const response = await fetch(`${this.apiBase}/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lastOpened: new Date().toISOString() })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.currentProject = data.data;
                localStorage.setItem('autopilot_current_project', projectId);
                console.log('[ProjectManager] Current project set to:', project.name);
                
                // Load project files
                await this.loadProjectFiles(projectId);
                
                return true;
            } else {
                throw new Error(data.error || 'Failed to set current project');
            }
        } catch (error) {
            console.error('[ProjectManager] Error setting current project:', error);
            return false;
        }
    }

    async loadProjectFiles(projectId) {
        try {
            const response = await fetch(`${this.apiBase}/projects/${projectId}/files`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const files = data.data || [];
                console.log('[ProjectManager] Loaded', files.length, 'files for project');
                
                // Update file explorer UI
                if (window.updateFileExplorer) {
                    window.updateFileExplorer(files);
                }
                
                return files;
            } else {
                throw new Error(data.error || 'Failed to load project files');
            }
        } catch (error) {
            console.error('[ProjectManager] Error loading project files:', error);
            return [];
        }
    }

    getCurrentProject() {
        return this.currentProject;
    }

    getLastProject() {
        // Get the most recently opened project
        if (this.projects.length === 0) return null;
        
        const sorted = [...this.projects].sort((a, b) => {
            const dateA = new Date(a.lastOpened || 0);
            const dateB = new Date(b.lastOpened || 0);
            return dateB - dateA;
        });
        
        return sorted[0];
    }

    async getRecentProjects(limit = 10) {
        // Sort by lastOpened
        return this.projects
            .sort((a, b) => new Date(b.lastOpened) - new Date(a.lastOpened))
            .slice(0, limit);
    }

    async loadProject(projectId) {
        return await this.setCurrentProject(projectId);
    }

    async createProject(name, type, path) {
        try {
            const response = await fetch(`${this.apiBase}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, type, path })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                const project = data.data;
                this.projects.push(project);
                await this.setCurrentProject(project.id);
                console.log('[ProjectManager] Project created:', name);
                return project;
            } else {
                throw new Error(data.error || 'Failed to create project');
            }
        } catch (error) {
            console.error('[ProjectManager] Error creating project:', error);
            this.showError('Failed to create project: ' + error.message);
            throw error;
        }
    }

    async createNewProject() {
        console.log('[ProjectManager] Opening new project dialog');
        this.showProjectModal();
    }

    showProjectModal() {
        console.log('[ProjectManager] Showing project modal');
        const modal = document.getElementById('projectModal');
        if (modal) {
            modal.style.display = 'flex';
            // TODO: Populate with project list
        }
    }

    async createNewFile() {
        console.log('[ProjectManager] Creating new file');
        if (!this.currentProject) {
            this.showError('No project selected');
            return;
        }
        // TODO: Implement file creation
    }

    async createNewFolder() {
        console.log('[ProjectManager] Creating new folder');
        if (!this.currentProject) {
            this.showError('No project selected');
            return;
        }
        // TODO: Implement folder creation
    }

    async refreshFileTree() {
        console.log('[ProjectManager] Refreshing file tree');
        if (!this.currentProject) {
            return;
        }
        await this.loadProjectFiles(this.currentProject.id);
    }

    async saveCurrentFile() {
        console.log('[ProjectManager] Saving current file');
        // TODO: Implement file saving
    }

    async saveAllFiles() {
        console.log('[ProjectManager] Saving all files');
        // TODO: Implement save all
    }

    async deleteProject(projectId) {
        try {
            const response = await fetch(`${this.apiBase}/projects/${projectId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                const index = this.projects.findIndex(p => p.id === projectId);
                if (index !== -1) {
                    const project = this.projects[index];
                    this.projects.splice(index, 1);
                    
                    if (this.currentProject?.id === projectId) {
                        if (this.projects.length > 0) {
                            await this.setCurrentProject(this.projects[0].id);
                        } else {
                            this.currentProject = null;
                        }
                    }
                    
                    console.log('[ProjectManager] Project deleted:', project.name);
                    return true;
                }
            } else {
                throw new Error(data.error || 'Failed to delete project');
            }
        } catch (error) {
            console.error('[ProjectManager] Error deleting project:', error);
            this.showError('Failed to delete project: ' + error.message);
            return false;
        }
    }

    async getProjectFiles(projectId) {
        return await this.loadProjectFiles(projectId);
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

    showError(message) {
        console.error('[ProjectManager]', message);
        // Show error in UI if available
        if (window.showNotification) {
            window.showNotification(message, 'error');
        }
    }
}

// Create global instance and assign to window
window.projectManager = new ProjectManager();

console.log('[ProjectManager] Module loaded');
