"""
Test configuration and shared fixtures for the Activities API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for the FastAPI application.
    
    Returns a fresh client instance that can be used to make requests
    to the application during tests.
    """
    return TestClient(app)
