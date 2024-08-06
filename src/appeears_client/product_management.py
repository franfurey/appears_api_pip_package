# src.appeears_client.product_management.py
import requests
from .config import base_url
from ..exceptions import RequestError
from ..models import get_product_by_id

class ProductManagement:
    def __init__(self, token: str):
        self.token = token
        self.base_url = base_url

    def get_product(self, product_id: str) -> dict:
        """Retrieves product information only if the product_id is valid."""
        try:
            # This will raise a ValueError if the product_id is not valid
            valid_product = get_product_by_id(product_id=product_id)
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.base_url}/product/{product_id}", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError("Failed to retrieve product")
        except ValueError as e:
            # Handle the error by re-raising it or converting it to a different type of error
            raise RequestError(f"Invalid product ID: {str(e)}")

    def get_all_products_and_layers(self) -> dict:
        """Retrieves all products and their layers using the authenticated session."""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/product", headers=headers)
        if response.status_code == 200:
            products = response.json()
            all_products = {}
            for product in products:
                product_id = product['ProductAndVersion']
                layers = self.get_product_layers(product_id=product_id)
                all_products[product_id] = {
                    'product_details': product,
                    'layers': layers
                }
            return all_products
        else:
            raise RequestError("Failed to retrieve all products")

    def get_product_layers(self, product_id: str) -> dict:
        """Retrieves layers for a given product using the authenticated session."""
        try:
            # Validate product_id by checking if it exists in the predefined PRODUCTS list
            valid_product = get_product_by_id(product_id=product_id)
            headers = {'Authorization': f'Bearer {self.token}'}
            layer_url = f"{self.base_url}/product/{product_id}"
            response = requests.get(layer_url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise RequestError(f"Failed to retrieve layers for product {product_id}")
        except ValueError as e:
            # If the product ID is not found in PRODUCTS, handle it appropriately
            raise RequestError(f"Invalid product ID: {str(e)}")