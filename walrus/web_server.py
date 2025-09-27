#!/usr/bin/env python3
"""
Walrus Web Repository Viewer
A GitHub-like web interface for viewing Walrus-stored repositories
"""

import os
import json
import tempfile
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort
import markdown
import mimetypes
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

app = Flask(__name__)

class WalrusWebViewer:
    """Web interface for viewing Walrus repositories"""
    
    def __init__(self, walrus_dir=".walrus"):
        self.walrus_dir = Path(walrus_dir)
        self.metadata_file = self.walrus_dir / "metadata.json"
        self.cache_dir = Path("web_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def load_repositories(self):
        """Load repository metadata"""
        if not self.metadata_file.exists():
            return {}
        
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def get_repository_list(self):
        """Get list of all repositories with summary info"""
        repos = self.load_repositories()
        repo_list = []
        
        for repo_path, metadata in repos.items():
            repo_info = {
                'name': metadata.get('directory_name', Path(repo_path).name),
                'path': repo_path,
                'blob_id': metadata.get('blob_id'),
                'last_updated': metadata.get('timestamp'),
                'hash': metadata.get('hash'),
                'size': self._get_blob_size(metadata.get('blob_id'))
            }
            repo_list.append(repo_info)
        
        # Sort by last updated (newest first)
        repo_list.sort(key=lambda x: x['last_updated'], reverse=True)
        return repo_list
    
    def _get_blob_size(self, blob_id):
        """Get blob size (placeholder for now)"""
        return "Unknown"
    
    def extract_repository(self, blob_id):
        """Extract repository from Walrus blob to cache"""
        cache_path = self.cache_dir / f"repo_{blob_id.replace('/', '_').replace('+', '-')}"
        
        # If already cached and recent, return cached version
        if cache_path.exists():
            return cache_path
        
        try:
            # Create temp file for download
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Download blob from Walrus using walrus read command
            print(f"Downloading blob {blob_id} from Walrus...")
            result = subprocess.run([
                'walrus', 'read', blob_id, '--out', temp_path
            ], capture_output=True, text=True, check=True)
            
            print(f"Successfully downloaded blob to {temp_path}")
            
            # Extract to cache directory
            cache_path.mkdir(parents=True, exist_ok=True)
            
            # Check if the file is a valid zip
            if zipfile.is_zipfile(temp_path):
                with zipfile.ZipFile(temp_path, 'r') as zip_file:
                    zip_file.extractall(cache_path)
                print(f"Successfully extracted to {cache_path}")
            else:
                print(f"Downloaded file is not a valid zip file")
                return None
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return cache_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error downloading blob {blob_id}: {e.stderr}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
        except Exception as e:
            print(f"Error extracting repository {blob_id}: {e}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
    
    def get_repository_files(self, blob_id, subpath=""):
        """Get file listing for repository"""
        cache_path = self.extract_repository(blob_id)
        if not cache_path:
            return None
        
        target_path = cache_path / subpath if subpath else cache_path
        if not target_path.exists():
            return None
        
        files = []
        dirs = []
        
        try:
            for item in sorted(target_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                item_info = {
                    'name': item.name,
                    'path': str(Path(subpath) / item.name) if subpath else item.name,
                    'is_dir': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                
                if item.is_dir():
                    dirs.append(item_info)
                else:
                    files.append(item_info)
        
        except Exception as e:
            print(f"Error reading directory: {e}")
            return None
        
        return dirs + files
    
    def get_file_content(self, blob_id, file_path):
        """Get content of a specific file"""
        cache_path = self.extract_repository(blob_id)
        if not cache_path:
            return None
        
        target_file = cache_path / file_path
        if not target_file.exists() or target_file.is_dir():
            return None
        
        try:
            # Check if file is binary
            with open(target_file, 'rb') as f:
                sample = f.read(8192)
                if b'\0' in sample:
                    return {
                        'type': 'binary',
                        'content': f"Binary file ({target_file.stat().st_size} bytes)",
                        'filename': target_file.name
                    }
            
            # Read text file
            with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine file type and apply syntax highlighting
            file_type = self._get_file_type(target_file.name)
            
            if file_type == 'markdown':
                html_content = markdown.markdown(content, extensions=['codehilite', 'fenced_code'])
                return {
                    'type': 'markdown',
                    'content': html_content,
                    'raw_content': content,
                    'filename': target_file.name
                }
            else:
                highlighted_content = self._highlight_code(content, target_file.name)
                return {
                    'type': 'code',
                    'content': highlighted_content,
                    'raw_content': content,
                    'filename': target_file.name,
                    'language': file_type
                }
                
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def _get_file_type(self, filename):
        """Determine file type for syntax highlighting"""
        ext = Path(filename).suffix.lower()
        
        type_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.xml': 'xml',
            '.sh': 'bash',
            '.cpp': 'cpp',
            '.c': 'c',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.sql': 'sql',
            '.txt': 'text'
        }
        
        return type_map.get(ext, 'text')
    
    def _highlight_code(self, content, filename):
        """Apply syntax highlighting to code"""
        try:
            lexer = get_lexer_for_filename(filename)
            formatter = HtmlFormatter(style='github', linenos=True, cssclass='highlight')
            return highlight(content, lexer, formatter)
        except ClassNotFound:
            # Fallback to plain text
            formatter = HtmlFormatter(style='github', linenos=True, cssclass='highlight')
            lexer = get_lexer_by_name('text')
            return highlight(content, lexer, formatter)

# Global viewer instance
viewer = WalrusWebViewer()

@app.route('/')
def index():
    """Main dashboard showing all repositories"""
    repositories = viewer.get_repository_list()
    return render_template('index.html', repositories=repositories)

@app.route('/repo/<blob_id>')
@app.route('/repo/<blob_id>/')
@app.route('/repo/<blob_id>/<path:subpath>')
def view_repository(blob_id, subpath=""):
    """View repository contents"""
    files = viewer.get_repository_files(blob_id, subpath)
    if files is None:
        abort(404)
    
    # Look for README file
    readme_content = None
    for file_info in files:
        if not file_info['is_dir'] and file_info['name'].lower().startswith('readme'):
            readme_path = Path(subpath) / file_info['name'] if subpath else file_info['name']
            readme_content = viewer.get_file_content(blob_id, str(readme_path))
            break
    
    return render_template('repository.html', 
                         blob_id=blob_id, 
                         current_path=subpath,
                         files=files,
                         readme=readme_content)

@app.route('/repo/<blob_id>/file/<path:file_path>')
def view_file(blob_id, file_path):
    """View individual file"""
    file_content = viewer.get_file_content(blob_id, file_path)
    if file_content is None:
        abort(404)
    
    return render_template('file.html',
                         blob_id=blob_id,
                         file_path=file_path,
                         file_content=file_content)

@app.route('/api/repositories')
def api_repositories():
    """API endpoint for repository list"""
    return jsonify(viewer.get_repository_list())

@app.route('/api/repo/<blob_id>/files')
@app.route('/api/repo/<blob_id>/files/<path:subpath>')
def api_repository_files(blob_id, subpath=""):
    """API endpoint for repository files"""
    files = viewer.get_repository_files(blob_id, subpath)
    if files is None:
        abort(404)
    return jsonify(files)

if __name__ == '__main__':
    print("🌐 Starting Walrus Web Repository Viewer...")
    print("📁 Monitoring .walrus/metadata.json for repositories")
    print("🔗 Access at: http://localhost:5000")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)