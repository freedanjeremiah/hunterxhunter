# Contributing to Walrus Git CLI

Thank you for your interest in contributing to Walrus Git CLI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/walrus-storage/walrus-git-cli/issues) to report bugs
- Search existing issues before creating a new one
- Provide detailed information including:
  - Operating system and version
  - Python version
  - Walrus CLI version
  - Steps to reproduce the issue
  - Expected vs actual behavior

### Suggesting Features
- Open a [GitHub Discussion](https://github.com/walrus-storage/walrus-git-cli/discussions) for feature ideas
- Explain the use case and benefits
- Consider backwards compatibility

### Code Contributions

#### Setup Development Environment
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/walrus-git-cli.git
cd walrus-git-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks (optional)
pre-commit install
```

#### Making Changes
1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Add tests for new functionality
4. Run the test suite: `pytest`
5. Format code: `black walrus_cli.py`
6. Check types: `mypy walrus_cli.py`
7. Commit your changes: `git commit -am 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

#### Code Style
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Add type hints where appropriate
- Write descriptive commit messages
- Keep functions focused and well-documented

#### Testing
- Write tests for new features and bug fixes
- Ensure all tests pass before submitting PR
- Aim for good test coverage
- Test on multiple platforms when possible

## 📋 Development Guidelines

### Code Organization
- Keep the main CLI logic in `walrus_cli.py`
- Publisher tools go in the `publisher/` directory
- Tests go in the `tests/` directory
- Documentation updates go in `README.md`

### Commit Messages
Use conventional commit format:
```
feat: add new feature
fix: resolve bug in push command
docs: update installation instructions
test: add tests for pull functionality
refactor: improve error handling
```

### Pull Request Process
1. Update documentation if needed
2. Add tests for new functionality
3. Ensure CI passes
4. Request review from maintainers
5. Address feedback
6. Squash commits if requested

## 🛠️ Technical Guidelines

### Dependencies
- Minimize external dependencies
- Use standard library when possible
- Document any new requirements in `requirements.txt`
- Consider backwards compatibility

### Error Handling
- Provide helpful error messages
- Handle edge cases gracefully
- Log errors appropriately
- Don't expose sensitive information in error messages

### Performance
- Consider memory usage for large directories
- Optimize for common use cases
- Profile performance-critical code
- Document performance characteristics

### Security
- Be cautious with file system operations
- Validate user inputs
- Don't log sensitive information
- Consider security implications of changes

## 📝 Documentation

### Code Documentation
- Add docstrings to functions and classes
- Document complex algorithms
- Include usage examples
- Keep documentation up to date

### User Documentation
- Update README.md for user-facing changes
- Add examples for new features
- Update troubleshooting section
- Consider creating tutorials

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_walrus_cli.py

# Run with coverage
pytest --cov=walrus_cli

# Run integration tests
pytest tests/integration/
```

### Test Types
- **Unit tests**: Test individual functions
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Test with large data

### Test Data
- Use temporary directories for file operations
- Clean up test artifacts
- Don't commit test data to repository
- Mock external dependencies when appropriate

## 🚀 Release Process

### Version Numbering
- Follow [Semantic Versioning](https://semver.org/)
- MAJOR.MINOR.PATCH format
- Update version in `setup.py` and `pyproject.toml`

### Release Checklist
1. Update CHANGELOG.md
2. Update version numbers
3. Run full test suite
4. Update documentation
5. Create release branch
6. Tag release
7. Build distribution
8. Upload to PyPI
9. Create GitHub release

## 📞 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/walrus-storage/walrus-git-cli/discussions)
- **Chat**: Join the Walrus community Discord
- **Email**: Contact maintainers for sensitive issues

## 🏆 Recognition

Contributors will be:
- Listed in the repository contributors
- Mentioned in release notes
- Added to CONTRIBUTORS.md file
- Given credit in documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Walrus Git CLI! 🙏