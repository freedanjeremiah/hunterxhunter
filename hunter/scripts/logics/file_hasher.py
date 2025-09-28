#!/usr/bin/env python3
"""
File Hash Script - Convert codebase to simple hash

This script provides functionality to:
1. Hash individual files
2. Hash entire directories/codebases
3. Generate consistent hashes for code comparison
4. Support multiple hash algorithms (MD5, SHA1, SHA256, SHA512)
5. Filter files by extension or patterns
6. Generate hierarchical hash structures
"""

import hashlib
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set
import fnmatch
from datetime import datetime


class FileHasher:
    """Class to handle file and directory hashing operations"""
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize FileHasher with specified hash algorithm
        
        Args:
            algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', 'sha512')
        """
        self.algorithm = algorithm.lower()
        self.supported_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        
        if self.algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Supported: {self.supported_algorithms}")
    
    def _get_hasher(self):
        """Get hasher object for the specified algorithm"""
        return hashlib.new(self.algorithm)
    
    def hash_file(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        Generate hash for a single file
        
        Args:
            file_path: Path to the file to hash
            chunk_size: Size of chunks to read for large files
            
        Returns:
            Hexadecimal hash string
        """
        hasher = self._get_hasher()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    
    def hash_string(self, content: str) -> str:
        """
        Generate hash for string content
        
        Args:
            content: String content to hash
            
        Returns:
            Hexadecimal hash string
        """
        hasher = self._get_hasher()
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()
    
    def should_include_file(self, file_path: str, include_patterns: List[str] = None, 
                          exclude_patterns: List[str] = None, 
                          include_extensions: Set[str] = None) -> bool:
        """
        Determine if a file should be included in hashing
        
        Args:
            file_path: Path to the file
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude
            include_extensions: Set of file extensions to include (e.g., {'.py', '.js'})
            
        Returns:
            True if file should be included
        """
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check extension filter
        if include_extensions and file_ext not in include_extensions:
            return False
        
        # Check exclude patterns first
        if exclude_patterns:
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(file_path, pattern):
                    return False
        
        # Check include patterns
        if include_patterns:
            for pattern in include_patterns:
                if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(file_path, pattern):
                    return True
            return False
        
        return True
    
    def hash_directory(self, directory_path: str, 
                      include_patterns: List[str] = None,
                      exclude_patterns: List[str] = None,
                      include_extensions: Set[str] = None,
                      recursive: bool = True) -> Dict:
        """
        Generate hash for entire directory
        
        Args:
            directory_path: Path to directory to hash
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude  
            include_extensions: Set of file extensions to include
            recursive: Whether to recurse into subdirectories
            
        Returns:
            Dictionary containing hash information
        """
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        file_hashes = {}
        combined_hasher = self._get_hasher()
        total_files = 0
        total_size = 0
        
        # Walk through directory
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                # Sort for consistent ordering
                dirs.sort()
                files.sort()
                
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, directory_path)
                    
                    if self.should_include_file(file_path, include_patterns, 
                                              exclude_patterns, include_extensions):
                        file_hash = self.hash_file(file_path)
                        if file_hash:  # Only include if hash was successful
                            file_hashes[relative_path] = {
                                'hash': file_hash,
                                'size': os.path.getsize(file_path)
                            }
                            # Update combined hash with file path and hash
                            combined_hasher.update(f"{relative_path}:{file_hash}".encode('utf-8'))
                            total_files += 1
                            total_size += file_hashes[relative_path]['size']
        else:
            # Only process files in the root directory
            for item in sorted(os.listdir(directory_path)):
                file_path = os.path.join(directory_path, item)
                if os.path.isfile(file_path):
                    if self.should_include_file(file_path, include_patterns, 
                                              exclude_patterns, include_extensions):
                        file_hash = self.hash_file(file_path)
                        if file_hash:
                            file_hashes[item] = {
                                'hash': file_hash,
                                'size': os.path.getsize(file_path)
                            }
                            combined_hasher.update(f"{item}:{file_hash}".encode('utf-8'))
                            total_files += 1
                            total_size += file_hashes[item]['size']
        
        return {
            'directory': directory_path,
            'algorithm': self.algorithm,
            'combined_hash': combined_hasher.hexdigest(),
            'file_count': total_files,
            'total_size': total_size,
            'timestamp': datetime.now().isoformat(),
            'file_hashes': file_hashes
        }
    
    def compare_hashes(self, hash1: Dict, hash2: Dict) -> Dict:
        """
        Compare two hash dictionaries
        
        Args:
            hash1: First hash dictionary
            hash2: Second hash dictionary
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            'same_combined_hash': hash1.get('combined_hash') == hash2.get('combined_hash'),
            'added_files': [],
            'removed_files': [],
            'modified_files': [],
            'unchanged_files': []
        }
        
        files1 = set(hash1.get('file_hashes', {}).keys())
        files2 = set(hash2.get('file_hashes', {}).keys())
        
        comparison['added_files'] = list(files2 - files1)
        comparison['removed_files'] = list(files1 - files2)
        
        # Check for modifications in common files
        common_files = files1 & files2
        for file_path in common_files:
            hash1_file = hash1['file_hashes'][file_path]['hash']
            hash2_file = hash2['file_hashes'][file_path]['hash']
            
            if hash1_file != hash2_file:
                comparison['modified_files'].append(file_path)
            else:
                comparison['unchanged_files'].append(file_path)
        
        return comparison


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Generate hashes for files and directories')
    parser.add_argument('path', help='Path to file or directory to hash')
    parser.add_argument('-a', '--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512'], 
                       default='sha256', help='Hash algorithm to use')
    parser.add_argument('-o', '--output', help='Output file for hash results (JSON format)')
    parser.add_argument('--include', nargs='*', help='Include patterns (glob)')
    parser.add_argument('--exclude', nargs='*', help='Exclude patterns (glob)')
    parser.add_argument('--extensions', nargs='*', help='File extensions to include (e.g., .py .js)')
    parser.add_argument('--no-recursive', action='store_true', help='Don\'t recurse into subdirectories')
    parser.add_argument('--simple', action='store_true', help='Output only the combined hash')
    
    args = parser.parse_args()
    
    hasher = FileHasher(args.algorithm)
    
    path = os.path.abspath(args.path)
    
    try:
        if os.path.isfile(path):
            # Hash single file
            file_hash = hasher.hash_file(path)
            if args.simple:
                print(file_hash)
            else:
                result = {
                    'file': path,
                    'algorithm': args.algorithm,
                    'hash': file_hash,
                    'size': os.path.getsize(path),
                    'timestamp': datetime.now().isoformat()
                }
                print(json.dumps(result, indent=2))
        
        elif os.path.isdir(path):
            # Hash directory
            include_extensions = set(args.extensions) if args.extensions else None
            
            result = hasher.hash_directory(
                path,
                include_patterns=args.include,
                exclude_patterns=args.exclude,
                include_extensions=include_extensions,
                recursive=not args.no_recursive
            )
            
            if args.simple:
                print(result['combined_hash'])
            else:
                print(json.dumps(result, indent=2))
            
            # Save to file if specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Hash results saved to: {args.output}")
        
        else:
            print(f"Error: Path does not exist: {path}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())