import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from routes.api import api_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "agentic-ads-secret-key-2024")

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(api_bp)

# Simple in-memory user store (use a database in production)
users_db = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/api/auth/google", methods=["POST"])
def google_auth():
    """Receive Google OAuth user data and store it."""
    data = request.get_json()
    if not data or not data.get("user"):
        return jsonify({"error": "No user data provided"}), 400

    user = data["user"]
    email = user.get("email", "")

    # Store/update user in our simple DB
    users_db[email] = {
        "name": user.get("name", ""),
        "email": email,
        "picture": user.get("picture", ""),
        "provider": user.get("provider", "google"),
        "sub": user.get("sub", ""),
        "last_login": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    }

    print(f"[Auth] User signed in: {user.get('name')} <{email}>")

    return jsonify({
        "status": "ok",
        "user": users_db[email],
        "message": f"Welcome, {user.get('name')}!"
    }), 200


@app.route("/api/auth/users", methods=["GET"])
def list_users():
    """List all signed-in users (admin endpoint)."""
    return jsonify({"users": list(users_db.values()), "count": len(users_db)}), 200


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    print(f"\n[AdGenius AI] Starting on http://localhost:{port}")
    print(f"[Config] Demo mode: {os.getenv('DEMO_MODE', 'true')}")
    print(f"[Config] OpenAI key: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET (using demo mode)'}\n")
    app.run(debug=debug, port=port)
