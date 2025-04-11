# SHL Assessment Recommendation Engine

An AI-powered web application that provides SHL assessment recommendations based on user queries, using Retrieval-Augmented Generation (RAG) techniques.

## Project Architecture

The application follows a client-server architecture with the following components:

1. **Web Scraper**: Scrapes SHL's product catalog to collect assessment information.
2. **Data Processor**: Processes and structures the scraped data, including text chunking for better semantic search.
3. **RAG Engine**: Implements semantic search using TF-IDF vectorization to find relevant assessments.
4. **Web Interface**: Provides a ChatGPT-like interface for users to query the system.

## Directory Structure

- `app.py`: Main Flask application setup
- `main.py`: Application entry point
- `rag_engine.py`: Implementation of the recommendation engine using TF-IDF
- `scraper.py`: Functions to scrape SHL product data
- `data_processor.py`: Text processing and chunking functions
- `data/`: Directory containing product data in JSON and CSV formats
- `static/`: Static assets including JavaScript and CSS
- `templates/`: HTML templates for the web interface

## Deployment

This application is fully configured for deployment on Render. For a comprehensive deployment guide with multiple options and troubleshooting tips, please refer to [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

### Quick Deployment Guide

1. **Set Up a GitHub Repository**
   - Create a new GitHub repository
   - Push this project to the repository

2. **Deploy Using Render Blueprint (Recommended)**
   - Sign up for a Render account at https://render.com/
   - From your Render dashboard, click "New +" and select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the render.yaml file and set up your service

3. **Alternative: Manual Configuration**
   - From your Render dashboard, click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Configure with:
     - Build Command: `pip install -r render-requirements.txt`
     - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 --log-level debug main:app`

### Optimized Deployment Files

This repository includes several files to make Render deployment seamless:

1. **render.yaml**: Blueprint configuration for one-click deployment
2. **render-requirements.txt**: All required Python dependencies
3. **run_on_render.sh**: A comprehensive bash script for running on Render
4. **Procfile**: Alternative method for specifying the start command

### Environment Variables

- `SESSION_SECRET`: Secret key for Flask sessions (optional, has default)
- `PORT`: Automatically set by Render
- `RENDER`: Set to 'true' to indicate running on Render

For detailed deployment instructions, troubleshooting, and advanced configuration options, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

### Manual Deployment with Docker

If you prefer to deploy manually using Docker, you can use the following steps:

1. **Create a Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY . .
   
   RUN pip install --no-cache-dir -r render-requirements.txt
   
   EXPOSE 5000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]
   ```

2. **Build the Docker image**
   ```bash
   docker build -t shl-rag-engine .
   ```

3. **Run the Docker container**
   ```bash
   docker run -p 5000:5000 shl-rag-engine
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

