#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        🧪 Testing AI Agent Features                       ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Test 1: Statistics
echo -e "${GREEN}1️⃣  Platform Statistics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/api/statistics/ | python -m json.tool
echo ""

# Test 2: Legal Research
echo -e "\n${GREEN}2️⃣  Legal Research Assistant (Semantic Search with AI)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Query: 'constitutional rights and federal jurisdiction'${NC}"
curl -s -X POST $BASE_URL/api/legal-research-advanced/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "constitutional rights and federal jurisdiction",
    "filters": {
      "jurisdiction": "federal",
      "court_level": "supreme"
    }
  }' | python -c "import sys, json; data=json.load(sys.stdin); print(f\"  Query: {data['query']}\"); print(f\"  Total Results: {data['total_results']}\"); print(f\"  Key Authorities: {len(data['key_authorities'])}\"); [print(f\"    - {case['case_name']}\") for case in data['key_authorities'][:3]]"
echo ""

# Test 3: Judge Complete Profile
echo -e "\n${GREEN}3️⃣  Judge Complete Profile${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $BASE_URL/api/judges/34/complete_profile/ | python -c "import sys, json; data=json.load(sys.stdin); info=data['basic_info']; stats=data['statistics']; print(f\"  Judge: {info['full_name']}\"); print(f\"  Gender: {info['gender']}\"); print(f\"  Birth: {info['date_birth']}\"); print(f\"  Location: {info['dob_city']}, {info['dob_state']}\"); print(f\"\n  Statistics:\"); print(f\"    - Total Cases: {stats['total_cases']}\"); print(f\"    - Total Opinions: {stats['total_opinions']}\"); print(f\"    - Grant Rate: {stats['grant_rate']}%\"); print(f\"    - Deny Rate: {stats['deny_rate']}%\"); print(f\"\n  Sample Cases:\"); [print(f\"    - {case['case_name_short'] or case['case_name']}\") for case in data['all_cases'][:3] if 'case_name' in case or 'case_name_short' in case]"
echo ""

# Test 4: Semantic Search
echo -e "\n${GREEN}4️⃣  Semantic Search (Vector Similarity)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Query: 'banking fraud liability'${NC}"
curl -s -X POST $BASE_URL/api/agents/semantic-search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "banking fraud liability",
    "max_results": 5
  }' | python -c "import sys, json; data=json.load(sys.stdin); print(f\"  Total Results: {data['total_results']}\"); print(f\"  Breakdown:\"); breakdown=data['breakdown']; print(f\"    - Opinions: {breakdown['opinions']}\"); print(f\"    - Cases: {breakdown['cases']}\"); print(f\"    - Judges: {breakdown['judges']}\")"
echo ""

# Test 5: Judge Cases List
echo -e "\n${GREEN}5️⃣  Judge Cases List${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$BASE_URL/api/judges/34/cases/" | python -c "import sys, json; data=json.load(sys.stdin); results=data.get('results', []); count=data.get('count', len(results)); print(f\"  Total Cases: {count}\"); print(f\"  Showing: {len(results)}\"); print(f\"\n  Recent Cases:\"); [print(f\"    - Opinion ID {case['opinion_id']}: {case.get('type', 'Unknown Type')}\") for case in results[:5]]" 2>/dev/null || echo "  No case data available"
echo ""

# Test 6: Case Prediction
echo -e "\n${GREEN}6️⃣  Case Prediction (AI Mock)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Case: Banking fraud with federal jurisdiction${NC}"
curl -s -X POST $BASE_URL/api/agents/case-prediction/ \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "banking fraud",
    "jurisdiction": "federal",
    "judge_id": 34,
    "brief_summary": "Federal banking fraud case"
  }' | python -c "import sys, json; data=json.load(sys.stdin); print(f\"  Predicted Outcome: {data['predicted_outcome']}\"); print(f\"  Success Probability: {data['success_probability']}%\"); print(f\"\n  Key Factors:\"); [print(f\"    - {f['factor']}: {f['impact']} (weight: {f['weight']})\") for f in data['factors']]"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ✅ All Tests Complete!                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📖 Full guide: ${YELLOW}TESTING_GUIDE.md${NC}"
echo -e "🌐 API Docs: ${YELLOW}FRONTEND_API_GUIDE.md${NC}"
echo ""

