# AutoPilot IDE v2.0 🚀

A modern, AI-powered Integrated Development Environment built with Flask and Python.

## 🎯 Features

- **AI-Powered Assistance**: Integrated AI chat for code help, debugging, and suggestions
- **Real-time Terminal**: Execute commands directly in the IDE
- **Project Management**: Create, manage, and switch between multiple projects
- **File Operations**: Full file system integration with create, read, update, delete
- **Extension System**: Modular extension architecture for customization
- **WebSocket Communication**: Real-time updates via Socket.IO
- **Modern Architecture**: Clean separation of concerns with service layer pattern

## 📁 Project Structure

```
Python-AI-IDE/
├── backend/                    # Backend application
│   ├── __init__.py
│   ├── app.py                 # Application factory
│   ├── config.py              # Configuration management
│   ├── socket_handlers.py     # WebSocket event handlers
│   ├── api/                   # REST API endpoints
│   │   ├── __init__.py
│   │   ├── extensions.py      # Extension management API
│   │   ├── projects.py        # Project management API
│   │   ├── files.py           # File operations API
│   │   └── terminal.py        # Terminal execution API
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── extension_service.py
│   │   ├── project_service.py
│   │   ├── file_service.py
│   │   ├── terminal_service.py
│   │   └── ai_service.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── logger.py          # Logging configuration
├── static/                    # Frontend static files
│   └── index.html            # Main HTML file
├── js/                       # JavaScript modules
│   ├── app.js
│   ├── api-module.js
│   ├── socket-module.js
│   ├── terminal-module.js
│   ├── ai-module.js
│   └── ...
├── data/                     # Application data
│   ├── projects.json         # Project metadata
│   └── extensions.json       # Extension metadata
├── projects/                 # User projects directory
├── logs/                     # Application logs
├── run.py                    # Main entry point
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dur2006/Python-AI-IDE.git
   cd Python-AI-IDE
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

## ⚙️ Configuration

### Environment Variables

```bash
# Flask environment (development, production, testing)
export FLASK_ENV=development

# Server configuration
export HOST=0.0.0.0
export PORT=5000

# Security
export SECRET_KEY=your-secret-key-here

# AI Configuration (optional)
export AI_MODEL=gpt-3.5-turbo
export OPENAI_API_KEY=your-api-key
```

### Configuration Files

Edit `backend/config.py` to customize:
- File paths
- API settings
- Terminal configuration
- Logging levels
- Security settings

## 🏗️ Architecture

### Backend Architecture

The backend follows a **layered architecture** pattern:

1. **API Layer** (`backend/api/`): REST endpoints for client communication
2. **Service Layer** (`backend/services/`): Business logic and data processing
3. **Socket Layer** (`backend/socket_handlers.py`): Real-time WebSocket communication
4. **Configuration Layer** (`backend/config.py`): Environment-specific settings

### Key Design Patterns

- **Application Factory**: Flexible app creation with different configurations
- **Service Layer Pattern**: Separation of business logic from API routes
- **Dependency Injection**: Services are injected where needed
- **Configuration Management**: Environment-based configuration

### API Endpoints

#### Projects
- `GET /api/projects` - List all projects
- `GET /api/projects/<id>` - Get project details
- `POST /api/projects` - Create new project
- `DELETE /api/projects/<id>` - Delete project
- `GET /api/projects/<id>/files` - Get project file tree

#### Files
- `GET /api/files/<project_id>/<path>` - Read file
- `PUT /api/files/<project_id>/<path>` - Update file
- `POST /api/files/<project_id>/<path>` - Create file
- `DELETE /api/files/<project_id>/<path>` - Delete file
- `GET /api/files/<project_id>/tree` - Get file tree

#### Extensions
- `GET /api/extensions` - List all extensions
- `GET /api/extensions/<id>` - Get extension details
- `POST /api/extensions/<id>/toggle` - Enable/disable extension
- `POST /api/extensions/<id>/install` - Install extension
- `POST /api/extensions/<id>/uninstall` - Uninstall extension

#### Terminal
- `POST /api/terminal/execute` - Execute command
- `GET /api/terminal/history` - Get command history
- `POST /api/terminal/clear` - Clear history

### WebSocket Events

#### Client → Server
- `terminal_command` - Execute terminal command
- `ai_message` - Send message to AI
- `ping` - Connection test

#### Server → Client
- `terminal_output` - Command execution result
- `ai_response` - AI-generated response
- `pong` - Ping response

## 🔒 Security Features

- **Path Traversal Protection**: File operations validate paths
- **Command Filtering**: Dangerous commands are blocked
- **Timeout Protection**: Commands have execution timeouts
- **CORS Configuration**: Configurable cross-origin settings
- **Input Validation**: All inputs are validated

## 🧪 Testing

```bash
# Set testing environment
export FLASK_ENV=testing

# Run tests (when implemented)
pytest tests/
```

## 📝 Development

### Adding a New Service

1. Create service file in `backend/services/`
2. Implement service class with business logic
3. Add service to `backend/services/__init__.py`
4. Create API endpoints in `backend/api/`
5. Register blueprint in `backend/api/__init__.py`

### Adding a New API Endpoint

```python
# backend/api/my_feature.py
from flask import Blueprint, jsonify
from backend.services.my_service import MyService

my_feature_bp = Blueprint('my_feature', __name__)
my_service = MyService()

@my_feature_bp.route('/action', methods=['POST'])
def perform_action():
    result = my_service.do_something()
    return jsonify(result), 200
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Flask framework and community
- Socket.IO for real-time communication
- All contributors and users

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the code comments

---

**Built with ❤️ by the AutoPilot IDE Team**
