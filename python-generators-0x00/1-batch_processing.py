#!/usr/bin/env python3
"""
Module for batch processing of user data.
"""

# Assuming 'seed.py' and the 'connect_to_prodev' function are provided
# and exist in the same directory or are otherwise accessible.
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Connects to the prodev database and yields users in batches.

    This function is a generator. It fetches a specified number of user records
    at a time from the 'user_data' table and yields them as a list of
    dictionaries. The connection to the database is managed within this function
    and closed when all records have been streamed.

    Args:
        batch_size (int): The number of user records to fetch per batch.

    Yields:
        list: A list of user records, where each record is a dictionary
              representing a user. An empty list is not yielded; iteration
              stops when no more records are available.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        # Assuming the cursor should be a dictionary cursor as per your original code
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:  # No more records to fetch
                break
            yield batch
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size):
    """
    Processes users in batches, filtering and printing users older than 25.

    This function utilizes the stream_users_in_batches generator to get
    data in manageable chunks. It then iterates through each user in a batch
    and prints the user's information if their age is greater than 25.

    Args:
        batch_size (int): The size of each batch to be fetched and processed.
                          This is passed directly to stream_users_in_batches.
    """
    # First loop: Iterates over batches yielded by the generator
    for batch in stream_users_in_batches(batch_size):
        # Second loop (nested): Iterates over users within the current batch
        for user in batch:
            # Ensure 'age' key exists and is convertible to int for safety
            if 'age' in user and isinstance(user['age'], (int, str)):
                try:
                    if int(user['age']) > 25:
                        print(user)
                except ValueError:
                    # Handle cases where age might be a non-integer string
                    # Or simply skip if age is not a valid number
                    # For this problem, we'll assume valid integer-like ages
                    # as per the original problem's apparent data structure.
                    pass # Or log an error: print(f"Warning: Could not parse age for user {user.get('user_id')}")
            # The original code did not have an else, assuming 'age' is always present and valid.
            # If print(user) was what you intended and your data is clean:
            # if int(user['age']) > 25:
            #     print(user)


# Example usage as provided in your 2-main.py
if __name__ == "__main__":
    # This batch_size is an example; your main script uses 50.
    # The function itself should work with any positive integer batch_size.
    batch_processing(batch_size=50)
