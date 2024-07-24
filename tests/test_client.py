# tests.test_client.py
import os
import pytest
from dotenv import load_dotenv
from src.client import AppEEARSClient
from src.exceptions import LoginError, RequestError

# Load environment variables
load_dotenv()

# Create a fixture to handle API client configuration and cleanup
@pytest.fixture(scope="module")
def client():
    """Setup of the API client before testing and teardown after."""
    api_client = AppEEARSClient(username=os.getenv("APPEARS_USER"), password=os.getenv("APPEARS_PASS"))
    yield api_client
    api_client.logout()

def test_login_success(client):
    """Verify that the token is obtained correctly when logging in."""
    assert client.token, "Login should provide a token"

def test_product_retrieval(client):
    """Tests the retrieval of information from a known product."""
    product_id = 'MOD11A1.061'
    product_info = client.get_product(product_id=product_id)
    assert isinstance(product_info, dict), "Should retrieve a dictionary with product info"
    assert 'Layer' in product_info, "Product info should contain 'Layer' key"
