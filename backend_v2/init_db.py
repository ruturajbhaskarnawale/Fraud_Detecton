from backend_v2.database.manager import init_db
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initializing Veridex Production Database...")
    try:
        init_db()
        print("Success: Database successfully audited and implemented.")
    except Exception as e:
        print(f"Error: Failed to initialize database: {e}")
