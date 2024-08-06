# src.appeears_client.file_management.py

import os
import re
import logging
import requests
import rasterio
from datetime import datetime

from .config import base_url
from ..exceptions import RequestError

class FileManager:
    def __init__(self, token: str):
        self.token = token
        self.base_url = base_url

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