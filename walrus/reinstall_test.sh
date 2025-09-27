#!/bin/bash
# Quick reinstall and test script

echo "🔄 Reinstalling Walrus Git CLI with updates..."

# Reinstall the package
pipx install -e . --force

echo "✅ Package reinstalled successfully!"
echo ""
echo "🧪 Testing the commands:"
echo ""

echo "1. Testing walrus-push --help"
walrus-push --help

echo ""
echo "2. Testing walrus-pull --help"  
walrus-pull --help

echo ""
echo "3. Testing walrus-list --help"
walrus-list --help

echo ""
echo "🎯 Available commands after installation:"
echo "  walrus-push .     # Push current directory"
echo "  walrus-pull .     # Pull to current directory"
echo "  walrus-list       # List repositories"
echo "  walrus            # Full CLI interface"