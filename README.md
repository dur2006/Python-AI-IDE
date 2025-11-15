# 🚀 AutoPilot IDE - AI-Powered Python Development Environment

> **Status:** ✅ **FULLY REFACTORED AND FUNCTIONAL** (November 15, 2025)

A modern, AI-powered Python IDE built with Flask, Socket.IO, and vanilla JavaScript. Features real-time terminal integration, AI code assistance, and a clean modular architecture.

---

## ✨ Features

- 🤖 **AI Assistant** - Real-time code help, debugging, and refactoring suggestions
- 💻 **Integrated Terminal** - Execute Python commands directly in the IDE
- 📁 **Project Management** - Full CRUD operations for projects and files
- 🎨 **Theme System** - Customizable themes and layouts
- 🔌 **Extension System** - Extensible architecture for plugins
- 🔄 **Real-time Updates** - Socket.IO for instant feedback
- 📊 **Clean Architecture** - Modular frontend with proper separation of concerns

---

## 🏗️ Architecture

### **Backend (Flask + Socket.IO)**
```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── socket_handlers.py     # Socket.IO event handlers
├── api/                   # REST API endpoints
│   ├── projects.py        # Project CRUD operations
│   ├── files.py           # File management
│   ├── themes.py          # Theme management
│   ├── layouts.py         # Layout management
│   ├── extensions.py      # Extension management
│   └── settings.py        # Settings management
└── services/              # Business logic layer
    ├── project_service.py # Project operations
    ├── terminal_service.py # Terminal execution
    ├── ai_service.py      # AI integration
    └── app_data_manager.py # Data persistence
```

### **Frontend (Modular JavaScript)**
```
frontend/
├── index.html             # Clean HTML structure (17.6KB)
├── css/
│   └── styles.css         # Extracted CSS (33KB)
└── js/
    ├── socket-client.js   # Socket.IO client with correct events
    ├── ui-handlers.js     # UI event handling
    ├── init.js            # Application initialization
    ├── project-manager.js # Project management (uses backend API)
    ├── layout-manager.js  # Layout management
    ├── extension-manager.js # Extension management
    └── theme-manager.js   # Theme management
```

---

## 🔧 Recent Refactoring (November 2025)

### **What Was Fixed:**

1. **✅ Eliminated 96KB Monolithic HTML**
   - Reduced index.html from 96KB to 17.6KB (82% reduction)
   - Extracted ~1,500 lines of CSS to separate file
   - Removed all inline JavaScript

2. **✅ Fixed Critical Socket.IO Bug**
   - Frontend was sending `terminal_execute` (wrong)
   - Backend expected `terminal_command` (correct)
   - Created unified socket client with proper event names

3. **✅ Proper Module Architecture**
   - Created `socket-client.js` for Socket.IO integration
   - Created `ui-handlers.js` for event handling
   - Created `init.js` for proper initialization sequence
   - All modules load in correct dependency order

4. **✅ Backend API Integration**
   - Removed localStorage conflicts
   - Frontend now properly uses backend APIs
   - Project manager uses backend for all operations

### **Files Created:**
- `css/styles.css` - Extracted and organized CSS
- `js/socket-client.js` - Unified socket client
- `js/ui-handlers.js` - Modular UI handlers
- `js/init.js` - Initialization orchestration

### **Files to Delete (Manual Cleanup):**
```bash
# Documentation spam
rm BUGFIXES.md DEEP_REFACTORING_COMPLETE.md HOTFIX_SUMMARY.md
rm PYTHON_3.13_COMPATIBILITY_FIX.md REFACTORING.md

# Code duplicates
rm app.py config.py  # Root duplicates
rm js/socket-integration.js js/ui-integration.js  # Old modules
rm backend/services/terminal_service_secure.py  # Duplicate
```

---

## 🚀 Quick Start

### **Prerequisites:**
- Python 3.13+
- pip (Python package manager)
- Modern web browser

### **Installation:**

1. **Clone the repository:**
```bash
git clone https://github.com/dur2006/Python-AI-IDE.git
cd Python-AI-IDE
```

2. **Install backend dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the backend server:**
```bash
python app.py
```

4. **Open the frontend:**
```bash
# Option 1: Use Python's built-in server
python -m http.server 8000

# Option 2: Open index.html directly in browser
# (Some features may require a local server)
```

