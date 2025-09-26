# Walrus CLI - Git-like Storage Application

A command-line application that mimics Git's push and pull functionality using Walrus for decentralized storage. This tool allows you to upload directories to Walrus and retrieve them later, similar to how Git manages repositories.

## Features

- **Push**: Upload directories to Walrus storage as compressed blobs
- **Pull**: Download and restore previously uploaded directories
- **Change Detection**: Only uploads when directory content changes
- **Metadata Management**: Tracks blob IDs, timestamps, and directory mappings locally
- **Error Handling**: Comprehensive error handling for network and file system issues

## Prerequisites

1. **Walrus CLI**: Install and configure the Walrus command-line tool
   - The `walrus` command must be available in your system PATH
   - Ensure you have proper Walrus network access and configuration

2. **Python 3.7+**: Required for running the application

## Installation

1. Clone or download the `walrus_cli.py` file
2. Make sure you have Python 3.7+ installed
3. Ensure the Walrus CLI is installed and configured

## Usage

### Basic Commands

#### Push a Directory
Upload a directory to Walrus storage:

```bash
# Push current directory
python walrus_cli.py push

# Push specific directory
python walrus_cli.py push /path/to/your/project
python walrus_cli.py push "C:\Users\Username\MyProject"
```

#### Pull a Directory
Download and restore a previously uploaded directory:

```bash
# Pull to current directory
python walrus_cli.py pull

# Pull to specific directory
python walrus_cli.py pull /path/to/restore/location
python walrus_cli.py pull "C:\Users\Username\RestoredProject"
```

#### List Repositories
View all tracked repositories:

```bash
python walrus_cli.py list
```

### Example Workflow

1. **Initial Setup**: Create a project directory
```bash
mkdir my-project
cd my-project
echo "Hello Walrus!" > README.txt
```

2. **Push to Walrus**: Upload your project
```bash
python walrus_cli.py push .
```
Output:
```
Pushing directory: C:\Users\Username\my-project
Creating archive...
Storing in Walrus...
Successfully pushed to Walrus. Blob ID: 0x1234567890abcdef...
```

3. **Make Changes**: Modify your project
```bash
echo "Updated content" >> README.txt
mkdir src
echo "print('Hello World')" > src/main.py
```

4. **Push Changes**: Upload updated version
```bash
python walrus_cli.py push .
```

5. **Pull from Another Location**: Restore your project elsewhere
```bash
cd /different/location
python walrus_cli.py pull /path/to/original/project
```

## How It Works

### Storage Mechanism
1. **Compression**: Directories are compressed into ZIP archives
2. **Walrus Upload**: Archives are uploaded using `walrus store` command
3. **Metadata Tracking**: Local `.walrus/metadata.json` file tracks:
   - Blob IDs returned by Walrus
   - Directory hashes for change detection
   - Timestamps of uploads
   - Original directory names

### Change Detection
- Calculates SHA-256 hash of all files in directory
- Only uploads if hash differs from last upload
- Skips `.walrus` configuration directory

### File Structure
```
your-project/
├── .walrus/
│   ├── config.json      # Configuration (future use)
│   └── metadata.json    # Repository metadata
├── your-files...
└── your-directories...
```

## Configuration

### Metadata Format
The `.walrus/metadata.json` file stores repository information:

```json
{
  "/absolute/path/to/directory": {
    "blob_id": "0x1234567890abcdef...",
    "hash": "sha256_hash_of_directory_content",
    "timestamp": "2025-01-15T10:30:00.123456",
    "directory_name": "my-project"
  }
}
```

## Error Handling

The application handles various error scenarios:

- **Walrus CLI not found**: Ensures Walrus is installed
- **Network issues**: Graceful handling of storage/retrieval failures  
- **File permissions**: Proper error messages for access issues
- **Invalid directories**: Validates directory existence
- **Corrupted archives**: Handles extraction errors

## Limitations

1. **Single Version**: Only stores the latest version (no version history like Git)
2. **Walrus Dependency**: Requires working Walrus CLI installation
3. **Local Metadata**: Metadata is stored locally (not in Walrus)
4. **No Branching**: Simple push/pull model without Git's branching features

## Troubleshooting

### Common Issues

**"walrus command not found"**
- Install Walrus CLI and ensure it's in your system PATH
- Test with: `walrus --help`

**"No repository found for directory"**
- Directory hasn't been pushed yet
- Use `python walrus_cli.py list` to see tracked repositories
- Push the directory first: `python walrus_cli.py push`

**"Failed to store blob in Walrus"**
- Check your Walrus network connection
- Verify Walrus CLI configuration
- Ensure sufficient storage quota

**Permission errors**
- Check file/directory permissions
- Run with appropriate privileges if needed

## Security Considerations

- Metadata contains absolute paths - be cautious when sharing `.walrus` directories
- Blob IDs are stored in plain text locally
- No encryption of directory contents (relies on Walrus security)

## Future Enhancements

- Version history and tagging
- Branch-like functionality
- Remote metadata storage in Walrus
- Selective file synchronization
- Configuration file support
- Progress indicators for large uploads

## Contributing

This is a standalone application. Feel free to extend it with additional features while maintaining the core Git-like interface principle.