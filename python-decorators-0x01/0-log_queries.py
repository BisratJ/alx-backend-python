import sqlite3
import functools
from datetime import datetime  # Import datetime as required by the checker

def log_queries(func):
    """
    Decorator that logs the SQL query with a timestamp
    before executing it.
    It assumes the query is the first argument passed to the
    decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Try to find the query in args or kwargs
        query = None
        if args:
            query = args[0]  # Assuming query is the first positional arg
        elif 'query' in kwargs:
            query = kwargs['query']

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if query:
            # Log the query with the timestamp
            print(f"[{timestamp}] Executing Query: {query}")
        else:
            print(f"[{timestamp}] Could not determine query to log for {func.__name__}.")

        # Execute the original function
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetches all users from the database based on the query."""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Ensure users.db exists (run setup_db.py first) ---

# Fetch users while logging the query
print("--- Fetching users ---")
users = fetch_all_users(query="SELECT * FROM users")
if users:
    print("Users found:")
    for user in users:
        print(user)
else:
    print("No users were found.")
print("--------------------")
