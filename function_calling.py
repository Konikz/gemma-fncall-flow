from typing import Any, Callable, Dict, List, Optional, Union
import logging
from validation import FunctionSchema, FunctionValidator, ValidationError, ParameterType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FunctionRegistry:
    """Registry for managing function definitions and their schemas."""
    def __init__(self):
        self._functions: Dict[str, Callable] = {}
        self._schemas: Dict[str, FunctionSchema] = {}

    def register(self, name: str, func: Callable, schema: Dict[str, Any]) -> None:
        """Register a function with its schema."""
        if name in self._functions:
            raise ValidationError(f"Function '{name}' is already registered")
        
        try:
            # Validate the function definition
            FunctionValidator.validate_function_definition(schema)
            
            # Create and store the schema
            function_schema = FunctionSchema(
                name=schema["name"],
                description=schema["description"],
                parameters=schema["parameters"],
                required=schema.get("required", [])
            )
            
            self._schemas[name] = function_schema
            self._functions[name] = func
            logger.info(f"Successfully registered function: {name}")
            
        except ValidationError as e:
            logger.error(f"Failed to register function {name}: {str(e)}")
            raise

    def unregister(self, name: str) -> None:
        """Remove a function from the registry."""
        if name not in self._functions:
            raise ValueError(f"Function {name} not found in registry")
        
        del self._functions[name]
        del self._schemas[name]
        logger.info(f"Successfully unregistered function: {name}")

    def update_function(self, name: str, new_func: Callable, new_schema: Dict[str, Any]) -> None:
        """Update an existing function's implementation and schema."""
        if name not in self._functions:
            raise ValueError(f"Function {name} not found in registry")
        
        try:
            # Validate the new schema
            FunctionValidator.validate_function_definition(new_schema)
            
            # Create and store the new schema
            function_schema = FunctionSchema(
                name=new_schema["name"],
                description=new_schema["description"],
                parameters=new_schema["parameters"],
                required=new_schema.get("required", [])
            )
            
            self._schemas[name] = function_schema
            self._functions[name] = new_func
            logger.info(f"Successfully updated function: {name}")
            
        except ValidationError as e:
            logger.error(f"Failed to update function {name}: {str(e)}")
            raise

    def get_function(self, name: str) -> Optional[Callable]:
        """Get a function by name."""
        return self._functions.get(name)

    def get_schema(self, name: str) -> Optional[FunctionSchema]:
        """Get a function's schema by name."""
        return self._schemas.get(name)

    def list_functions(self) -> List[Dict[str, str]]:
        """List all registered functions with their descriptions."""
        return [
            {"name": name, "description": schema.description}
            for name, schema in self._schemas.items()
        ]

class GemmaFunctionCaller:
    """Main class for handling function calls with the Gemma model."""
    def __init__(self, registry: FunctionRegistry):
        self.registry = registry
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt listing available functions."""
        functions = self.registry.list_functions()
        if not functions:
            return "No functions are currently available."

        prompt = "Available functions:\n\n"
        for func in functions:
            prompt += f"- {func['name']}: {func['description']}\n"
        return prompt

    def update_system_prompt(self) -> None:
        """Update the system prompt when functions change."""
        self._system_prompt = self._build_system_prompt()

    def call_function(self, name: str, parameters: Dict[str, Any], max_retries: int = 3) -> Any:
        """Call a registered function with the given parameters."""
        function = self.registry.get_function(name)
        if not function:
            raise ValueError(f"Function {name} not found")

        schema = self.registry.get_schema(name)
        if not schema:
            raise ValueError(f"Schema for function {name} not found")

        # Validate parameters
        try:
            schema.validate_parameters(parameters)
        except ValidationError as e:
            logger.error(f"Parameter validation failed for {name}: {str(e)}")
            raise

        # Execute function with retry logic
        retries = 0
        last_error = None

        while retries < max_retries:
            try:
                result = function(**parameters)
                logger.info(f"Successfully called function {name}")
                return result
            except Exception as e:
                last_error = e
                retries += 1
                logger.warning(f"Attempt {retries} failed for {name}: {str(e)}")

        logger.error(f"Function {name} failed after {max_retries} attempts")
        raise RuntimeError(f"Function execution failed: {str(last_error)}")

    def get_system_prompt(self) -> str:
        """Get the current system prompt."""
        return self._system_prompt

    def register_function(self, name: str, func: Callable, schema: Dict[str, Any]) -> None:
        """Register a new function and update the system prompt."""
        self.registry.register(name, func, schema)
        self.update_system_prompt()

    def unregister_function(self, name: str) -> None:
        """Unregister a function and update the system prompt."""
        self.registry.unregister(name)
        self.update_system_prompt()

    def update_function(self, name: str, new_func: Callable, new_schema: Dict[str, Any]) -> None:
        """Update an existing function and update the system prompt."""
        self.registry.update_function(name, new_func, new_schema)
        self.update_system_prompt() 