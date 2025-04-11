import os
from app import app

if __name__ == "__main__":
    # Get port from environment variable for Render deployment
    port = int(os.environ.get("PORT", 5000))
    # When running directly with Python, use Flask's development server
    app.run(host="0.0.0.0", port=port, debug=True)
