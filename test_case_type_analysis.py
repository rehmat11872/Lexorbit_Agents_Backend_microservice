import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_case_type_analysis():
    print(f"\n{'='*60}")
    print(f"RUNNING TEST: Case Type Analysis (Success Rates by Category)")
    print(f"Endpoint: cases/type-analysis/")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/cases/type-analysis/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS")
            print(f"Found {len(data)} categories.\n")
            
            # Print in the format requested by UI
            print("Case Type Analysis")
            print("Success rates by case category\n")
            
            for item in data:
                print(f"{item.get('category')}")
                print(f"{item.get('total_cases')} cases")
                print(f"{item.get('granted_percentage')}% Granted")
                print(f"{item.get('denied_percentage')}% Denied")
                print("-" * 20)
                
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_case_type_analysis()
