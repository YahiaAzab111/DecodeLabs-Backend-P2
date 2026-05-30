"""
DecodeLabs Internship - Backend Development
Project 2: Database Integration (CRUD)
Author: Yahia
Stack: Python + Flask + SQLite
"""

from flask import Flask, jsonify
from database import init_db
from employee_routes import employees_bp

app = Flask(__name__)

# Register the employees blueprint
app.register_blueprint(employees_bp)

# Initialize the database and create tables on startup
with app.app_context():
    init_db()


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "status": "error",
        "message": "HTTP method not allowed on this route."
    }), 405


if __name__ == "__main__":
    print("Server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
