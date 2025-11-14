"""
Socket.IO Event Handlers
Handles real-time WebSocket communication
"""

from flask_socketio import emit

from backend.services.terminal_service import TerminalService
from backend.services.ai_service import AIService


def register_socket_handlers(socketio, app):
    """Register all socket event handlers with app context"""
    
    terminal_service = TerminalService()
    ai_service = AIService()
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        app.logger.info("Client connected")
        emit('connection_response', {
            'status': 'connected',
            'message': 'Successfully connected to AutoPilot IDE backend'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        app.logger.info("Client disconnected")
    
    @socketio.on('terminal_command')
    def handle_terminal_command(data):
        """Handle terminal command execution"""
        try:
            command = data.get('command', '')
            cwd = data.get('cwd')
            
            if not command:
                emit('terminal_output', {
                    'stderr': 'No command provided',
                    'returncode': 1
                })
                return
            
            result = terminal_service.execute_command(command, cwd)
            emit('terminal_output', result)
            
        except Exception as e:
            app.logger.error(f"Error executing terminal command: {e}")
            emit('terminal_output', {
                'stderr': f'Error: {str(e)}',
                'returncode': 1
            })
    
    @socketio.on('ai_message')
    def handle_ai_message(data):
        """Handle AI chat message"""
        try:
            message = data.get('message', '')
            context = data.get('context', {})
            
            if not message:
                emit('ai_response', {
                    'message': 'Please provide a message',
                    'error': True
                })
                return
            
            response = ai_service.generate_response(message, context)
            emit('ai_response', {
                'message': response,
                'error': False
            })
            
        except Exception as e:
            app.logger.error(f"Error processing AI message: {e}")
            emit('ai_response', {
                'message': f'Error: {str(e)}',
                'error': True
            })
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for connection testing"""
        emit('pong', {'timestamp': app.config.get('VERSION', '2.0.0')})
    
    @socketio.on('error')
    def handle_error(error):
        """Handle socket errors"""
        app.logger.error(f"Socket error: {error}")
    
    app.logger.info("Socket handlers registered successfully")
