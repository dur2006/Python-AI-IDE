"""
AutoPilot IDE - Main Entry Point
Run this file to start the application
"""

import os
from backend.app import create_app, socketio


def main():
    """Main application entry point"""
    # Get environment from environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create application
    app = create_app(env)
    
    # Get configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # Print startup information
    print("\n" + "="*60)
    print(f"🚀 AutoPilot IDE v{app.config['VERSION']}")
    print("="*60)
    print(f"Environment: {env}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug}")
    print("="*60 + "\n")
    
    # Run application with SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        log_output=True
    )


if __name__ == '__main__':
    main()
