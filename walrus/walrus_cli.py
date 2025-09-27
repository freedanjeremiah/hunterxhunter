#!/usr/bin/env python3
"""
Walrus CLI - A Git-like application using Walrus for storage
Supports push and pull operations similar to Git but using Walrus blobs for storage
"""

import argparse
import sys
import os
import json
import hashlib
import zipfile
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


class WalrusConfig:
    """Manage local configuration and metadata"""
    
    def __init__(self, config_dir: str = ".walrus"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.metadata_file = self.config_dir / "metadata.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_metadata(self) -> Dict:
        """Load metadata about stored repositories"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_metadata(self, metadata: Dict):
        """Save metadata about stored repositories"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)


class WalrusStorage:
    """Interface to Walrus storage system"""
    
    @staticmethod
    def store_blob(file_path: str, epochs: int = 5) -> Optional[str]:
        """Store a blob in Walrus and return the blob ID"""
        try:
            result = subprocess.run(
                ['walrus', 'store', '--epochs', str(epochs), file_path],
                capture_output=True,
                text=True,
                check=True
            )
            # Extract blob ID from walrus store output
            # The output should contain the blob ID
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Look for lines containing blob ID patterns
                    if 'blob id' in line.lower() or 'blob_id' in line.lower():
                        # Extract the ID part after the colon
                        if ':' in line:
                            blob_id = line.split(':', 1)[1].strip()
                            return blob_id
                    # Look for standalone blob ID (URL-safe base64 or hex)
                    elif any(char in line for char in ['_', '-']) and len(line.strip()) > 20:
                        return line.strip()
                    # Look for hex-like patterns
                    elif line.strip().startswith(('0x', 'blob_')):
                        return line.strip()
                
                # If no clear pattern found, try the last non-empty line
                for line in reversed(lines):
                    if line.strip() and len(line.strip()) > 10:
                        return line.strip()
            
            return None
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"Error storing blob: {error_msg}")
            return None
        except FileNotFoundError:
            print("Error: 'walrus' command not found. Please ensure Walrus is installed and in PATH.")
            return None
    
    @staticmethod
    def retrieve_blob(blob_id: str, output_path: str) -> bool:
        """Retrieve a blob from Walrus by ID"""
        try:
            result = subprocess.run(
                ['walrus', 'read', blob_id],
                capture_output=True,
                check=True
            )
            
            # Save the blob content to output file
            with open(output_path, 'wb') as f:
                f.write(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            print(f"Error retrieving blob {blob_id}: {error_msg}")
            return False
        except FileNotFoundError:
            print("Error: 'walrus' command not found. Please ensure Walrus is installed and in PATH.")
            return False


class WalrusCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.config = WalrusConfig()
        self.storage = WalrusStorage()
    
    def create_directory_archive(self, directory: str) -> str:
        """Create a zip archive of the directory"""
        if not os.path.isdir(directory):
            raise ValueError(f"Directory '{directory}' does not exist")
        
        # Create temporary zip file
        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_file.close()
        
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            directory_path = Path(directory)
            for file_path in directory_path.rglob('*'):
                if file_path.is_file():
                    # Skip .walrus directory to avoid recursion
                    if '.walrus' in file_path.parts:
                        continue
                    
                    arcname = file_path.relative_to(directory_path.parent)
                    zipf.write(file_path, arcname)
        
        return temp_file.name
    
    def extract_archive(self, archive_path: str, destination: str):
        """Extract zip archive to destination directory"""
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(destination)
    
    def calculate_directory_hash(self, directory: str) -> str:
        """Calculate hash of directory contents for change detection"""
        hasher = hashlib.sha256()
        directory_path = Path(directory)
        
        for file_path in sorted(directory_path.rglob('*')):
            if file_path.is_file() and '.walrus' not in file_path.parts:
                hasher.update(str(file_path.relative_to(directory_path)).encode())
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def push(self, directory: str = ".") -> bool:
        """Push directory to Walrus storage"""
        try:
            directory = os.path.abspath(directory)
            directory_name = os.path.basename(directory)
            
            print(f"Pushing directory: {directory}")
            
            # Calculate hash to detect changes
            current_hash = self.calculate_directory_hash(directory)
            metadata = self.config.load_metadata()
            
            # Check if directory content has changed
            if directory in metadata:
                last_hash = metadata[directory].get('hash')
                if last_hash == current_hash:
                    print("No changes detected. Directory is up to date.")
                    return True
            
            # Create archive
            print("Creating archive...")
            archive_path = self.create_directory_archive(directory)
            
            try:
                # Store in Walrus
                print("Storing in Walrus...")
                blob_id = self.storage.store_blob(archive_path)
                
                if blob_id:
                    # Update metadata
                    if directory not in metadata:
                        metadata[directory] = {}
                    
                    metadata[directory].update({
                        'blob_id': blob_id,
                        'hash': current_hash,
                        'timestamp': datetime.now().isoformat(),
                        'directory_name': directory_name
                    })
                    
                    self.config.save_metadata(metadata)
                    print(f"Successfully pushed to Walrus. Blob ID: {blob_id}")
                    return True
                else:
                    print("Failed to store blob in Walrus")
                    return False
                    
            finally:
                # Clean up temporary archive
                os.unlink(archive_path)
                
        except Exception as e:
            print(f"Error during push: {str(e)}")
            return False
    
    def pull(self, directory: str = ".") -> bool:
        """Pull directory from Walrus storage"""
        try:
            directory = os.path.abspath(directory)
            metadata = self.config.load_metadata()
            
            if directory not in metadata:
                print(f"No repository found for directory: {directory}")
                print("Available repositories:")
                for repo_dir in metadata.keys():
                    print(f"  - {repo_dir}")
                return False
            
            repo_info = metadata[directory]
            blob_id = repo_info.get('blob_id')
            
            if not blob_id:
                print("No blob ID found for this repository")
                return False
            
            print(f"Pulling from Walrus (Blob ID: {blob_id})...")
            
            # Create temporary file for downloaded blob
            temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            temp_file.close()
            
            try:
                # Retrieve blob from Walrus
                if self.storage.retrieve_blob(blob_id, temp_file.name):
                    print("Extracting archive...")
                    
                    # Create parent directory if it doesn't exist
                    parent_dir = os.path.dirname(directory)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    
                    # Extract archive
                    self.extract_archive(temp_file.name, parent_dir)
                    print(f"Successfully pulled repository to: {directory}")
                    return True
                else:
                    print("Failed to retrieve blob from Walrus")
                    return False
                    
            finally:
                # Clean up temporary file
                os.unlink(temp_file.name)
                
        except Exception as e:
            print(f"Error during pull: {str(e)}")
            return False
    
    def list_repositories(self):
        """List all tracked repositories"""
        metadata = self.config.load_metadata()
        
        if not metadata:
            print("No repositories tracked")
            return
        
        print("Tracked repositories:")
        for directory, info in metadata.items():
            timestamp = info.get('timestamp', 'Unknown')
            blob_id = info.get('blob_id', 'Unknown')
            print(f"  {directory}")
            print(f"    Blob ID: {blob_id}")
            print(f"    Last updated: {timestamp}")


def main_push():
    """Entry point for 'walrus-push' standalone command"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Push directory to Walrus storage",
        prog="walrus-push"
    )
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to push (default: current directory)')
    parser.add_argument('--epochs', type=int, default=5,
                       help='Number of epochs to store the blob (default: 5)')
    
    args = parser.parse_args()
    
    try:
        cli = WalrusCLI()
        success = cli.push(args.directory)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main_pull():
    """Entry point for 'walrus-pull' standalone command"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Pull directory from Walrus storage",
        prog="walrus-pull"
    )
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to pull to (default: current directory)')
    
    args = parser.parse_args()
    
    try:
        cli = WalrusCLI()
        success = cli.pull(args.directory)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main_list():
    """Entry point for 'walrus-list' standalone command"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="List tracked Walrus repositories",
        prog="walrus-list"
    )
    
    parser.parse_args()  # This handles --help properly
    
    try:
        cli = WalrusCLI()
        cli.list_repositories()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for walrus CLI"""
    parser = argparse.ArgumentParser(
        description="Walrus CLI - Git-like interface for Walrus storage",
        prog="walrus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  walrus push .           Push current directory to Walrus
  walrus push /my/dir     Push specific directory
  walrus pull .           Pull to current directory
  walrus pull /restore    Pull to specific directory
  walrus list             List all tracked repositories

For more information, visit: https://docs.walrus.storage/"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push directory to Walrus storage')
    push_parser.add_argument('directory', nargs='?', default='.', 
                           help='Directory to push (default: current directory)')
    push_parser.add_argument('--epochs', type=int, default=5,
                           help='Number of epochs to store the blob (default: 5)')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull directory from Walrus storage')
    pull_parser.add_argument('directory', nargs='?', default='.', 
                           help='Directory to pull to (default: current directory)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tracked repositories')
    list_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Show detailed information')
    
    # Version command
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        cli = WalrusCLI()
        
        if args.command == 'push':
            success = cli.push(args.directory)
            sys.exit(0 if success else 1)
        elif args.command == 'pull':
            success = cli.pull(args.directory)
            sys.exit(0 if success else 1)
        elif args.command == 'list':
            cli.list_repositories()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()