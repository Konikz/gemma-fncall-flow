import pytest
from unittest.mock import Mock
from function_calling import FunctionRegistry, GemmaFunctionCaller
from validation import ValidationError, ParameterType

def create_test_function():
    """Create a test function and its schema."""
    def test_func(name: str, age: int = 0) -> str:
        return f"Hello, {name}! You are {age} years old."

    schema = {
        "name": "test_func",
        "description": "A test function",
        "parameters": {
            "name": {
                "type": ParameterType.STRING.value,
                "description": "The name parameter"
            },
            "age": {
                "type": ParameterType.NUMBER.value,
                "description": "The age parameter",
                "minimum": 0
            }
        },
        "required": ["name"]
    }

    return test_func, schema

def test_function_registry_registration():
    """Test function registration in the registry."""
    registry = FunctionRegistry()
    func, schema = create_test_function()

    # Test successful registration
    registry.register("test_func", func, schema)
    assert registry.get_function("test_func") == func
    assert registry.get_schema("test_func") is not None

    # Test duplicate registration
    with pytest.raises(ValidationError):
        registry.register("test_func", func, schema)

    # Test invalid schema
    invalid_schema = {
        "name": "invalid_func",
        "parameters": {}  # Missing description
    }
    with pytest.raises(ValidationError):
        registry.register("invalid_func", func, invalid_schema)

def test_function_registry_unregistration():
    """Test function unregistration from the registry."""
    registry = FunctionRegistry()
    func, schema = create_test_function()

    # Register and then unregister
    registry.register("test_func", func, schema)
    registry.unregister("test_func")
    assert registry.get_function("test_func") is None
    assert registry.get_schema("test_func") is None

    # Test unregistering non-existent function
    with pytest.raises(ValueError):
        registry.unregister("non_existent")

def test_function_registry_update():
    """Test updating a function in the registry."""
    registry = FunctionRegistry()
    func, schema = create_test_function()

    # Register initial function
    registry.register("test_func", func, schema)

    # Update with new function and schema
    def new_func(name: str) -> str:
        return f"Hi, {name}!"

    new_schema = {
        "name": "test_func",
        "description": "Updated test function",
        "parameters": {
            "name": {
                "type": ParameterType.STRING.value,
                "description": "The name parameter"
            }
        },
        "required": ["name"]
    }

    registry.update_function("test_func", new_func, new_schema)
    assert registry.get_function("test_func") == new_func

    # Test updating non-existent function
    with pytest.raises(ValueError):
        registry.update_function("non_existent", new_func, new_schema)

def test_gemma_function_caller():
    """Test the GemmaFunctionCaller class."""
    registry = FunctionRegistry()
    caller = GemmaFunctionCaller(registry)
    func, schema = create_test_function()

    # Test function registration and calling
    caller.register_function("test_func", func, schema)
    result = caller.call_function("test_func", {"name": "Alice", "age": 25})
    assert result == "Hello, Alice! You are 25 years old."

    # Test function call with invalid parameters
    with pytest.raises(ValidationError):
        caller.call_function("test_func", {"name": "Alice", "age": -1})

    # Test calling non-existent function
    with pytest.raises(ValueError):
        caller.call_function("non_existent", {})

    # Test unregistering function
    caller.unregister_function("test_func")
    with pytest.raises(ValueError):
        caller.call_function("test_func", {"name": "Alice"})

def test_function_retry_logic():
    """Test the retry logic in function calling."""
    registry = FunctionRegistry()
    caller = GemmaFunctionCaller(registry)

    # Create a mock function that fails twice then succeeds
    mock_func = Mock(side_effect=[ValueError, ValueError, "success"])
    schema = {
        "name": "retry_func",
        "description": "A function to test retry logic",
        "parameters": {}
    }

    caller.register_function("retry_func", mock_func, schema)
    result = caller.call_function("retry_func", {}, max_retries=3)
    assert result == "success"
    assert mock_func.call_count == 3

    # Test max retries exceeded
    mock_func.reset_mock()
    mock_func.side_effect = ValueError
    with pytest.raises(RuntimeError):
        caller.call_function("retry_func", {}, max_retries=2)
    assert mock_func.call_count == 2

def test_system_prompt_updates():
    """Test that system prompt updates correctly with function changes."""
    registry = FunctionRegistry()
    caller = GemmaFunctionCaller(registry)
    func, schema = create_test_function()

    # Test initial state
    assert "No functions are currently available" in caller.get_system_prompt()

    # Test after adding function
    caller.register_function("test_func", func, schema)
    prompt = caller.get_system_prompt()
    assert "test_func" in prompt
    assert "A test function" in prompt

    # Test after removing function
    caller.unregister_function("test_func")
    assert "No functions are currently available" in caller.get_system_prompt()

def test_function_validation():
    """Test function parameter validation."""
    registry = FunctionRegistry()
    caller = GemmaFunctionCaller(registry)
    func, schema = create_test_function()

    caller.register_function("test_func", func, schema)

    # Test missing required parameter
    with pytest.raises(ValidationError):
        caller.call_function("test_func", {})

    # Test invalid parameter type
    with pytest.raises(ValidationError):
        caller.call_function("test_func", {"name": 123})

    # Test invalid parameter value
    with pytest.raises(ValidationError):
        caller.call_function("test_func", {"name": "Alice", "age": -1}) 