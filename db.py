import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv("POSTGRES_URL")


def get_connection():
    return psycopg2.connect(DB_URL)


# CREATE
def create_resource(source_text, source_file, title, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resource_table (source_text, source_file, title, description) VALUES (%s, %s, %s, %s)",
        (source_text, source_file, title, description)
    )

    conn.commit()
    cur.close()
    conn.close()


# READ
def get_resources():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resource_table ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# UPDATE
def update_resource(id, source_text, title, description, source_file=None):
    conn = get_connection()
    cur = conn.cursor()

    if source_file:
        cur.execute(
            "UPDATE resource_table SET source_text=%s, title=%s,description=%s, source_file=%s WHERE id=%s",
            (source_text, title, description, source_file, id)
        )
    else:
        cur.execute(
            "UPDATE resource_table SET source_text=%s, title=%s,description=%s WHERE id=%s",
            (source_text, title, description, id)
        )

    conn.commit()
    cur.close()
    conn.close()


# DELETE
def delete_resource(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM resource_table WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()


def get_all_resources():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, description FROM resource_table;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows   # returns list of (title, description)


def get_resource_by_title(title):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id,source_text, source_file, title, description
        FROM resource_table WHERE title = %s
    """, (title,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row   # returns (source_text, source_file, title, description)
