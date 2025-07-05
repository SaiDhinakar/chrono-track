# ChronoTrack – A Minimal CLI-Based Version Control System

[![PyPI version](https://badge.fury.io/py/chronotrack.svg)](https://badge.fury.io/py/chronotrack)
[![Python Support](https://img.shields.io/pypi/pyversions/chronotrack.svg)](https://pypi.org/project/chronotrack/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/chronotrack/chronotrack/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/chronotrack/chronotrack/actions)

A lightweight, object-oriented version tracking system for personal use, inspired by Git but built from scratch with Python and SQLite — no AI, no cloud, just clean version history.

## 🚀 Features

- **Simple Version Control**: Track file changes, create commits, and manage version history
- **Lightweight**: No external dependencies, uses only Python standard library
- **SQLite Backend**: Reliable, file-based database for storing version history
- **CLI Interface**: Easy-to-use command-line interface similar to Git
- **File Backups**: Automatic backup system for safe version management
- **Change Detection**: SHA256-based file change detection
- **Revert Capability**: Safely revert to previous versions
- **Object-Oriented**: Clean, extensible architecture following OOP principles

## 📦 Installation

### Install from PyPI (Recommended)

```bash
pip install chronotrack
```

### Install with uv (Fast)

```bash
uv add chronotrack
```

### Install from Source

```bash
git clone https://github.com/chronotrack/chronotrack.git
cd chronotrack
uv sync
uv run pip install -e .
```

## 🛠️ Quick Start

### Initialize a Repository

```bash
chrono init
```

### Check Status

```bash
chrono status
```

### Create a Commit

```bash
chrono commit "Initial commit"
```

### View Commit History

```bash
chrono log
```

### Revert to Previous Version

```bash
chrono revert 1
```

## 📚 Command Reference

### Repository Management

| Command | Description | Example |
|---------|-------------|---------|
| `chrono init` | Initialize ChronoTrack repository | `chrono init` |
| `chrono init --force` | Force re-initialization | `chrono init --force` |
| `chrono status` | Show current repository status | `chrono status` |
| `chrono stats` | Show repository statistics | `chrono stats` |
| `chrono cleanup` | Clean up and optimize repository | `chrono cleanup` |
| `chrono reset --confirm` | Reset repository (dangerous!) | `chrono reset --confirm` |

### Version Control

| Command | Description | Example |
|---------|-------------|---------|
| `chrono commit "message"` | Create a new commit | `chrono commit "Add new feature"` |
| `chrono log` | Show commit history | `chrono log` |
| `chrono log --limit 5` | Show last 5 commits | `chrono log --limit 5` |
| `chrono show <id>` | Show commit details | `chrono show 3` |
| `chrono revert <id>` | Revert to specific commit | `chrono revert 2` |
| `chrono files` | List all tracked files | `chrono files` |

## 🏗️ Architecture

ChronoTrack follows object-oriented principles with a clean, modular architecture:

```
chronotrack/
├── base_model.py      # Abstract base class and database manager
├── models.py          # Data models (Commit, File, Chrono)
├── file_tracker.py    # File scanning and change detection
├── commit_manager.py  # Commit operations and history management
├── version_control.py # Main facade class
└── cli.py            # Command-line interface
```

### OOP Principles

- **Encapsulation**: Private methods and data hiding
- **Inheritance**: All models inherit from BaseModel
- **Abstraction**: VersionControlSystem acts as facade
- **Polymorphism**: Method overriding in model classes

### Database Schema

#### commits table
- `id`: Primary key (INTEGER)
- `commit_message`: Commit message (TEXT)
- `time`: Timestamp (TIMESTAMP)

#### files table
- `id`: Primary key (INTEGER)
- `file_path`: Relative file path (TEXT)
- `file_hash`: SHA256 hash (TEXT)

#### chrono table
- `id`: Primary key (INTEGER)
- `commit_id`: Foreign key to commits (INTEGER)
- `file_id`: Foreign key to files (INTEGER)
- `status`: Change type ('added', 'modified', 'deleted')
- `time`: Timestamp (TIMESTAMP)

## 🔧 Development

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/chronotrack/chronotrack.git
cd chronotrack

# Install dependencies with uv
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# With uv
uv run pytest

# With pip
python -m pytest
```

### Code Formatting

```bash
# Format code
uv run ruff format src/

# Check linting
uv run ruff check src/
```

### Building Package

```bash
# Build with uv
uv build

# Build with pip
python -m build
```

## 📋 Usage Examples

### Basic Workflow

```bash
# Initialize repository
chrono init

# Check what files are new or changed
chrono status

# Create first commit
chrono commit "Initial project setup"

# Make some changes to files
echo "new content" > file.txt

# Check status again
chrono status

# Commit changes
chrono commit "Updated file.txt"

# View history
chrono log

# Show specific commit
chrono show 1

# Revert to previous version
chrono revert 1
```

### Working with Multiple Files

```bash
# After making changes to multiple files
chrono status
# Output:
# Changes detected: 3 files
# 
# Added files:
#   + new_file.py
# 
# Modified files:
#   M existing_file.py
#   M config.json

# Commit all changes
chrono commit "Add new feature and update config"

# View detailed commit info
chrono show 2
```

### Repository Statistics

```bash
chrono stats
# Output:
# Repository Statistics:
#   Total commits: 5
#   Total tracked files: 12
#   Database size: 98304 bytes
#   Backup size: 156780 bytes
#   Repository path: /home/user/project
```

## 🚫 Ignored Files

ChronoTrack automatically ignores common files and directories:

- `.chrono/` - ChronoTrack data directory
- `.git/` - Git repository data
- `__pycache__/` - Python cache files
- `*.pyc` - Python compiled files
- `.DS_Store` - macOS system files
- `.vscode/` - VS Code settings
- `.idea/` - IntelliJ IDEA settings
- `node_modules/` - Node.js dependencies
- `.env` - Environment files

## 🔒 Safety Features

- **Backup System**: All files are backed up before commits
- **Emergency Backups**: Automatic backups before destructive operations
- **Transaction Safety**: Database operations use ACID transactions
- **Confirmation Required**: Dangerous operations require explicit confirmation
- **Error Handling**: Graceful error handling with informative messages

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/chronotrack/)
- [GitHub Repository](https://github.com/chronotrack/chronotrack)
- [Documentation](https://github.com/chronotrack/chronotrack#readme)
- [Issue Tracker](https://github.com/chronotrack/chronotrack/issues)

## 🙏 Acknowledgments

- Inspired by Git's version control concepts
- Built with Python's excellent standard library
- SQLite for reliable data storage
- The open-source community for inspiration and tools

---

**ChronoTrack** - Simple, reliable version control for personal projects.
