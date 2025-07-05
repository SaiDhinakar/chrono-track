"""
ChronoTrack - A Minimal CLI-Based Version Control System
"""

__version__ = "0.1.0"
__author__ = "ChronoTrack Team"
__email__ = "contact@chronotrack.dev"
__description__ = "A lightweight, object-oriented version tracking system for personal use"

from .version_control import VersionControlSystem
from .models import Commit, File, Chrono
from .file_tracker import FileTracker
from .commit_manager import CommitManager

__all__ = [
    "VersionControlSystem",
    "Commit",
    "File", 
    "Chrono",
    "FileTracker",
    "CommitManager",
]
