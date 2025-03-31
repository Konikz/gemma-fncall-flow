"""
Unit tests for SQLite database operations implementation.
Tests CRUD operations, connection management, and error handling.
"""

import pytest
import os
import sqlite3
from examples.database_example import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    """Creates temporary SQLite database for testing.
    
    Args:
        tmp_path: pytest fixture providing temporary directory
        
    Returns:
        DatabaseManager instance with temporary database
    """
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(str(db_path))
    yield manager
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

def test_database_initialization(db_manager):
    """Verifies database schema initialization."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None

def test_create_user(db_manager):
    """Tests user record creation with valid data."""
    user = db_manager.create_user("Test User", "user@example.com", 30)
    assert user["name"] == "Test User"
    assert user["email"] == "user@example.com"
    assert user["age"] == 30

def test_create_user_duplicate_email(db_manager):
    """Tests unique constraint on email field."""
    db_manager.create_user("Test User", "user@example.com", 30)
    with pytest.raises(ValueError):
        db_manager.create_user("Another User", "user@example.com", 25)

def test_get_user(db_manager):
    """Tests user record retrieval by ID."""
    created_user = db_manager.create_user("Test User", "user@example.com", 30)
    retrieved_user = db_manager.get_user("user@example.com")
    assert retrieved_user == created_user

def test_get_nonexistent_user(db_manager):
    """Tests retrieval of non-existent user record."""
    assert db_manager.get_user(999) is None

def test_update_user(db_manager):
    """Tests user record update with valid data."""
    created_user = db_manager.create_user("Test User", "user@example.com", 30)
    updated_user = db_manager.update_user("user@example.com", {"name": "Updated User"})
    assert updated_user["name"] == "Updated User"
    assert updated_user["email"] == "user@example.com"

def test_update_nonexistent_user(db_manager):
    """Tests update operation on non-existent user record."""
    assert db_manager.update_user(999, name="Test User") is None

def test_delete_user(db_manager):
    """Tests user record deletion."""
    created_user = db_manager.create_user("Test User", "user@example.com", 30)
    db_manager.delete_user("user@example.com")
    with pytest.raises(ValueError):
        db_manager.get_user("user@example.com")

def test_delete_nonexistent_user(db_manager):
    """Tests deletion of non-existent user record."""
    assert not db_manager.delete_user(999)

def test_list_users(db_manager):
    """Tests retrieval of all user records."""
    db_manager.create_user("Test User 1", "user1@example.com", 30)
    db_manager.create_user("Test User 2", "user2@example.com", 25)
    users = db_manager.list_users()
    assert len(users) == 2
    assert all(user["name"] in ["Test User 1", "Test User 2"] for user in users)

def test_connection_cleanup(db_manager):
    """Tests database connection cleanup after operations."""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result == (1,)
    
    # Verify connection is closed
    with pytest.raises(sqlite3.ProgrammingError):
        cursor.execute("SELECT 1") 