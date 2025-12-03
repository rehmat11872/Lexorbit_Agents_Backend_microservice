#!/bin/bash

echo "=========================================="
echo "  Fix Data Links & Re-Download"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Check your API version"
echo "  2. Clear incomplete data"
echo "  3. Download judges with ALL related data"
echo "  4. Verify data is properly linked"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "=========================================="
echo "STEP 1: Checking API Version"
echo "=========================================="

# Check .env file
if grep -q "v3" .env 2>/dev/null; then
    echo "❌ ERROR: Your .env still has v3!"
    echo ""
    echo "Please run:"
    echo "  nano .env"
    echo ""
    echo "Find the line:"
    echo "  COURTLISTENER_BASE_URL=...v3"
    echo ""
    echo "Change to:"
    echo "  COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v4"
    echo ""
    echo "Save and run this script again."
    exit 1
else
    echo "✓ API version looks correct"
fi

echo ""
echo "=========================================="
echo "STEP 2: Clearing Incomplete Data"
echo "=========================================="

python manage.py shell << EOF
from court_data.models import Judge, Opinion, Docket, Citation
print(f"Before delete:")
print(f"  Judges: {Judge.objects.count()}")
print(f"  Opinions: {Opinion.objects.count()}")
print(f"  Dockets: {Docket.objects.count()}")
print(f"  Citations: {Citation.objects.count()}")
print("")
print("Deleting incomplete data...")
Judge.objects.all().delete()
Opinion.objects.all().delete()
Docket.objects.all().delete()
Citation.objects.all().delete()
print("✓ Cleared")
EOF

echo ""
echo "=========================================="
echo "STEP 3: Downloading Courts"
echo "=========================================="

python manage.py fetch_courts --max-results 100
echo "✓ Courts downloaded"

echo ""
echo "=========================================="
echo "STEP 4: Downloading Judges (with ALL data)"
echo "=========================================="

echo ""
echo "Downloading Supreme Court justices..."
echo "This will take 10-15 minutes per judge."
echo ""

# Supreme Court justices with good data
JUDGES=(2776 2587 2730)  # Sotomayor, Kagan, Gorsuch

for JUDGE_ID in "${JUDGES[@]}"; do
    echo ""
    echo "→ Downloading judge $JUDGE_ID..."
    python manage.py fetch_judge_complete --judge-id $JUDGE_ID
    echo "✓ Judge $JUDGE_ID complete"
done

echo ""
echo "=========================================="
echo "STEP 5: Verifying Data Links"
echo "=========================================="

python manage.py shell << EOF
from court_data.models import Court, Judge, Opinion, Docket, Citation

print("")
print("Database Summary:")
print("=" * 50)
print(f"Courts:     {Court.objects.count():>6}")
print(f"Judges:     {Judge.objects.count():>6}")
print(f"Dockets:    {Docket.objects.count():>6}")
print(f"Opinions:   {Opinion.objects.count():>6}")
print(f"Citations:  {Citation.objects.count():>6}")
print("")

print("Checking data links...")
print("=" * 50)

for judge in Judge.objects.all():
    opinions_count = judge.authored_opinions.count()
    print(f"")
    print(f"Judge: {judge.full_name}")
    print(f"  Opinions authored: {opinions_count}")
    
    if opinions_count > 0:
        print(f"  Sample cases:")
        for op in judge.authored_opinions.all()[:3]:
            if op.docket:
                case_name = op.docket.case_name_short or op.docket.case_name
                citations_count = op.cited_by.count()
                print(f"    - {case_name}")
                print(f"      Cited by {citations_count} other cases")
    else:
        print(f"  ⚠️  WARNING: No opinions found!")

print("")
print("=" * 50)
print("✓ Verification complete")
EOF

echo ""
echo "=========================================="
echo "✅ DONE!"
echo "=========================================="
echo ""
echo "Your data is now properly linked!"
echo ""
echo "Start the server:"
echo "  python manage.py runserver"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/api/judges/1/complete_profile/"
echo ""
echo "=========================================="

