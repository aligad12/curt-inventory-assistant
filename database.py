import sqlite3
from contextlib import contextmanager

DB_NAME = "curt_inventory.db"

@contextmanager
def get_connection():
    """Context manager for database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Create the inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL)
            )
        ''')
        conn.commit()

def seed_db():
    """Seed the database with initial data."""
    sample_parts = [
        ("Brake Pads", 12, "Braking", "Mechanical Workshop"),
        ("ECU", 2, "Electronics", "Electronics Lab"),
        ("Radiator", 3, "Cooling", "Mechanical Workshop"),
        ("Steering Wheel", 4, "Chassis", "Assembly Bay"),
        ("Fuel Injector", 8, "Engine", "Engine Room"),
        ("Wiring Harness", 5, "Electronics", "Electronics Lab"),
        ("Suspension Spring", 10, "Suspension", "Mechanical Workshop"),
        ("Battery", 3, "Electronics", "Electronics Lab"),
        ("Tire Set", 6, "Wheels", "Storage Room"),
        ("Carbon Fiber Sheet", 15, "Chassis", "Assembly Bay"),
    ]
    with get_connection() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
        if existing == 0: # only seed once, so we dont duplicate on every run
            conn.executemany('''
                INSERT INTO parts (name, quantity, category, location)
                VALUES (?, ?, ?, ?)
            ''', sample_parts)
            conn.commit()


# This is the Data Access Layer (DAL) for the inventory database i just have created.
def get_part(name: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM parts WHERE (LOWER)name = LOWER(?)", (name,)).fetchone()
        return dict(row) if row else None


def get_by_category(category: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM parts WHERE LOWER(category) = LOWER(?)", (category,)).fetchall()
        return [dict(row) for row in rows]


def get_all_parts():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM parts").fetchall()
        return [dict(row) for row in rows]

def update_quantity(pname: str, delta: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE parts SET quantity = quantity + ? WHERE LOWER(name) = LOWER(?)", (delta, pname))
        conn.commit()


if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database ready. Current Parts:")
    for p in get_all_parts():
        print(p)
