#!/bin/bash

echo "=========================================="
echo "  Quick Data Download (Testing)"
echo "=========================================="
echo ""
echo "This will download a SMALL dataset for testing:"
echo "  - 100 courts"
echo "  - 20 Supreme Court judges"
echo "  - 100 recent Supreme Court cases"
echo "  - 100 opinions with full text"
echo "  - 1000 citations"
echo ""
echo "Estimated time: 20-30 minutes"
echo "Database size: ~500 MB"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

START_TIME=$(date +%s)

echo ""
echo "→ 1/5 Downloading courts..."
python manage.py fetch_courts --max-results 100

echo ""
echo "→ 2/5 Downloading Supreme Court judges..."
python manage.py fetch_judges --court scotus --max-results 20

echo ""
echo "→ 3/5 Downloading recent Supreme Court cases..."
python manage.py fetch_cases --court scotus --date-filed-after 2023-01-01 --max-results 100

echo ""
echo "→ 4/5 Downloading opinions..."
python manage.py fetch_opinions --date-filed-after 2023-01-01 --max-results 100

echo ""
echo "→ 5/5 Downloading citations..."
python manage.py fetch_citations --max-results 1000

# Complete
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))

echo ""
echo "=========================================="
echo "✓ Quick dataset ready!"
echo "=========================================="
echo ""
echo "Total time: ${MINUTES} minutes"
echo ""
echo "Database summary:"

python manage.py shell -c "
from court_data.models import *
print(f'  Courts:     {Court.objects.count():>6}')
print(f'  Judges:     {Judge.objects.count():>6}')
print(f'  Cases:      {Docket.objects.count():>6}')
print(f'  Opinions:   {Opinion.objects.count():>6}')
print(f'  Citations:  {Citation.objects.count():>6}')
"

echo ""
echo "Start server: python manage.py runserver"
echo "=========================================="

