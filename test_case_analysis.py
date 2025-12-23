import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_general_prediction():
    print(f"\n{'='*60}")
    print(f"RUNNING TEST: General Case Analysis & Prediction")
    print(f"Endpoint: cases/predict/")
    print(f"{'='*60}")
    
    payload = {
        "case_type": "Contract Dispute",
        "jurisdiction": "Superior Court of California",
        "case_summary": "Breach of software licensing agreement regarding cloud infrastructure deployment.",
        "key_facts": "Plaintiff signed a 3-year exclusivity contract. Defendant terminated after 12 months."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cases/predict/", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS")
            print(json.dumps(data, indent=2))
            
            # Verify UI-specific fields
            print("\nVerification for UI:")
            print(f"Success Probability: {data.get('success_probability')}%")
            print(f"Confidence: {data.get('confidence_level')}")
            print(f"Outcome Breakdown:")
            print(f"  - Favorable: {data.get('outcome_breakdown', {}).get('favorable')}%")
            print(f"  - Uncertain: {data.get('outcome_breakdown', {}).get('uncertain')}%")
            print(f"  - Unfavorable: {data.get('outcome_breakdown', {}).get('unfavorable')}%")
            
            print("\nContributing Factors:")
            for factor in data.get('contributing_factors', []):
                print(f"  - {factor.get('name')}: {factor.get('sentiment')}")
                
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_general_prediction()
