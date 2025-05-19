import os
import logging
from flask import Flask
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-testing")

# Add current year to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Import and register routes
from routes import register_routes
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
