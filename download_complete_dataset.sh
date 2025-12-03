#!/bin/bash

echo "=========================================="
echo "  Complete Data Download for Frontend"
echo "=========================================="
echo ""
echo "This will download:"
echo "  - All courts (~500)"
echo "  - Judges from major courts (~200)"
echo "  - Recent cases (2020-2024, ~5000)"
echo "  - Opinions with full text (~5000)"
echo "  - Citation relationships (~10000)"
echo ""
echo "Estimated time: 4-6 hours"
echo "Database size: ~5-10 GB"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Track start time
START_TIME=$(date +%s)

# ==========================================
# PHASE 1: Foundation Data
# ==========================================
echo ""
echo "=========================================="
echo "PHASE 1: Downloading Courts & Judges"
echo "=========================================="

# 1.1 Download all courts
echo ""
echo "→ Downloading all courts..."
python manage.py fetch_courts
echo "✓ Courts downloaded"

# 1.2 Download Supreme Court judges (most important)
echo ""
echo "→ Downloading Supreme Court judges..."
python manage.py fetch_judges --court scotus --max-results 50
echo "✓ Supreme Court judges downloaded"

# 1.3 Download Federal Circuit judges (major circuits)
echo ""
echo "→ Downloading Federal Circuit judges..."
for court in ca9 ca2 ca5 ca1 ca3 ca4 ca6 ca7 ca8 ca10 ca11 cadc cafc; do
    echo "  - $court..."
    python manage.py fetch_judges --court $court --max-results 20
done
echo "✓ Circuit judges downloaded"

# 1.4 Download District Court judges (sample from major districts)
echo ""
echo "→ Downloading sample District Court judges..."
for court in dcd nysd cand ndca; do
    echo "  - $court..."
    python manage.py fetch_judges --court $court --max-results 10
done
echo "✓ District judges downloaded"

# ==========================================
# PHASE 2: Cases & Opinions
# ==========================================
echo ""
echo "=========================================="
echo "PHASE 2: Downloading Cases & Opinions"
echo "=========================================="

# 2.1 Supreme Court cases (highest quality)
echo ""
echo "→ Downloading Supreme Court cases (2020-2024)..."
python manage.py fetch_cases --court scotus --date-filed-after 2020-01-01 --max-results 1000
echo "✓ Supreme Court cases downloaded"

# 2.2 Federal Circuit cases
echo ""
echo "→ Downloading Federal Circuit cases (2022-2024)..."
for court in ca9 ca2 ca5; do
    echo "  - $court..."
    python manage.py fetch_cases --court $court --date-filed-after 2022-01-01 --max-results 500
done
echo "✓ Circuit cases downloaded"

# 2.3 District Court cases (sample)
echo ""
echo "→ Downloading District Court cases (2023-2024)..."
python manage.py fetch_cases --court dcd --date-filed-after 2023-01-01 --max-results 500
echo "✓ District court cases downloaded"

# 2.4 Opinions for all cases
echo ""
echo "→ Downloading opinions with full text..."
python manage.py fetch_opinions --date-filed-after 2020-01-01 --max-results 5000
echo "✓ Opinions downloaded"

# ==========================================
# PHASE 3: Citations
# ==========================================
echo ""
echo "=========================================="
echo "PHASE 3: Downloading Citations"
echo "=========================================="

echo ""
echo "→ Downloading citation relationships..."
python manage.py fetch_citations --max-results 10000
echo "✓ Citations downloaded"

# ==========================================
# COMPLETE
# ==========================================
echo ""
echo "=========================================="
echo "✓ DOWNLOAD COMPLETE!"
echo "=========================================="

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))

echo ""
echo "Total time: ${HOURS}h ${MINUTES}m"
echo ""
echo "Database summary:"
echo "=========================================="

# Show counts
python manage.py shell -c "
from court_data.models import *
print(f'  Courts:     {Court.objects.count():>6}')
print(f'  Judges:     {Judge.objects.count():>6}')
print(f'  Cases:      {Docket.objects.count():>6}')
print(f'  Opinions:   {Opinion.objects.count():>6}')
print(f'  Citations:  {Citation.objects.count():>6}')
"

echo ""
echo "=========================================="
echo "Your frontend is now ready!"
echo ""
echo "Start the server:"
echo "  python manage.py runserver"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/api/judges/"
echo "=========================================="

