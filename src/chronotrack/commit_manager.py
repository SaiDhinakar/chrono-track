"""
Commit management system for ChronoTrack.
Handles commit creation, logging, and revert operations.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from .models import Commit, File, Chrono
from .file_tracker import FileTracker


class CommitManager:
    """
    Manages commit operations and version history.
    Encapsulates commit-related business logic.
    """
    
    def __init__(self, root_dir: str = ".", db_path: str = ".chrono/chrono.db"):
        self.root_dir = Path(root_dir).resolve()
        self.db_path = db_path
        self.file_tracker = FileTracker(root_dir, db_path)
        self.backup_dir = Path(".chrono/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_commit(self, message: str) -> Optional[Commit]:
        """
        Create a new commit with the current state of files.
        Returns the created commit or None if no changes.
        """
        # Check if there are any changes
        if not self.file_tracker.has_changes():
            print("No changes to commit.")
            return None
        
        # Get current changes
        added_files, modified_files, deleted_files = self.file_tracker.detect_changes()
        
        # Create commit object
        commit = Commit(commit_message=message, db_path=self.db_path)
        commit_id = commit.save()
        
        # Process added files
        for file_path, file_hash in added_files.items():
            file_obj = File(file_path=file_path, file_hash=file_hash, db_path=self.db_path)
            file_id = file_obj.save()
            
            # Create chrono record
            chrono = Chrono(
                commit_id=commit_id,
                file_id=file_id,
                status='added',
                db_path=self.db_path
            )
            chrono.save()
            
            # Backup the file
            self._backup_file_for_commit(file_path, commit_id)
        
        # Process modified files
        for file_path, file_hash in modified_files.items():
            # Update file hash
            file_obj = File(db_path=self.db_path)
            existing_file = file_obj.load_by_path(file_path)
            
            if existing_file:
                existing_file.file_hash = file_hash
                existing_file.save()
                
                # Create chrono record
                chrono = Chrono(
                    commit_id=commit_id,
                    file_id=existing_file.id,
                    status='modified',
                    db_path=self.db_path
                )
                chrono.save()
                
                # Backup the file
                self._backup_file_for_commit(file_path, commit_id)
        
        # Process deleted files
        for file_path in deleted_files:
            file_obj = File(db_path=self.db_path)
            existing_file = file_obj.load_by_path(file_path)
            
            if existing_file:
                # Create chrono record for deletion
                chrono = Chrono(
                    commit_id=commit_id,
                    file_id=existing_file.id,
                    status='deleted',
                    db_path=self.db_path
                )
                chrono.save()
        
        print(f"Commit created successfully: {commit.show_info()}")
        print(f"  Added: {len(added_files)} files")
        print(f"  Modified: {len(modified_files)} files")
        print(f"  Deleted: {len(deleted_files)} files")
        
        return commit
    
    def _backup_file_for_commit(self, file_path: str, commit_id: int):
        """Create a backup of a file for a specific commit."""
        backup_subdir = self.backup_dir / str(commit_id)
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        source_path = self.root_dir / file_path
        if source_path.exists():
            # Create backup maintaining directory structure
            backup_file_path = backup_subdir / file_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                import shutil
                shutil.copy2(source_path, backup_file_path)
            except (IOError, OSError) as e:
                print(f"Warning: Could not backup file {file_path}: {e}")
    
    def get_commit_history(self, limit: int = None) -> List[Commit]:
        """Get commit history, optionally limited to a number of commits."""
        commits = Commit.get_all_commits(self.db_path)
        
        if limit:
            commits = commits[:limit]
        
        return commits
    
    def get_commit_details(self, commit_id: int) -> Optional[Dict]:
        """Get detailed information about a specific commit."""
        commit = Commit(db_path=self.db_path)
        commit_obj = commit.load_by_id(commit_id)
        
        if not commit_obj:
            return None
        
        # Get chrono records for this commit
        chrono_records = Chrono.get_by_commit(commit_id, self.db_path)
        
        details = {
            'commit': commit_obj,
            'files': {
                'added': [],
                'modified': [],
                'deleted': []
            },
            'total_changes': len(chrono_records)
        }
        
        for chrono in chrono_records:
            file_obj = chrono.get_file()
            if file_obj:
                details['files'][chrono.status].append({
                    'path': file_obj.file_path,
                    'hash': file_obj.file_hash
                })
        
        return details
    
    def revert_to_commit(self, commit_id: int) -> bool:
        """
        Revert the working directory to a specific commit state.
        This is a destructive operation that overwrites current files.
        """
        commit_details = self.get_commit_details(commit_id)
        if not commit_details:
            print(f"Commit {commit_id} not found.")
            return False
        
        print(f"Reverting to commit {commit_id}...")
        print("WARNING: This will overwrite current files!")
        
        # Get the backup directory for this commit
        backup_dir = self.backup_dir / str(commit_id)
        
        if not backup_dir.exists():
            print(f"Backup directory for commit {commit_id} not found.")
            return False
        
        try:
            # First, backup current state
            self._create_emergency_backup()
            
            # Get all files that were part of this commit
            chrono_records = Chrono.get_by_commit(commit_id, self.db_path)
            
            # Restore files from backup
            for chrono in chrono_records:
                file_obj = chrono.get_file()
                if file_obj and chrono.status != 'deleted':
                    backup_file_path = backup_dir / file_obj.file_path
                    target_file_path = self.root_dir / file_obj.file_path
                    
                    if backup_file_path.exists():
                        # Create target directory if it doesn't exist
                        target_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        import shutil
                        shutil.copy2(backup_file_path, target_file_path)
                        print(f"Restored: {file_obj.file_path}")
                    else:
                        print(f"Warning: Backup not found for {file_obj.file_path}")
                
                # Handle deleted files (remove them from working directory)
                elif chrono.status == 'deleted':
                    file_obj = chrono.get_file()
                    if file_obj:
                        target_file_path = self.root_dir / file_obj.file_path
                        if target_file_path.exists():
                            target_file_path.unlink()
                            print(f"Removed: {file_obj.file_path}")
            
            print(f"Successfully reverted to commit {commit_id}")
            return True
            
        except Exception as e:
            print(f"Error during revert: {e}")
            return False
    
    def _create_emergency_backup(self):
        """Create an emergency backup before destructive operations."""
        emergency_dir = self.backup_dir / "emergency" / str(int(datetime.now().timestamp()))
        emergency_dir.mkdir(parents=True, exist_ok=True)
        
        current_files = self.file_tracker.scan_directory()
        
        for file_path in current_files.keys():
            source_path = self.root_dir / file_path
            backup_path = emergency_dir / file_path
            
            if source_path.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    import shutil
                    shutil.copy2(source_path, backup_path)
                except (IOError, OSError) as e:
                    print(f"Warning: Could not create emergency backup for {file_path}: {e}")
        
        print(f"Emergency backup created at: {emergency_dir}")
    
    def show_status(self) -> Dict[str, any]:
        """Show the current status of the repository."""
        status = self.file_tracker.get_status_summary()
        
        if status['total_changes'] == 0:
            print("Working directory is clean.")
        else:
            print(f"Changes detected: {status['total_changes']} files")
            
            if status['added']:
                print("\nAdded files:")
                for file_path in status['added']:
                    print(f"  + {file_path}")
            
            if status['modified']:
                print("\nModified files:")
                for file_path in status['modified']:
                    print(f"  M {file_path}")
            
            if status['deleted']:
                print("\nDeleted files:")
                for file_path in status['deleted']:
                    print(f"  D {file_path}")
        
        return status
    
    def show_log(self, limit: int = 10):
        """Display commit history."""
        commits = self.get_commit_history(limit)
        
        if not commits:
            print("No commits found.")
            return
        
        print(f"Showing {len(commits)} commits:")
        print("-" * 50)
        
        for commit in commits:
            print(f"Commit {commit.id}: {commit.commit_message}")
            print(f"Date: {commit.time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show file changes for this commit
            details = self.get_commit_details(commit.id)
            if details:
                changes = details['files']
                change_summary = []
                
                if changes['added']:
                    change_summary.append(f"{len(changes['added'])} added")
                if changes['modified']:
                    change_summary.append(f"{len(changes['modified'])} modified")
                if changes['deleted']:
                    change_summary.append(f"{len(changes['deleted'])} deleted")
                
                if change_summary:
                    print(f"Changes: {', '.join(change_summary)}")
            
            print("-" * 50)
