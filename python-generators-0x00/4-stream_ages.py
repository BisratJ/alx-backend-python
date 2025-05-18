#!/usr/bin/env python3

from seed import connect_to_prodev

def stream_user_ages():
    """
    Generator that connects to the database and yields user ages one by one.
    """
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:
        yield int(row['age'])

    cursor.close()
    connection.close()

def calculate_average_age():
    """
    Calculates the average age using the stream_user_ages generator
    without loading all ages into memory.
    """
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No user data available.")

if __name__ == "__main__":
    calculate_average_age()
