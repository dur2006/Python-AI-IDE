"""
AutoPilot IDE - Application Launcher
This file serves as the entry point and imports the actual app from backend.
The main application logic is in backend/app.py using the application factory pattern.
"""

import os
import sys
from pathlib import Path

# Ensure backend is in path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import create_app, socketio


def main():
    """Main application entry point"""
    # Get environment from environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create application using factory pattern
    app = create_app(env)
    
    # Get configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # Print startup information
    print("\n" + "="*60)
    print(f"🚀 {app.config['APP_NAME']} v{app.config['VERSION']}")
    print("="*60)
    print(f"Environment: {env}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug}")
    print(f"Open your browser and navigate to http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run application with SocketIO
    # NOTE: use_reloader=False to avoid watchdog/threading issues with Python 3.13
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,  # Disabled due to Python 3.13 threading incompatibility
        log_output=True,
        allow_unsafe_werkzeug=True  # For development
    )


if __name__ == '__main__':
    main()
