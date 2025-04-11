import os
import json
import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Retrieval-Augmented Generation engine for SHL product recommendations.
    Uses TF-IDF vectorization and cosine similarity for semantic search to find relevant assessments.
    """
    
    def __init__(self, data_path: str = "data/shl_products.json"):
        """
        Initialize the RAG engine with TF-IDF vectorization.
        
        Args:
            data_path: Path to the JSON file containing SHL product data
        """
        self.data_path = data_path
        self.products = []
        self.chunks = []
        self.product_indices = []  # Maps chunk index back to product index
        self.vectorizer = None
        self.embeddings = None
        
        logger.info("Initializing RAG engine with TF-IDF vectorization")
        try:
            self.vectorizer = TfidfVectorizer(
                min_df=2, max_df=0.95, 
                max_features=200, 
                stop_words='english'
            )
            logger.info("TF-IDF vectorizer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vectorizer: {str(e)}")
            raise
    
    def load_data(self) -> None:
        """
        Load SHL product data from the JSON file.
        Extracts chunks for semantic search.
        """
        try:
            if not os.path.exists(self.data_path):
                logger.error(f"Data file not found: {self.data_path}")
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
            
            logger.info(f"Loaded {len(self.products)} products from {self.data_path}")
            
            # Extract chunks for embedding
            self.chunks = []
            self.product_indices = []
            
            for i, product in enumerate(self.products):
                # Add title as a chunk with high importance
                self.chunks.append(f"Title: {product['title']}")
                self.product_indices.append(i)
                
                # Add each text chunk
                for chunk in product.get('chunks', []):
                    if chunk.strip():
                        self.chunks.append(chunk)
                        self.product_indices.append(i)
            
            logger.info(f"Extracted {len(self.chunks)} chunks from {len(self.products)} products")
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def build_index(self) -> None:
        """
        Build the TF-IDF index for search.
        """
        try:
            if not self.chunks:
                logger.error("No chunks available for indexing. Load data first.")
                return
            
            logger.info(f"Building TF-IDF index for {len(self.chunks)} chunks...")
            self.embeddings = self.vectorizer.fit_transform(self.chunks)
            logger.info(f"Index built successfully with shape {self.embeddings.shape}")
        
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform TF-IDF search to find chunks relevant to the query.
        
        Args:
            query: User query
            top_k: Number of results to return
        
        Returns:
            List of top_k relevant chunks with metadata
        """
        try:
            # Transform the query using the fitted vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarity between query and all chunks
            similarities = cosine_similarity(query_vector, self.embeddings)[0]
            
            # Get indices of top_k highest similarities
            top_indices = np.argsort(-similarities)[:top_k * 2]  # Get more to filter duplicates
            
            # Collect unique product indices and their highest similarity scores
            unique_products = {}
            for idx in top_indices:
                product_idx = self.product_indices[idx]
                similarity = similarities[idx]
                
                if product_idx not in unique_products or similarity > unique_products[product_idx]['similarity']:
                    unique_products[product_idx] = {
                        'product_idx': product_idx,
                        'chunk_idx': idx,
                        'similarity': similarity,
                        'chunk': self.chunks[idx]
                    }
            
            # Get the top_k unique products
            results = list(unique_products.values())
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def get_recommendations(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on the user query.
        
        Args:
            query: User query
            top_k: Number of recommendations to return
        
        Returns:
            List of top_k relevant products with metadata
        """
        try:
            search_results = self.search(query, top_k=top_k)
            
            recommendations = []
            for result in search_results:
                product_idx = result['product_idx']
                product = self.products[product_idx]
                
                recommendation = {
                    'title': product['title'],
                    'url': product['url'],
                    'description': product['description'][:300] + "..." if len(product['description']) > 300 else product['description'],
                    'similarity': float(result['similarity']),
                    'relevant_chunk': result['chunk'][:150] + "..." if len(result['chunk']) > 150 else result['chunk'],
                    'image_url': product.get('image_url', '')
                }
                recommendations.append(recommendation)
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

if __name__ == "__main__":
    # Test the RAG engine
    engine = RAGEngine()
    engine.load_data()
    engine.build_index()
    
    test_query = "leadership assessment for executives"
    recommendations = engine.get_recommendations(test_query)
    
    print(f"Query: {test_query}")
    print(f"Found {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations):
        print(f"\n{i+1}. {rec['title']} (score: {rec['similarity']:.4f})")
        print(f"   URL: {rec['url']}")
        print(f"   Description: {rec['description']}")
