# src.appeears_client.task_orchestrator.py

import time
from .task_management import TaskManagement
from .file_management import FileManager

class TaskOrchestrator:
    def __init__(self, token: str):
        self.task_manager = TaskManagement(token=token)
        self.file_manager = FileManager(token=token)

    def execute_and_retrieve_task(self, latitude: float, longitude: float, product_id: str, band_names: list, days_back: int = 30):
        """Orchestrates the task submission, status checking, and file retrieval."""
        try:
            # Submit the task and get task_id
            response = self.task_manager.submit_point_task(
                latitude=latitude,
                longitude=longitude,
                product_id=product_id,
                band_names=band_names,
                days_back=days_back
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
