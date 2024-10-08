# AppEEARS API Client

Python client for interacting with NASA Earthdata's AρρEEARS API. This package facilitates authentication, querying, and handling of data from AppEEARS, allowing Python users to efficiently access and manipulate remote sensing data.

## Features

- **Easy Authentication**: Seamlessly authenticate using NASA Earthdata Login.
- **Data Retrieval**: Functions to query and manipulate available product data.
- **Error Handling**: Integrated API-specific error handling to manage and respond to API issues effectively.

## Installation

Install the package using pip:

```bash
pip install appeears-api-client
```

## Usage
### Initial configuration
Import the client and create an instance with your credentials:

```bash
from appeears_api.client import APIClient

client = APIClient(username='your_username', password='your_password')
```

### Authentication
Log in to authenticate and begin your session:

```bash
client.login()
```

### Obtain product data
Retrieve information about a specific product by its ID:

```bash
product_info = client.get_product_info(product_id='MOD11A1.061')
print(product_info)
```

### Retrieve All Products and Layers
Get details on all available products and their respective layers:

```bash
all_products = client.product_manager.get_all_products_and_layers()
print(all_products)
```

### Fetch and Store Point Data
Submit a task for specific coordinates, bands, and time period, and retrieve the processed data:

```bash
response = client.submit_and_retrieve_point_task(
    latitude=34.05, 
    longitude=-118.25, 
    product_id='MOD11A1.061', 
    band_names=['LST_Day_1km', 'LST_Night_1km'], 
    start_date='2023-01-01', 
    end_date='2023-01-31'
)
print(response)
```

## Sending Area-Based Tasks

The API client also supports submitting tasks based on a specific geographical area. This is particularly useful for processing large datasets that cover geographical regions. Below is an example of how to submit an area-based task using the API client:

### Example: Retrieve Temperature Data for a Defined Area

This example demonstrates how to submit a task to retrieve daytime and nighttime land surface temperature data for a specific area defined by GeoJSON coordinates.

```bash
import os
from datetime import datetime
from src.appeears import APIClient

# Load environment variables (ensure your .env file contains the necessary API credentials)
from dotenv import load_dotenv
load_dotenv()

# Create an instance of the API client with your credentials
client = APIClient(username=os.getenv('APPEEARS_USER'), password=os.getenv('APPEEARS_PASS'))

# Define the geographical area of interest in GeoJSON format
geo_json = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-78.54051709643014, 18.699926638788938],
                        [-78.54051709643014, 17.571631940899735],
                        [-75.89563723926521, 17.571631940899735],
                        [-75.89563723926521, 18.699926638788938],
                        [-78.54051709643014, 18.699926638788938]
                    ]
                ]
            }
        }
    ]
}

# Define the time period for the data
start_date = datetime.strptime("01-01-2023", "%m-%d-%Y")
end_date = datetime.strptime("01-31-2023", "%m-%d-%Y")

# Define the product and layers to retrieve
layers = [
    {"product": "MOD11A1.061", "layer": "LST_Day_1km"},
    {"product": "MOD11A1.061", "layer": "LST_Night_1km"}
]

# Submit the area-based task and get the response
response = client.submit_and_retrieve_area_task(
    geo_json=geo_json,
    product_id="MOD11A1.061",
    band_names=["LST_Day_1km", "LST_Night_1km"],
    start_date=start_date,
    end_date=end_date
)

# Handle the response
if 'task_id' in response:
    print("Area task submitted successfully. Task ID:", response['task_id'])
else:
    print("Error submitting area task:", response)
```

### Logout
Don't forget to log out when you are finished:

```bash
client.logout()
```

## Contributions
Contributions are welcome! If you wish to contribute, please:

- Fork the repository.
- Create a new branch for your modifications.
- Make your changes and write tests when possible.
- Send a pull request with a clear description of the changes.

## License
Distributed under the MIT license. See LICENSE for more information.

## Contact
Francisco Furey

[![GMAIL](https://img.shields.io/badge/Francisco-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:franciscofurey@gmail.com)
[![LinkedIn](https://img.shields.io/badge/Francisco-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/francisco-furey-44519113b/)

Follow the project and contribute on GitHub.