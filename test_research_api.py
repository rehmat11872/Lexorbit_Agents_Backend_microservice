import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_test(name, payload):
    print(f"\n{'='*60}")
    print(f"RUNNING TEST: {name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/agents/legal-research/", json=payload)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS ({duration:.2f}s)")
            
            print(f"\n[SUMMARY]")
            print(data.get('summary'))
            
            print(f"\n[KEY AUTHORITIES]")
            authorities = data.get('key_authorities', [])
            if not authorities:
                print("No authorities found (check if DB has ingested opinions).")
            for auth_str in authorities:
                print(f"• {auth_str}")
            
            print(f"\n[ANALYSIS]")
            print(data.get('analysis'))
            
            print(f"\n[CITATIONS]")
            for cit in data.get('citations', []):
                print(f"• {cit}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    # Test 1: No Filters
    run_test("Research WITHOUT Filters", {
        "question": "What is the burden of proof in employment discrimination cases under Title VII?"
    })
    
    # Test 2: With Advanced Filters
    run_test("Research WITH Advanced Filters (Federal Supreme)", {
        "question": "burden of proof Title VII",
        "jurisdiction": "federal",
        "court_level": "supreme",
        "date_from": "1970-01-01"
    })
