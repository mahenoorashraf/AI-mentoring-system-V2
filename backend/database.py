import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-PLC253F\\SQLEXPRESS;"
        "DATABASE=AI_Mentoring_V2;"
        "Trusted_Connection=yes;"
    )