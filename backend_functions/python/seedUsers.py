# Python
import psycopg2
from faker import Faker
import hashlib

fake = Faker()
connection = psycopg2.connect(
    user='postgres',
    password='fyukiAmane03!',
    host='localhost',
    port='5432',
    database='municipal_app'
)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

try:
    with connection:
        with connection.cursor() as cursor:
            for _ in range(100):
                username = fake.user_name()
                email = fake.unique.email()
                password_hash = hash_password("defaultPassword123")
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                """, (username, email, password_hash))
    print("100 users inserted successfully.")
except Exception as e:
    print("Error:", e)
finally:
    connection.close()