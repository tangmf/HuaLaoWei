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
                # cursor.execute('TRUNCATE TABLE users RESTART IDENTITY CASCADE')
                # print("Users table truncated.")

                # Check if users table has data
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"Users table already has {count} records. Skipping seeding.")
                    return

                # Generate test user
                # password is testpassword
                test_user = ("testuser", "testuser@example.com", "9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05", faker.date_time_between(start_date='-1d', end_date='now'))
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, last_login)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, test_user)
                print("Test user inserted.")

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
