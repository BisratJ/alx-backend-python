import sqlite3
import os

# Define the database file name
DB_FILE = 'database.db'

def setup_database():
    """Sets up a dummy SQLite database for demonstration."""
    # Remove old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
            )
        ''')
        # Insert some dummy data
        users_data = [
            ('Alice', 30),
            ('Bob', 24),
            ('Charlie', 35),
            ('David', 42)
        ]
        cursor.executemany('INSERT INTO users (name, age) VALUES (?, ?)', users_data)
        conn.commit()
        print("Database setup complete.")
    except sqlite3.Error as e:
        print(f"Database error during setup: {e}")
    finally:
        if conn:
            conn.close()

class DatabaseConnection:
    """
    A custom context manager for handling SQLite database connections.

    Attributes:
        db_name (str): The name of the database file.
        connection (sqlite3.Connection): The database connection object.
    """

    def __init__(self, db_name):
        """
        Initializes the DatabaseConnection context manager.

        Args:
            db_name (str): The name of the database file to connect to.
        """
        self.db_name = db_name
        self.connection = None
        print(f"Initializing connection to {self.db_name}...")

    def __enter__(self):
        """
        Establishes the database connection when entering the 'with' block.

        Returns:
            sqlite3.Connection: The active database connection object.

        Raises:
            sqlite3.Error: If connection fails.
        """
        try:
            print("Opening database connection...")
            self.connection = sqlite3.connect(self.db_name)
            return self.connection
        except sqlite3.Error as e:
            print(f"Failed to connect to database: {e}")
            raise # Re-raise the exception so it's not swallowed

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection when exiting the 'with' block.

        Args:
            exc_type: The type of exception raised (if any).
            exc_val: The exception value (if any).
            exc_tb: The traceback (if any).

        Returns:
            bool: False, so any exceptions are re-raised after cleanup.
        """
        if self.connection:
            print("Closing database connection...")
            self.connection.close()
        # If an exception occurred, exc_type, exc_val, and exc_tb will be set.
        # If we return False (or None), any exception will be re-raised.
        # If we return True, the exception will be suppressed.
        # We generally want to know about errors, so we'll let them propagate.
        if exc_type:
            print(f"An exception occurred: {exc_val}")
        return False # Do not suppress exceptions

# Main execution block
if __name__ == "__main__":
    # Set up the database first
    setup_database()

    print("\nAttempting to query the database using the context manager:")
    # Use the context manager to perform a query
    try:
        with DatabaseConnection(DB_FILE) as conn:
            print("Connection successful. Executing query...")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            print("\nQuery Results:")
            for row in results:
                print(row)
    except sqlite3.Error as e:
        print(f"An error occurred during database operation: {e}")
    print("\nExited the 'with' block.")
