import pandas as pd
import pyodbc

# Read mentors.csv
df = pd.read_csv("../data/mentors.csv")

# Clean column names
df.columns = df.columns.str.replace(r'\s+', '', regex=True)

print(df.columns.tolist())
print(df.head())

# Connect to SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PLC253F\\SQLEXPRESS;"
    "DATABASE=AI_Mentoring_V2;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# Insert data
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO mentors
        (
            MentorID,
            MentorName,
            Expertise,
            MentorType,
            AvailabilityHours
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    row["mentor_id"],
    row["mentor_name"],
    row["expertise"],
    row["mentor_type"],
    row["availability_hours"]
    )

# Save changes
conn.commit()

print("✅ Mentors imported successfully!")

conn.close()