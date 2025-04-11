import os
import json
import csv
import logging
import re
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Cleans text by removing extra whitespace, special characters, etc.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,?!-]', '', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits long text into chunks with some overlap to maintain context.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        # Get chunk of text
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:]
        else:
            # Try to find a natural break point (period, paragraph, etc.)
            natural_break = text.rfind('.', start + chunk_size - 200, end)
            if natural_break != -1:
                end = natural_break + 1
            chunk = text[start:end]
        
        chunks.append(chunk)
        # Next chunk starts with some overlap
        start = max(0, end - overlap)
    
    return chunks

def process_data(products: List[Dict[str, Any]]) -> None:
    """
    Processes scraped SHL product data and stores it in structured formats.
    """
    logger.info(f"Processing {len(products)} SHL products...")
    
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Process each product
    processed_products = []
    for product in products:
        # Clean the product data
        clean_product = {
            'title': clean_text(product.get('title', '')),
            'url': product.get('url', ''),
            'description': clean_text(product.get('description', '')),
            'image_url': product.get('image_url', '')
        }
        
        # Chunk long descriptions
        if len(clean_product['description']) > 1000:
            chunks = chunk_text(clean_product['description'])
            clean_product['chunks'] = chunks
        else:
            clean_product['chunks'] = [clean_product['description']]
        
        processed_products.append(clean_product)
    
    # Save processed data as JSON
    json_file = os.path.join(data_dir, "shl_products.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(processed_products, f, ensure_ascii=False, indent=4)
    
    # Save processed data as CSV (main info only, not chunks)
    csv_file = os.path.join(data_dir, "shl_products.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url', 'description', 'image_url'])
        writer.writeheader()
        for product in processed_products:
            # Create a copy without the chunks for CSV
            csv_product = {k: v for k, v in product.items() if k != 'chunks'}
            writer.writerow(csv_product)
    
    logger.info(f"Processed data saved to {json_file} and {csv_file}")

if __name__ == "__main__":
    # Test with sample data
    sample_products = [
        {
            'title': 'Sample Product 1',
            'url': 'https://example.com/product1',
            'description': 'This is a sample product description. ' * 10,
            'image_url': 'https://example.com/image1.jpg'
        },
        {
            'title': 'Sample Product 2',
            'url': 'https://example.com/product2',
            'description': 'Another sample product description. ' * 5,
            'image_url': 'https://example.com/image2.jpg'
        }
    ]
    process_data(sample_products)