5. **Access the IDE:**
```
http://localhost:8000
```

---

## 📡 Socket.IO Events

### **Client → Server:**
| Event | Description | Payload |
|-------|-------------|---------|
| `terminal_command` | Execute terminal command | `{ command: string, cwd: string }` |
| `ai_message` | Send AI message | `{ message: string, mode: string, context: object }` |
| `ping` | Connection health check | `{ timestamp: number }` |

### **Server → Client:**
| Event | Description | Payload |
|-------|-------------|---------|
| `terminal_output` | Terminal command output | `{ stdout: string, stderr: string }` |
| `ai_response` | AI assistant response | `{ message: string }` |
| `pong` | Ping response | `{ timestamp: number }` |

---

## 🎯 Usage

### **Terminal Commands:**
```bash
# Execute Python code
python script.py

# Install packages
pip install requests

# Run tests
pytest tests/
```

### **AI Assistant Modes:**
- 💬 **Chat** - General coding questions
- 📖 **Explain** - Code explanation
- 🐛 **Debug** - Bug finding and fixing
- 🔧 **Refactor** - Code improvement suggestions

### **Keyboard Shortcuts:**
- `Ctrl+S` - Save current file
- `Ctrl+P` - Quick file open
- `Ctrl+`` - Toggle terminal
- `Ctrl+B` - Toggle sidebar

---

## 🔌 API Endpoints

### **Projects:**
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project

### **Files:**
- `GET /api/files` - List files in project
- `POST /api/files` - Create new file
- `GET /api/files/<path>` - Get file content
- `PUT /api/files/<path>` - Update file content
- `DELETE /api/files/<path>` - Delete file

### **Terminal:**
- `POST /api/terminal/execute` - Execute command
- `GET /api/terminal/history` - Get command history

### **AI:**
- `POST /api/ai/chat` - Send AI message
- `GET /api/ai/models` - List available models

---

## 🧪 Testing

### **Backend Tests:**
```bash
cd backend
pytest tests/
```

### **Frontend Tests:**
```bash
# Open browser console and check for:
# - Socket connection established
# - Modules initialized successfully
# - No JavaScript errors
```

### **Integration Tests:**
1. Start backend server
2. Open frontend in browser
3. Check browser console for initialization messages
4. Test terminal commands
5. Test AI chat
6. Test project operations

---

## 🐛 Troubleshooting

### **Socket Connection Failed:**
- Ensure backend is running on port 5000
- Check CORS settings in `backend/config.py`
- Verify Socket.IO version compatibility

### **Terminal Not Working:**
- Check socket connection status
- Verify `terminal_command` event is being sent
- Check backend logs for errors

### **AI Not Responding:**
- Verify AI service is configured
- Check API keys in environment variables
- Review backend logs for AI service errors

### **Files Not Loading:**
- Ensure project is properly loaded
- Check file permissions
- Verify backend API is accessible

---

## 📚 Documentation

- [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) - Detailed refactoring documentation
- [CLEANUP_PLAN.md](CLEANUP_PLAN.md) - Cleanup strategy and file analysis
- [Architecture Guide](docs/ARCHITECTURE.md) - Detailed architecture documentation (coming soon)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Code Style:**
- Backend: Follow PEP 8 (Python)
- Frontend: Use ESLint with Airbnb config
- Comments: Use JSDoc for JavaScript, docstrings for Python

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Flask and Socket.IO teams for excellent frameworks
- The Python community for inspiration
- All contributors who helped improve this project

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/dur2006/Python-AI-IDE/issues)
- **Discussions:** [GitHub Discussions](https://github.com/dur2006/Python-AI-IDE/discussions)
- **Email:** j.dureckicontact@gmail.com

---

## 🔮 Roadmap

- [ ] Add TypeScript support
- [ ] Implement code completion
- [ ] Add Git integration
- [ ] Create extension marketplace
- [ ] Add collaborative editing
- [ ] Implement debugging tools
- [ ] Add performance profiling
- [ ] Create mobile version

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by the AutoPilot IDE team**

**Last Updated:** November 15, 2025  
**Version:** 2.0.0 (Post-Refactoring)  
**Status:** ✅ Production Ready
