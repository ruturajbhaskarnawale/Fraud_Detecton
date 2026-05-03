import time
import requests
import os

def check_health():
    print("--- MONITORING START ---", flush=True)
    backend_up = False
    frontend_up = False
    
    # Check Backend (FastAPI)
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        if r.status_code == 200:
            print("✅ Backend is ALIVE", flush=True)
            backend_up = True
        else:
            print(f"⚠️ Backend returned status {r.status_code}", flush=True)
    except Exception as e:
        print(f"❌ Backend is DOWN: {e}", flush=True)
        
    # Check Frontend (Next.js)
    try:
        r = requests.get("http://localhost:3000", timeout=5)
        if r.status_code == 200:
            print("✅ Frontend is ALIVE", flush=True)
            frontend_up = True
        else:
            print(f"⚠️ Frontend returned status {r.status_code}", flush=True)
    except Exception as e:
        print(f"❌ Frontend is DOWN: {e}", flush=True)
        
    return backend_up, frontend_up

if __name__ == "__main__":
    check_health()
