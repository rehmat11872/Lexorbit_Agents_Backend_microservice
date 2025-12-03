#!/bin/bash

echo "=========================================="
echo "Testing CourtListener API Connection"
echo "=========================================="
echo ""

# Test internet connection
echo "1️⃣  Testing internet connection..."
if ping -c 1 www.google.com &> /dev/null; then
    echo "✓ Internet connection OK"
else
    echo "✗ No internet connection!"
    echo "  → Check your WiFi/network"
    exit 1
fi

# Test CourtListener connection
echo ""
echo "2️⃣  Testing CourtListener API..."
if curl -s --head https://www.courtlistener.com | head -n 1 | grep "HTTP" &> /dev/null; then
    echo "✓ Can reach CourtListener"
else
    echo "✗ Cannot reach CourtListener!"
    echo "  → Check firewall/VPN"
    exit 1
fi

# Test API v4
echo ""
echo "3️⃣  Testing API v4 endpoint..."
response=$(curl -s -w "%{http_code}" "https://www.courtlistener.com/api/rest/v4/" -o /dev/null)
if [ "$response" = "200" ]; then
    echo "✓ API v4 is accessible"
else
    echo "✗ API v4 returned: $response"
fi

# Test with your API key
echo ""
echo "4️⃣  Testing with your API key..."
source venv/bin/activate
API_KEY=$(python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('COURTLISTENER_API_KEY', 'NOT_FOUND'))")

if [ "$API_KEY" = "NOT_FOUND" ]; then
    echo "✗ API key not found in .env"
else
    echo "✓ API key found: ${API_KEY:0:10}..."
    
    # Test API with key
    response=$(curl -s -w "%{http_code}" \
        -H "Authorization: Token $API_KEY" \
        "https://www.courtlistener.com/api/rest/v4/courts/?page_size=1" \
        -o /dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✓ API key works!"
        echo ""
        echo "=========================================="
        echo "✓ ALL TESTS PASSED!"
        echo "=========================================="
        echo ""
        echo "Ready to fetch data! Try:"
        echo "  python manage.py fetch_judge_complete --judge-id 2776"
    else
        echo "✗ API returned: $response"
        echo "  → Check your API key"
    fi
fi

echo ""

