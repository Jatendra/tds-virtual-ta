#!/usr/bin/env python3
"""
Quick test script for current Railway deployment
"""

import requests
import json

RAILWAY_URL = "https://web-production-c2451.up.railway.app"

def test_endpoints():
    """Test all endpoints to identify the issue"""
    
    print(f"🚀 Testing TDS Virtual TA at: {RAILWAY_URL}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing Root Endpoint (/)...")
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Root endpoint works - Web interface loads")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Health endpoint
    print("\n2. Testing Health Endpoint (/health)...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint works")
            print(f"   App Status: {data.get('status', 'unknown')}")
            print(f"   Data Loaded: {data.get('data_loaded', False)}")
            print(f"   Components: {data.get('components', {})}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 3: API endpoint
    print("\n3. Testing Main API Endpoint (/api/)...")
    payload = {
        "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
        "image": None
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint works")
            print(f"   Answer length: {len(data.get('answer', ''))}")
            print(f"   Links count: {len(data.get('links', []))}")
            print(f"   Links: {[link.get('text', '') for link in data.get('links', [])]}")
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API endpoint error: {e}")
    
    # Test 4: Token calculator
    print("\n4. Testing Token Calculator (/api/calculate-tokens)...")
    token_payload = {
        "text": "This is a test message",
        "model": "gpt-3.5-turbo-0125",
        "token_type": "input"
    }
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/calculate-tokens",
            json=token_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Token calculator works")
            print(f"   Tokens: {data.get('token_count', 0)}")
            print(f"   Cost: ${data.get('cost_dollars', 0):.6f}")
        else:
            print(f"❌ Token calculator failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Token calculator error: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSIS:")
    print("If all endpoints work here but browser shows 'Failed to fetch',")
    print("the issue is likely CORS-related. Deploy the updated main.py")
    print("with CORS middleware to fix the browser API calls.")
    print(f"\n🌐 Your app: {RAILWAY_URL}")

if __name__ == "__main__":
    test_endpoints() 