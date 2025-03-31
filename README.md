# Gemma Function Calling

A robust function calling implementation for the Gemma language model, enabling seamless integration with external APIs, databases, and system operations.

## Features

- Dynamic Function Registry for runtime function management
- Robust Input Validation with type checking
- Comprehensive Error Handling and logging
- Automatic Schema Management
- Extensible Design for custom function integration
- Comprehensive Test Coverage

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Make (optional, for using Makefile commands)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/gemma-fncall-flow.git
cd gemma-fncall-flow
```

2. Install dependencies:
```bash
make install  # or pip install -e ".[test,dev]"
```

### Development Commands

```bash
# Run tests
make test  # or pytest tests/ -v

# Check code quality
make lint  # check code quality
make format  # auto-format code

# Clean up temporary files
make clean
```

## Usage

### Basic Example

```python
from gemma_fncall_flow import FunctionRegistry, GemmaFunctionCaller
from validation import ParameterType

# Initialize registry and caller
registry = FunctionRegistry()
caller = GemmaFunctionCaller(registry)

# Define function schema
schema = {
    "name": "greet",
    "description": "Greet a person by name",
    "parameters": {
        "name": {
            "type": ParameterType.STRING.value,
            "description": "Name of the person to greet",
            "required": True
        }
    },
    "required": ["name"]
}

# Define and register function
def greet(name: str) -> str:
    return f"Hello, {name}!"
registry.register("greet", greet, schema)

# Call function
result = caller.call_function("greet", {"name": "Alice"})
print(result)  # Output: Hello, Alice!
```

## Project Structure

```
gemma-fncall-flow/
├── tests/                   # Test suite
│   ├── test_function_calling.py
│   ├── test_validation.py
│   ├── test_weather_example.py
│   ├── test_file_system_example.py
│   └── test_database_example.py
├── gemma_fncall_flow/       # Core implementation
│   ├── __init__.py
│   ├── function_calling.py
│   └── validation.py
├── setup.py                 # Package configuration
├── requirements.txt         # Dependencies
├── requirements-test.txt    # Test dependencies
├── Makefile                # Development commands
└── README.md               # Documentation
```

## API Reference

### FunctionRegistry

```python
registry = FunctionRegistry()

# Register function
registry.register_function(my_function)

# Get function schema
schema = registry.get_function_schema("function_name")

# List registered functions
functions = registry.list_functions()
```

### GemmaFunctionCaller

```python
caller = GemmaFunctionCaller(registry)

# Call function
result = caller.call_function(
    "function_name",
    {"param1": "value1"}
)

# Get function documentation
doc = caller.get_function_documentation("function_name")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 