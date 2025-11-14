"""
Database Package
Provides database initialization, session management, and migration support
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
import logging

from backend.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections, sessions, and initialization"""
    
    def __init__(self, database_url: str = None, echo: bool = False):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL (default: SQLite in data directory)
            echo: Enable SQL query logging
        """
        if database_url is None:
            # Default to SQLite in data directory
            data_dir = Path(__file__).parent.parent.parent / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            database_url = f'sqlite:///{data_dir}/autopilot_ide.db'
        
        self.database_url = database_url
        self.echo = echo
        
        # Create engine with appropriate settings
        if database_url.startswith('sqlite'):
            # SQLite-specific settings
            self.engine = create_engine(
                database_url,
                echo=echo,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
            # Enable foreign keys for SQLite
            event.listen(self.engine, 'connect', self._set_sqlite_pragma)
        else:
            # PostgreSQL/MySQL settings
            self.engine = create_engine(
                database_url,
                echo=echo,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        logger.info(f"Database manager initialized: {database_url}")
    
    def _set_sqlite_pragma(self, dbapi_conn, connection_record):
        """Enable foreign keys for SQLite"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    def init_db(self, drop_all: bool = False):
        """
        Initialize database schema
        
        Args:
            drop_all: Drop all tables before creating (WARNING: destroys data)
        """
        try:
            if drop_all:
                logger.warning("Dropping all database tables...")
                Base.metadata.drop_all(self.engine)
            
            logger.info("Creating database tables...")
            Base.metadata.create_all(self.engine)
            logger.info("✅ Database initialized successfully")
            
            # Create default data
            self._create_default_data()
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _create_default_data(self):
        """Create default data (themes, layouts, etc.)"""
        from backend.database.models import Theme, Layout, Extension
        
        session = self.Session()
        try:
            # Check if default data already exists
            if session.query(Theme).count() > 0:
                logger.info("Default data already exists, skipping...")
                return
            
            # Create default themes
            default_themes = [
                Theme(
                    name='Dark (Default)',
                    description='Default dark theme',
                    is_default=True,
                    is_active=True,
                    colors={
                        'primary': '#667eea',
                        'secondary': '#764ba2',
                        'background': '#1e1e1e',
                        'surface': '#252526',
                        'text': '#d4d4d4',
                        'textSecondary': '#858585',
                        'border': '#3e3e42',
                        'accent': '#007acc'
                    }
                ),
                Theme(
                    name='Light',
                    description='Light theme for daytime coding',
                    is_default=False,
                    is_active=False,
                    colors={
                        'primary': '#667eea',
                        'secondary': '#764ba2',
                        'background': '#ffffff',
                        'surface': '#f3f3f3',
                        'text': '#1e1e1e',
                        'textSecondary': '#6e6e6e',
                        'border': '#e5e5e5',
                        'accent': '#0066cc'
                    }
                )
            ]
            
            # Create default layouts
            default_layouts = [
                Layout(
                    name='Default Layout',
                    description='Standard IDE layout with all panels visible',
                    is_default=True,
                    is_active=True,
                    config={
                        'sidebar': {'visible': True, 'width': 250},
                        'editor': {'visible': True},
                        'terminal': {'visible': True, 'height': 250},
                        'aiPanel': {'visible': True, 'width': 380}
                    }
                ),
                Layout(
                    name='Focus Mode',
                    description='Editor only - minimize distractions',
                    is_default=False,
                    is_active=False,
                    config={
                        'sidebar': {'visible': False, 'width': 250},
                        'editor': {'visible': True},
                        'terminal': {'visible': False, 'height': 250},
                        'aiPanel': {'visible': False, 'width': 380}
                    }
                ),
                Layout(
                    name='Coding Layout',
                    description='Editor with sidebar and terminal',
                    is_default=False,
                    is_active=False,
                    config={
                        'sidebar': {'visible': True, 'width': 200},
                        'editor': {'visible': True},
                        'terminal': {'visible': True, 'height': 300},
                        'aiPanel': {'visible': True, 'width': 300}
                    }
                )
            ]
            
            # Create default extensions
            default_extensions = [
                Extension(
                    name='Python Language Support',
                    description='Syntax highlighting and IntelliSense for Python',
                    version='1.0.0',
                    author='AutoPilot Team',
                    icon='python',
                    is_installed=True,
                    is_enabled=True
                ),
                Extension(
                    name='Git Integration',
                    description='Version control with Git',
                    version='1.0.0',
                    author='AutoPilot Team',
                    icon='git',
                    is_installed=True,
                    is_enabled=True
                ),
                Extension(
                    name='Code Formatter',
                    description='Auto-format code with Black',
                    version='1.0.0',
                    author='AutoPilot Team',
                    icon='format',
                    is_installed=True,
                    is_enabled=True
                ),
                Extension(
                    name='Linter',
                    description='Code quality checks with Pylint',
                    version='1.0.0',
                    author='AutoPilot Team',
                    icon='search',
                    is_installed=True,
                    is_enabled=True
                ),
                Extension(
                    name='Debugger',
                    description='Interactive debugging support',
                    version='1.0.0',
                    author='AutoPilot Team',
                    icon='bug',
                    is_installed=True,
                    is_enabled=True
                )
            ]
            
            # Add all default data
            session.add_all(default_themes)
            session.add_all(default_layouts)
            session.add_all(default_extensions)
            
            session.commit()
            logger.info("✅ Default data created successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to create default data: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions
        
        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).first()
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close all database connections"""
        self.Session.remove()
        self.engine.dispose()
        logger.info("Database connections closed")
    
    def get_status(self) -> dict:
        """Get database status information"""
        from backend.database.models import (
            User, Project, Theme, Extension, Layout,
            Session as SessionModel, TerminalHistory, AIConversation
        )
        
        with self.get_session() as session:
            return {
                'database_url': self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url,
                'users': session.query(User).count(),
                'projects': session.query(Project).count(),
                'themes': session.query(Theme).count(),
                'extensions': session.query(Extension).count(),
                'layouts': session.query(Layout).count(),
                'active_sessions': session.query(SessionModel).filter(
                    SessionModel.expires_at > session.query(SessionModel).first().created_at
                ).count() if session.query(SessionModel).first() else 0,
                'terminal_history': session.query(TerminalHistory).count(),
                'ai_conversations': session.query(AIConversation).count()
            }


# Global database manager instance
_db_manager = None


def get_db_manager(database_url: str = None, echo: bool = False) -> DatabaseManager:
    """
    Get global database manager instance
    
    Args:
        database_url: SQLAlchemy database URL (only used on first call)
        echo: Enable SQL query logging (only used on first call)
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url, echo)
    return _db_manager


def init_database(database_url: str = None, drop_all: bool = False, echo: bool = False):
    """
    Initialize database with schema and default data
    
    Args:
        database_url: SQLAlchemy database URL
        drop_all: Drop all tables before creating (WARNING: destroys data)
        echo: Enable SQL query logging
    """
    db_manager = get_db_manager(database_url, echo)
    db_manager.init_db(drop_all)


def get_session():
    """
    Get database session (for use in Flask app context)
    
    Returns:
        SQLAlchemy session
    """
    db_manager = get_db_manager()
    return db_manager.Session()


@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations
    
    Usage:
        with session_scope() as session:
            user = session.query(User).first()
    """
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session


# Export commonly used items
__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'init_database',
    'get_session',
    'session_scope',
    'Base'
]
