import redis
import psycopg2
import sys

def check_postgres():
    url = "postgresql://jotex_user:Lucky%402005%2B@localhost:5432/jotex_db"
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print("Postgres: CONNECTED")
    except Exception as e:
        print(f"Postgres: FAILED - {e}")

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("Redis: CONNECTED")
    except Exception as e:
        print(f"Redis: FAILED - {e}")

if __name__ == "__main__":
    check_postgres()
    check_redis()
