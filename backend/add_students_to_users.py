import pyodbc
from werkzeug.security import generate_password_hash

# SQL Server Connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PLC253F\\SQLEXPRESS;"
    "DATABASE=AI_Mentoring_V2;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# Read all students
cursor.execute("SELECT StudentID, Password FROM students")
students = cursor.fetchall()

count = 0

for student in students:

    username = student.StudentID
    password = student.Password

    # Check if user already exists
    cursor.execute(
        "SELECT UserID FROM Users WHERE Username=?",
        (username,)
    )

    existing = cursor.fetchone()

    hashed_password = generate_password_hash(password)
    email = f"{username.lower()}@example.com"

    if existing:
        # Update existing user (e.g., S001)
        cursor.execute("""
            UPDATE Users
            SET PasswordHash=?,
                Role=?,
                Email=?
            WHERE Username=?
        """,
        (
            hashed_password,
            "Student",
            email,
            username
        ))
        print(f"Updated {username}")

    else:
        # Insert new user
        cursor.execute("""
            INSERT INTO Users
            (Username, PasswordHash, Role, Email)
            VALUES (?, ?, ?, ?)
        """,
        (
            username,
            hashed_password,
            "Student",
            email
        ))
        print(f"Inserted {username}")

    count += 1

conn.commit()

print(f"\nCompleted! Processed {count} students.")

cursor.close()
conn.close()