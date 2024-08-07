# src.appeears_client.task_orchestrator.py
import time
from datetime import datetime

from .file_management import FileManager
from .task_management import TaskManagement

class TaskOrchestrator:
    def __init__(self, token: str):
        self.task_manager = TaskManagement(token=token)
        self.file_manager = FileManager(token=token)

    def execute_and_retrieve_area_task(
        self, 
        geo_json: dict, 
        product_id: str,
        band_names: list,
        start_date: datetime, 
        end_date: datetime
    ):
        """Orchestrates the area task submission, status checking, and file retrieval."""
        try:
            # Convert datetime objects to strings in the required format
            formatted_start_date = start_date.strftime("%m-%d-%Y")
            formatted_end_date = end_date.strftime("%m-%d-%Y")

            # Prepare layers list based on product_id and band_names, assuming all bands belong to the same product
            layers = [{"product": product_id, "layer": band_name} for band_name in band_names]

            # Submit the task and get task_id
            response = self.task_manager.submit_area_task(
                geo_json=geo_json,
                start_date=formatted_start_date,
                end_date=formatted_end_date,
                layers=layers
            )

            if 'task_id' not in response:
                print("Failed to submit task:", response.get('error', 'Unknown Error'))
                return None

            task_id = response['task_id']
            print(f"Task submitted successfully, task ID: {task_id}")

            # Check task status until done or failed
            while True:
                task_complete = self.task_manager.check_task_status(task_id=task_id)
                if task_complete:
                    print("Task completed successfully.")
                    break
                else:
                    print("Task not completed yet. Waiting...")
                    time.sleep(10)  # Wait before checking again to avoid too many requests

            # List files of the completed task
            files = self.task_manager.list_task_files(task_id=task_id)
            if files:
                return files
            else:
                print("No files available or task failed.")
                return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def execute_and_retrieve_point_task(
            self, 
            latitude: float, 
            longitude: float, 
            product_id: str, 
            band_names: list, 
            start_date: datetime, 
            end_date: datetime
        ):
        """Orchestrates the task submission, status checking, and file retrieval."""
        try:
            # Submit the task and get task_id
            response = self.task_manager.submit_point_task(
                latitude=latitude,
                longitude=longitude,
                product_id=product_id,
                band_names=band_names,
                start_date=start_date,
                end_date=end_date
            )

            if 'task_id' not in response:
                print("Failed to submit task:", response.get('error', 'Unknown Error'))
                return None

            task_id = response['task_id']
            print(f"Task submitted successfully, task ID: {task_id}")

            # Check task status until done or failed
            while True:
                if self.task_manager.check_task_status(task_id=task_id):
                    print("Task completed successfully.")
                    break
                else:
                    print("Task not completed yet. Waiting...")
                    time.sleep(10)  # Wait before checking again to avoid too many requests

            # List files of the completed task
            files = self.task_manager.list_task_files(task_id=task_id)
            if files:
                return files
            else:
                print("No files available or task failed.")
                return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
