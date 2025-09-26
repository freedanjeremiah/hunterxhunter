#!/usr/bin/env python3
"""
Example usage script for Walrus CLI
Demonstrates how to use the walrus push/pull functionality
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and display its output"""
    print(f"\n{'='*50}")
    print(f"📋 {description}")
    print(f"{'='*50}")
    print(f"Command: {command}")
    print("-" * 30)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("Output:")
            print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def create_sample_project():
    """Create a sample project directory"""
    project_dir = Path("sample-project")
    project_dir.mkdir(exist_ok=True)
    
    # Create sample files
    (project_dir / "README.md").write_text("""# Sample Project

This is a sample project to demonstrate Walrus CLI functionality.

## Features
- File 1: Main application
- File 2: Configuration
- File 3: Documentation
""")
    
    (project_dir / "main.py").write_text("""#!/usr/bin/env python3

def main():
    print("Hello from Walrus CLI sample project!")
    print("This project is stored in Walrus!")

if __name__ == "__main__":
    main()
""")
    
    (project_dir / "config.json").write_text("""{
    "app_name": "Walrus Sample",
    "version": "1.0.0",
    "description": "Sample application using Walrus storage"
}
""")
    
    # Create subdirectory
    src_dir = project_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    (src_dir / "utils.py").write_text("""def greet(name):
    return f"Hello {name} from Walrus!"

def calculate_sum(a, b):
    return a + b
""")
    
    print(f"✅ Created sample project in: {project_dir.absolute()}")
    return project_dir

def main():
    """Run the example demonstration"""
    print("🚀 Walrus CLI - Example Usage Demonstration")
    print("=" * 60)
    
    # Check if walrus_cli.py exists
    if not Path("walrus_cli.py").exists():
        print("❌ Error: walrus_cli.py not found in current directory")
        print("Please make sure you're running this from the directory containing walrus_cli.py")
        sys.exit(1)
    
    # Create sample project
    project_dir = create_sample_project()
    
    # Show initial directory structure
    print(f"\n📁 Sample project structure:")
    for root, dirs, files in os.walk(project_dir):
        level = root.replace(str(project_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    # Demonstrate push command
    success = run_command(
        f"python walrus_cli.py push {project_dir}",
        f"Push sample project to Walrus"
    )
    
    if not success:
        print("❌ Push failed. Please check your Walrus CLI installation.")
        print("Make sure 'walrus' command is available and configured.")
        return
    
    # List repositories
    run_command(
        "python walrus_cli.py list",
        "List all tracked repositories"
    )
    
    # Modify project and push again
    print(f"\n🔄 Making changes to the project...")
    (project_dir / "CHANGELOG.md").write_text("""# Changelog

## Version 1.1.0
- Added new features
- Improved performance
- Updated documentation

## Version 1.0.0
- Initial release
""")
    
    print("✅ Added CHANGELOG.md to the project")
    
    # Push updated project
    run_command(
        f"python walrus_cli.py push {project_dir}",
        "Push updated project with changes"
    )
    
    # Demonstrate pull to a different location
    pull_dir = Path("restored-project")
    if pull_dir.exists():
        import shutil
        shutil.rmtree(pull_dir)
    
    run_command(
        f"python walrus_cli.py pull {pull_dir}",
        f"Pull project to new location: {pull_dir}"
    )
    
    # Show restored project structure
    if pull_dir.exists():
        print(f"\n📁 Restored project structure:")
        for root, dirs, files in os.walk(pull_dir):
            level = root.replace(str(pull_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    
    print(f"\n🎉 Demonstration completed successfully!")
    print(f"Sample files created in: {project_dir.absolute()}")
    print(f"Restored files available in: {pull_dir.absolute()}")
    
    print(f"\n💡 Next steps:")
    print(f"1. Examine the created directories and files")
    print(f"2. Try modifying files and pushing again")
    print(f"3. Use 'python walrus_cli.py list' to see all repositories")
    print(f"4. Pull the project to different locations")

if __name__ == "__main__":
    main()