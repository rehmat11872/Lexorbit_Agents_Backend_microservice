#!/bin/bash

# Legal Research API - General Legal Questions Testing Script
# Tests various areas of law with general legal concepts

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Legal Research API - General Legal Questions Test         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Test if server is running
echo -e "${BLUE}[CHECK]${NC} Verifying server is running..."
if ! curl -s "${BASE_URL}/" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Warning:${NC} Server not responding. Please start:"
    echo "  python manage.py runserver"
    exit 1
fi
echo -e "${GREEN}✓${NC} Server is running"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 1: Tort Law Questions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1
echo -e "${BLUE}Test 1:${NC} Elements of negligence"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the elements of negligence in tort law?"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 2
echo -e "${BLUE}Test 2:${NC} Duty of care and reasonable person standard"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "duty of care reasonable person standard foreseeability"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 3
echo -e "${BLUE}Test 3:${NC} Strict liability"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "strict liability products liability dangerous activities"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 2: Contract Law Questions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 4
echo -e "${BLUE}Test 4:${NC} Promissory estoppel doctrine"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the doctrine of promissory estoppel in contract law"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 5
echo -e "${BLUE}Test 5:${NC} Contract formation elements"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "offer acceptance consideration mutual assent contract formation"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 6
echo -e "${BLUE}Test 6:${NC} Breach of contract and remedies"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "material breach anticipatory breach contract remedies"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 3: Property Law Questions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 7
echo -e "${BLUE}Test 7:${NC} Adverse possession"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "adverse possession property rights continuous exclusive possession"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 8
echo -e "${BLUE}Test 8:${NC} Easements and property rights"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "easement by necessity express easement property rights"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 4: Criminal Law Questions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 9
echo -e "${BLUE}Test 9:${NC} Mens rea and criminal intent"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "mens rea criminal intent actus reus guilty mind"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 10
echo -e "${BLUE}Test 10:${NC} Self-defense justification"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "self-defense justification imminent threat reasonable force"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 5: Questions with Filters"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 11 - Federal jurisdiction
echo -e "${BLUE}Test 11:${NC} Contract law (Federal jurisdiction)"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "breach of contract damages remedies",
    "filters": {"jurisdiction": "federal"}
  }')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Filters: Federal | Summary: \(.summary[:80])..."'
echo ""

# Test 12 - Supreme Court
echo -e "${BLUE}Test 12:${NC} Property rights (Supreme Court only)"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "property rights takings clause just compensation",
    "filters": {"court_level": "supreme"}
  }')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Filters: Supreme Court | Summary: \(.summary[:80])..."'
echo ""

# Test 13 - Date range
echo -e "${BLUE}Test 13:${NC} Recent cases (2020+)"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "negligence tort liability standard of care",
    "filters": {"date_from": "2020-01-01"}
  }')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Filters: 2020+ | Summary: \(.summary[:80])..."'
echo ""

# Test 14 - Judge filter
echo -e "${BLUE}Test 14:${NC} Specific judge (Kavanaugh)"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract interpretation ambiguity construction",
    "filters": {"judge_name": "Kavanaugh"}
  }')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Filters: Kavanaugh | Summary: \(.summary[:80])..."'
echo ""

# Test 15 - Multiple filters
echo -e "${BLUE}Test 15:${NC} Multiple filters (Federal + Supreme)"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "due process constitutional rights fundamental liberties",
    "filters": {
      "jurisdiction": "federal",
      "court_level": "supreme"
    }
  }')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Filters: Federal+Supreme | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 6: Constitutional Law"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 16
echo -e "${BLUE}Test 16:${NC} Due process clause"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "procedural due process substantive due process fundamental rights"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 17
echo -e "${BLUE}Test 17:${NC} Equal protection analysis"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "equal protection clause strict scrutiny suspect classification"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 7: Semantic Search Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 18
echo -e "${BLUE}Test 18:${NC} Semantic search - legal obligation concepts"
RESULT=$(curl -s -X POST "${BASE_URL}/api/agents/semantic-search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "legal obligation duty responsibility requirement", "max_results": 5}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Query: \(.query)"'
if [ "$(echo "$RESULT" | jq '.results | length')" -gt 0 ]; then
    echo "First result:"
    echo "$RESULT" | jq -r '.results[0] | "  Type: \(.type) | Title: \(.title[:60])..."'
fi
echo ""

# Test 19
echo -e "${BLUE}Test 19:${NC} Semantic search - damages and compensation"
RESULT=$(curl -s -X POST "${BASE_URL}/api/agents/semantic-search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "monetary damages compensation injury harm", "max_results": 10}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Query: \(.query)"'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 8: Specialized Areas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 20
echo -e "${BLUE}Test 20:${NC} Employment law - wrongful termination"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "wrongful termination at-will employment public policy exception"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 21
echo -e "${BLUE}Test 21:${NC} Corporate law - fiduciary duty"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "fiduciary duty loyalty care corporate directors shareholders"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

# Test 22
echo -e "${BLUE}Test 22:${NC} Intellectual property - copyright fair use"
RESULT=$(curl -s -X POST "${BASE_URL}/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "copyright fair use transformative use commercial purpose"}')
echo "$RESULT" | jq -r '"Results: \(.total_results) | Summary: \(.summary[:80])..."'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Testing Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 SUMMARY:"
echo "  - Tested 22 different legal questions"
echo "  - Covered: Tort, Contract, Property, Criminal, Constitutional Law"
echo "  - Tested: Federal/Supreme Court filters, Date filters, Judge filters"
echo "  - Tested: Semantic search, Specialized areas (Employment, Corporate, IP)"
echo ""
echo "💡 LEGAL AREAS TESTED:"
echo "  ✓ Tort Law (negligence, strict liability, duty of care)"
echo "  ✓ Contract Law (promissory estoppel, formation, breach)"
echo "  ✓ Property Law (adverse possession, easements)"
echo "  ✓ Criminal Law (mens rea, self-defense)"
echo "  ✓ Constitutional Law (due process, equal protection)"
echo "  ✓ Employment Law (wrongful termination)"
echo "  ✓ Corporate Law (fiduciary duty)"
echo "  ✓ Intellectual Property (copyright fair use)"
echo ""
echo "📖 For all 64 questions, see: TEST_QUESTIONS.md"
echo ""
