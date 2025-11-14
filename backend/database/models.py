"""
Database Models
SQLAlchemy models for all application entities with relationships and validation
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import re

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    projects = relationship('Project', back_populates='owner', cascade='all, delete-orphan')
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    settings = relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan')
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email format')
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', username):
            raise ValueError('Username must be 3-50 characters, alphanumeric with _ or -')
        return username
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Session(Base):
    """Session model for user authentication tokens"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(255))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"


class Project(Base):
    """Project model for managing code projects"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    path = Column(String(500), nullable=False)
    project_type = Column(String(50), default='Python')  # Python, JavaScript, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_opened = Column(DateTime, default=func.now())
    
    # Metadata
    metadata = Column(JSON)  # Store additional project metadata
    
    # Relationships
    owner = relationship('User', back_populates='projects')
    files = relationship('ProjectFile', back_populates='project', cascade='all, delete-orphan')
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate project name"""
        if not name or len(name) < 1 or len(name) > 100:
            raise ValueError('Project name must be 1-100 characters')
        return name
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', type='{self.project_type}')>"


class ProjectFile(Base):
    """Project file model for tracking files in projects"""
    __tablename__ = 'project_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1000), nullable=False)
    file_type = Column(String(50))  # .py, .js, .txt, etc.
    size = Column(Integer)  # File size in bytes
    content_hash = Column(String(64))  # SHA-256 hash for change detection
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship('Project', back_populates='files')
    
    def __repr__(self):
        return f"<ProjectFile(id={self.id}, filename='{self.filename}', project_id={self.project_id})>"


class Theme(Base):
    """Theme model for UI customization"""
    __tablename__ = 'themes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    colors = Column(JSON, nullable=False)  # Store color scheme as JSON
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}', active={self.is_active})>"


class Extension(Base):
    """Extension model for IDE extensions/plugins"""
    __tablename__ = 'extensions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False)
    author = Column(String(100))
    icon = Column(String(50))
    is_installed = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=False)
    install_path = Column(String(500))
    config = Column(JSON)  # Extension configuration
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Extension(id={self.id}, name='{self.name}', version='{self.version}')>"


class Layout(Base):
    """Layout model for UI layout configurations"""
    __tablename__ = 'layouts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    config = Column(JSON, nullable=False)  # Layout configuration
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Layout(id={self.id}, name='{self.name}', active={self.is_active})>"


class UserSettings(Base):
    """User settings model for personalized preferences"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # Editor settings
    font_size = Column(Integer, default=14)
    font_family = Column(String(100), default='Consolas, Monaco, monospace')
    tab_size = Column(Integer, default=4)
    insert_spaces = Column(Boolean, default=True)
    word_wrap = Column(Boolean, default=True)
    show_line_numbers = Column(Boolean, default=True)
    show_minimap = Column(Boolean, default=True)
    bracket_pair_colorization = Column(Boolean, default=True)
    
    # Behavior settings
    auto_save = Column(Boolean, default=True)
    auto_save_interval = Column(Integer, default=5000)  # milliseconds
    format_on_save = Column(Boolean, default=True)
    format_on_paste = Column(Boolean, default=False)
    
    # Theme and layout
    theme_id = Column(Integer, ForeignKey('themes.id'))
    layout_id = Column(Integer, ForeignKey('layouts.id'))
    
    # Additional settings as JSON
    custom_settings = Column(JSON)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='settings')
    theme = relationship('Theme')
    layout = relationship('Layout')
    
    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id})>"


class TerminalHistory(Base):
    """Terminal command history model"""
    __tablename__ = 'terminal_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    command = Column(Text, nullable=False)
    cwd = Column(String(500))
    return_code = Column(Integer)
    execution_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f"<TerminalHistory(id={self.id}, command='{self.command[:50]}...', rc={self.return_code})>"


class AIConversation(Base):
    """AI conversation history model"""
    __tablename__ = 'ai_conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context (code, file info, etc.)
    model = Column(String(50))  # AI model used
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship('User')
    
    @validates('role')
    def validate_role(self, key, role):
        """Validate role value"""
        if role not in ['user', 'assistant', 'system']:
            raise ValueError('Role must be user, assistant, or system')
        return role
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, role='{self.role}', user_id={self.user_id})>"


class AuditLog(Base):
    """Audit log model for tracking important actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))  # project, file, extension, etc.
    resource_id = Column(Integer)
    details = Column(JSON)  # Additional details about the action
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"


class ErrorLog(Base):
    """Error log model for tracking application errors"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    request_path = Column(String(500))
    request_method = Column(String(10))
    ip_address = Column(String(45))
    severity = Column(String(20), default='error')  # debug, info, warning, error, critical
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship('User')
    
    @validates('severity')
    def validate_severity(self, key, severity):
        """Validate severity level"""
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if severity not in valid_levels:
            raise ValueError(f'Severity must be one of: {", ".join(valid_levels)}')
        return severity
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type='{self.error_type}', severity='{self.severity}')>"


# Indexes for performance
from sqlalchemy import Index

# Create composite indexes for common queries
Index('idx_sessions_user_expires', Session.user_id, Session.expires_at)
Index('idx_projects_owner_active', Project.owner_id, Project.is_active)
Index('idx_project_files_project_deleted', ProjectFile.project_id, ProjectFile.is_deleted)
Index('idx_terminal_history_user_created', TerminalHistory.user_id, TerminalHistory.created_at)
Index('idx_ai_conversations_user_created', AIConversation.user_id, AIConversation.created_at)
Index('idx_audit_logs_user_action_created', AuditLog.user_id, AuditLog.action, AuditLog.created_at)
Index('idx_error_logs_severity_created', ErrorLog.severity, ErrorLog.created_at)
