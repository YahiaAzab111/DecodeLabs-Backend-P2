# DecodeLabs Backend — Project 2: Database Integration (CRUD)

**Domain:** Backend Development  
**Stack:** Python + Flask + SQLite  
**Internship Batch:** 2026

---

## What This Project Does

This project connects the REST API from Project 1 to a real database. Instead of storing data in memory (which disappears when the server restarts), all employee records are now persisted to a SQLite database file (`employees.db`).

The project covers the full CRUD lifecycle — Create, Read, Update, Delete — with proper database-level constraints to protect data integrity.

---

## Project Structure

```
DecodeLabs-Backend-P2/
├── app.py              # Server entry point, DB init, error handlers
├── database.py         # Connection management and schema creation
├── employee_routes.py  # All /employees CRUD route logic
├── requirements.txt
└── .gitignore
```

---

## Database Schema

```sql
CREATE TABLE employees (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,      -- prevents duplicate entries
    department  TEXT    NOT NULL,
    age         INTEGER NOT NULL CHECK(age >= 18),  -- enforced at DB level
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```

---

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/employees` | Create a new employee | 201 / 400 / 409 |
| GET | `/employees` | Get all employees | 200 |
| GET | `/employees?active=true` | Get active employees only | 200 |
| GET | `/employees/<id>` | Get one employee | 200 / 404 |
| PUT | `/employees/<id>` | Update employee fields | 200 / 404 / 409 |
| DELETE | `/employees/<id>` | Delete an employee | 204 / 404 |

---

## How to Run

```bash
pip install -r requirements.txt
python app.py
```

The database file (`employees.db`) is created automatically on first run.

---

## Example Requests

```bash
# Create an employee
curl -X POST http://127.0.0.1:5000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Ahmed Salah", "email": "ahmed@company.com", "department": "Engineering", "age": 26}'

# Try the same email again — should return 409 Conflict
curl -X POST http://127.0.0.1:5000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Someone Else", "email": "ahmed@company.com", "department": "HR", "age": 30}'

# Get all employees
curl http://127.0.0.1:5000/employees

# Update an employee
curl -X PUT http://127.0.0.1:5000/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"department": "Backend Team", "age": 27}'

# Delete an employee
curl -X DELETE http://127.0.0.1:5000/employees/1
```

---

## Key Concepts Demonstrated

- **Data persistence** — SQLite stores data permanently; server restarts don't wipe records
- **Duplicate prevention** — UNIQUE constraint on email + 409 Conflict response
- **Schema-level validation** — CHECK constraint ensures age >= 18 at the database level
- **Full CRUD** — all four operations implemented with correct HTTP verbs and status codes
- **Modular architecture** — database logic separated from route logic
- **Dynamic updates** — PUT only modifies fields that are actually sent in the request body
