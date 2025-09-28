#!/usr/bin/env python3
"""
REINFOREST: Reinforcing Semantic Code Similarity for Cross-Lingual Code Search
===============================================================================

A simplified implementation of REINFOREST based on arXiv:2305.03843.
This implementation focuses on semantic hybrid techniques that combine:
- Static AST-based features
- Dynamic semantic features (simulated)
- Both positive and negative reference samples for training/comparison

Author: Simplified implementation for hunterxhunter project
Reference: Anthony Saieva, Saikat Chakraborty, Gail Kaiser. 
          "REINFOREST: Reinforcing Semantic Code Similarity for Cross-Lingual Code Search Models"
          arXiv:2305.03843, 2023.
"""

import ast
import json
import hashlib
import re
import math
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import os
import sys


@dataclass
class CodeEmbedding:
    """Represents a code embedding with semantic features."""
    file_path: str
    language: str
    ast_features: Dict[str, Any]
    lexical_features: Dict[str, Any]
    semantic_features: Dict[str, Any]
    embedding_vector: List[float]
    

class SemanticExtractor:
    """Extracts semantic features from code."""
    
    def __init__(self):
        self.feature_weights = {
            'ast_depth': 0.2,
            'ast_nodes': 0.15,
            'function_count': 0.1,
            'class_count': 0.1,
            'variable_count': 0.1,
            'complexity': 0.15,
            'lexical_diversity': 0.1,
            'semantic_density': 0.1
        }
    
    def extract_ast_features(self, code: str) -> Dict[str, Any]:
        """Extract AST-based features from code."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'error': 'syntax_error', 'depth': 0, 'nodes': 0}
        
        features = {
            'depth': self._get_ast_depth(tree),
            'total_nodes': len(list(ast.walk(tree))),
            'function_defs': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            'class_defs': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            'assignments': len([n for n in ast.walk(tree) if isinstance(n, ast.Assign)]),
            'loops': len([n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))]),
            'conditionals': len([n for n in ast.walk(tree) if isinstance(n, ast.If)]),
            'calls': len([n for n in ast.walk(tree) if isinstance(n, ast.Call)])
        }
        
        # Calculate cyclomatic complexity approximation
        features['complexity'] = 1 + features['loops'] + features['conditionals']
        
        return features
    
    def extract_lexical_features(self, code: str) -> Dict[str, Any]:
        """Extract lexical features from code."""
        lines = code.split('\n')
        tokens = re.findall(r'\w+', code.lower())
        
        features = {
            'lines_of_code': len([line for line in lines if line.strip()]),
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'empty_lines': len([line for line in lines if not line.strip()])
        }
        
        # Lexical diversity (vocabulary richness)
        features['lexical_diversity'] = features['unique_tokens'] / features['total_tokens'] if features['total_tokens'] > 0 else 0
        
        return features
    
    def extract_semantic_features(self, code: str) -> Dict[str, Any]:
        """Extract semantic features (simulated dynamic features)."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'error': 'syntax_error'}
        
        # Simulate dynamic features based on static analysis
        features = {
            'variable_scope_complexity': self._analyze_variable_scopes(tree),
            'function_interaction_score': self._analyze_function_interactions(tree),
            'data_flow_complexity': self._analyze_data_flow(tree),
            'control_flow_density': self._analyze_control_flow(tree)
        }
        
        return features
    
    def _get_ast_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum depth of AST."""
        if not hasattr(node, '_fields') or not node._fields:
            return depth
        
        max_child_depth = depth
        for field_name in node._fields:
            field_value = getattr(node, field_name)
            if isinstance(field_value, list):
                for child in field_value:
                    if isinstance(child, ast.AST):
                        child_depth = self._get_ast_depth(child, depth + 1)
                        max_child_depth = max(max_child_depth, child_depth)
            elif isinstance(field_value, ast.AST):
                child_depth = self._get_ast_depth(field_value, depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def _analyze_variable_scopes(self, tree: ast.AST) -> float:
        """Analyze variable scope complexity."""
        scopes = defaultdict(set)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                scope_level = self._get_scope_level(node, tree)
                scopes[scope_level].add(node.id)
        
        # Calculate complexity based on variable distribution across scopes
        total_vars = sum(len(vars_set) for vars_set in scopes.values())
        if total_vars == 0:
            return 0.0
        
        complexity = 0.0
        for level, vars_set in scopes.items():
            proportion = len(vars_set) / total_vars
            if proportion > 0:
                complexity -= proportion * math.log2(proportion)
        
        return complexity
    
    def _analyze_function_interactions(self, tree: ast.AST) -> float:
        """Analyze function interaction complexity."""
        functions = {}
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.append(node.func.id)
        
        if not functions:
            return 0.0
        
        # Calculate interaction score based on internal vs external calls
        internal_calls = sum(1 for call in calls if call in functions)
        total_calls = len(calls)
        
        return internal_calls / total_calls if total_calls > 0 else 0.0
    
    def _analyze_data_flow(self, tree: ast.AST) -> float:
        """Analyze data flow complexity."""
        assignments = 0
        reads = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                assignments += 1
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                reads += 1
        
        return reads / (assignments + 1)  # +1 to avoid division by zero
    
    def _analyze_control_flow(self, tree: ast.AST) -> float:
        """Analyze control flow density."""
        control_nodes = 0
        total_nodes = 0
        
        for node in ast.walk(tree):
            total_nodes += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                control_nodes += 1
        
        return control_nodes / total_nodes if total_nodes > 0 else 0.0
    
    def _get_scope_level(self, target_node: ast.AST, tree: ast.AST) -> int:
        """Get the scope level of a node (simplified)."""
        level = 0
        # This is a simplified implementation
        # In practice, you'd need to traverse the tree structure
        return level


class REINFORESTModel:
    """Main REINFOREST model for semantic code similarity."""
    
    def __init__(self):
        self.extractor = SemanticExtractor()
        self.embeddings: List[CodeEmbedding] = []
        self.positive_pairs: List[Tuple[int, int]] = []  # indices of similar code pairs
        self.negative_pairs: List[Tuple[int, int]] = []  # indices of dissimilar code pairs
    
    def add_code_sample(self, code: str, file_path: str, language: str = 'python') -> int:
        """Add a code sample and return its index."""
        ast_features = self.extractor.extract_ast_features(code)
        lexical_features = self.extractor.extract_lexical_features(code)
        semantic_features = self.extractor.extract_semantic_features(code)
        
        # Create embedding vector
        embedding_vector = self._create_embedding_vector(
            ast_features, lexical_features, semantic_features
        )
        
        embedding = CodeEmbedding(
            file_path=file_path,
            language=language,
            ast_features=ast_features,
            lexical_features=lexical_features,
            semantic_features=semantic_features,
            embedding_vector=embedding_vector
        )
        
        self.embeddings.append(embedding)
        return len(self.embeddings) - 1
    
    def add_positive_pair(self, idx1: int, idx2: int):
        """Add a positive (similar) code pair."""
        self.positive_pairs.append((idx1, idx2))
    
    def add_negative_pair(self, idx1: int, idx2: int):
        """Add a negative (dissimilar) code pair."""
        self.negative_pairs.append((idx1, idx2))
    
    def calculate_similarity(self, idx1: int, idx2: int) -> float:
        """Calculate semantic similarity between two code samples."""
        if idx1 >= len(self.embeddings) or idx2 >= len(self.embeddings):
            raise IndexError("Invalid embedding index")
        
        emb1 = self.embeddings[idx1]
        emb2 = self.embeddings[idx2]
        
        # Calculate cosine similarity between embedding vectors
        cosine_sim = self._cosine_similarity(emb1.embedding_vector, emb2.embedding_vector)
        
        # Apply REINFOREST enhancement using positive/negative pairs
        enhanced_sim = self._apply_reinforcement(cosine_sim, idx1, idx2)
        
        return enhanced_sim
    
    def search_similar_code(self, query_idx: int, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find the most similar code samples to the query."""
        if query_idx >= len(self.embeddings):
            raise IndexError("Invalid query index")
        
        similarities = []
        for i in range(len(self.embeddings)):
            if i != query_idx:
                sim = self.calculate_similarity(query_idx, i)
                similarities.append((i, sim))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def cross_language_search(self, query_idx: int, target_language: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search for similar code in a specific language."""
        if query_idx >= len(self.embeddings):
            raise IndexError("Invalid query index")
        
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            if i != query_idx and embedding.language == target_language:
                sim = self.calculate_similarity(query_idx, i)
                similarities.append((i, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _create_embedding_vector(self, ast_features: Dict, lexical_features: Dict, semantic_features: Dict) -> List[float]:
        """Create a feature vector from extracted features."""
        vector = []
        
        # AST features
        ast_vals = [
            ast_features.get('depth', 0),
            ast_features.get('total_nodes', 0),
            ast_features.get('function_defs', 0),
            ast_features.get('class_defs', 0),
            ast_features.get('assignments', 0),
            ast_features.get('loops', 0),
            ast_features.get('conditionals', 0),
            ast_features.get('calls', 0),
            ast_features.get('complexity', 0)
        ]
        
        # Lexical features
        lex_vals = [
            lexical_features.get('lines_of_code', 0),
            lexical_features.get('total_tokens', 0),
            lexical_features.get('unique_tokens', 0),
            lexical_features.get('avg_line_length', 0),
            lexical_features.get('lexical_diversity', 0)
        ]
        
        # Semantic features
        sem_vals = [
            semantic_features.get('variable_scope_complexity', 0),
            semantic_features.get('function_interaction_score', 0),
            semantic_features.get('data_flow_complexity', 0),
            semantic_features.get('control_flow_density', 0)
        ]
        
        # Normalize features
        vector.extend(self._normalize_values(ast_vals))
        vector.extend(self._normalize_values(lex_vals))
        vector.extend(self._normalize_values(sem_vals))
        
        return vector
    
    def _normalize_values(self, values: List[float]) -> List[float]:
        """Normalize values to [0, 1] range."""
        if not values:
            return values
        
        max_val = max(values) if max(values) > 0 else 1
        return [v / max_val for v in values]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _apply_reinforcement(self, base_similarity: float, idx1: int, idx2: int) -> float:
        """Apply REINFOREST reinforcement using positive/negative pairs."""
        # Check if this pair has reinforcement information
        pair = (idx1, idx2) if idx1 < idx2 else (idx2, idx1)
        reverse_pair = (idx2, idx1) if idx1 < idx2 else (idx1, idx2)
        
        reinforcement_factor = 1.0
        
        # Boost similarity for positive pairs
        if pair in self.positive_pairs or reverse_pair in self.positive_pairs:
            reinforcement_factor += 0.3
        
        # Reduce similarity for negative pairs
        if pair in self.negative_pairs or reverse_pair in self.negative_pairs:
            reinforcement_factor -= 0.3
        
        # Apply reinforcement to base similarity
        enhanced_similarity = base_similarity * reinforcement_factor
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, enhanced_similarity))
    
    def get_embedding_info(self, idx: int) -> Dict[str, Any]:
        """Get detailed information about an embedding."""
        if idx >= len(self.embeddings):
            raise IndexError("Invalid embedding index")
        
        return asdict(self.embeddings[idx])
    
    def export_model(self, filepath: str):
        """Export the model to a JSON file."""
        model_data = {
            'embeddings': [asdict(emb) for emb in self.embeddings],
            'positive_pairs': self.positive_pairs,
            'negative_pairs': self.negative_pairs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
    
    def load_model(self, filepath: str):
        """Load the model from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        self.embeddings = [CodeEmbedding(**emb_data) for emb_data in model_data['embeddings']]
        self.positive_pairs = [tuple(pair) for pair in model_data['positive_pairs']]
        self.negative_pairs = [tuple(pair) for pair in model_data['negative_pairs']]


# Example usage functions
def analyze_code_files(file_paths: List[str]) -> REINFORESTModel:
    """Analyze multiple code files and create a REINFOREST model."""
    model = REINFORESTModel()
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Determine language from file extension
            ext = os.path.splitext(file_path)[1].lower()
            language = 'python' if ext == '.py' else ext[1:] if ext else 'unknown'
            
            model.add_code_sample(code, file_path, language)
            print(f"Added {file_path} to model")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return model


def demo_reinforest():
    """Demonstrate REINFOREST functionality."""
    print("REINFOREST Demo: Semantic Code Similarity Analysis")
    print("=" * 60)
    
    # Use existing sample files
    script_dir = os.path.dirname(__file__)
    sample_files = [
        os.path.join(script_dir, 'sample1.py'),
        os.path.join(script_dir, 'sample2.py')
    ]
    
    # Filter existing files
    existing_files = [f for f in sample_files if os.path.exists(f)]
    
    if not existing_files:
        print("No sample files found. Please ensure sample1.py and sample2.py exist.")
        return
    
    # Create model
    model = analyze_code_files(existing_files)
    
    if len(model.embeddings) >= 2:
        # Add positive pair (both are calculator implementations)
        model.add_positive_pair(0, 1)
        
        # Calculate similarity
        similarity = model.calculate_similarity(0, 1)
        print(f"\nSemantic similarity between sample1.py and sample2.py: {similarity:.4f}")
        
        # Search for similar code
        similar_codes = model.search_similar_code(0, top_k=3)
        print(f"\nMost similar codes to {existing_files[0]}:")
        for idx, sim_score in similar_codes:
            print(f"  - {model.embeddings[idx].file_path}: {sim_score:.4f}")
    
    print("\nREINFOREST analysis complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_reinforest()
    else:
        print("Usage: python reinforest.py [demo]")
        print("Run with 'demo' argument to see example analysis")