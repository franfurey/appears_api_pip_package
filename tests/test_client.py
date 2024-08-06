# tests.test_client.py
import os
import pytest
from dotenv import load_dotenv
from src.appears import APIClient
from src.exceptions import LoginError, RequestError

# Load environment variables
load_dotenv()

# Create a fixture to handle API client configuration and cleanup
@pytest.fixture(scope="module")
def client():
    """Setup of the API client before testing and teardown after."""
    api_client = APIClient(username=os.getenv("APPEARS_USER"), password=os.getenv("APPEARS_PASS"))
    yield api_client
    api_client.logout()

def test_login_success(client):
    """Verify that the token is obtained correctly when logging in."""
    assert client.token, "Login should provide a token"

def test_product_retrieval(client):
    """Tests the retrieval of information from a known product."""
    product_id = 'MYD09A1.061'
    product_info = client.get_product_info(product_id=product_id)
    assert isinstance(product_info, dict), "Should retrieve a dictionary with product info"

def test_get_all_products_and_layers(client):
    """Tests the retrieval of all products and their layers."""
    try:
        all_products = client.product_manager.get_all_products_and_layers()
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
        layers = client.product_manager.get_product_layers(product_id=product_id)
        assert isinstance(layers, dict), "Should retrieve a dictionary with product layers"
    except RequestError as e:
        pytest.fail(f"RequestError occurred: {e}")

def test_submit_and_retrieve_task(client):
    """Tests the full cycle of submitting and retrieving task data."""
    latitude = 40.7128
    longitude = -74.0060
    product_id = 'example_product'
    band_names = ["band1", "band2"]
    days_back = 30

    try:
        response = client.submit_and_retrieve_task(
            latitude=latitude,
            longitude=longitude,
            product_id=product_id,
            band_names=band_names,
            days_back=days_back
        )
        assert isinstance(response, dict), "Should retrieve a dictionary with task data"
    except RequestError as e:
        pytest.fail(f"RequestError occurred: {e}")

def test_logout(client):
    """Verify that logging out completes without error."""
    try:
        client.logout()
        assert True  # Simply check if logout passed without raising an exception
    except RequestError:
        pytest.fail("Logout failed")