"""
employee_routes.py
Full CRUD operations for the /employees resource.

C - POST   /employees          → Create
R - GET    /employees          → Read all
R - GET    /employees/<id>     → Read one
U - PUT    /employees/<id>     → Update
D - DELETE /employees/<id>     → Delete
"""

from flask import Blueprint, jsonify, request
from database import get_connection
import sqlite3

employees_bp = Blueprint("employees", __name__)


# ─── Helper ────────────────────────────────────────────────────────────────────

def row_to_dict(row):
    """Converts a sqlite3.Row object into a plain Python dict."""
    return dict(row)


# ─── CREATE ────────────────────────────────────────────────────────────────────

@employees_bp.route("/employees", methods=["POST"])
def create_employee():
    """
    POST /employees
    Creates a new employee record.
    Returns 409 if the email already exists (UNIQUE constraint).
    Returns 400 for missing or invalid fields.
    Returns 201 Created on success.
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"status": "error", "message": "JSON body is required."}), 400

    required_fields = ["name", "email", "department", "age"]
    missing = [f for f in required_fields if f not in body]
    if missing:
        return jsonify({
            "status": "error",
            "message": f"Missing required field(s): {', '.join(missing)}."
        }), 400

    if not isinstance(body["age"], int) or body["age"] < 18:
        return jsonify({
            "status": "error",
            "message": "'age' must be an integer of 18 or above."
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (name, email, department, age, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(body["name"]).strip(),
            str(body["email"]).strip().lower(),
            str(body["department"]).strip(),
            body["age"],
            int(body.get("is_active", 1))
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        # Fetch and return the newly created record
        conn = get_connection()
        employee = conn.execute(
            "SELECT * FROM employees WHERE id = ?", (new_id,)
        ).fetchone()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Employee created successfully.",
            "data": row_to_dict(employee)
        }), 201

    except sqlite3.IntegrityError:
        # Triggered when the UNIQUE constraint on email is violated
        return jsonify({
            "status": "error",
            "message": f"An employee with email '{body['email']}' already exists."
        }), 409


# ─── READ ALL ──────────────────────────────────────────────────────────────────

@employees_bp.route("/employees", methods=["GET"])
def get_all_employees():
    """
    GET /employees
    Returns all employees.
    Supports optional query param: ?active=true to filter active employees only.
    """
    active_filter = request.args.get("active")

    conn = get_connection()

    if active_filter == "true":
        rows = conn.execute(
            "SELECT * FROM employees WHERE is_active = 1 ORDER BY id"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM employees ORDER BY id"
        ).fetchall()

    conn.close()

    return jsonify({
        "status": "success",
        "count": len(rows),
        "data": [row_to_dict(r) for r in rows]
    }), 200


# ─── READ ONE ──────────────────────────────────────────────────────────────────

@employees_bp.route("/employees/<int:emp_id>", methods=["GET"])
def get_employee(emp_id):
    """
    GET /employees/<id>
    Returns a single employee by ID.
    Returns 404 if not found.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (emp_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "status": "error",
            "message": f"Employee with id {emp_id} not found."
        }), 404

    return jsonify({
        "status": "success",
        "data": row_to_dict(row)
    }), 200


# ─── UPDATE ────────────────────────────────────────────────────────────────────

@employees_bp.route("/employees/<int:emp_id>", methods=["PUT"])
def update_employee(emp_id):
    """
    PUT /employees/<id>
    Replaces the employee's data with the provided fields.
    Only updates fields that are actually sent in the body.
    Returns 404 if the employee doesn't exist.
    Returns 409 if the new email conflicts with another record.
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"status": "error", "message": "JSON body is required."}), 400

    # Check the employee exists first
    conn = get_connection()
    existing = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (emp_id,)
    ).fetchone()
    conn.close()

    if existing is None:
        return jsonify({
            "status": "error",
            "message": f"Employee with id {emp_id} not found."
        }), 404

    # Build the update dynamically — only update fields that were sent
    allowed_fields = ["name", "email", "department", "age", "is_active"]
    updates = {}

    for field in allowed_fields:
        if field in body:
            updates[field] = body[field]

    if not updates:
        return jsonify({
            "status": "error",
            "message": "No valid fields provided for update."
        }), 400

    if "age" in updates and (not isinstance(updates["age"], int) or updates["age"] < 18):
        return jsonify({
            "status": "error",
            "message": "'age' must be an integer of 18 or above."
        }), 400

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [emp_id]

    try:
        conn = get_connection()
        conn.execute(
            f"UPDATE employees SET {set_clause} WHERE id = ?", values
        )
        conn.commit()

        updated = conn.execute(
            "SELECT * FROM employees WHERE id = ?", (emp_id,)
        ).fetchone()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Employee updated successfully.",
            "data": row_to_dict(updated)
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "message": f"Email '{body.get('email')}' is already used by another employee."
        }), 409


# ─── DELETE ────────────────────────────────────────────────────────────────────

@employees_bp.route("/employees/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    """
    DELETE /employees/<id>
    Permanently removes an employee from the database.
    Returns 404 if the employee doesn't exist.
    Returns 204 No Content on success (no body returned — standard for DELETE).
    """
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM employees WHERE id = ?", (emp_id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({
            "status": "error",
            "message": f"Employee with id {emp_id} not found."
        }), 404

    conn.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()

    return "", 204
