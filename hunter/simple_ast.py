import ast
import os
import sys


def analyze_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=file_path)
        
        print(f"\nAST for: {file_path}")
        print("=" * 60)
        print(ast.dump(tree, indent=2))
        
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")


def analyze_directory(directory):
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print(f"No Python files found in {directory}")
        return
    
    print(f"Found {len(python_files)} Python files in {directory}")
    
    for file_path in python_files:
        analyze_file(file_path)


if len(sys.argv) != 2:
    print("Usage: python simple_ast.py <path_to_codebase>")
    sys.exit(1)

path = sys.argv[1]

if not os.path.exists(path):
    print(f"Error: Path '{path}' does not exist")
    sys.exit(1)

if os.path.isfile(path):
    if path.endswith('.py'):
        analyze_file(path)
    else:
        print(f"Error: '{path}' is not a Python file")
        sys.exit(1)
elif os.path.isdir(path):
    analyze_directory(path)
else:
    print(f"Error: '{path}' is neither a file nor directory")
    sys.exit(1)