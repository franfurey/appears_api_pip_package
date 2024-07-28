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
    product_id = 'MYD09A1.061'
    product_info = client.get_product(product_id=product_id)
    assert isinstance(product_info, dict), "Should retrieve a dictionary with product info"

def test_get_all_products_and_layers(client):
    """Tests the retrieval of all products and their layers."""
    try:
        all_products = client.get_all_products_and_layers()
        assert isinstance(all_products, dict), "Should retrieve a dictionary with all products and layers"
        for product_id, details in all_products.items():
            assert 'product_details' in details, "Each product should have product details"
            assert 'layers' in details, "Each product should have layers"
    except RequestError as e:
        pytest.fail(f"RequestError occurred: {e}")

def test_get_product_layers(client):
    """Tests the retrieval of layers for a specific product."""
    product_id = 'MYD09A1.061'
    try:
        layers = client.get_product_layers(product_id)
        assert isinstance(layers, dict), "Should retrieve a dictionary with product layers"
    except RequestError as e:
        pytest.fail(f"RequestError occurred: {e}")

def test_fetch_and_store_point_data(client):
    """Tests fetching and storing point data."""
    latitude = 40.7128
    longitude = -74.0060
    product = "example_product"
    bands = ["band1", "band2"]
    days_back = 30

    try:
        point_data = client.fetch_and_store_point_data(
            latitude, longitude, product, bands, client.token, days_back
        )
        assert isinstance(point_data, dict), "Should retrieve a dictionary with point data"
    except RequestError as e:
        pytest.fail(f"RequestError occurred: {e}")