"""
Basic tests for ChronoTrack
"""

import os
import tempfile
from pathlib import Path
import pytest
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronotrack import VersionControlSystem


class TestChronoTrack:
    """Test suite for ChronoTrack functionality."""
    
    def test_initialization(self):
        """Test repository initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                vcs = VersionControlSystem()
                assert vcs.initialize() == True
                assert vcs.is_initialized() == True
                assert Path(".chrono").exists()
                assert Path(".chrono/chrono.db").exists()
            finally:
                os.chdir(original_dir)
    
    def test_file_tracking(self):
        """Test file tracking and status detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                vcs = VersionControlSystem()
                vcs.initialize()
                
                # Create test file
                test_file = Path("test.txt")
                test_file.write_text("Test content")
                
                # Check status
                status = vcs.status()
                assert 'added' in status
                assert len(status['added']) == 1
                assert 'test.txt' in status['added']
            finally:
                os.chdir(original_dir)
    
    def test_commit_creation(self):
        """Test commit creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                vcs = VersionControlSystem()
                vcs.initialize()
                
                # Create and commit file
                test_file = Path("test.txt")
                test_file.write_text("Test content")
                
                commit = vcs.commit("Test commit")
                assert commit is not None
                assert commit.commit_message == "Test commit"
                
                # Check clean status
                status = vcs.status()
                assert status['total_changes'] == 0
            finally:
                os.chdir(original_dir)
    
    def test_commit_history(self):
        """Test commit history."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                vcs = VersionControlSystem()
                vcs.initialize()
                
                # Create multiple commits
                for i in range(3):
                    test_file = Path(f"test{i}.txt")
                    test_file.write_text(f"Content {i}")
                    vcs.commit(f"Commit {i}")
                
                # Check history
                commits = vcs.log()
                assert len(commits) == 3
                
                # Check order (newest first)
                assert commits[0].commit_message == "Commit 2"
                assert commits[1].commit_message == "Commit 1"
                assert commits[2].commit_message == "Commit 0"
            finally:
                os.chdir(original_dir)
    
    def test_error_handling(self):
        """Test error handling for uninitialized repository."""
        vcs = VersionControlSystem()
        
        # These should fail gracefully
        status = vcs.status()
        assert 'error' in status
        
        commit = vcs.commit("Test")
        assert commit is None
        
        commits = vcs.log()
        assert len(commits) == 0


if __name__ == '__main__':
    pytest.main([__file__])
