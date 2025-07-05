"""
File tracking system for ChronoTrack.
Handles file scanning, change detection, and hash computation.
"""

import os
import hashlib
from typing import Dict, List, Set, Tuple
from pathlib import Path
from .models import File


class FileTracker:
    """
    Handles file scanning and change detection.
    Implements encapsulation of file tracking logic.
    """
    
    def __init__(self, root_dir: str = ".", db_path: str = ".chrono/chrono.db"):
        self.root_dir = Path(root_dir).resolve()
        self.db_path = db_path
        self.ignore_patterns = {
            '.chrono',
            '.git',
            '__pycache__',
            '.pyc',
            '.DS_Store',
            '.vscode',
            '.idea',
            'node_modules',
            '.env'
        }
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if a file or directory should be ignored."""
        # Check if any part of the path matches ignore patterns
        for part in file_path.parts:
            if part in self.ignore_patterns:
                return True
        
        # Check file extensions
        if file_path.suffix in {'.pyc', '.pyo', '.pyd'}:
            return True
        
        # Check if it's a hidden file (starts with .)
        if file_path.name.startswith('.') and file_path.name not in {'.gitignore'}:
            return True
        
        return False
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (IOError, OSError) as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            return ""
    
    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path from root directory."""
        try:
            return str(file_path.relative_to(self.root_dir))
        except ValueError:
            # If file is not under root_dir, return absolute path
            return str(file_path)
    
    def scan_directory(self) -> Dict[str, str]:
        """
        Scan the directory and return a dictionary of {relative_path: hash}.
        Implements directory traversal with ignore patterns.
        """
        file_hashes = {}
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                relative_path = self._get_relative_path(file_path)
                file_hash = self._compute_file_hash(file_path)
                
                if file_hash:  # Only include files we could hash
                    file_hashes[relative_path] = file_hash
        
        return file_hashes
    
    def get_tracked_files(self) -> Dict[str, str]:
        """Get all currently tracked files from database."""
        tracked_files = {}
        
        try:
            all_files = File.get_all_files(self.db_path)
            for file_obj in all_files:
                tracked_files[file_obj.file_path] = file_obj.file_hash
        except Exception as e:
            print(f"Warning: Could not load tracked files: {e}")
        
        return tracked_files
    
    def detect_changes(self) -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
        """
        Detect changes between current directory state and tracked files.
        Returns (added_files, modified_files, deleted_files).
        """
        current_files = self.scan_directory()
        tracked_files = self.get_tracked_files()
        
        # Convert to sets for easier comparison
        current_paths = set(current_files.keys())
        tracked_paths = set(tracked_files.keys())
        
        # Find added files (in current but not tracked)
        added_paths = current_paths - tracked_paths
        added_files = {path: current_files[path] for path in added_paths}
        
        # Find deleted files (in tracked but not current)
        deleted_paths = tracked_paths - current_paths
        deleted_files = list(deleted_paths)
        
        # Find modified files (in both but with different hashes)
        common_paths = current_paths & tracked_paths
        modified_files = {}
        for path in common_paths:
            if current_files[path] != tracked_files[path]:
                modified_files[path] = current_files[path]
        
        return added_files, modified_files, deleted_files
    
    def has_changes(self) -> bool:
        """Check if there are any changes in the working directory."""
        added, modified, deleted = self.detect_changes()
        return len(added) > 0 or len(modified) > 0 or len(deleted) > 0
    
    def get_status_summary(self) -> Dict[str, any]:
        """Get a summary of the current repository status."""
        added_files, modified_files, deleted_files = self.detect_changes()
        
        return {
            'added': list(added_files.keys()),
            'modified': list(modified_files.keys()),
            'deleted': deleted_files,
            'total_changes': len(added_files) + len(modified_files) + len(deleted_files)
        }
    
    def get_file_content(self, file_path: str) -> str:
        """Get the content of a file for backup/restore purposes."""
        full_path = self.root_dir / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Handle binary files
            with open(full_path, 'rb') as f:
                return f.read().hex()
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    
    def write_file_content(self, file_path: str, content: str, is_binary: bool = False):
        """Write content to a file."""
        full_path = self.root_dir / file_path
        
        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if is_binary:
                # Content is hex-encoded binary data
                with open(full_path, 'wb') as f:
                    f.write(bytes.fromhex(content))
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        except (IOError, OSError) as e:
            print(f"Error writing file {file_path}: {e}")
    
    def backup_file(self, file_path: str, backup_dir: str = ".chrono/backups"):
        """Create a backup of a file."""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        source_path = self.root_dir / file_path
        if source_path.exists():
            # Create backup with timestamp
            import time
            timestamp = str(int(time.time()))
            backup_file_path = backup_path / f"{file_path.replace('/', '_')}_{timestamp}"
            
            try:
                import shutil
                shutil.copy2(source_path, backup_file_path)
                return str(backup_file_path)
            except (IOError, OSError) as e:
                print(f"Error backing up file {file_path}: {e}")
                return None
        
        return None
