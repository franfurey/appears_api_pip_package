# AppEEARS API Client

## Description.
A Python client for interacting with NASA Earthdata's AρρEEARS API. This package facilitates authentication, querying and handling of data coming from AρρEEARS, allowing Python users to work more efficiently with this service.

## Features
- Easy authentication with NASA Earthdata Login.
- Functions to obtain and manipulate available product data.
- Integrated API-specific error handling.

## Installation

Install the package using pip:

```bash
pip install appears-api-client
```

## Usage
### Initial configuration
First, import the client and create an instance with your credentials:

```bash
from appears_api.client import AppEEARSClient

client = AppEEARSClient(username='your_username', password='your_password')
```

### Obtain product data

```bash
product_info = client.get_product(product_id='MOD11A1.061')
print(product_info)
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
Your name - @YourTwitter
Email - example@example.com
