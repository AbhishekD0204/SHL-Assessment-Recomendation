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
        top_k = data.get('top_k', 4)  # Allow customizing number of results
        
        if not user_query.strip():
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Ensure RAG engine is initialized
        if rag_engine is None:
            initialize_rag()
        
        # Get recommendations
        recommendations = rag_engine.get_recommendations(user_query, top_k=top_k)
        
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

@app.route('/api/search', methods=['GET'])
def search():
    try:
        # Get query from URL parameters
        user_query = request.args.get('q', '')
        top_k = request.args.get('limit', 4)
        
        # Convert top_k to integer with error handling
        try:
            top_k = int(top_k)
        except (ValueError, TypeError):
            top_k = 4
            
        if not user_query.strip():
            return jsonify({
                'success': False,
                'error': 'Query parameter q cannot be empty'
            }), 400
            
        # Ensure RAG engine is initialized
        if rag_engine is None:
            initialize_rag()
            
        # Get recommendations
        recommendations = rag_engine.get_recommendations(user_query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'query': user_query,
            'count': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/text', methods=['GET', 'POST'])
def text_query():
    """
    Simple endpoint that accepts plain text queries and returns JSON.
    Works with both GET (query parameter) and POST (form or plain text body).
    """
    try:
        # Handle different request types
        if request.method == 'GET':
            user_query = request.args.get('query', '')
        elif request.content_type and 'application/json' in request.content_type:
            data = request.get_json(silent=True) or {}
            user_query = data.get('query', '')
        elif request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
            user_query = request.form.get('query', '')
        else:
            # For plain text POST body
            user_query = request.get_data(as_text=True)
            
        # Get limit parameter
        try:
            limit = request.args.get('limit', 4)
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 4
            
        if not user_query.strip():
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
            
        # Ensure RAG engine is initialized
        if rag_engine is None:
            initialize_rag()
            
        # Get recommendations
        recommendations = rag_engine.get_recommendations(user_query, top_k=limit)
        
        return jsonify({
            'success': True,
            'query': user_query,
            'count': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error processing text query: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API Documentation endpoint
@app.route('/api', methods=['GET'])
def api_documentation():
    """Provide simple API documentation."""
    api_docs = {
        'version': '1.0',
        'endpoints': [
            {
                'name': 'GET /api/search',
                'description': 'Search for SHL assessment recommendations using GET method',
                'parameters': [
                    {'name': 'q', 'type': 'string', 'required': True, 'description': 'Search query text'},
                    {'name': 'limit', 'type': 'integer', 'required': False, 'default': 4, 'description': 'Maximum number of results to return'}
                ],
                'example': '/api/search?q=leadership%20assessment&limit=5'
            },
            {
                'name': 'POST /api/query',
                'description': 'Search for SHL assessment recommendations using POST method with JSON body',
                'body_parameters': [
                    {'name': 'query', 'type': 'string', 'required': True, 'description': 'Search query text'},
                    {'name': 'top_k', 'type': 'integer', 'required': False, 'default': 4, 'description': 'Maximum number of results to return'}
                ],
                'example_body': {'query': 'leadership assessment', 'top_k': 5}
            },
            {
                'name': 'GET/POST /api/text',
                'description': 'Flexible endpoint that accepts plain text queries in multiple formats',
                'methods': ['GET', 'POST'],
                'notes': 'This endpoint is versatile and accepts queries in several formats: GET parameter, POST form, JSON body, or raw text body',
                'parameters': [
                    {'name': 'query', 'type': 'string', 'required': True, 'description': 'Search query text (GET parameter)'},
                    {'name': 'limit', 'type': 'integer', 'required': False, 'default': 4, 'description': 'Maximum number of results to return'}
                ],
                'post_formats': [
                    {'content_type': 'application/json', 'example': '{"query": "leadership assessment"}'},
                    {'content_type': 'application/x-www-form-urlencoded', 'example': 'query=leadership+assessment'},
                    {'content_type': 'text/plain', 'example': 'leadership assessment'}
                ],
                'examples': [
                    'GET /api/text?query=leadership%20assessment&limit=3',
                    'POST /api/text with raw text body "leadership assessment"'
                ]
            }
        ]
    }
    return jsonify(api_docs)

# App is initialized with app_context above

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
