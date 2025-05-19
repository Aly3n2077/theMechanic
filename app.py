import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Import routes at the end to avoid circular imports
if __name__ == "__main__":
    from routes import register_routes
    register_routes(app)
    app.run(host="0.0.0.0", port=5000, debug=True)
