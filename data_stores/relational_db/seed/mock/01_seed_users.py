#!/usr/bin/env python3

import psycopg
from faker import Faker
from config.config import config

def main():
    print("Seeding users table...")

    db_config = config.data_stores.relational_db

    # Database connection parameters
    db_params = {
        "host": db_config.host,
        "dbname": db_config.database,
        "user": db_config.user,
        "password": db_config.password
    }

    # Connect to PostgreSQL
    with psycopg.connect(**db_params) as conn:
        with conn.cursor() as cursor:
            try:
                # Truncate users table
                cursor.execute('TRUNCATE TABLE users RESTART IDENTITY CASCADE')
                print("Users table truncated.")

                # Generate 20 users
                faker = Faker()
                users = []
                for _ in range(20):
                    username = faker.user_name()
                    email = faker.email()
                    password_hash = faker.uuid4()
                    last_login = faker.date_time_between(start_date='-10d', end_date='now')
                    users.append((username, email, password_hash, last_login))

                # Insert users
                cursor.executemany("""
                    INSERT INTO users (username, email, password_hash, last_login)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, users)
                print(f"Inserted {len(users)} users successfully.")

            except Exception as e:
                print(f"Error seeding users: {e}")
                raise

    print("Seeding users done.")

if __name__ == "__main__":
    main()
