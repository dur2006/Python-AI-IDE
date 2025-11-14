# AutoPilot IDE - Quick Start Guide

## 🚀 Get Started in 5 Minutes

Welcome to AutoPilot IDE! This guide will get you up and running quickly.

---

## 📋 Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **Git** (optional, for cloning)

---

## 🔧 Installation

### Step 1: Clone or Download

**Option A: Clone with Git**
```bash
git clone https://github.com/dur2006/Python-AI-IDE.git
cd Python-AI-IDE
```

**Option B: Download ZIP**
- Download from GitHub
- Extract to your desired location
- Open terminal in that directory

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask
- Flask-SocketIO
- Flask-CORS
- python-socketio
- (and other dependencies in requirements.txt)

### Step 3: Run Migration (First Time Only)

If you have existing data or want to ensure everything is set up:

```bash
python backend/scripts/migrate_data.py
```

This will:
- ✅ Create the `data/` directory
- ✅ Initialize all data files
- ✅ Migrate any existing data
- ✅ Verify everything is ready

---

## ▶️ Starting the Application

### Simple Start

```bash
python app.py
```

That's it! The application will start on `http://localhost:5000`

### With Custom Configuration

```bash
# Production mode
FLASK_ENV=production python app.py

# Custom port
PORT=8000 python app.py

# Both
FLASK_ENV=production PORT=8000 python app.py
```

### Alternative Entry Point

```bash
python run.py
```

---

## 🌐 Accessing the IDE

Once started, open your browser and navigate to:

```
http://localhost:5000
```

You should see the AutoPilot IDE interface with:
- 📁 Sidebar (Projects & Files)
- ✏️ Code Editor
- 💻 Terminal
- 🤖 AI Assistant Panel

---

## 🎯 First Steps

### 1. Create Your First Project

1. Click the **"+"** button in the sidebar
2. Enter project name (e.g., "My First Project")
3. Select project type (Python, JavaScript, etc.)
4. Click **Create**

### 2. Explore the Interface

**Sidebar (Left)**
- View all your projects
- Browse project files
- Create new files/folders

**Editor (Center)**
- Write and edit code
- Syntax highlighting
- Auto-completion

**Terminal (Bottom)**
- Run commands
- Execute Python scripts
- Install packages

**AI Panel (Right)**
- Ask coding questions
- Get code suggestions
- Debug assistance

### 3. Write Some Code

1. Create a new file: `hello.py`
2. Write some Python code:
   ```python
   print("Hello from AutoPilot IDE!")
   ```
3. Run it in the terminal:
   ```bash
   python hello.py
   ```

### 4. Try the AI Assistant

1. Open the AI panel (right side)
2. Ask a question like:
   - "How do I read a file in Python?"
   - "Explain this code: [paste code]"
   - "Write a function to sort a list"

---

## 🎨 Customization

### Change Theme

1. Click **Settings** icon
2. Go to **Themes**
3. Select your preferred theme:
   - Dark (Default)
   - Light
   - Custom themes

### Adjust Layout

1. Click **Layout** icon
2. Choose a preset:
   - **Default**: All panels visible
   - **Focus Mode**: Editor only
   - **Coding Layout**: Optimized for development

### Configure Settings

1. Click **Settings** icon
2. Adjust preferences:
   - Font size
   - Tab size
   - Auto-save
   - Word wrap
   - And more...

---

## 🔌 Extensions

### View Extensions

1. Click **Extensions** icon in sidebar
2. See installed and available extensions

### Install an Extension

1. Browse available extensions
2. Click **Install** on desired extension
3. Extension activates automatically

### Toggle Extensions

1. Go to Extensions panel
2. Click toggle switch to enable/disable
3. Changes apply immediately

**Default Extensions:**
- 🐍 Python Language Support
- 📦 Git Integration
- ✨ Code Formatter
- 🔍 Linter
- 🐛 Debugger

---

## 💡 Tips & Tricks

### Keyboard Shortcuts

- **Ctrl/Cmd + S**: Save file
- **Ctrl/Cmd + F**: Find in file
- **Ctrl/Cmd + /**: Toggle comment
- **Ctrl/Cmd + `**: Toggle terminal

### Terminal Commands

```bash
# Install Python packages
pip install package-name

# Run Python scripts
python script.py

# Check Python version
python --version

# List files
ls  # or 'dir' on Windows

# Clear terminal
clear  # or 'cls' on Windows
```

### AI Assistant Tips

- Be specific in your questions
- Provide context when asking about code
- Ask for explanations, not just solutions
- Use it to learn, not just copy-paste

---

## 📁 Project Structure

After setup, your directory will look like:

```
Python-AI-IDE/
├── app.py                 # Main entry point
├── run.py                 # Alternative entry point
├── backend/               # Backend code
│   ├── app.py            # Application factory
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   └── scripts/          # Utility scripts
├── data/                  # Your data (auto-created)
│   ├── projects.json
│   ├── extensions.json
│   ├── themes.json
│   ├── layouts.json
│   └── settings.json
├── projects/              # Your projects (auto-created)
│   └── [your projects]
├── static/                # Frontend files
│   ├── index.html
│   ├── css/
│   └── js/
└── requirements.txt       # Python dependencies
```

---

## 🐛 Troubleshooting

### Application won't start

**Problem**: Port 5000 already in use  
**Solution**: Use a different port
```bash
PORT=8000 python app.py
```

**Problem**: Missing dependencies  
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

**Problem**: Python version too old  
**Solution**: Upgrade to Python 3.8+
```bash
python --version  # Check version
```

### Can't see my projects

**Problem**: Data directory not initialized  
**Solution**: Run migration script
```bash
python backend/scripts/migrate_data.py
```

### Extensions not working

**Problem**: Extensions not loading  
**Solution**: Check data/extensions.json exists
```bash
# Run migration to fix
python backend/scripts/migrate_data.py
```

### Terminal not responding

**Problem**: Command stuck  
**Solution**: Refresh the page or restart the application

### AI Assistant not responding

**Problem**: AI service not configured  
**Solution**: Check AI configuration in backend/config.py

---

## 📚 Next Steps

### Learn More

- Read [REFACTORING.md](REFACTORING.md) for architecture details
- Explore the API endpoints
- Check out the service layer
- Customize your workflow

### Advanced Usage

- Set up environment variables
- Configure production deployment
- Create custom extensions
- Integrate with external tools

### Get Help

- Check the documentation
- Open an issue on GitHub
- Contact the development team

---

## 🎉 You're Ready!

You now have a fully functional AI-powered IDE. Start coding and let the AI assistant help you along the way!

**Happy Coding! 🚀**

---

## 📞 Support

- **Documentation**: See REFACTORING.md
- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions

---

**Version**: 2.0.0  
**Last Updated**: November 14, 2025  
**Status**: Production Ready ✅
