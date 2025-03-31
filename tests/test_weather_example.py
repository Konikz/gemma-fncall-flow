import pytest
import os
from unittest.mock import patch, Mock
import responses
import requests
from examples.weather_example import (
    WeatherAPI,
    format_weather_response,
    format_forecast_response,
    create_weather_function,
    create_forecast_function
)

@pytest.fixture
def mock_weather_data():
    """Mock weather data fixture."""
    return {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {
            "temp": 15.6,
            "feels_like": 14.8,
            "humidity": 76
        },
        "weather": [
            {"description": "scattered clouds"}
        ]
    }

@pytest.fixture
def mock_forecast_data():
    """Mock forecast data fixture."""
    return {
        "city": {
            "name": "London",
            "country": "GB"
        },
        "list": [
            {
                "dt": 1617235200,  # 2021-04-01 00:00:00
                "main": {
                    "temp": 12.3
                },
                "weather": [
                    {"description": "clear sky"}
                ]
            },
            {
                "dt": 1617246000,  # 2021-04-01 03:00:00
                "main": {
                    "temp": 10.5
                },
                "weather": [
                    {"description": "clear sky"}
                ]
            }
        ]
    }

@pytest.fixture
def api_key():
    """Set up and tear down the API key environment variable."""
    with patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_key"}):
        yield "test_key"

def test_weather_api_initialization(api_key):
    """Test WeatherAPI initialization."""
    api = WeatherAPI()
    assert api.api_key == "test_key"
    assert api.base_url == "http://api.openweathermap.org/data/2.5"

def test_weather_api_initialization_no_key():
    """Test WeatherAPI initialization without API key."""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError):
            WeatherAPI()

@responses.activate
def test_get_weather(api_key):
    """Test getting current weather."""
    api = WeatherAPI()
    mock_response = {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {"temp": 15.6},
        "weather": [{"description": "cloudy"}]
    }

    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/weather",
        json=mock_response,
        status=200
    )

    result = api.get_weather("London")
    assert result == mock_response

@responses.activate
def test_get_forecast(api_key):
    """Test getting weather forecast."""
    api = WeatherAPI()
    mock_response = {
        "city": {"name": "London"},
        "list": [{"dt": 1617235200, "main": {"temp": 15.6}}]
    }

    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/forecast",
        json=mock_response,
        status=200
    )

    result = api.get_forecast("London", days=1)
    assert result == mock_response

def test_format_weather_response(mock_weather_data):
    """Test formatting weather response."""
    formatted = format_weather_response(mock_weather_data, "metric")
    assert "London, GB" in formatted
    assert "15.6°C" in formatted
    assert "14.8°C" in formatted
    assert "76%" in formatted
    assert "scattered clouds" in formatted

def test_format_forecast_response(mock_forecast_data):
    """Test formatting forecast response."""
    formatted = format_forecast_response(mock_forecast_data, "metric")
    assert "London, GB" in formatted
    assert "2021-04-01" in formatted
    assert "11.4°C" in formatted  # Average of 12.3 and 10.5
    assert "clear sky" in formatted

def test_create_weather_function(api_key):
    """Test creating weather function."""
    api = WeatherAPI()
    weather_func = create_weather_function(api)

    assert "function" in weather_func
    assert "schema" in weather_func
    schema = weather_func["schema"]
    assert schema["name"] == "get_weather"
    assert "location" in schema["parameters"]
    assert "unit" in schema["parameters"]
    assert schema["required"] == ["location"]

def test_create_forecast_function(api_key):
    """Test creating forecast function."""
    api = WeatherAPI()
    forecast_func = create_forecast_function(api)

    assert "function" in forecast_func
    assert "schema" in forecast_func
    schema = forecast_func["schema"]
    assert schema["name"] == "get_forecast"
    assert "location" in schema["parameters"]
    assert "days" in schema["parameters"]
    assert "unit" in schema["parameters"]
    assert schema["required"] == ["location"]

@responses.activate
def test_weather_function_integration(api_key, mock_weather_data):
    """Test weather function integration."""
    api = WeatherAPI()
    weather_func = create_weather_function(api)

    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/weather",
        json=mock_weather_data,
        status=200
    )

    result = weather_func["function"]("London", "metric")
    assert isinstance(result, str)
    assert "London" in result
    assert "15.6°C" in result

@responses.activate
def test_forecast_function_integration(api_key, mock_forecast_data):
    """Test forecast function integration."""
    api = WeatherAPI()
    forecast_func = create_forecast_function(api)

    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/forecast",
        json=mock_forecast_data,
        status=200
    )

    result = forecast_func["function"]("London", 1, "metric")
    assert isinstance(result, str)
    assert "London" in result
    assert "2021-04-01" in result

@responses.activate
def test_api_error_handling(api_key):
    """Test API error handling."""
    api = WeatherAPI()

    # Test 404 error
    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/weather",
        json={"message": "City not found"},
        status=404
    )

    with pytest.raises(requests.RequestException):
        api.get_weather("NonexistentCity")

    # Test network error
    responses.add(
        responses.GET,
        "http://api.openweathermap.org/data/2.5/forecast",
        body=requests.RequestException()
    )

    with pytest.raises(requests.RequestException):
        api.get_forecast("London") 