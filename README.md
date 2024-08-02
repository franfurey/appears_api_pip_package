# AppEEARS API Client

Python client for interacting with NASA Earthdata's AρρEEARS API. This package facilitates authentication, querying, and handling of data from AppEEARS, allowing Python users to efficiently access and manipulate remote sensing data.

## Features

- **Easy Authentication**: Seamlessly authenticate using NASA Earthdata Login.
- **Data Retrieval**: Functions to query and manipulate available product data.
- **Error Handling**: Integrated API-specific error handling to manage and respond to API issues effectively.

## Installation

Install the package using pip:

```bash
pip install appears-api-client
```

## Usage
### Initial configuration
Import the client and create an instance with your credentials:

```bash
from appears_api.client import AppEEARSClient

client = AppEEARSClient(username='your_username', password='your_password')
```

### Obtain product data
Retrieve information about a specific product by its ID:

```bash
product_info = client.get_product(product_id='MOD11A1.061')
print(product_info)
```

### Retrieve All Products and Layers
Get details on all available products and their respective layers:

```bash
all_products = client.get_all_products_and_layers()
print(all_products)
```

### Fetch and Store Point Data
Submit a request for point data for specific coordinates and bands:

```bash
response = client.fetch_and_store_point_data(
    latitude=34.05, 
    longitude=-118.25, 
    product_id='MOD11A1.061', 
    band_names=['LST_Day_1km', 'LST_Night_1km'], 
    token=client.token, 
    days_back=15
)
print(response)
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