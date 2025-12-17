#!/bin/bash

# ====================================================================
# Complete Data Download Script
# Downloads all models with proper relationships and embeddings
# ====================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          Legal AI Agent - Complete Data Download              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment
echo -e "${BLUE}[1/4]${NC} Activating virtual environment..."
source venv/bin/activate

# Check if server is running
echo -e "${BLUE}[2/4]${NC} Checking if Django server is running..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✓${NC} Server is running"
else
    echo -e "${YELLOW}⚠${NC}  Server not running. Please start it in another terminal:"
    echo "      python manage.py runserver"
    echo ""
    read -p "Press Enter when server is running..."
fi

# Ask user what to download
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Select dataset size:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1) Quick Test (1 judge, 20 opinions)    - 2-3 minutes"
echo "2) Development (3 judges, 60 opinions)  - 8-10 minutes"
echo "3) Production (9 judges, 270 opinions)  - 30-45 minutes"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo -e "\n${BLUE}[3/4]${NC} Downloading QUICK TEST dataset..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        echo -e "\n${YELLOW}Fetching:${NC} Brett Kavanaugh (1713) - 20 opinions"
        python manage.py fetch_judge_complete 1713 --max-opinions 20
        
        echo -e "\n${GREEN}✓ Quick test dataset downloaded!${NC}"
        ;;
    
    2)
        echo -e "\n${BLUE}[3/4]${NC} Downloading DEVELOPMENT dataset..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        echo -e "\n${YELLOW}Fetching [1/3]:${NC} Brett Kavanaugh (1713) - 20 opinions"
        python manage.py fetch_judge_complete 1713 --max-opinions 20
        
        echo -e "\n${YELLOW}Fetching [2/3]:${NC} John Roberts (3045) - 20 opinions"
        python manage.py fetch_judge_complete 3045 --max-opinions 20
        
        echo -e "\n${YELLOW}Fetching [3/3]:${NC} Sonia Sotomayor (2776) - 20 opinions"
        python manage.py fetch_judge_complete 2776 --max-opinions 20
        
        echo -e "\n${GREEN}✓ Development dataset downloaded!${NC}"
        ;;
    
    3)
        echo -e "\n${BLUE}[3/4]${NC} Downloading PRODUCTION dataset..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${YELLOW}This will take 30-45 minutes...${NC}"
        echo ""
        
        # Conservative wing
        echo -e "\n${YELLOW}Fetching [1/9]:${NC} John Roberts (3045) - 30 opinions"
        python manage.py fetch_judge_complete 3045 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [2/9]:${NC} Clarence Thomas (2745) - 30 opinions"
        python manage.py fetch_judge_complete 2745 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [3/9]:${NC} Samuel Alito (3454) - 30 opinions"
        python manage.py fetch_judge_complete 3454 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [4/9]:${NC} Neil Gorsuch (4238) - 30 opinions"
        python manage.py fetch_judge_complete 4238 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [5/9]:${NC} Brett Kavanaugh (1713) - 30 opinions"
        python manage.py fetch_judge_complete 1713 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [6/9]:${NC} Amy Coney Barrett (4285) - 20 opinions"
        python manage.py fetch_judge_complete 4285 --max-opinions 20
        
        # Liberal wing
        echo -e "\n${YELLOW}Fetching [7/9]:${NC} Sonia Sotomayor (2776) - 30 opinions"
        python manage.py fetch_judge_complete 2776 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [8/9]:${NC} Elena Kagan (2873) - 30 opinions"
        python manage.py fetch_judge_complete 2873 --max-opinions 30
        
        echo -e "\n${YELLOW}Fetching [9/9]:${NC} Ketanji Brown Jackson (4464) - 20 opinions"
        python manage.py fetch_judge_complete 4464 --max-opinions 20
        
        echo -e "\n${GREEN}✓ Production dataset downloaded!${NC}"
        ;;
    
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# Verify data
echo ""
echo -e "${BLUE}[4/4]${NC} Verifying database..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python manage.py shell << 'PYTHON'
from court_data.models import Judge, Court, Docket, OpinionCluster, Opinion, OpinionsCited

print("\n📊 DATABASE CONTENTS:")
print(f"   Courts:          {Court.objects.count()}")
print(f"   Judges:          {Judge.objects.count()}")
print(f"   Dockets:         {Docket.objects.count()}")
print(f"   OpinionClusters: {OpinionCluster.objects.count()}")
print(f"   Opinions:        {Opinion.objects.count()}")
print(f"   OpinionsCited:   {OpinionsCited.objects.count()}")

total = Court.objects.count() + Judge.objects.count() + Docket.objects.count() + \
        OpinionCluster.objects.count() + Opinion.objects.count() + OpinionsCited.objects.count()
print(f"\n   📦 Total Records: {total}")

print("\n🧠 EMBEDDINGS:")
judges_emb = Judge.objects.exclude(embedding__isnull=True).count()
dockets_emb = Docket.objects.exclude(embedding__isnull=True).count()
opinions_emb = Opinion.objects.exclude(embedding__isnull=True).count()

print(f"   Judges:   {judges_emb}/{Judge.objects.count()}")
print(f"   Dockets:  {dockets_emb}/{Docket.objects.count()}")
print(f"   Opinions: {opinions_emb}/{Opinion.objects.count()}")

if opinions_emb > 0:
    print("\n✅ Embeddings generated successfully!")
else:
    print("\n⚠️  No embeddings found!")

# Show sample
if Opinion.objects.exists():
    opinion = Opinion.objects.select_related('cluster__docket__court', 'author').first()
    print("\n📄 SAMPLE OPINION:")
    print(f"   Case:   {opinion.cluster.docket.case_name_short}")
    print(f"   Judge:  {opinion.author.full_name if opinion.author else 'Unknown'}")
    print(f"   Court:  {opinion.cluster.docket.court.name}")
    print(f"   Text:   {len(opinion.plain_text)} characters")
PYTHON

# Final message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Data download complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "   1. Test API endpoints:"
echo "      ./test_agents.sh"
echo ""
echo "   2. Try semantic search:"
echo "      curl -X POST http://localhost:8000/api/legal-research-advanced/ \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"query\": \"constitutional rights\"}'"
echo ""
echo "   3. View judge profile:"
echo "      curl http://localhost:8000/api/judges/1/complete_profile/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✨ Your Legal AI Agent is ready to use!${NC}"
echo ""

