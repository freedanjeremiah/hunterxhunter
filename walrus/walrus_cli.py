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
import shutil
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
    def _find_walrus_binary():
        """Find the original Walrus CLI binary"""
        import shutil
        import os
        
        # Possible locations for the original Walrus CLI
        possible_paths = [
            os.path.expanduser('~/.cargo/bin/walrus'),
            os.path.expanduser('~/.cargo/bin/walrus.exe'),  # Windows
            '/usr/local/bin/walrus-original',
            '/usr/bin/walrus-original', 
            '/opt/walrus/bin/walrus',
            'walrus-original',
            'walrus-original.exe'  # Windows
        ]
        
        # Check each possible path
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # Try using shutil.which to find in PATH
        walrus_path = shutil.which('walrus-original') or shutil.which('walrus')
        if walrus_path:
            return walrus_path
        
        # If not found, we'll need to use a workaround
        # For now, return 'walrus' and handle the error gracefully
        return 'walrus'
    
    @staticmethod
    def store_blob(file_path: str, epochs: int = 5) -> Optional[str]:
        """Store a blob in Walrus and return the blob ID"""
        try:
            walrus_binary = WalrusStorage._find_walrus_binary()
            
            # Try to use the original Walrus CLI
            result = subprocess.run(
                [walrus_binary, 'store', '--epochs', str(epochs), file_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract blob ID from walrus store output
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Look for "Blob ID: " pattern (case insensitive)
                    if 'blob id:' in line.lower():
                        # Extract the ID part after the colon
                        blob_id = line.split(':', 1)[1].strip()
                        return blob_id
                    # Also check for alternative formats
                    elif 'blob_id' in line.lower() and ':' in line:
                        blob_id = line.split(':', 1)[1].strip()
                        return blob_id
                
                # If no clear pattern found, look for blob ID in progress messages
                for line in lines:
                    if 'blob encoded; blob ID:' in line:
                        # Extract from progress message format
                        if 'blob ID:' in line:
                            start = line.find('blob ID:') + 8
                            end = line.find(' ', start)
                            if end == -1:
                                blob_id = line[start:].strip()
                            else:
                                blob_id = line[start:end].strip()
                            return blob_id
            return None
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            
            # Check if it's our custom CLI being called instead
            if "invalid choice: 'store'" in error_msg:
                print("❌ Error: Custom Walrus CLI is being called instead of original Walrus CLI")
                print("Please ensure the original Walrus CLI is installed and accessible")
                print("")
                print("Solutions:")
                print("1. Install original Walrus CLI: curl --proto '=https' --tlsv1.2 -sSf https://install.walrus.site | sh")
                print("2. Or use different command names to avoid conflicts")
            else:
                print(f"Error storing blob: {error_msg}")
            return None
            
        except FileNotFoundError:
            print("Error: Original Walrus CLI not found.")
            print("Please install the original Walrus CLI from: https://docs.walrus.storage/")
            return None
    
    @staticmethod
    def retrieve_blob(blob_id: str, output_path: str) -> bool:
        """Retrieve a blob from Walrus by ID"""
        try:
            walrus_binary = WalrusStorage._find_walrus_binary()
            
            # Try 'walrus read' first, then fallback if needed
            commands_to_try = [
                [walrus_binary, 'read', blob_id],
                [walrus_binary, 'blob', 'show', blob_id]
            ]
            
            result = None
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        check=True
                    )
                    break
                except subprocess.CalledProcessError:
                    continue
            
            if result is None:
                raise subprocess.CalledProcessError(1, "walrus read/blob")
            
            # Save the blob content to output file
            with open(output_path, 'wb') as f:
                f.write(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            print(f"Error retrieving blob {blob_id}: {error_msg}")
            return False
            
        except FileNotFoundError:
            print("Error: Original Walrus CLI not found.")
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
        
        # Load ignore patterns
        ignore_patterns = self._load_ignore_patterns(directory)
        
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
                    
                    # Check ignore patterns
                    relative_path = file_path.relative_to(directory_path)
                    if self._should_ignore(str(relative_path), ignore_patterns):
                        continue
                    
                    arcname = str(relative_path)
                    zipf.write(file_path, arcname)
        
        return temp_file.name
    
    def _load_ignore_patterns(self, directory: str) -> List[str]:
        """Load ignore patterns from .walrusignore file"""
        ignore_file = Path(directory) / '.walrusignore'
        default_patterns = [
            'web_venv/',
            'venv/',
            'env/',
            '__pycache__/',
            '*.pyc',
            '.git/',
            'node_modules/',
            '.DS_Store',
            '*.log'
        ]
        
        patterns = default_patterns.copy()
        
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                print(f"Warning: Could not read .walrusignore: {e}")
        
        return patterns
    
    def _should_ignore(self, path: str, patterns: List[str]) -> bool:
        """Check if a path should be ignored based on patterns"""
        import fnmatch
        
        # Normalize path separators
        path = path.replace('\\', '/')
        
        for pattern in patterns:
            pattern = pattern.replace('\\', '/')
            
            # Directory pattern (ends with /)
            if pattern.endswith('/'):
                if path.startswith(pattern[:-1] + '/') or path == pattern[:-1]:
                    return True
            # File pattern
            elif fnmatch.fnmatch(path, pattern):
                return True
            # Check if any parent directory matches
            elif '/' in path:
                path_parts = path.split('/')
                for i in range(len(path_parts)):
                    partial_path = '/'.join(path_parts[:i+1])
                    if fnmatch.fnmatch(partial_path, pattern):
                        return True
        
        return False
    
    def extract_archive(self, archive_path: str, destination: str):
        """Extract zip archive to destination directory with better error handling"""
        print(f"🔧 Extracting archive: {archive_path}")
        print(f"🔧 Destination: {destination}")
        
        if not zipfile.is_zipfile(archive_path):
            print(f"❌ File is not a valid ZIP archive: {archive_path}")
            return
        
        extracted_count = 0
        skipped_count = 0
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            print(f"📋 Archive contains {len(zipf.infolist())} files")
            
            for member in zipf.infolist():
                try:
                    print(f"📄 Extracting: {member.filename}")
                    zipf.extract(member, destination)
                    extracted_count += 1
                except PermissionError as e:
                    # Try to fix permissions and retry
                    target_path = Path(destination) / member.filename
                    if target_path.exists():
                        try:
                            # Make file writable
                            target_path.chmod(0o666)
                            zipf.extract(member, destination)
                            extracted_count += 1
                            print(f"✅ Fixed permissions and extracted: {member.filename}")
                        except (PermissionError, OSError):
                            print(f"⚠️  Skipping {member.filename}: {e}")
                            skipped_count += 1
                            continue
                    else:
                        print(f"⚠️  Skipping {member.filename}: {e}")
                        skipped_count += 1
                        continue
                except Exception as e:
                    print(f"⚠️  Error extracting {member.filename}: {e}")
                    skipped_count += 1
                    continue
        
        print(f"📊 Extraction complete: {extracted_count} extracted, {skipped_count} skipped")
    
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
    
    def pull(self, source_directory: str = ".", destination: str = None, keep_temp: bool = False) -> bool:
        """Pull directory from Walrus storage"""
        try:
            source_directory = os.path.abspath(source_directory)
            metadata = self.config.load_metadata()
            
            print(f"🔍 Looking for repository: {source_directory}")
            print(f"📋 Available repositories in metadata:")
            for repo_dir in metadata.keys():
                print(f"   - {repo_dir}")
            
            if source_directory not in metadata:
                print(f"❌ No repository found for directory: {source_directory}")
                print("Available repositories:")
                for repo_dir in metadata.keys():
                    print(f"  - {repo_dir}")
                return False    
            
            repo_info = metadata[source_directory]
            blob_id = repo_info.get('blob_id')
            
            if not blob_id:
                print("❌ No blob ID found for this repository")
                return False
            
            print(f"📡 Pulling from Walrus (Blob ID: {blob_id})...")
            
            # Determine destination directory
            if destination:
                dest_dir = os.path.abspath(destination)
                print(f"📁 Destination: {dest_dir}")
            else:
                dest_dir = source_directory
                print(f"📁 Destination: {dest_dir} (original location)")
            
            # Create temporary file for downloaded blob
            temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            temp_file.close()
            print(f"💾 Temporary download file: {temp_file.name}")
            
            try:
                # Retrieve blob from Walrus
                print("⬇️  Downloading blob from Walrus...")
                if self.storage.retrieve_blob(blob_id, temp_file.name):
                    print("✅ Blob downloaded successfully")
                    
                    # Check if downloaded file is valid
                    if not os.path.exists(temp_file.name):
                        print("❌ Downloaded file does not exist")
                        return False
                    
                    file_size = os.path.getsize(temp_file.name)
                    print(f"📊 Downloaded file size: {file_size} bytes")
                    
                    if file_size == 0:
                        print("❌ Downloaded file is empty")
                        return False
                    
                    print("📦 Extracting archive...")
                    
                    # Create destination directory and all parent directories
                    print(f"📁 Creating destination directory: {dest_dir}")
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # Extract archive to the parent of destination
                    parent_dir = os.path.dirname(dest_dir)
                    print(f"📂 Extracting to parent directory: {parent_dir}")
                    
                    # Extract archive
                    self.extract_archive(temp_file.name, parent_dir)
                    
                    # Check if extraction created the expected directory structure
                    print(f"🔍 Checking extraction results...")
                    if os.path.exists(dest_dir) and os.listdir(dest_dir):
                        print(f"✅ Direct extraction successful")
                    else:
                        # Check if files were extracted to a subdirectory (common with archives)
                        extracted_items = os.listdir(parent_dir) if os.path.exists(parent_dir) else []
                        print(f"📋 Items in parent directory: {extracted_items}")
                        
                        # Look for the actual extracted directory
                        possible_dirs = [
                            os.path.join(parent_dir, 'walrus'),
                            os.path.join(parent_dir, os.path.basename(source_directory)),
                        ]
                        
                        found_source = None
                        for possible_dir in possible_dirs:
                            if os.path.exists(possible_dir) and os.listdir(possible_dir):
                                found_source = possible_dir
                                print(f"✅ Found extracted content in: {found_source}")
                                break
                        
                        if found_source:
                            # Move/copy files to the correct destination
                            import shutil
                            if found_source != dest_dir:
                                print(f"🔄 Moving files from {found_source} to {dest_dir}")
                                if os.path.exists(dest_dir):
                                    shutil.rmtree(dest_dir)
                                shutil.move(found_source, dest_dir)
                        else:
                            print(f"❌ Could not find extracted content in expected locations")
                            return False
                    
                    # Verify extraction worked
                    if os.path.exists(dest_dir) and os.listdir(dest_dir):
                        print(f"✅ Successfully pulled repository to: {dest_dir}")
                        print(f"📋 Contents:")
                        for item in os.listdir(dest_dir)[:10]:  # Show first 10 items
                            print(f"   - {item}")
                        if len(os.listdir(dest_dir)) > 10:
                            print(f"   ... and {len(os.listdir(dest_dir)) - 10} more items")
                        
                        # Handle temporary file cleanup
                        if keep_temp:
                            print(f"💾 Keeping temporary file: {temp_file.name}")
                            print(f"📝 You can manually delete it later if needed")
                        else:
                            print(f"🧹 Cleaning up temporary file: {temp_file.name}")
                            os.unlink(temp_file.name)
                        
                        return True
                    else:
                        print(f"❌ Final verification failed - destination directory is empty")
                        return False
                else:
                    print("❌ Failed to retrieve blob from Walrus")
                    return False
                    
            except Exception as extract_error:
                print(f"❌ Error during extraction: {extract_error}")
                # Clean up temp file on error unless keep_temp is True
                if not keep_temp and os.path.exists(temp_file.name):
                    print(f"🧹 Cleaning up temporary file due to error: {temp_file.name}")
                    os.unlink(temp_file.name)
                return False
                
        except Exception as e:
            print(f"❌ Error during pull: {str(e)}")
            import traceback
            print("🔍 Full error trace:")
            traceback.print_exc()
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
    parser.add_argument('source', nargs='?', default='.', 
                       help='Source directory path (from metadata) to pull')
    parser.add_argument('--to', '--destination', dest='destination',
                       help='Destination directory to pull to (default: original location)')
    parser.add_argument('--keep-temp', action='store_true',
                       help='Keep temporary ZIP file after extraction')
    
    args = parser.parse_args()
    
    try:
        cli = WalrusCLI()
        success = cli.pull(args.source, args.destination, args.keep_temp)
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
    pull_parser.add_argument('source', nargs='?', default='.', 
                           help='Source directory path (from metadata) to pull')
    pull_parser.add_argument('--to', '--destination', dest='destination',
                           help='Destination directory to pull to (default: original location)')
    pull_parser.add_argument('--keep-temp', action='store_true',
                           help='Keep temporary ZIP file after extraction')
    
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
            success = cli.pull(args.source, args.destination, getattr(args, 'keep_temp', False))
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