from enum import Enum
from typing import Any, Dict, List, Optional, Union
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParameterType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ParameterSchema:
    """Schema for validating function parameters."""
    def __init__(self, 
                 type: Union[str, ParameterType],
                 description: str,
                 required: bool = False,
                 minimum: Optional[float] = None,
                 maximum: Optional[float] = None,
                 pattern: Optional[str] = None,
                 enum_values: Optional[List[Any]] = None,
                 items: Optional[Dict[str, Any]] = None,
                 properties: Optional[Dict[str, Any]] = None):
        self.type = ParameterType(type) if isinstance(type, str) else type
        self.description = description
        self.required = required
        self.minimum = minimum
        self.maximum = maximum
        self.pattern = pattern
        self.enum_values = enum_values
        self.items = items
        self.properties = properties

    def validate(self, value: Any) -> None:
        """Validate a parameter value against the schema."""
        if value is None:
            if self.required:
                raise ValidationError(f"Required parameter is missing")
            return

        if self.type == ParameterType.STRING:
            if not isinstance(value, str):
                raise ValidationError(f"Expected string, got {type(value)}")
            if self.pattern and not re.match(self.pattern, value):
                raise ValidationError(f"String does not match pattern: {self.pattern}")

        elif self.type == ParameterType.NUMBER:
            if not isinstance(value, (int, float)):
                raise ValidationError(f"Expected number, got {type(value)}")
            if self.minimum is not None and value < self.minimum:
                raise ValidationError(f"Value {value} is less than minimum {self.minimum}")
            if self.maximum is not None and value > self.maximum:
                raise ValidationError(f"Value {value} is greater than maximum {self.maximum}")

        elif self.type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValidationError(f"Expected boolean, got {type(value)}")

        elif self.type == ParameterType.ARRAY:
            if not isinstance(value, list):
                raise ValidationError(f"Expected array, got {type(value)}")
            if self.items:
                item_validator = ParameterSchema(**self.items)
                for item in value:
                    item_validator.validate(item)

        elif self.type == ParameterType.OBJECT:
            if not isinstance(value, dict):
                raise ValidationError(f"Expected object, got {type(value)}")
            if self.properties:
                for prop_name, prop_schema in self.properties.items():
                    if prop_name in value:
                        prop_validator = ParameterSchema(**prop_schema)
                        prop_validator.validate(value[prop_name])

        elif self.type == ParameterType.ENUM:
            if self.enum_values is None:
                raise ValidationError("Enum values not specified in schema")
            if value not in self.enum_values:
                raise ValidationError(f"Value {value} not in enum values: {self.enum_values}")

class FunctionSchema:
    """Schema for validating function definitions."""
    def __init__(self, 
                 name: str,
                 description: str,
                 parameters: Dict[str, Dict[str, Any]],
                 required: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.parameters = {
            name: ParameterSchema(**param_schema)
            for name, param_schema in parameters.items()
        }
        self.required = required or []

    def validate_parameters(self, params: Dict[str, Any]) -> None:
        """Validate function parameters against the schema."""
        # Check for required parameters
        for param_name in self.required:
            if param_name not in params:
                raise ValidationError(f"Required parameter '{param_name}' is missing")

        # Validate each provided parameter
        for param_name, param_value in params.items():
            if param_name not in self.parameters:
                raise ValidationError(f"Unknown parameter: {param_name}")
            try:
                self.parameters[param_name].validate(param_value)
            except ValidationError as e:
                raise ValidationError(f"Invalid value for parameter '{param_name}': {str(e)}")

class FunctionValidator:
    """Validator for function definitions and calls."""
    @staticmethod
    def validate_function_definition(schema: Dict[str, Any]) -> None:
        """Validate a function definition schema."""
        required_fields = ["name", "description", "parameters"]
        for field in required_fields:
            if field not in schema:
                raise ValidationError(f"Missing required field in function definition: {field}")

        if not isinstance(schema["parameters"], dict):
            raise ValidationError("Parameters must be an object")

        # Validate parameter definitions
        for param_name, param_schema in schema["parameters"].items():
            if "type" not in param_schema:
                raise ValidationError(f"Parameter '{param_name}' missing type")
            if "description" not in param_schema:
                raise ValidationError(f"Parameter '{param_name}' missing description")

            try:
                param_type = ParameterType(param_schema["type"])
            except ValueError:
                raise ValidationError(f"Invalid parameter type for '{param_name}': {param_schema['type']}")

    @staticmethod
    def create_schema_from_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a parameter schema from a dictionary of parameters."""
        schema = {}
        for param_name, param_value in params.items():
            if isinstance(param_value, str):
                param_type = ParameterType.STRING
            elif isinstance(param_value, bool):
                param_type = ParameterType.BOOLEAN
            elif isinstance(param_value, (int, float)):
                param_type = ParameterType.NUMBER
            elif isinstance(param_value, list):
                param_type = ParameterType.ARRAY
            elif isinstance(param_value, dict):
                param_type = ParameterType.OBJECT
            else:
                raise ValidationError(f"Unsupported parameter type for '{param_name}': {type(param_value)}")

            schema[param_name] = {
                "type": param_type.value,
                "description": f"Parameter: {param_name}"
            }

        return schema 