#!/usr/bin/env python3
"""
Quick start script for Walrus Publisher Node
Minimal setup and launch script
"""

import subprocess
import sys
import time


def check_walrus():
    """Quick check if Walrus CLI is available"""
    try:
        result = subprocess.run(['walrus', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Walrus CLI: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Walrus CLI not found!")
        print("Please install Walrus CLI first: https://docs.walrus.storage/")
        return False


def quick_setup():
    """Minimal setup - just generate wallet and get basic info"""
    print("🚀 Walrus Publisher Quick Start")
    print("=" * 40)
    
    if not check_walrus():
        return False
    
    print("\n📊 Getting system information...")
    try:
        result = subprocess.run(['walrus', 'info'], 
                              capture_output=True, text=True, check=True)
        print("System Info:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not get system info: {e}")
    
    return True


def run_daemon(port=8080):
    """Run the publisher daemon"""
    address = f"0.0.0.0:{port}"
    
    print(f"\n🚀 Starting Walrus Publisher Daemon on {address}")
    print("This will run a combined publisher + aggregator service")
    print("Your node will be available for client connections")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        subprocess.run(['walrus', 'daemon', address], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start daemon: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Daemon stopped")
        return True
    except FileNotFoundError:
        print("❌ Walrus CLI not found")
        return False


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup':
            quick_setup()
        elif sys.argv[1] == 'run':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            if quick_setup():
                run_daemon(port)
        else:
            print("Usage: python3 quick_start.py [setup|run] [port]")
    else:
        print("🐋 Walrus Publisher Quick Start")
        print("Commands:")
        print("  python3 quick_start.py setup     - Check system and get info")
        print("  python3 quick_start.py run       - Start publisher daemon on port 8080")
        print("  python3 quick_start.py run 8081  - Start publisher daemon on port 8081")
        print("\nFor full setup, use: python3 publisher_setup.py setup")


if __name__ == "__main__":
    main()