#!/usr/bin/env python3

from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Connects to the prodev database and streams users in batches.

    Args:
        batch_size (int): Number of records to fetch per batch.

    Yields:
        list: A list of user records (as dictionaries).
    """
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    connection.close()

def batch_processing(batch_size):
    """
    Processes users in batches and prints users older than 25.

    Args:
        batch_size (int): Size of each batch to process.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if int(user['age']) > 25:
                print(user)

# Example usage
if __name__ == "__main__":
    batch_processing(batch_size=100)
