# src.appeears_client.auth.py
import requests
from .config import base_url
from ..exceptions import LoginError, RequestError

class AppEEARSClient:
    def __init__(self, username: str, password: str):
        self.token = self.login(username=username, password=password)

    def login(self, username: str, password: str) -> str:
        """Log in and return a token."""
        response = requests.post(f"{base_url}/login", auth=(username, password))
        if response.status_code == 200:
            return response.json()['token']
        else:
            raise LoginError("Failed to log in to AppEEARS API")
    
    def logout(self):
        """Logs out of the API."""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/logout", headers=headers)
        if response.status_code != 204:
            raise RequestError("Failed to log out")
