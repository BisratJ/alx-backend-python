import mysql.connector
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """Generator that yields batches of users"""
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    
    offset = 0
    while True:
        cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
        batch = cursor.fetchall()
        if not batch:
            cursor.close()
            connection.close()
            break
        yield batch
        offset += batch_size

def batch_processing(batch_size):
    """Process batches to filter users over 25"""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user  # Changed from print to yield
