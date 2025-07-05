#!/usr/bin/env python3
"""
ChronoTrack CLI - Main entry point for the chrono command
"""

import argparse
import sys
from pathlib import Path

from .version_control import VersionControlSystem


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chrono",
        description="ChronoTrack - A minimal CLI-based version control system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  chrono init                    Initialize tracking in current directory
  chrono status                  Show current status
  chrono commit "Fix bug"        Create a commit with message
  chrono log                     Show commit history
  chrono log --limit 5           Show last 5 commits
  chrono revert 3                Revert to commit ID 3
  chrono show 2                  Show details of commit ID 2
  chrono files                   List all tracked files
  chrono stats                   Show repository statistics
  chrono cleanup                 Clean up and optimize repository
  chrono reset --confirm         Reset repository (dangerous!)
        """
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize ChronoTrack repository')
    init_parser.add_argument('--force', action='store_true', 
                           help='Force initialization even if already initialized')
    
    # Status command
    subparsers.add_parser('status', help='Show current repository status')
    
    # Commit command
    commit_parser = subparsers.add_parser('commit', help='Create a new commit')
    commit_parser.add_argument('message', help='Commit message')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Show commit history')
    log_parser.add_argument('--limit', type=int, default=10, 
                          help='Maximum number of commits to show (default: 10)')
    
    # Revert command
    revert_parser = subparsers.add_parser('revert', help='Revert to a specific commit')
    revert_parser.add_argument('commit_id', type=int, help='Commit ID to revert to')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show detailed commit information')
    show_parser.add_argument('commit_id', type=int, help='Commit ID to show')
    
    # Files command
    subparsers.add_parser('files', help='List all tracked files')
    
    # Stats command
    subparsers.add_parser('stats', help='Show repository statistics')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Clean up and optimize repository')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset repository (dangerous!)')
    reset_parser.add_argument('--confirm', action='store_true', 
                            help='Confirm the reset operation')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize version control system
    try:
        vcs = VersionControlSystem()
    except Exception as e:
        print(f"Error initializing ChronoTrack: {e}")
        sys.exit(1)
    
    # Handle commands
    try:
        if args.command == 'init':
            success = vcs.initialize(force=args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == 'status':
            status = vcs.status()
            sys.exit(0 if 'error' not in status else 1)
        
        elif args.command == 'commit':
            commit = vcs.commit(args.message)
            sys.exit(0 if commit else 1)
        
        elif args.command == 'log':
            commits = vcs.log(limit=args.limit)
            sys.exit(0)
        
        elif args.command == 'revert':
            success = vcs.revert(args.commit_id)
            sys.exit(0 if success else 1)
        
        elif args.command == 'show':
            details = vcs.show_commit(args.commit_id)
            sys.exit(0 if details else 1)
        
        elif args.command == 'files':
            files = vcs.list_files()
            sys.exit(0)
        
        elif args.command == 'stats':
            stats = vcs.get_stats()
            sys.exit(0 if 'error' not in stats else 1)
        
        elif args.command == 'cleanup':
            success = vcs.cleanup()
            sys.exit(0 if success else 1)
        
        elif args.command == 'reset':
            success = vcs.reset(confirm=args.confirm)
            sys.exit(0 if success else 1)
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
