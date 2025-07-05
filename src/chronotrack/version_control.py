"""
Main Version Control System facade for ChronoTrack.
Provides a unified interface to all version control operations.
Implements the Facade pattern for abstraction.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict

from .base_model import DatabaseManager
from .models import Commit, File, Chrono
from .file_tracker import FileTracker
from .commit_manager import CommitManager


class VersionControlSystem:
    """
    Facade class that provides a unified interface to all ChronoTrack operations.
    Implements abstraction by hiding complex subsystem interactions.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.chrono_dir = self.root_dir / ".chrono"
        self.db_path = str(self.chrono_dir / "chrono.db")
        
        # Initialize subsystems
        self.db_manager = DatabaseManager(self.db_path)
        self.file_tracker = FileTracker(str(self.root_dir), self.db_path)
        self.commit_manager = CommitManager(str(self.root_dir), self.db_path)
        
        # Track if repository is initialized
        self._is_initialized = self.chrono_dir.exists()
    
    def is_initialized(self) -> bool:
        """Check if the repository is initialized."""
        return self._is_initialized and (self.chrono_dir / "chrono.db").exists()
    
    def initialize(self, force: bool = False) -> bool:
        """
        Initialize ChronoTrack repository in the current directory.
        
        Args:
            force: If True, reinitialize even if already initialized
            
        Returns:
            bool: True if initialization was successful
        """
        if self.is_initialized() and not force:
            print(f"ChronoTrack repository already initialized in {self.root_dir}")
            return True
        
        try:
            # Create .chrono directory
            self.chrono_dir.mkdir(exist_ok=True)
            
            # Initialize database
            self.db_manager.initialize_database()
            
            # Create subdirectories
            (self.chrono_dir / "backups").mkdir(exist_ok=True)
            (self.chrono_dir / "config").mkdir(exist_ok=True)
            
            # Create initial configuration
            self._create_initial_config()
            
            self._is_initialized = True
            print(f"Initialized ChronoTrack repository in {self.root_dir}")
            print(f"Database created at: {self.db_path}")
            
            return True
            
        except Exception as e:
            print(f"Error initializing repository: {e}")
            return False
    
    def _create_initial_config(self):
        """Create initial configuration file."""
        config = {
            "version": "1.0.0",
            "created": str(Path.cwd()),
            "ignore_patterns": [
                ".chrono",
                ".git",
                "__pycache__",
                "*.pyc",
                ".DS_Store"
            ]
        }
        
        import json
        config_path = self.chrono_dir / "config" / "chrono.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def status(self) -> Dict[str, any]:
        """
        Get the current status of the repository.
        
        Returns:
            Dict containing status information
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return {'error': 'Not initialized'}
        
        return self.commit_manager.show_status()
    
    def commit(self, message: str) -> Optional[Commit]:
        """
        Create a new commit with the given message.
        
        Args:
            message: Commit message
            
        Returns:
            Commit object if successful, None otherwise
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return None
        
        if not message.strip():
            print("Error: Commit message cannot be empty.")
            return None
        
        return self.commit_manager.create_commit(message)
    
    def log(self, limit: int = 10) -> List[Commit]:
        """
        Show commit history.
        
        Args:
            limit: Maximum number of commits to show
            
        Returns:
            List of Commit objects
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return []
        
        self.commit_manager.show_log(limit)
        return self.commit_manager.get_commit_history(limit)
    
    def revert(self, commit_id: int) -> bool:
        """
        Revert to a specific commit.
        
        Args:
            commit_id: ID of the commit to revert to
            
        Returns:
            bool: True if revert was successful
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return False
        
        return self.commit_manager.revert_to_commit(commit_id)
    
    def show_commit(self, commit_id: int) -> Optional[Dict]:
        """
        Show detailed information about a specific commit.
        
        Args:
            commit_id: ID of the commit to show
            
        Returns:
            Dict containing commit details
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return None
        
        details = self.commit_manager.get_commit_details(commit_id)
        
        if not details:
            print(f"Commit {commit_id} not found.")
            return None
        
        commit = details['commit']
        files = details['files']
        
        print(f"Commit {commit.id}: {commit.commit_message}")
        print(f"Date: {commit.time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total changes: {details['total_changes']}")
        
        if files['added']:
            print(f"\nAdded files ({len(files['added'])}):")
            for file_info in files['added']:
                print(f"  + {file_info['path']}")
        
        if files['modified']:
            print(f"\nModified files ({len(files['modified'])}):")
            for file_info in files['modified']:
                print(f"  M {file_info['path']}")
        
        if files['deleted']:
            print(f"\nDeleted files ({len(files['deleted'])}):")
            for file_info in files['deleted']:
                print(f"  D {file_info['path']}")
        
        return details
    
    def list_files(self) -> List[File]:
        """
        List all tracked files.
        
        Returns:
            List of File objects
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return []
        
        files = File.get_all_files(self.db_path)
        
        if not files:
            print("No files are currently tracked.")
            return []
        
        print(f"Tracked files ({len(files)}):")
        for file_obj in files:
            print(f"  {file_obj.file_path} (hash: {file_obj.file_hash[:8]}...)")
        
        return files
    
    def cleanup(self) -> bool:
        """
        Clean up old backups and optimize the database.
        
        Returns:
            bool: True if cleanup was successful
        """
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository. Run 'chrono init' first.")
            return False
        
        try:
            # Vacuum the database to reclaim space
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
            
            print("Database optimized.")
            
            # Clean up old emergency backups (keep only last 5)
            emergency_dir = self.chrono_dir / "backups" / "emergency"
            if emergency_dir.exists():
                emergency_backups = sorted([d for d in emergency_dir.iterdir() if d.is_dir()])
                if len(emergency_backups) > 5:
                    import shutil
                    for backup_dir in emergency_backups[:-5]:
                        shutil.rmtree(backup_dir)
                        print(f"Cleaned up old emergency backup: {backup_dir.name}")
            
            return True
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False
    
    def reset(self, confirm: bool = False) -> bool:
        """
        Reset the repository (dangerous operation).
        
        Args:
            confirm: Must be True to actually perform the reset
            
        Returns:
            bool: True if reset was successful
        """
        if not confirm:
            print("Error: Reset operation requires confirmation.")
            print("This will delete all commit history and tracked files.")
            print("Use reset with --confirm flag if you're sure.")
            return False
        
        if not self.is_initialized():
            print("Error: Not a ChronoTrack repository.")
            return False
        
        try:
            # Reset database
            self.db_manager.reset_database()
            
            # Clean up backups
            import shutil
            backup_dir = self.chrono_dir / "backups"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                backup_dir.mkdir()
            
            print("Repository reset successfully.")
            print("All commit history and backups have been deleted.")
            
            return True
            
        except Exception as e:
            print(f"Error during reset: {e}")
            return False
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get repository statistics.
        
        Returns:
            Dict containing repository statistics
        """
        if not self.is_initialized():
            return {'error': 'Not initialized'}
        
        try:
            commits = Commit.get_all_commits(self.db_path)
            files = File.get_all_files(self.db_path)
            
            # Calculate database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # Calculate backup size
            backup_size = 0
            backup_dir = self.chrono_dir / "backups"
            if backup_dir.exists():
                for root, dirs, files_list in os.walk(backup_dir):
                    for file in files_list:
                        backup_size += os.path.getsize(os.path.join(root, file))
            
            stats = {
                'total_commits': len(commits),
                'total_files': len(files),
                'database_size': db_size,
                'backup_size': backup_size,
                'repository_path': str(self.root_dir),
                'chrono_path': str(self.chrono_dir)
            }
            
            print(f"Repository Statistics:")
            print(f"  Total commits: {stats['total_commits']}")
            print(f"  Total tracked files: {stats['total_files']}")
            print(f"  Database size: {stats['database_size']} bytes")
            print(f"  Backup size: {stats['backup_size']} bytes")
            print(f"  Repository path: {stats['repository_path']}")
            
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {'error': str(e)}
