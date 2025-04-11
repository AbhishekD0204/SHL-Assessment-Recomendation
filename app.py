import os
import json
import logging
import csv
from flask import Flask, render_template, request, jsonify
from rag_engine import RAGEngine
from scraper import scrape_shl_products
from data_processor import process_data

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "shl_recommendation_secret")

# Production settings
if os.environ.get("RENDER", False):
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['DEBUG'] = False

# Initialize RAG engine
rag_engine = None

# Check if data exists, otherwise scrape and process it
def initialize_data():
    data_dir = "data"
    json_file = os.path.join(data_dir, "shl_products.json")
    csv_file = os.path.join(data_dir, "shl_products.csv")
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # If data doesn't exist, scrape and process it
    if not os.path.exists(json_file) or not os.path.exists(csv_file):
        logger.info("Data files not found. Scraping SHL products...")
        shl_products = scrape_shl_products()
        
        # Process the scraped data
        logger.info("Processing scraped data...")
        process_data(shl_products)
    
    return

# Initialize the RAG engine
def initialize_rag():
    global rag_engine
    logger.info("Initializing RAG engine with TF-IDF...")
    rag_engine = RAGEngine(data_path="data/shl_products.json")
    rag_engine.load_data()
    rag_engine.build_index()
    logger.info("RAG engine initialized successfully.")

# Initialize data and RAG engine
with app.app_context():
    try:
        initialize_data()
        initialize_rag()
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    try:
        # Get the query from the request
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query.strip():
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Ensure RAG engine is initialized
        if rag_engine is None:
            initialize_rag()
        
        # Get recommendations
        recommendations = rag_engine.get_recommendations(user_query, top_k=4)
        
        return jsonify({
            'success': True,
            'query': user_query,
            'recommendations': recommendations
        })
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# App is initialized with app_context above

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
