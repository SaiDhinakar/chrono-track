"""
Model classes for ChronoTrack.
Implements Commit, File, and Chrono models inheriting from BaseModel.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base_model import BaseModel


class Commit(BaseModel):
    """
    Represents a commit in the version control system.
    Encapsulates commit data and operations.
    """
    
    def __init__(self, commit_message: str = "", commit_id: int = None, 
                 timestamp: datetime = None, db_path: str = ".chrono/chrono.db"):
        super().__init__(db_path)
        self.id = commit_id
        self.commit_message = commit_message
        self.time = timestamp or datetime.now()
    
    def save(self) -> int:
        """Save commit to database. Returns the commit ID."""
        if self.id is None:
            # Insert new commit
            query = "INSERT INTO commits (commit_message, time) VALUES (?, ?)"
            self.id = self._execute_insert(query, (self.commit_message, self.time))
        else:
            # Update existing commit
            query = "UPDATE commits SET commit_message = ?, time = ? WHERE id = ?"
            self._execute_update(query, (self.commit_message, self.time, self.id))
        
        return self.id
    
    def load_by_id(self, commit_id: int) -> Optional['Commit']:
        """Load commit by ID."""
        query = "SELECT * FROM commits WHERE id = ?"
        rows = self._execute_query(query, (commit_id,))
        
        if rows:
            row = rows[0]
            return Commit(
                commit_message=row['commit_message'],
                commit_id=row['id'],
                timestamp=datetime.fromisoformat(row['time']),
                db_path=self.db_path
            )
        return None
    
    def delete(self) -> bool:
        """Delete commit from database."""
        if self.id is None:
            return False
        
        query = "DELETE FROM commits WHERE id = ?"
        affected_rows = self._execute_update(query, (self.id,))
        return affected_rows > 0
    
    def show_info(self) -> str:
        """Return formatted commit information."""
        return f"Commit {self.id}: {self.commit_message} ({self.time.strftime('%Y-%m-%d %H:%M:%S')})"
    
    def get_files(self) -> List['File']:
        """Get all files associated with this commit."""
        query = '''
            SELECT f.* FROM files f
            JOIN chrono c ON f.id = c.file_id
            WHERE c.commit_id = ?
        '''
        rows = self._execute_query(query, (self.id,))
        
        files = []
        for row in rows:
            file_obj = File(
                file_path=row['file_path'],
                file_hash=row['file_hash'],
                file_id=row['id'],
                db_path=self.db_path
            )
            files.append(file_obj)
        
        return files
    
    @classmethod
    def get_all_commits(cls, db_path: str = ".chrono/chrono.db") -> List['Commit']:
        """Get all commits ordered by time (newest first)."""
        instance = cls(db_path=db_path)
        query = "SELECT * FROM commits ORDER BY time DESC"
        rows = instance._execute_query(query)
        
        commits = []
        for row in rows:
            commit = Commit(
                commit_message=row['commit_message'],
                commit_id=row['id'],
                timestamp=datetime.fromisoformat(row['time']),
                db_path=db_path
            )
            commits.append(commit)
        
        return commits


class File(BaseModel):
    """
    Represents a tracked file in the version control system.
    Encapsulates file data and operations.
    """
    
    def __init__(self, file_path: str = "", file_hash: str = "", 
                 file_id: int = None, db_path: str = ".chrono/chrono.db"):
        super().__init__(db_path)
        self.id = file_id
        self.file_path = file_path
        self.file_hash = file_hash
    
    def save(self) -> int:
        """Save file to database. Returns the file ID."""
        if self.id is None:
            # Check if file already exists
            existing_file = self.load_by_path(self.file_path)
            if existing_file:
                # Update existing file
                self.id = existing_file.id
                query = "UPDATE files SET file_hash = ? WHERE id = ?"
                self._execute_update(query, (self.file_hash, self.id))
            else:
                # Insert new file
                query = "INSERT INTO files (file_path, file_hash) VALUES (?, ?)"
                self.id = self._execute_insert(query, (self.file_path, self.file_hash))
        else:
            # Update existing file
            query = "UPDATE files SET file_path = ?, file_hash = ? WHERE id = ?"
            self._execute_update(query, (self.file_path, self.file_hash, self.id))
        
        return self.id
    
    def load_by_id(self, file_id: int) -> Optional['File']:
        """Load file by ID."""
        query = "SELECT * FROM files WHERE id = ?"
        rows = self._execute_query(query, (file_id,))
        
        if rows:
            row = rows[0]
            return File(
                file_path=row['file_path'],
                file_hash=row['file_hash'],
                file_id=row['id'],
                db_path=self.db_path
            )
        return None
    
    def load_by_path(self, file_path: str) -> Optional['File']:
        """Load file by path."""
        query = "SELECT * FROM files WHERE file_path = ?"
        rows = self._execute_query(query, (file_path,))
        
        if rows:
            row = rows[0]
            return File(
                file_path=row['file_path'],
                file_hash=row['file_hash'],
                file_id=row['id'],
                db_path=self.db_path
            )
        return None
    
    def delete(self) -> bool:
        """Delete file from database."""
        if self.id is None:
            return False
        
        query = "DELETE FROM files WHERE id = ?"
        affected_rows = self._execute_update(query, (self.id,))
        return affected_rows > 0
    
    def show_info(self) -> str:
        """Return formatted file information."""
        return f"File {self.id}: {self.file_path} (hash: {self.file_hash[:8]}...)"
    
    @classmethod
    def get_all_files(cls, db_path: str = ".chrono/chrono.db") -> List['File']:
        """Get all tracked files."""
        instance = cls(db_path=db_path)
        query = "SELECT * FROM files ORDER BY file_path"
        rows = instance._execute_query(query)
        
        files = []
        for row in rows:
            file_obj = File(
                file_path=row['file_path'],
                file_hash=row['file_hash'],
                file_id=row['id'],
                db_path=db_path
            )
            files.append(file_obj)
        
        return files


class Chrono(BaseModel):
    """
    Represents the relationship between commits and files.
    Junction table model with status tracking.
    """
    
    def __init__(self, commit_id: int = None, file_id: int = None, 
                 status: str = "", chrono_id: int = None, 
                 timestamp: datetime = None, db_path: str = ".chrono/chrono.db"):
        super().__init__(db_path)
        self.id = chrono_id
        self.commit_id = commit_id
        self.file_id = file_id
        self.status = status  # 'added', 'modified', 'deleted'
        self.time = timestamp or datetime.now()
    
    def save(self) -> int:
        """Save chrono record to database. Returns the chrono ID."""
        if self.id is None:
            # Insert new chrono record
            query = "INSERT INTO chrono (commit_id, file_id, status, time) VALUES (?, ?, ?, ?)"
            self.id = self._execute_insert(query, (self.commit_id, self.file_id, self.status, self.time))
        else:
            # Update existing chrono record
            query = "UPDATE chrono SET commit_id = ?, file_id = ?, status = ?, time = ? WHERE id = ?"
            self._execute_update(query, (self.commit_id, self.file_id, self.status, self.time, self.id))
        
        return self.id
    
    def load_by_id(self, chrono_id: int) -> Optional['Chrono']:
        """Load chrono record by ID."""
        query = "SELECT * FROM chrono WHERE id = ?"
        rows = self._execute_query(query, (chrono_id,))
        
        if rows:
            row = rows[0]
            return Chrono(
                commit_id=row['commit_id'],
                file_id=row['file_id'],
                status=row['status'],
                chrono_id=row['id'],
                timestamp=datetime.fromisoformat(row['time']),
                db_path=self.db_path
            )
        return None
    
    def delete(self) -> bool:
        """Delete chrono record from database."""
        if self.id is None:
            return False
        
        query = "DELETE FROM chrono WHERE id = ?"
        affected_rows = self._execute_update(query, (self.id,))
        return affected_rows > 0
    
    def show_info(self) -> str:
        """Return formatted chrono information."""
        return f"Chrono {self.id}: Commit {self.commit_id} -> File {self.file_id} ({self.status})"
    
    def get_file(self) -> Optional[File]:
        """Get the file associated with this chrono record."""
        if self.file_id is None:
            return None
        
        file_obj = File(db_path=self.db_path)
        return file_obj.load_by_id(self.file_id)
    
    def get_commit(self) -> Optional[Commit]:
        """Get the commit associated with this chrono record."""
        if self.commit_id is None:
            return None
        
        commit_obj = Commit(db_path=self.db_path)
        return commit_obj.load_by_id(self.commit_id)
    
    @classmethod
    def get_by_commit(cls, commit_id: int, db_path: str = ".chrono/chrono.db") -> List['Chrono']:
        """Get all chrono records for a specific commit."""
        instance = cls(db_path=db_path)
        query = "SELECT * FROM chrono WHERE commit_id = ? ORDER BY time"
        rows = instance._execute_query(query, (commit_id,))
        
        chronos = []
        for row in rows:
            chrono = Chrono(
                commit_id=row['commit_id'],
                file_id=row['file_id'],
                status=row['status'],
                chrono_id=row['id'],
                timestamp=datetime.fromisoformat(row['time']),
                db_path=db_path
            )
            chronos.append(chrono)
        
        return chronos
