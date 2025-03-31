"""
Tests for the file system example implementation.
"""

import pytest
import os
import shutil
from pathlib import Path
from examples.file_system_example import FileSystemManager

@pytest.fixture
def fs_manager(tmp_path):
    """Create a temporary file system for testing."""
    manager = FileSystemManager(str(tmp_path))
    yield manager
    # Cleanup
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)

def test_directory_initialization(fs_manager):
    """Test directory initialization."""
    assert os.path.exists(fs_manager.base_path)
    assert os.path.isdir(fs_manager.base_path)

def test_create_file(fs_manager):
    """Test file creation."""
    result = fs_manager.create_file("test.txt", "Hello, World!")
    assert result["path"] == "test.txt"
    assert result["content"] == "Hello, World!"
    assert os.path.exists(os.path.join(fs_manager.base_path, "test.txt"))

def test_create_file_in_subdirectory(fs_manager):
    """Test file creation in subdirectory."""
    result = fs_manager.create_file("subdir/test.txt", "Hello, World!")
    assert result["path"] == "subdir/test.txt"
    assert os.path.exists(os.path.join(fs_manager.base_path, "subdir/test.txt"))

def test_read_file(fs_manager):
    """Test file reading."""
    fs_manager.create_file("test.txt", "Hello, World!")
    result = fs_manager.read_file("test.txt")
    assert result["content"] == "Hello, World!"
    assert result["path"] == "test.txt"

def test_read_nonexistent_file(fs_manager):
    """Test reading nonexistent file."""
    with pytest.raises(FileNotFoundError):
        fs_manager.read_file("nonexistent.txt")

def test_update_file(fs_manager):
    """Test file update."""
    fs_manager.create_file("test.txt", "Hello, World!")
    result = fs_manager.update_file("test.txt", "Hello, Updated World!")
    assert result["content"] == "Hello, Updated World!"
    
    # Verify content was actually updated
    with open(os.path.join(fs_manager.base_path, "test.txt")) as f:
        assert f.read() == "Hello, Updated World!"

def test_update_nonexistent_file(fs_manager):
    """Test updating nonexistent file."""
    with pytest.raises(FileNotFoundError):
        fs_manager.update_file("nonexistent.txt", "New content")

def test_delete_file(fs_manager):
    """Test file deletion."""
    fs_manager.create_file("test.txt", "Hello, World!")
    assert fs_manager.delete_file("test.txt")
    assert not os.path.exists(os.path.join(fs_manager.base_path, "test.txt"))

def test_delete_nonexistent_file(fs_manager):
    """Test deleting nonexistent file."""
    assert not fs_manager.delete_file("nonexistent.txt")

def test_list_directory(fs_manager):
    """Test directory listing."""
    # Create some test files
    fs_manager.create_file("file1.txt", "Content 1")
    fs_manager.create_file("file2.txt", "Content 2")
    fs_manager.create_file("subdir/file3.txt", "Content 3")
    
    # List root directory
    items = fs_manager.list_directory()
    assert len(items) == 3  # Including subdir
    
    # List subdirectory
    items = fs_manager.list_directory("subdir")
    assert len(items) == 1

def test_list_nonexistent_directory(fs_manager):
    """Test listing nonexistent directory."""
    with pytest.raises(NotADirectoryError):
        fs_manager.list_directory("nonexistent")

def test_search_files(fs_manager):
    """Test file search."""
    # Create test files
    fs_manager.create_file("test1.txt", "Content 1")
    fs_manager.create_file("test2.txt", "Content 2")
    fs_manager.create_file("other.dat", "Content 3")
    
    # Search for .txt files
    results = fs_manager.search_files("*.txt")
    assert len(results) == 2
    assert all(r["extension"] == ".txt" for r in results)
    
    # Search in subdirectory
    fs_manager.create_file("subdir/test3.txt", "Content 4")
    results = fs_manager.search_files("*.txt", "subdir")
    assert len(results) == 1

def test_search_in_nonexistent_directory(fs_manager):
    """Test searching in nonexistent directory."""
    with pytest.raises(NotADirectoryError):
        fs_manager.search_files("*.txt", "nonexistent")

def test_path_validation(fs_manager):
    """Test path validation."""
    # Test valid paths
    assert fs_manager._validate_path("test.txt").name == "test.txt"
    assert fs_manager._validate_path("subdir/test.txt").name == "test.txt"
    
    # Test invalid paths
    with pytest.raises(ValueError):
        fs_manager._validate_path("../outside.txt")
    with pytest.raises(ValueError):
        fs_manager._validate_path("/absolute/path.txt")

def test_file_info(fs_manager):
    """Test file information retrieval."""
    fs_manager.create_file("test.txt", "Hello, World!")
    info = fs_manager.get_file_info("test.txt")
    
    assert info["path"] == "test.txt"
    assert info["size"] > 0
    assert "created" in info
    assert "modified" in info
    assert info["is_file"] is True
    assert info["is_directory"] is False
    assert info["extension"] == ".txt"

def test_get_info_nonexistent_file(fs_manager):
    """Test getting info for nonexistent file."""
    with pytest.raises(FileNotFoundError):
        fs_manager.get_file_info("nonexistent.txt") 