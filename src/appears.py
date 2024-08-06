# src.appeears.py
from datetime import datetime

from .appeears_client.auth import AppEEARSClient
from .appeears_client.file_management import FileManager
from .appeears_client.task_management import TaskManagement
from .appeears_client.task_orchestrator import TaskOrchestrator
from .appeears_client.product_management import ProductManagement

class APIClient:
    def __init__(self, username: str, password: str):
        self.client = AppEEARSClient(username=username, password=password)
        self.token = self.client.token
        self.product_manager = ProductManagement(token=self.token)
        self.task_manager = TaskManagement(token=self.token)
        self.file_manager = FileManager(token=self.token)
        self.task_orchestrator = TaskOrchestrator(token=self.token)

    def login(self):
        self.token = self.client.login()
        self.refresh_clients()

    def logout(self):
        self.client.logout()

    def refresh_clients(self):
        """Refresh internal client instances with new token if it was updated."""
        self.product_manager = ProductManagement(token=self.token)
        self.task_manager = TaskManagement(token=self.token)
        self.file_manager = FileManager(token=self.token)
        self.task_orchestrator = TaskOrchestrator(token=self.token)

    def get_product_info(self, product_id: str):
        return self.product_manager.get_product(product_id)

    def submit_and_retrieve_task(
            self, 
            latitude: float, 
            longitude: float, 
            product_id: str, 
            band_names: list, 
            start_date: datetime,  
            end_date: datetime
        ):
        
        result = self.task_orchestrator.execute_and_retrieve_task(
                    latitude=latitude, 
                    longitude=longitude, 
                    product_id=product_id, 
                    band_names=band_names, 
                    start_date=start_date, 
                    end_date=end_date
                )
        return result