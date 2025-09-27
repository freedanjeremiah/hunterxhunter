# Changelog

All notable changes to Walrus Git CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-27

### Added
- 🚀 Initial release of Walrus Git CLI
- 📤 `walrus push` command for uploading directories to Walrus storage
- 📥 `walrus pull` command for downloading directories from Walrus storage  
- 📋 `walrus list` command for listing tracked repositories
- 🔍 Smart change detection using SHA-256 hashing
- 📦 ZIP compression for efficient storage
- 🏷️ Metadata management with local `.walrus/metadata.json` tracking
- 🎯 Professional CLI with argparse and rich help messages
- 🐍 Python 3.8+ support
- 🔧 Multiple installation methods (pip, setup.py, install.sh)
- 📚 Comprehensive documentation and examples
- 🛡️ MIT License
- ✅ Cross-platform support (Linux, macOS, Windows)
- 🎪 Alternative command shortcuts (walrus-push, walrus-pull, walrus-list)
- 🏗️ Publisher node tools in separate directory
- 📊 Professional packaging with pyproject.toml and setup.py
- 🧪 Test suite for core functionality
- 📄 Professional README with badges and examples
- 🔄 Automated installation script with prerequisite checking

### Technical Details
- Integration with Walrus CLI using `walrus store` and `walrus read` commands
- Error handling for network issues, missing dependencies, and file system errors
- Support for epochs configuration in Walrus storage
- Temporary file management with automatic cleanup
- JSON-based metadata storage and retrieval
- Directory traversal with `.walrus` exclusion
- Command-line interface with subcommands and help system

### Dependencies
- Python 3.8 or higher
- PyYAML for configuration file handling
- Walrus CLI for storage operations
- Standard library modules: argparse, subprocess, zipfile, hashlib, tempfile, pathlib

## [Unreleased]

### Planned Features
- 📈 Version history and tagging support
- 🌿 Branch-like functionality for different versions
- ☁️ Remote metadata storage in Walrus
- 📄 Selective file synchronization
- ⚙️ Configuration file support
- 📊 Progress indicators for large uploads
- 🔐 Encryption options for sensitive data
- 🤖 CI/CD integration examples
- 📱 Web interface for repository management
- 🔗 Integration with other version control systems