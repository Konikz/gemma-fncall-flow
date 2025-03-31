from setuptools import setup, find_packages

setup(
    name="gemma-function-calling",
    version="0.1.0",
    description="A robust function calling implementation for the Gemma language model",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "google-generativeai>=0.3.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "SQLAlchemy>=2.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "isort>=5.0.0",
        "mypy>=1.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
) 