import pandas as pd
import pyodbc

# Read CSV
df = pd.read_csv("../data/students.csv")
# Remove spaces, tabs, newlines from column names
df.columns = df.columns.str.replace(r'\s+', '', regex=True)

print(df.columns.tolist())

# SQL Server connection
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-PLC253F\\SQLEXPRESS;"
    "DATABASE=AI_Mentoring_V2;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()
print(df.head())

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO students
        (StudentID, Password, Age, Program, Semester, GPA,
         Attendance, AssignmentsCompletion, StressLevel,
         SleepHours, MentalWellbeing, ProductivityScore,
         Distractions, CareerClarity, SkillReadiness,
         EngagementScore)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    row["student_id"],
    row["password"],
    row["age"],
    row["program"],
    row["semester"],
    row["gpa"],
    row["attendance"],
    row["assignments_completion"],
    row["stress_level"],
    row["sleep_hours"],
    row["mental_wellbeing"],
    row["productivity_score"],
    row["distractions"],
    row["career_clarity"],
    row["skill_readiness"],
    row["engagement_score"]
    )

conn.commit()
conn.close()

print("✅ Students imported successfully!")