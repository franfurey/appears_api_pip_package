# src.client.py
import requests
from .exceptions import LoginError, RequestError

class AppEEARSClient:
    """Client to interact with the AppEEARS API."""
    def __init__(self, username: str, password: str):
        self.base_url = "https://appeears.earthdatacloud.nasa.gov/api"
        self.token = self.login(username, password)

    def login(self, username: str, password: str) -> str:
        """Logs in to the API and returns a token."""
        response = requests.post(f"{self.base_url}/login", auth=(username, password))
        if response.status_code == 200:
            return response.json()['token']
        else:
            raise LoginError("Failed to log in to AppEEARS API")

    def get_product(self, product_id: str) -> dict:
        """Retrieves product information."""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/product/{product_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise RequestError("Failed to retrieve product")

    def logout(self):
        """Logs out of the API."""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/logout", headers=headers)
        if response.status_code != 204:
            raise RequestError("Failed to log out")
