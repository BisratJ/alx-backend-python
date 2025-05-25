import asyncio
import aiosqlite
import os
import time

# Define the database file name
DB_FILE = 'async_database.db'

async def setup_async_database():
    """Sets up a dummy SQLite database asynchronously."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
            )
        ''')
        users_data = [
            ('Alice', 30),
            ('Bob', 24),
            ('Charlie', 35),
            ('David', 42),
            ('Eve', 22),
            ('Frank', 50),
            ('Grace', 45)
        ]
        await db.executemany(
            'INSERT INTO users (name, age) VALUES (?, ?)',
            users_data
            )
        await db.commit()
        print("Async database setup complete.")

async def async_fetch_users():
    """Fetches all users from the database asynchronously."""
    print("Fetching all users...")
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print(f"Fetched {len(results)} users.")
            return results

async def async_fetch_older_users():
    """Fetches users older than 40 asynchronously."""
    print("Fetching users older than 40...")
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT * FROM users WHERE age > ?", (40,)
            ) as cursor:
            results = await cursor.fetchall()
            print(f"Fetched {len(results)} users older than 40.")
            return results

async def fetch_concurrently():
    """Runs both fetch queries concurrently and prints results."""
    print("Starting concurrent fetches...")
    start_time = time.time()

    # Use asyncio.gather to run both functions concurrently
    all_users_task = async_fetch_users()
    older_users_task = async_fetch_older_users()

    results = await asyncio.gather(all_users_task, older_users_task)

    end_time = time.time()
    print(f"\nConcurrent fetches finished in {end_time - start_time:.4f} seconds.")

    all_users, older_users = results

    print("\n--- All Users ---")
    for user in all_users:
        print(user)

    print("\n--- Users Older Than 40 ---")
    for user in older_users:
        print(user)

# Main execution block
if __name__ == "__main__":
    # Set up the database first (using asyncio.run for setup)
    asyncio.run(setup_async_database())

    # Run the concurrent fetch function
    print("\nRunning concurrent fetch...")
    asyncio.run(fetch_concurrently())
    print("\nProgram finished.")
