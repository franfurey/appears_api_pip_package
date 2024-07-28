# src.client.py
import re
import os
import time
import pprint
import logging
import requests
import rasterio
from datetime import datetime, timedelta

from .exceptions import LoginError, RequestError
from .models import Product, Band, get_product_by_id

class AppEEARSClient:
    """Client to interact with the AppEEARS API."""
    def __init__(self, username: str, password: str):
        self.base_url = "https://appeears.earthdatacloud.nasa.gov/api"
        self.token = self.login(username=username, password=password)

    def login(self, username: str, password: str) -> str:
        """Logs in to the API and returns a token."""
        response = requests.post(f"{self.base_url}/login", auth=(username, password))
        if response.status_code == 200:
            return response.json()['token']
        else:
            raise LoginError("Failed to log in to AppEEARS API")

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

    def logout(self):
        """Logs out of the API."""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/logout", headers=headers)
        if response.status_code != 204:
            raise RequestError("Failed to log out")

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

    def fetch_and_store_point_data(
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

    def execute_and_retrieve_task(self, latitude: float, longitude: float, product_id: str, band_names: list, days_back: int = 30):
        """ Submits a task, checks its status until completion, and retrieves the files if the task is completed successfully. """
        try:
            # Submit the task and get task_id
            response = self.fetch_and_store_point_data(
                latitude=latitude,
                longitude=longitude,
                product_id=product_id,
                band_names=band_names,
                token=self.token,
                days_back=days_back
            )

            if 'task_id' not in response:
                print("Failed to submit task:", response.get('error', 'Unknown Error'))
                return

            task_id = response['task_id']
            print(f"Task submitted successfully, task ID: {task_id}")

            # Check task status until done or failed
            while True:
                if self.check_task_status(task_id=task_id):
                    print("Task completed successfully.")
                    break
                else:
                    print("Task not completed yet. Waiting...")
                    time.sleep(10)  # Wait before checking again to avoid too many requests

            # List files of the completed task
            files = self.list_task_files(task_id=task_id)
            if files:
                return files
            else:
                print("No files available or task failed.")
                return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
        
    def download_and_process_file(self, task_id: str, file_id: str, file_name: str, token: str, destination_dir: str):
        """
        Download and process a GeoTIFF file using AppEEARS API.
        
        :param task_id: The task ID from which to download the file.
        :param file_id: The specific file ID to download.
        :param file_name: The name of the file to check and download.
        :param token: The authorization token used for the API.
        :param destination_dir: Directory to save downloaded files.
        """
        # Verify if the file is a GeoTIFF file
        if not file_name.endswith('.tif'):
            print(f"Skipping non-TIF file: {file_name}")
            return {"message": "Skipped non-TIF file"}

        # Constructing the download URL
        url = f"https://appeears.earthdatacloud.nasa.gov/api/bundle/{task_id}/{file_id}"
        headers = {"Authorization": f"Bearer {token}"}
        file_path = os.path.join(destination_dir, file_name)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Download the file
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            print(f"File {file_name} successfully downloaded to {file_path}")
            return {"message": f"File {file_name} successfully downloaded to {file_path}"}
        else:
            error_msg = response.text
            print(f"Error downloading the file: {error_msg}")
            return {"error": f"Error downloading file: {error_msg}"}
        
    def extract_info_and_coordinates_from_tif(self, filename: str, file_path: str):
        """
        Extracts the band, date, and coordinates of each pixel from a GeoTIFF file.
        
        :param filename: The name of the file being processed.
        :param file_path: The full path to the GeoTIFF file.
        """
        logging.info(f"Extracting band and date information from the file {filename}")

        # Extracts band and date information from the filename
        match = re.search(r'B(\d+)_doy(\d{7})_', filename)
        if not match:
            logging.warning(f"Could not extract information from the file {filename}")
            return None

        band = match
        doy = int(match.group(2)[-3:])  # Extracts the day of the year and converts to integer
        year = int(match.group(2)[:4])  # Extract the year
        date = datetime.strptime(f'{year}{doy}', '%Y%j').date()  # Convert to date

        data_points = []

        # Open the GeoTIFF file to read data and coordinates
        with rasterio.open(file_path) as src:
            # Gets the values of the first band
            band_data = src.read(1)

            for row in range(src.height):
                for col in range(src.width):
                    value = band_data[row, col]
                    # Gets the coordinates of the pixel
                    longitude, latitude = src.xy(row, col)

                    # Stores the band, date, coordinates and value in a list
                    data_points.append({
                        'band': band,
                        'date': date,
                        'latitude': latitude,
                        'longitude': longitude,
                        'value': value
                    })

        logging.info(f"Extracted information and coordinates for the file {filename}")
        return data_points
    
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
            "task_name": f"Area_Task_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}",
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
