import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)

cursor = conn.cursor()

def log_pdf_data(filename: str, embedding_ids: list):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_logs (
            id SERIAL PRIMARY KEY,
            filename TEXT,
            embedding_ids TEXT
        )
    """)
    cursor.execute("INSERT INTO pdf_logs (filename, embedding_ids) VALUES (%s, %s)",
                   (filename, ",".join(embedding_ids)))
    conn.commit()