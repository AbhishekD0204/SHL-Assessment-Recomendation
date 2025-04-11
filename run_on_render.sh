#!/bin/bash

# This script is for deploying the SHL RAG Recommendation Engine on Render
# It will be executed by Render after the build process

# Set environment variables
echo "Setting up environment variables..."
export RENDER=true

# Install dependencies
echo "Installing dependencies..."
pip install -r render-requirements.txt

# Set PORT environment variable if not already set (default to 10000)
export PORT=${PORT:-10000}

# Create log directory if it doesn't exist
mkdir -p logs

# Make sure data directory exists for storing scraped data
mkdir -p data

# Run initial scraping if needed (this is usually handled by the application on first run)
# Uncomment if you want to pre-populate the data
# echo "Pre-populating data..."
# python -c "from scraper import scrape_shl_products, save_scraped_data; save_scraped_data(scrape_shl_products())"

# Start the Gunicorn server with improved error handling
echo "Starting Gunicorn on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level debug \
  --error-logfile logs/gunicorn-error.log \
  --access-logfile logs/gunicorn-access.log \
  --forwarded-allow-ips='*' \
  --preload \
  main:app