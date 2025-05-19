import os
import logging
from app import app
from routes import register_routes
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Register routes
register_routes(app)

# Add current year to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
