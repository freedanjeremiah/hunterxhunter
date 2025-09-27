#!/usr/bin/env python3
"""
Walrus Publisher Node Setup and Management Script
Helps configure and run a Walrus publisher node
"""

import subprocess
import json
import os
import sys
from pathlib import Path
import yaml
import argparse
import time


class WalrusPublisher:
    """Walrus Publisher Node Manager"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.walrus'
        self.config_file = self.config_dir / 'publisher_config.yaml'
        self.default_config = {
            'network_address': '0.0.0.0:8080',
            'storage_path': './walrus_storage',
            'max_blob_size': '1GB',
            'epochs': 10,
            'stake_amount': 1000
        }
    
    def create_config(self, network_address: str = '0.0.0.0:8080'):
        """Create publisher configuration"""
        self.config_dir.mkdir(exist_ok=True)
        
        config = self.default_config.copy()
        config['network_address'] = network_address
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Created publisher config at: {self.config_file}")
        return config
    
    def load_config(self):
        """Load publisher configuration"""
        if not self.config_file.exists():
            return self.create_config()
        
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def check_prerequisites(self):
        """Check if Walrus CLI and dependencies are available"""
        try:
            result = subprocess.run(['walrus', '--version'], 
                                 capture_output=True, text=True)
            print(f"✅ Walrus CLI found: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("❌ Walrus CLI not found. Please install Walrus first.")
            return False
    
    def generate_wallet(self):
        """Generate a new Sui wallet for the publisher"""
        try:
            print("🔑 Generating new Sui wallet for publisher...")
            result = subprocess.run(
                ['walrus', 'generate-sui-wallet'],
                capture_output=True, text=True, check=True
            )
            print("✅ Wallet generated successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate wallet: {e.stderr}")
            return False
    
    def get_wal_tokens(self):
        """Get WAL tokens from testnet faucet"""
        try:
            print("💰 Getting WAL tokens from testnet faucet...")
            result = subprocess.run(
                ['walrus', 'get-wal'],
                capture_output=True, text=True, check=True
            )
            print("✅ WAL tokens obtained successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get WAL tokens: {e.stderr}")
            print("Note: This only works on testnet")
            return False
    
    def stake_tokens(self, amount: int = 1000):
        """Stake tokens with storage nodes"""
        try:
            print(f"🏦 Staking {amount} tokens...")
            result = subprocess.run(
                ['walrus', 'stake', str(amount)],
                capture_output=True, text=True, check=True
            )
            print("✅ Tokens staked successfully")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stake tokens: {e.stderr}")
            return False
    
    def run_publisher(self, network_address: str = None):
        """Run the Walrus publisher service"""
        config = self.load_config()
        
        if network_address:
            config['network_address'] = network_address
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        
        address = config['network_address']
        
        print(f"🚀 Starting Walrus Publisher on {address}")
        print("📝 Publisher handles blob upload requests from clients")
        print("⏹️  Press Ctrl+C to stop the publisher")
        print("-" * 50)
        
        try:
            # Run the publisher service
            subprocess.run(
                ['walrus', 'publisher', address],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Publisher failed to start: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Publisher stopped by user")
            return True
    
    def run_aggregator(self, network_address: str = None):
        """Run the Walrus aggregator service"""
        config = self.load_config()
        
        if network_address:
            config['network_address'] = network_address
        
        address = config.get('network_address', '0.0.0.0:8081').replace('8080', '8081')
        
        print(f"🚀 Starting Walrus Aggregator on {address}")
        print("📊 Aggregator collects and processes storage requests")
        print("⏹️  Press Ctrl+C to stop the aggregator")
        print("-" * 50)
        
        try:
            subprocess.run(
                ['walrus', 'aggregator', address],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Aggregator failed to start: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Aggregator stopped by user")
            return True
    
    def run_daemon(self, network_address: str = None):
        """Run combined publisher and aggregator daemon"""
        config = self.load_config()
        
        if network_address:
            config['network_address'] = network_address
        
        address = config.get('network_address', '0.0.0.0:8080')
        
        print(f"🚀 Starting Walrus Daemon (Publisher + Aggregator) on {address}")
        print("🔄 This combines both publisher and aggregator functionality")
        print("📡 Your node will handle both upload and storage coordination")
        print("⏹️  Press Ctrl+C to stop the daemon")
        print("-" * 50)
        
        try:
            subprocess.run(
                ['walrus', 'daemon', address],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Daemon failed to start: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Daemon stopped by user")
            return True
    
    def get_system_info(self):
        """Get Walrus system information"""
        try:
            print("📊 Fetching Walrus System Information...")
            result = subprocess.run(
                ['walrus', 'info'],
                capture_output=True, text=True, check=True
            )
            print("📊 Walrus System Information:")
            print("-" * 40)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get system info: {e.stderr}")
            return False
    
    def check_health(self):
        """Check health of storage nodes"""
        try:
            print("🏥 Checking Storage Node Health...")
            result = subprocess.run(
                ['walrus', 'health'],
                capture_output=True, text=True, check=True
            )
            print("🏥 Storage Node Health:")
            print("-" * 30)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check health: {e.stderr}")
            return False
    
    def list_blobs(self):
        """List all blobs owned by current wallet"""
        try:
            print("📦 Listing your blobs...")
            result = subprocess.run(
                ['walrus', 'list-blobs'],
                capture_output=True, text=True, check=True
            )
            print("📦 Your Blobs:")
            print("-" * 20)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list blobs: {e.stderr}")
            return False
    
    def setup_complete_node(self):
        """Complete setup process for a new publisher node"""
        print("🏗️  Starting complete Walrus Publisher Node setup...")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Create config
        print("\n📋 Step 1: Creating configuration...")
        self.create_config()
        
        # Step 3: Generate wallet
        print("\n🔑 Step 2: Setting up wallet...")
        if not self.generate_wallet():
            print("⚠️  Wallet generation failed, but continuing...")
        
        # Step 4: Try to get WAL tokens (testnet only)
        print("\n💰 Step 3: Attempting to get WAL tokens...")
        if not self.get_wal_tokens():
            print("⚠️  WAL token acquisition failed (normal on mainnet)")
        
        # Step 5: Get system info
        print("\n📊 Step 4: Checking system status...")
        self.get_system_info()
        
        print("\n✅ Setup completed!")
        print("\n📋 Next steps:")
        print("1. If on testnet and WAL tokens failed: Run 'walrus get-wal' manually")
        print("2. Stake tokens: python3 publisher_setup.py stake 1000")
        print("3. Start your node: python3 publisher_setup.py daemon")
        print("4. Monitor health: python3 publisher_setup.py health")
        
        return True


def main():
    """Main entry point for publisher setup"""
    parser = argparse.ArgumentParser(
        description="Walrus Publisher Node Setup and Management",
        prog="python3 publisher_setup.py"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Complete setup command
    setup_parser = subparsers.add_parser('setup', help='Complete publisher node setup')
    setup_parser.add_argument('--address', default='0.0.0.0:8080',
                            help='Network address for publisher (default: 0.0.0.0:8080)')
    
    # Individual setup commands
    config_parser = subparsers.add_parser('config', help='Create configuration only')
    config_parser.add_argument('--address', default='0.0.0.0:8080',
                             help='Network address for publisher')
    
    # Wallet and tokens
    wallet_parser = subparsers.add_parser('wallet', help='Generate new wallet')
    wal_parser = subparsers.add_parser('get-wal', help='Get WAL tokens (testnet)')
    stake_parser = subparsers.add_parser('stake', help='Stake tokens')
    stake_parser.add_argument('amount', type=int, default=1000, nargs='?',
                            help='Amount to stake (default: 1000)')
    
    # Run services
    pub_parser = subparsers.add_parser('publisher', help='Run publisher service only')
    pub_parser.add_argument('--address', help='Network address to bind to')
    
    agg_parser = subparsers.add_parser('aggregator', help='Run aggregator service only')
    agg_parser.add_argument('--address', help='Network address to bind to')
    
    daemon_parser = subparsers.add_parser('daemon', help='Run combined daemon (recommended)')
    daemon_parser.add_argument('--address', help='Network address to bind to')
    
    # Monitoring commands
    info_parser = subparsers.add_parser('info', help='Show Walrus system information')
    health_parser = subparsers.add_parser('health', help='Check storage node health')
    blobs_parser = subparsers.add_parser('blobs', help='List your blobs')
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐋 Walrus Publisher Node Manager")
        print("=" * 40)
        parser.print_help()
        print("\n💡 Quick start: python3 publisher_setup.py setup")
        return
    
    publisher = WalrusPublisher()
    
    if args.command == 'setup':
        success = publisher.setup_complete_node()
        sys.exit(0 if success else 1)
    
    # Check prerequisites for all other commands
    if not publisher.check_prerequisites():
        sys.exit(1)
    
    if args.command == 'config':
        publisher.create_config(args.address)
        
    elif args.command == 'wallet':
        publisher.generate_wallet()
        
    elif args.command == 'get-wal':
        publisher.get_wal_tokens()
        
    elif args.command == 'stake':
        publisher.stake_tokens(args.amount)
        
    elif args.command == 'publisher':
        publisher.run_publisher(args.address)
        
    elif args.command == 'aggregator':
        publisher.run_aggregator(args.address)
        
    elif args.command == 'daemon':
        publisher.run_daemon(args.address)
        
    elif args.command == 'info':
        publisher.get_system_info()
        
    elif args.command == 'health':
        publisher.check_health()
        
    elif args.command == 'blobs':
        publisher.list_blobs()


if __name__ == "__main__":
    main()