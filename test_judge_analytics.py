import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_test(name, endpoint, method="GET", payload=None):
    print(f"\n{'='*60}")
    print(f"RUNNING TEST: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}/{endpoint}")
        else:
            response = requests.post(f"{BASE_URL}/{endpoint}", json=payload)
            
        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS")
            print(json.dumps(data, indent=2)[:1000] + ("..." if len(str(data)) > 1000 else ""))
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    # 1. Test Judge List (Search & Default Limit 3)
    run_test("Judge List (Default Limit 3)", "judges/")
    run_test("Judge Search (Angel Kelley)", "judges/?search=Angel")
    
    # Get a judge ID from the first result for subsequent tests
    try:
        res = requests.get(f"{BASE_URL}/judges/").json()
        if res:
            judge_id = res[1]['id']
            judge_name = res[1]['full_name']
            print(f"\nSelected Judge for deep dive: {judge_name} (ID: {judge_id})")
            
            # 2. Test Judge Profile
            run_test(f"Judge Profile: {judge_name}", f"judges/{judge_id}/profile/")
            
            # 3. Test Case History
            run_test(f"Case History: {judge_name}", f"judges/{judge_id}/case-history/")
            
            # 4. Test Prediction
            print(f"\n{'='*60}")
            print(f"RUNNING TEST: Prediction: {judge_name}")
            print(f"Endpoint: judges/{judge_id}/predict/")
            print(f"{'='*60}")
            
            prediction_payload = {
                "case_type": "Contract Dispute",
                "client_position": "Plaintiff",
                "case_description": "Breach of software licensing agreement between TechCorp and StartupXYZ."
            }
            res = requests.post(f"{BASE_URL}/judges/{judge_id}/predict/", json=prediction_payload)
            print(f"Status: {'SUCCESS' if res.status_code == 200 else 'FAILED (' + str(res.status_code) + ')'}")
            if res.status_code == 200:
                data = res.json()
                print(json.dumps(data, indent=2))
                
                print("\nVerification for UI:")
                print(f"Success Probability: {data.get('success_probability')}%")
                print(f"Confidence: {data.get('confidence_level')}")
                print(f"Est. Decision Time: {data.get('estimated_decision_time')}")
                
                print("\nContributing Factors:")
                for f in data.get('contributing_factors', []):
                    print(f"  - {f.get('name')} ({f.get('weight')}): {f.get('value')}")
                
                print("\nStrategic Recommendations:")
                for r in data.get('strategic_recommendations', []):
                    print(f"  - {r}")
        else:
            print("\nNo judges found in database. Please run ingestion first.")
    except Exception as e:
        print(f"Error fetching judge for deep dive: {e}")
