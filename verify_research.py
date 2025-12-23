import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legal_agent_platform.settings')
django.setup()

from api.ai_services import legal_research_service, embedding_service
from court_data.models import Court, Docket, OpinionCluster, Opinion, Judge

def verify_research_flow():
    print("--- Verifying Legal Research Flow ---")
    
    # Check if we have data
    opinion_count = Opinion.objects.count()
    print(f"Total Opinions in DB: {opinion_count}")
    
    if opinion_count == 0:
        print("Warning: No opinions found. Verification will be limited.")
        return

    # Test query with federal filter
    filters = {
        'jurisdiction': 'federal',
        'court_level': 'supreme'
    }
    
    print(f"\nTesting semantic search with filters: {filters}")
    results = embedding_service.semantic_search_opinions("discrimination", filters=filters, max_results=5)
    
    print(f"Found {len(results)} results")
    for res in results:
        print(f" - {res['title']} ({res['court']})")
        
    # Verify the response structure for the full research API
    print("\nTesting full research_question response:")
    # Mocking self.client for this test to avoid API costs
    legal_research_service.client = None 
    
    response = legal_research_service.research_question("What is burden of proof?", filters=filters)
    
    expected_keys = ['query', 'summary', 'analysis', 'key_authorities', 'citations', 'source_opinions']
    missing_keys = [k for k in expected_keys if k not in response]
    
    if not missing_keys:
        print("✅ Response structure is CORRECT")
        print(json.dumps(response, indent=2, default=str)[:500] + "...")
    else:
        print(f"❌ Missing keys: {missing_keys}")

if __name__ == "__main__":
    verify_research_flow()
