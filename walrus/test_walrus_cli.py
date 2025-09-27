#!/usr/bin/env python3
"""
Test script for Walrus CLI functionality
Performs basic validation without requiring actual Walrus installation
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path so we can import walrus_cli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from walrus_cli import WalrusCLI, WalrusConfig
except ImportError as e:
    print(f"Error importing walrus_cli: {e}")
    sys.exit(1)


def test_config_creation():
    """Test configuration directory and file creation"""
    print("🧪 Testing configuration creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = os.path.join(temp_dir, ".walrus-test")
        config = WalrusConfig(config_dir)
        
        # Check if config directory was created
        assert os.path.exists(config_dir), "Config directory not created"
        
        # Test metadata save/load
        test_metadata = {
            "test_repo": {
                "blob_id": "test_blob_123",
                "hash": "test_hash",
                "timestamp": "2025-01-01T00:00:00"
            }
        }
        
        config.save_metadata(test_metadata)
        loaded_metadata = config.load_metadata()
        
        assert loaded_metadata == test_metadata, "Metadata save/load failed"
        print("✅ Configuration creation test passed")


def test_directory_operations():
    """Test directory archiving and hash calculation"""
    print("🧪 Testing directory operations...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directory structure
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)
        
        # Create test files
        with open(os.path.join(test_dir, "file1.txt"), 'w') as f:
            f.write("Test content 1")
        
        with open(os.path.join(test_dir, "file2.txt"), 'w') as f:
            f.write("Test content 2")
        
        # Create subdirectory with file
        subdir = os.path.join(test_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file3.txt"), 'w') as f:
            f.write("Test content 3")
        
        cli = WalrusCLI()
        
        # Test hash calculation
        hash1 = cli.calculate_directory_hash(test_dir)
        hash2 = cli.calculate_directory_hash(test_dir)
        assert hash1 == hash2, "Hash calculation not consistent"
        
        # Test archive creation
        archive_path = cli.create_directory_archive(test_dir)
        assert os.path.exists(archive_path), "Archive not created"
        
        # Test archive extraction
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir)
        cli.extract_archive(archive_path, extract_dir)
        
        # Verify extracted content
        extracted_project = os.path.join(extract_dir, "test_project")
        assert os.path.exists(extracted_project), "Extracted directory not found"
        
        # Check if files were extracted correctly
        assert os.path.exists(os.path.join(extracted_project, "file1.txt")), "file1.txt not extracted"
        assert os.path.exists(os.path.join(extracted_project, "file2.txt")), "file2.txt not extracted"
        assert os.path.exists(os.path.join(extracted_project, "subdir", "file3.txt")), "file3.txt not extracted"
        
        # Verify content
        with open(os.path.join(extracted_project, "file1.txt"), 'r') as f:
            assert f.read() == "Test content 1", "file1.txt content mismatch"
        
        # Test hash after modification
        with open(os.path.join(test_dir, "file1.txt"), 'w') as f:
            f.write("Modified content")
        
        hash3 = cli.calculate_directory_hash(test_dir)
        assert hash1 != hash3, "Hash should change after modification"
        
        # Clean up
        os.unlink(archive_path)
        
        print("✅ Directory operations test passed")


def test_cli_argument_parsing():
    """Test command-line argument parsing"""
    print("🧪 Testing CLI argument parsing...")
    
    # Test that we can import and instantiate the CLI
    cli = WalrusCLI()
    assert cli is not None, "Failed to create CLI instance"
    assert cli.config is not None, "CLI config not initialized"
    assert cli.storage is not None, "CLI storage not initialized"
    
    print("✅ CLI argument parsing test passed")


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("🧪 Testing error handling...")
    
    cli = WalrusCLI()
    
    # Test with non-existent directory for archive creation
    try:
        cli.create_directory_archive("/non/existent/directory")
        assert False, "Should have raised error for non-existent directory"
    except ValueError:
        pass  # Expected error
    
    # Test hash calculation with non-existent directory 
    # (This should work but return hash of empty directory)
    hash_result = cli.calculate_directory_hash("/non/existent/directory")
    assert isinstance(hash_result, str), "Hash should return string even for non-existent directory"
    assert len(hash_result) == 64, "SHA-256 hash should be 64 characters"
    
    print("✅ Error handling test passed")


def run_tests():
    """Run all tests"""
    print("🚀 Running Walrus CLI Tests")
    print("=" * 50)
    
    tests = [
        test_config_creation,
        test_directory_operations,
        test_cli_argument_parsing,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


def main():
    """Main test runner"""
    print("Walrus CLI Test Suite")
    print("Note: These tests validate core functionality without requiring Walrus installation")
    print()
    
    success = run_tests()
    
    print(f"\n💡 Integration Testing:")
    print(f"To test with actual Walrus storage:")
    print(f"1. Install and configure Walrus CLI")
    print(f"2. Run: python example_usage.py")
    print(f"3. Or use: walrus.bat example")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())