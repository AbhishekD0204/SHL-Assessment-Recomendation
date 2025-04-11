# Comprehensive Render Deployment Guide

This document provides detailed instructions for deploying the SHL Assessment Recommendation Engine on Render.

## Prerequisites

1. A [Render](https://render.com/) account
2. A GitHub or GitLab repository with your project code
3. Basic familiarity with Git and command line operations

## Deployment Options

You have three options for deploying this application on Render:

1. **Blueprint Deployment** (Recommended): Using the provided render.yaml file
2. **Manual Web Service Setup**: Configuring the service through Render's web interface
3. **Custom Script**: Using the provided run_on_render.sh script

## Option 1: Blueprint Deployment (Recommended)

1. **Fork or Clone the Repository**
   ```bash
   git clone <repository-url>
   cd shl-rag-recommendation-engine
   ```

2. **Push to Your GitHub Account**
   ```bash
   git remote set-url origin <your-github-repo-url>
   git push -u origin main
   ```

3. **Deploy on Render via Blueprint**
   - Log in to your Render account
   - Click "New" and select "Blueprint"
   - Connect your GitHub account and select your repository
   - Render will automatically detect the render.yaml file
   - Follow the prompts to complete the deployment

## Option 2: Manual Web Service Setup

1. **Log in to Render**
   - Go to the Render dashboard at https://dashboard.render.com/

2. **Create a New Web Service**
   - Click "New" and select "Web Service"
   - Connect your GitHub or GitLab repository
   - Select the repository that contains your application

3. **Configure the Service**
   - Name: `shl-rag-recommendation-engine` (or your preferred name)
   - Environment: Python 3
   - Region: Choose the region closest to your users
   - Branch: main (or your preferred branch)
   - Build Command: `pip install -r render-requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 5 --log-level debug main:app`

4. **Set Environment Variables** (optional)
   - Click "Advanced" and then "Add Environment Variable"
   - Add `SESSION_SECRET` if you want to customize it
   - Add `RENDER=true` to indicate the application is running on Render

5. **Deploy the Service**
   - Click "Create Web Service"
   - Render will build and deploy your application

## Option 3: Using the Custom Script

1. **Log in to Render**
   - Go to the Render dashboard

2. **Create a New Web Service**
   - Connect your GitHub/GitLab repository

3. **Configure the Service**
   - Name: `shl-rag-recommendation-engine`
   - Environment: Python 3
   - Build Command: `chmod +x run_on_render.sh`
   - Start Command: `./run_on_render.sh`

4. **Deploy the Service**
   - Click "Create Web Service"

## Verifying Deployment

1. **Check Build Logs**
   - Monitor the build process in the Render dashboard
   - Look for any errors in the logs

2. **Test the Application**
   - Once deployment is complete, click on the URL provided by Render
   - Verify that the application loads correctly
   - Test the search functionality to ensure it's working properly

## Troubleshooting

### Common Issues and Solutions

1. **Application Fails to Start**
   - Check the logs in the Render dashboard
   - Verify that all dependencies are correctly listed in render-requirements.txt
   - Ensure the start command is correctly specified

2. **Error 503: Service Unavailable**
   - This usually means your application failed its health check
   - Check if your application is binding to the correct port (should be $PORT)
   - Verify that the health check path (`/`) is accessible

3. **Static Files Not Loading**
   - Ensure that the static files are in the `static` directory
   - Check the URLs in your templates to ensure they're referencing static files correctly

4. **Slow Application Performance**
   - Consider increasing the number of Gunicorn workers
   - Check if your application is performing any heavy operations during startup

## Maintenance and Updates

1. **Updating Your Application**
   - Push changes to your GitHub/GitLab repository
   - Render will automatically rebuild and deploy if auto-deploy is enabled

2. **Monitoring**
   - Use the Render dashboard to monitor your application's health
   - Check the logs regularly for any issues

3. **Custom Domains** (optional)
   - In the Render dashboard, go to your web service
   - Click on "Settings" and then "Custom Domain"
   - Follow the instructions to set up your custom domain

## Scaling Your Application

1. **Upgrading Your Plan**
   - For higher traffic or more resources, consider upgrading from the free plan
   - This will provide more memory, CPU, and bandwidth

2. **Increasing Workers**
   - Modify the `--workers` parameter in your start command
   - A good rule of thumb is (2 × number of CPU cores) + 1