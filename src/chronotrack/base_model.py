"""
Base model class for ChronoTrack ORM-like functionality.
Provides common database operations for all models.
"""

import sqlite3
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os


class BaseModel(ABC):
    """
    Abstract base class for all ChronoTrack models.
    Implements common database operations following OOP principles.
    """
    
    def __init__(self, db_path: str = ".chrono/chrono.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database and directory exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results."""
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def _execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def _execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return affected rows."""
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    @abstractmethod
    def save(self) -> int:
        """Save the model instance to database. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def load_by_id(self, model_id: int) -> Optional['BaseModel']:
        """Load a model instance by ID. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def delete(self) -> bool:
        """Delete the model instance from database. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def show_info(self) -> str:
        """Return string representation of the model. Must be implemented by subclasses."""
        pass
    
    def __str__(self) -> str:
        """String representation using show_info method (polymorphism)."""
        return self.show_info()


class DatabaseManager:
    """
    Handles database initialization and schema creation.
    Separate from BaseModel to follow single responsibility principle.
    """
    
    def __init__(self, db_path: str = ".chrono/chrono.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def initialize_database(self):
        """Create all necessary tables for ChronoTrack."""
        with sqlite3.connect(self.db_path) as conn:
            # Create commits table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS commits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_message TEXT NOT NULL,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create files table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL UNIQUE,
                    file_hash TEXT NOT NULL
                )
            ''')
            
            # Create chrono table (junction table)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chrono (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_id INTEGER NOT NULL,
                    file_id INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('added', 'modified', 'deleted')),
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (commit_id) REFERENCES commits (id),
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')
            
            conn.commit()
    
    def reset_database(self):
        """Reset the database by dropping all tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DROP TABLE IF EXISTS chrono')
            conn.execute('DROP TABLE IF EXISTS files')
            conn.execute('DROP TABLE IF EXISTS commits')
            conn.commit()
        
        self.initialize_database()
