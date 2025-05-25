import sqlite3
import functools

def log_queries(func):
    """
    Decorator that logs the SQL query executed by a function.
    It assumes the query is the first argument passed to the
    decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Try to find the query in args or kwargs
        query = None
        if args:
            query = args[0] # Assuming query is the first positional arg
        elif 'query' in kwargs:
            query = kwargs['query']

        if query:
            print(f"Executing Query: {query}")
        else:
            print("Could not determine query to log.")

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

# Fetch users while logging the query
print("--- Fetching users ---")
users = fetch_all_users(query="SELECT * FROM users")
if users:
    print("Users found:")
    for user in users:
        print(user)
print("--------------------")
