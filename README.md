# Price Comparison Website for E-commerce Platforms

## Overview
The Price Comparison Website is a Python-based mini-project designed to help users make informed purchasing decisions by comparing product prices across multiple e-commerce platforms. This application fetches real-time product data using web scraping techniques and APIs, processes the information, and displays a consolidated list of prices along with product details.

## Features
- **Product Search**: Users can search for products across various e-commerce platforms.
- **Price Comparison**: View price variations for the same product across different platforms.
- **Filtering Options**: Filter results by price range and availability.
- **Direct Links**: Access product links directly for quick purchases.

## Technologies Used
- Python
- Flask
- BeautifulSoup
- Selenium
- HTML/CSS/JavaScript

## Project Structure
```
price-comparison-website
├── src
│   ├── app.py
│   ├── scraper
│   │   ├── __init__.py
│   │   ├── scraper.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── api_handler.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── data_processing.py
│   ├── templates
│   │   └── index.html
│   └── static
│       ├── css
│       │   └── styles.css
│       └── js
│           └── scripts.js
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd price-comparison-website
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/app.py
   ```
2. Open your web browser and go to `http://127.0.0.1:5000` to access the application.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.