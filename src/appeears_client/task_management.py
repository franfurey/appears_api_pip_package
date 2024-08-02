# src.appeears_client.task_management.py
import os
import re
import time
import pprint
import logging
import requests
import rasterio
from datetime import datetime, timedelta

from .config import base_url
from ..exceptions import RequestError
from ..models import get_product_by_id

class TaskManagement:
    def __init__(self, token: str):
        self.token = token

    def check_task_status(self, task_id: str) -> bool:
        """ Checks the status of the task and returns True if it is complete. """
        status_url = f"{self.base_url}/task/{task_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        while True:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                task_info = response.json()
                task_status = task_info['status']
                print(f"Task status for {task_id}: {task_status}")

                if task_status == 'done':
                    return True
                elif task_status in ['error', 'failed']:
                    print(f"Task {task_id} failed with status {task_status}")
                    return False
                else:
                    # Wait for a bit before checking again
                    time.sleep(20)
            else:
                print(f"Error checking task status for {task_id}: HTTP {response.status_code}")
                return False

    def list_task_files(self, task_id: str) -> list:
        """ Lists the available files of a completed task. """
        url = f"{self.base_url}/bundle/{task_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            files = response.json().get('files', [])
            print(f"Files found for the task {task_id}: {len(files)} listed files")
            pprint.pprint(files)
            return files
        else:
            print(f"Could not list the files for the task {task_id}: HTTP {response.status_code}")
            return []
        
    def submit_point_task(
            self, 
            latitude: float, 
            longitude: float, 
            product_id: str, 
            band_names: list, 
            token: str,
            days_back: int = 30
            ) -> dict:
        """Submits a task for a specific geographic point and retrieves specified bands of a product."""
        try:
            # Validate product_id and bands
            product = get_product_by_id(product_id=product_id)
            valid_bands = [band for band in product.bands if band.name in band_names]
            if not valid_bands:
                raise ValueError("One or more bands are not valid for the specified product.")

            # Set up dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            formatted_start_date = start_date.strftime("%m-%d-%Y")  # MM-DD-YYYY
            formatted_end_date = end_date.strftime("%m-%d-%Y")      # MM-DD-YYYY

            task_name = f"{product_id} {end_date.strftime('%Y-%m-%d %H:%M:%S')}"

            task_params = {
                "task_type": "point",
                "task_name": task_name,
                "params": {
                    "coordinates": [{"latitude": latitude, "longitude": longitude}],
                    "dates": [{"startDate": formatted_start_date, "endDate": formatted_end_date}],
                    "layers": [{"product": product_id, "layer": band.name} for band in valid_bands],
                    "output": {
                        "format": {"type": "geotiff"},
                        "projection": "geographic"
                    }
                }
            }

            response = requests.post(
                f"{self.base_url}/task",
                headers={"Authorization": f"Bearer {token}"},
                json=task_params
            )

            if response.status_code == 202:
                task_response = response.json()
                task_id = task_response.get('task_id', None)
                return {"message": "Task submitted successfully", "task_id": task_id}
            else:
                return {"error": "Failed to submit task", "status_code": response.status_code, "response": response.json()}
        except ValueError as e:
            return {"error": str(e)}
    
    def submit_area_task(self, geo_json: dict, start_date: str, end_date: str, layers: list, projection: str = "geographic", format_type: str = "geotiff"):
        """
        Submits an area-based task to the AppEEARS API.

        :param geo_json: A GeoJSON dictionary defining the area of interest.
        :param start_date: The start date for the data request (format: MM-DD-YYYY).
        :param end_date: The end date for the data request (format: MM-DD-YYYY).
        :param layers: A list of dictionaries specifying layers and their corresponding products.
        :param projection: The projection type for the output, default is 'geographic'.
        :param format_type: The format of the output file, default is 'geotiff'.
        """
        task_params = {
            "task_type": "area",
            "task_name": f"Area_Task {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "params": {
                "geo": geo_json,
                "dates": [{
                    "startDate": start_date,
                    "endDate": end_date,
                    "recurring": False
                }],
                "layers": layers,
                "output": {
                    "format": {"type": format_type},
                    "projection": projection
                }
            }
        }

        response = requests.post(
            f"{self.base_url}/task",
            headers={"Authorization": f"Bearer {self.token}"},
            json=task_params
        )

        if response.status_code == 202:
            task_response = response.json()
            return {"message": "Area task submitted successfully", "task_id": task_response.get('task_id', None)}
        else:
            return {"error": "Failed to submit area task", "status_code": response.status_code, "response": response.text}