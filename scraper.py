import os
import json
import csv
import time
import logging
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SHL website URL
SHL_BASE_URL = "https://www.shl.com/solutions/products/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_website_text_content(url):
    """
    Gets clean text content from a URL using trafilatura.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return None

def scrape_product_details(product_url):
    """
    Scrapes detailed information about a specific SHL product.
    """
    try:
        # Get the product page
        response = requests.get(product_url, headers=HEADERS)
        if response.status_code != 200:
            logger.error(f"Failed to get product page: {product_url}, status code: {response.status_code}")
            return None

        # Parse the product details
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get product title
        title_elem = soup.find('h1')
        title = title_elem.text.strip() if title_elem else "Unknown Product"
        
        # Extract full description using trafilatura for better text extraction
        description = get_website_text_content(product_url)
        if not description:
            # Fallback to BeautifulSoup if trafilatura fails
            description_elems = soup.find_all(['p', 'li'])
            description = " ".join([elem.text.strip() for elem in description_elems if elem.text.strip()])
        
        # Get product image if available
        image_elem = soup.find('img', class_='attachment-post-thumbnail')
        image_url = image_elem.get('src') if image_elem else None
        
        return {
            'title': title,
            'url': product_url,
            'description': description,
            'image_url': image_url
        }
    
    except Exception as e:
        logger.error(f"Error scraping product details for {product_url}: {str(e)}")
        return None

def scrape_shl_products():
    """
    Scrapes SHL product catalog from the main products page.
    Returns a list of product dictionaries.
    """
    logger.info(f"Scraping SHL products from {SHL_BASE_URL}...")
    products = []
    
    try:
        # Get the main products page
        response = requests.get(SHL_BASE_URL, headers=HEADERS)
        if response.status_code != 200:
            logger.error(f"Failed to get SHL products page, status code: {response.status_code}")
            return products
        
        # Parse the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find product links
        product_links = []
        
        # Look for product cards or links
        product_elems = soup.find_all('a', href=True)
        for elem in product_elems:
            href = elem.get('href', '')
            # Filter for product links - typically they'll be under /solutions/products/ or similar path
            if 'product' in href.lower() and not href.endswith('#') and not href == SHL_BASE_URL:
                # Make sure we have absolute URLs
                product_url = urljoin(SHL_BASE_URL, href)
                if product_url not in [p for p in product_links]:
                    product_links.append(product_url)
        
        logger.info(f"Found {len(product_links)} product links to scrape")
        
        # Scrape detailed information for each product
        for i, product_url in enumerate(product_links):
            logger.info(f"Scraping product {i+1}/{len(product_links)}: {product_url}")
            product_info = scrape_product_details(product_url)
            if product_info:
                products.append(product_info)
            # Be nice to the server
            time.sleep(1)
        
        # Save the scraped data
        save_scraped_data(products)
        
        logger.info(f"Successfully scraped {len(products)} SHL products")
        return products
    
    except Exception as e:
        logger.error(f"Error scraping SHL products: {str(e)}")
        return products

def save_scraped_data(products):
    """
    Saves the scraped product data to JSON and CSV files.
    """
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save JSON file
    json_file = os.path.join(data_dir, "shl_products.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    # Save CSV file
    csv_file = os.path.join(data_dir, "shl_products.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'description', 'image_url'])
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    logger.info(f"Saved {len(products)} products to {json_file} and {csv_file}")

# Main execution
if __name__ == "__main__":
    products = scrape_shl_products()
    logger.info(f"Scraped {len(products)} SHL products")
