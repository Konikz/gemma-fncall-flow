import pytest
from validation import (
    ParameterType,
    ValidationError,
    ParameterSchema,
    FunctionSchema,
    FunctionValidator
)

def test_parameter_type_values():
    """Test that ParameterType enum has correct values."""
    assert ParameterType.STRING.value == "string"
    assert ParameterType.NUMBER.value == "number"
    assert ParameterType.BOOLEAN.value == "boolean"
    assert ParameterType.ARRAY.value == "array"
    assert ParameterType.OBJECT.value == "object"
    assert ParameterType.ENUM.value == "enum"

def test_parameter_schema_validation():
    """Test parameter schema validation."""
    # Test string validation
    string_schema = ParameterSchema(
        type=ParameterType.STRING,
        description="A string parameter",
        pattern=r"^[A-Za-z]+$"
    )
    string_schema.validate("Hello")
    with pytest.raises(ValidationError):
        string_schema.validate(123)
    with pytest.raises(ValidationError):
        string_schema.validate("Hello123")

    # Test number validation
    number_schema = ParameterSchema(
        type=ParameterType.NUMBER,
        description="A number parameter",
        minimum=0,
        maximum=100
    )
    number_schema.validate(50)
    with pytest.raises(ValidationError):
        number_schema.validate("50")
    with pytest.raises(ValidationError):
        number_schema.validate(-1)
    with pytest.raises(ValidationError):
        number_schema.validate(101)

    # Test boolean validation
    boolean_schema = ParameterSchema(
        type=ParameterType.BOOLEAN,
        description="A boolean parameter"
    )
    boolean_schema.validate(True)
    boolean_schema.validate(False)
    with pytest.raises(ValidationError):
        boolean_schema.validate("true")
    with pytest.raises(ValidationError):
        boolean_schema.validate(1)

    # Test array validation
    array_schema = ParameterSchema(
        type=ParameterType.ARRAY,
        description="An array parameter",
        items={
            "type": ParameterType.STRING.value,
            "description": "Array item"
        }
    )
    array_schema.validate(["one", "two", "three"])
    with pytest.raises(ValidationError):
        array_schema.validate("not an array")
    with pytest.raises(ValidationError):
        array_schema.validate([1, 2, 3])

    # Test object validation
    object_schema = ParameterSchema(
        type=ParameterType.OBJECT,
        description="An object parameter",
        properties={
            "name": {
                "type": ParameterType.STRING.value,
                "description": "Name field"
            }
        }
    )
    object_schema.validate({"name": "test"})
    with pytest.raises(ValidationError):
        object_schema.validate("not an object")
    with pytest.raises(ValidationError):
        object_schema.validate({"name": 123})

    # Test enum validation
    enum_schema = ParameterSchema(
        type=ParameterType.ENUM,
        description="An enum parameter",
        enum_values=["red", "green", "blue"]
    )
    enum_schema.validate("red")
    with pytest.raises(ValidationError):
        enum_schema.validate("yellow")

def test_function_schema_validation():
    """Test function schema validation."""
    schema = FunctionSchema(
        name="test_function",
        description="A test function",
        parameters={
            "param1": {
                "type": ParameterType.STRING.value,
                "description": "First parameter"
            },
            "param2": {
                "type": ParameterType.NUMBER.value,
                "description": "Second parameter",
                "minimum": 0
            }
        },
        required=["param1"]
    )

    # Test valid parameters
    schema.validate_parameters({
        "param1": "test",
        "param2": 42
    })

    # Test missing required parameter
    with pytest.raises(ValidationError):
        schema.validate_parameters({
            "param2": 42
        })

    # Test invalid parameter type
    with pytest.raises(ValidationError):
        schema.validate_parameters({
            "param1": "test",
            "param2": "not a number"
        })

    # Test unknown parameter
    with pytest.raises(ValidationError):
        schema.validate_parameters({
            "param1": "test",
            "unknown": "value"
        })

def test_function_validator():
    """Test function validator."""
    # Test valid function definition
    valid_schema = {
        "name": "test_function",
        "description": "A test function",
        "parameters": {
            "param1": {
                "type": "string",
                "description": "First parameter"
            }
        }
    }
    FunctionValidator.validate_function_definition(valid_schema)

    # Test missing required field
    invalid_schema = {
        "name": "test_function",
        "parameters": {}
    }
    with pytest.raises(ValidationError):
        FunctionValidator.validate_function_definition(invalid_schema)

    # Test invalid parameter type
    invalid_schema = {
        "name": "test_function",
        "description": "A test function",
        "parameters": {
            "param1": {
                "type": "invalid_type",
                "description": "First parameter"
            }
        }
    }
    with pytest.raises(ValidationError):
        FunctionValidator.validate_function_definition(invalid_schema)

def test_create_schema_from_parameters():
    """Test creating schema from parameters."""
    params = {
        "string_param": "test",
        "number_param": 42,
        "boolean_param": True,
        "array_param": [1, 2, 3],
        "object_param": {"key": "value"}
    }

    schema = FunctionValidator.create_schema_from_parameters(params)

    assert schema["string_param"]["type"] == ParameterType.STRING.value
    assert schema["number_param"]["type"] == ParameterType.NUMBER.value
    assert schema["boolean_param"]["type"] == ParameterType.BOOLEAN.value
    assert schema["array_param"]["type"] == ParameterType.ARRAY.value
    assert schema["object_param"]["type"] == ParameterType.OBJECT.value

    # Test unsupported type
    with pytest.raises(ValidationError):
        FunctionValidator.create_schema_from_parameters({
            "invalid": lambda x: x
        }) 