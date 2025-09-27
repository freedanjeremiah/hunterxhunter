#!/usr/bin/env python3
"""
GumTree-Inspired AST Analyzer
============================

A Python implementation inspired by GumTree for AST analysis and comparison.
Includes semantic hybrid techniques and tree differencing capabilities.

References:
- GumTree: https://github.com/GumTreeDiff/gumtree
- ast-grep: https://ast-grep.github.io/advanced/tool-comparison.html
- REINFOREST: arXiv:2305.03843
- Multi-Semantic Feature Fusion: Nature 2023
- GraphCodeBERT: arXiv:2009.08366
- Source code similarity survey: arXiv:2306.16171
"""

import ast
import os
import sys
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import argparse


@dataclass
class ASTNode:
    """Represents an AST node with semantic information."""
    node_type: str
    label: str
    value: Optional[str]
    position: Tuple[int, int]  # (line, col)
    size: int  # subtree size
    height: int
    hash_value: str
    semantic_features: Dict[str, Any]
    children: List['ASTNode']


class SemanticAnalyzer:
    """Extracts semantic features from AST nodes."""
    
    @staticmethod
    def extract_features(node: ast.AST) -> Dict[str, Any]:
        """Extract semantic features from an AST node."""
        features = {
            'node_type': type(node).__name__,
            'is_leaf': len(list(ast.iter_child_nodes(node))) == 0,
            'complexity': 1,
            'depth': 0,
            'identifiers': [],
            'literals': [],
            'operators': [],
            'control_flow': False,
            'function_call': False,
            'class_definition': False,
            'function_definition': False,
        }
        
        # Extract identifiers
        if isinstance(node, ast.Name):
            features['identifiers'].append(node.id)
        
        # Extract literals
        if isinstance(node, ast.Constant):
            features['literals'].append(str(node.value))
        
        # Extract operators
        if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, 
                            ast.Pow, ast.LShift, ast.RShift, ast.BitOr, 
                            ast.BitXor, ast.BitAnd, ast.FloorDiv)):
            features['operators'].append(type(node).__name__)
        
        # Control flow detection
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            features['control_flow'] = True
            features['complexity'] += 1
        
        # Function/class definitions
        if isinstance(node, ast.FunctionDef):
            features['function_definition'] = True
            features['identifiers'].append(node.name)
        
        if isinstance(node, ast.ClassDef):
            features['class_definition'] = True
            features['identifiers'].append(node.name)
        
        # Function calls
        if isinstance(node, ast.Call):
            features['function_call'] = True
            if isinstance(node.func, ast.Name):
                features['identifiers'].append(node.func.id)
        
        return features


