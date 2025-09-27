#!/bin/bash
# Professional Installation Script for Walrus Git CLI
# Supports multiple platforms and installation methods

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="walrus-git-cli"
PYTHON_MIN_VERSION="3.8"

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 🐋 Walrus Git CLI Installer                  ║"
    echo "║              Git-like interface for Walrus storage           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        print_error "Please install Python ${PYTHON_MIN_VERSION}+ and try again"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_status "Found Python ${PYTHON_VERSION}"
    
    # Version comparison (simplified)
    if [[ "$PYTHON_VERSION" < "$PYTHON_MIN_VERSION" ]]; then
        print_error "Python ${PYTHON_MIN_VERSION}+ is required, but ${PYTHON_VERSION} is installed"
        exit 1
    fi
    
    print_success "Python version check passed"
}

check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip is not installed"
        print_error "Please install pip and try again"
        exit 1
    fi
    
    print_success "Found pip: $PIP_CMD"
}

check_walrus_cli() {
    print_status "Checking Walrus CLI installation..."
    
    if command -v walrus &> /dev/null; then
        WALRUS_VERSION=$(walrus --version 2>/dev/null || echo "unknown")
        print_success "Walrus CLI found: $WALRUS_VERSION"
    else
        print_warning "Walrus CLI not found in PATH"
        print_warning "Please install Walrus CLI from: https://docs.walrus.storage/"
        print_warning "The package will install but won't function without Walrus CLI"
        
        read -p "Continue installation anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
    fi
}

install_package() {
    print_status "Installing Walrus Git CLI package..."
    
    # Try different installation methods
    if [[ -f "pyproject.toml" ]]; then
        print_status "Installing using modern Python packaging..."
        $PIP_CMD install -e .
    elif [[ -f "setup.py" ]]; then
        print_status "Installing using setup.py..."
        $PIP_CMD install -e .
    else
        print_error "No setup.py or pyproject.toml found"
        print_error "Please run this script from the walrus-git-cli directory"
        exit 1
    fi
    
    print_success "Package installation completed"
}

verify_installation() {
    print_status "Verifying installation..."
    
    # Check if commands are available
    COMMANDS=("walrus" "walrus-push" "walrus-pull" "walrus-list")
    FAILED_COMMANDS=()
    
    for cmd in "${COMMANDS[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            print_success "$cmd command available"
        else
            print_warning "$cmd command not found in PATH"
            FAILED_COMMANDS+=("$cmd")
        fi
    done
    
    if [[ ${#FAILED_COMMANDS[@]} -gt 0 ]]; then
        print_warning "Some commands not found in PATH. You may need to:"
        print_warning "1. Restart your terminal"
        print_warning "2. Add ~/.local/bin to your PATH"
        print_warning "3. Use python -m pip install --user if installed locally"
    fi
    
    # Test basic functionality
    print_status "Testing basic functionality..."
    if walrus --help &> /dev/null; then
        print_success "Basic functionality test passed"
    else
        print_warning "Basic functionality test failed"
    fi
}

show_usage_info() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 Installation Complete!                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "Available commands:"
    echo "  📤 walrus push .           - Push current directory to Walrus"
    echo "  📥 walrus pull .           - Pull from Walrus to current directory"
    echo "  📋 walrus list             - List tracked repositories"
    echo "  ❓ walrus --help           - Show detailed help"
    echo
    echo "Alternative commands:"
    echo "  📤 walrus-push .           - Direct push command"
    echo "  📥 walrus-pull .           - Direct pull command"
    echo "  📋 walrus-list             - Direct list command"
    echo
    echo "Example usage:"
    echo "  cd /path/to/your/project"
    echo "  walrus push .              # Upload project to Walrus"
    echo "  cd /another/location"
    echo "  walrus pull .              # Download project from Walrus"
    echo
    echo "For more information:"
    echo "  📖 Documentation: https://docs.walrus.storage/"
    echo "  🐛 Issues: https://github.com/walrus-storage/walrus-git-cli/issues"
}

handle_error() {
    print_error "Installation failed!"
    print_error "Please check the error messages above and try again"
    print_error "If you need help, please visit: https://github.com/walrus-storage/walrus-git-cli/issues"
    exit 1
}

main() {
    # Set up error handling
    trap handle_error ERR
    
    print_header
    
    # Perform checks
    check_python
    check_pip
    check_walrus_cli
    
    # Install package
    install_package
    
    # Verify installation
    verify_installation
    
    # Show usage information
    show_usage_info
    
    print_success "Walrus Git CLI installation completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Walrus Git CLI Installer"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check-only   Only check prerequisites, don't install"
        echo
        exit 0
        ;;
    --check-only)
        print_header
        check_python
        check_pip
        check_walrus_cli
        print_success "All prerequisites check passed!"
        exit 0
        ;;
esac

# Run main installation
main