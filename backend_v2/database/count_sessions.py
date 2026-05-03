import psycopg2
import sys

def count_sessions():
    url = "postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db"
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sessions;")
        count = cur.fetchone()[0]
        print(f"Total Sessions: {count}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"FAILED - {e}")

if __name__ == "__main__":
    count_sessions()