class TreeBuilder:
    """Builds enhanced AST trees with semantic information."""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
    
    def build_tree(self, node: ast.AST, parent_pos: Tuple[int, int] = (0, 0)) -> ASTNode:
        """Build an enhanced AST tree with semantic features."""
        # Get position information
        line = getattr(node, 'lineno', parent_pos[0])
        col = getattr(node, 'col_offset', parent_pos[1])
        position = (line, col)
        
        # Extract semantic features
        semantic_features = self.semantic_analyzer.extract_features(node)
        
        # Build label and value
        label = type(node).__name__
        value = None
        
        if isinstance(node, ast.Name):
            value = node.id
        elif isinstance(node, ast.Constant):
            value = str(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            value = node.name
        
        # Build children recursively
        children = []
        for child in ast.iter_child_nodes(node):
            child_tree = self.build_tree(child, position)
            children.append(child_tree)
        
        # Calculate tree metrics
        size = 1 + sum(child.size for child in children)
        height = 1 + max((child.height for child in children), default=0)
        
        # Generate hash for similarity comparison
        hash_content = f"{label}:{value}:{len(children)}"
        hash_value = hashlib.md5(hash_content.encode()).hexdigest()[:8]
        
        # Update complexity based on children
        complexity = semantic_features['complexity'] + sum(
            child.semantic_features.get('complexity', 0) for child in children
        )
        semantic_features['complexity'] = complexity
        semantic_features['depth'] = height
        
        return ASTNode(
            node_type=label,
            label=label,
            value=value,
            position=position,
            size=size,
            height=height,
            hash_value=hash_value,
            semantic_features=semantic_features,
            children=children
        )


class TreeMatcher:
    """Implements tree matching algorithms inspired by GumTree."""
    
    def __init__(self, min_similarity: float = 0.6):
        self.min_similarity = min_similarity
    
    def calculate_similarity(self, node1: ASTNode, node2: ASTNode) -> float:
        """Calculate semantic similarity between two AST nodes."""
        if node1.node_type != node2.node_type:
            return 0.0
        
        similarity = 0.0
        total_weight = 0.0
        
        # Type similarity (exact match)
        similarity += 1.0
        total_weight += 1.0
        
        # Value similarity
        if node1.value and node2.value:
            value_sim = SequenceMatcher(None, node1.value, node2.value).ratio()
            similarity += value_sim
            total_weight += 1.0
        elif node1.value == node2.value:  # Both None
            similarity += 1.0
            total_weight += 1.0
        
        # Structural similarity
        size_diff = abs(node1.size - node2.size) / max(node1.size, node2.size)
        struct_sim = 1.0 - size_diff
        similarity += struct_sim * 0.5
        total_weight += 0.5
        
        # Semantic feature similarity
        features1 = node1.semantic_features
        features2 = node2.semantic_features
        
        semantic_sim = self._compare_semantic_features(features1, features2)
        similarity += semantic_sim * 0.8
        total_weight += 0.8
        
        return similarity / total_weight if total_weight > 0 else 0.0
    
    def _compare_semantic_features(self, features1: Dict, features2: Dict) -> float:
        """Compare semantic features between two nodes."""
        similarity = 0.0
        comparisons = 0
        
        # Boolean feature comparison
        bool_features = ['control_flow', 'function_call', 'class_definition', 
                        'function_definition', 'is_leaf']
        for feature in bool_features:
            if features1.get(feature) == features2.get(feature):
                similarity += 1.0
            comparisons += 1
        
        # List feature comparison (identifiers, literals, operators)
        list_features = ['identifiers', 'literals', 'operators']
        for feature in list_features:
            list1 = set(features1.get(feature, []))
            list2 = set(features2.get(feature, []))
            if list1 or list2:
                jaccard = len(list1 & list2) / len(list1 | list2) if (list1 | list2) else 1.0
                similarity += jaccard
                comparisons += 1
        
        # Numeric feature comparison
        complexity_diff = abs(features1.get('complexity', 0) - features2.get('complexity', 0))
        max_complexity = max(features1.get('complexity', 0), features2.get('complexity', 0), 1)
        complexity_sim = 1.0 - (complexity_diff / max_complexity)
        similarity += complexity_sim
        comparisons += 1
        
        return similarity / comparisons if comparisons > 0 else 0.0
    
    def find_mappings(self, tree1: ASTNode, tree2: ASTNode) -> Dict[str, str]:
        """Find node mappings between two trees using bottom-up matching."""
        mappings = {}
        
        def collect_nodes(node: ASTNode, node_list: List[ASTNode]):
            """Collect all nodes in post-order (children first)."""
            for child in node.children:
                collect_nodes(child, node_list)
            node_list.append(node)
        
        nodes1, nodes2 = [], []
        collect_nodes(tree1, nodes1)
        collect_nodes(tree2, nodes2)
        
        # Bottom-up matching: start with leaves and work upwards
        for node1 in nodes1:
            best_match = None
            best_similarity = 0.0
            
            for node2 in nodes2:
                if node2.hash_value in mappings.values():
                    continue  # Already mapped
                
                similarity = self.calculate_similarity(node1, node2)
                if similarity > best_similarity and similarity >= self.min_similarity:
                    best_similarity = similarity
                    best_match = node2
            
            if best_match:
                mappings[node1.hash_value] = best_match.hash_value
        
        return mappings


class CodeAnalyzer:
    """Main analyzer class that orchestrates AST analysis and comparison."""
    
    def __init__(self):
        self.tree_builder = TreeBuilder()
        self.tree_matcher = TreeMatcher()
    
    def analyze_file(self, file_path: str) -> Optional[ASTNode]:
        """Analyze a single Python file and return its AST tree."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            enhanced_tree = self.tree_builder.build_tree(tree)
            return enhanced_tree
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def compare_files(self, file1_path: str, file2_path: str) -> Dict[str, Any]:
        """Compare two Python files and return similarity analysis."""
        tree1 = self.analyze_file(file1_path)
        tree2 = self.analyze_file(file2_path)
        
        if not tree1 or not tree2:
            return {"error": "Failed to parse one or both files"}
        
        # Find mappings between trees
        mappings = self.tree_matcher.find_mappings(tree1, tree2)
        
        # Calculate overall similarity
        total_nodes1 = self._count_nodes(tree1)
        total_nodes2 = self._count_nodes(tree2)
        mapped_nodes = len(mappings)
        
        similarity = (2 * mapped_nodes) / (total_nodes1 + total_nodes2)
        
        return {
            "file1": file1_path,
            "file2": file2_path,
            "similarity": similarity,
            "total_nodes_file1": total_nodes1,
            "total_nodes_file2": total_nodes2,
            "mapped_nodes": mapped_nodes,
            "mappings": mappings,
            "tree1_complexity": tree1.semantic_features.get('complexity', 0),
            "tree2_complexity": tree2.semantic_features.get('complexity', 0),
        }
    
    def _count_nodes(self, node: ASTNode) -> int:
        """Count total number of nodes in a tree."""
        return node.size
    
    def analyze_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Analyze all Python files in a directory and compare them pairwise."""
        python_files = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        results = []
        
        # Pairwise comparison
        for i in range(len(python_files)):
            for j in range(i + 1, len(python_files)):
                comparison = self.compare_files(python_files[i], python_files[j])
                results.append(comparison)
        
        return results
    
    def print_tree(self, node: ASTNode, indent: int = 0, max_depth: int = 5) -> str:
        """Print tree structure in a readable format."""
        if indent > max_depth:
            return "  " * indent + "...\n"
        
        result = "  " * indent + f"{node.label}"
        
        if node.value:
            result += f": {node.value}"
        
        result += f" [{node.hash_value}]"
        result += f" (size: {node.size}, complexity: {node.semantic_features.get('complexity', 0)})\n"
        
        for child in node.children:
            result += self.print_tree(child, indent + 1, max_depth)
        
        return result


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='GumTree-inspired AST analyzer for Python code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze file.py                     # Analyze single file
  %(prog)s compare file1.py file2.py           # Compare two files
  %(prog)s directory /path/to/code             # Analyze directory
  %(prog)s tree file.py                        # Show tree structure
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single file')
    analyze_parser.add_argument('file', help='Python file to analyze')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two files')
    compare_parser.add_argument('file1', help='First Python file')
    compare_parser.add_argument('file2', help='Second Python file')
    
    # Directory command
    dir_parser = subparsers.add_parser('directory', help='Analyze directory')
    dir_parser.add_argument('path', help='Directory path to analyze')
    
    # Tree command
    tree_parser = subparsers.add_parser('tree', help='Show tree structure')
    tree_parser.add_argument('file', help='Python file to show tree for')
    tree_parser.add_argument('--depth', type=int, default=5, help='Maximum tree depth')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    analyzer = CodeAnalyzer()
    
    if args.command == 'analyze':
        tree = analyzer.analyze_file(args.file)
        if tree:
            print(f"Analysis of {args.file}:")
            print(f"Total nodes: {tree.size}")
            print(f"Tree height: {tree.height}")
            print(f"Complexity: {tree.semantic_features.get('complexity', 0)}")
            print(f"Features: {json.dumps(tree.semantic_features, indent=2)}")
    
    elif args.command == 'compare':
        result = analyzer.compare_files(args.file1, args.file2)
        print("File Comparison Results:")
        print("=" * 50)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'directory':
        results = analyzer.analyze_directory(args.path)
        print(f"Directory Analysis Results ({len(results)} comparisons):")
        print("=" * 60)
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        for result in results:
            print(f"Similarity: {result.get('similarity', 0):.3f} | "
                  f"{os.path.basename(result.get('file1', ''))} <-> "
                  f"{os.path.basename(result.get('file2', ''))}")
    
    elif args.command == 'tree':
        tree = analyzer.analyze_file(args.file)
        if tree:
            print(f"Tree structure for {args.file}:")
            print("=" * 50)
            print(analyzer.print_tree(tree, max_depth=args.depth))


if __name__ == '__main__':
    main()