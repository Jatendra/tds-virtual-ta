#!/usr/bin/env python3
"""
Test script for deployed TDS Virtual TA API on Railway
"""

import requests
import json
import time

# Replace this with your actual Railway URL
RAILWAY_URL = "https://web-production-c2451.up.railway.app"

def test_deployed_api():
    """Test the deployed TDS Virtual TA API"""
    
    print(f"🚀 Testing TDS Virtual TA deployed at: {RAILWAY_URL}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Data loaded: {health_data.get('data_loaded', False)}")
            print(f"   Components: {health_data.get('components', {})}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Main API endpoint
    print("\n2. Testing Question Answering...")
    test_question = "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"
    
    payload = {
        "question": test_question,
        "image": None
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{RAILWAY_URL}/api/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=35
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Question answering works!")
            print(f"   Response time: {end_time - start_time:.2f}s")
            print(f"   Answer preview: {data['answer'][:150]}...")
            print(f"   Links provided: {len(data['links'])}")
        else:
            print(f"❌ Question answering failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Question answering error: {e}")
        return False
    
    # Test 3: Token Calculator
    print("\n3. Testing Token Calculator...")
    token_payload = {
        "text": "This is a test message for token calculation",
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
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token calculator works!")
            print(f"   Tokens: {data['token_count']}")
            print(f"   Cost: ${data['cost_dollars']:.6f} ({data['cost_cents']:.4f} cents)")
        else:
            print(f"❌ Token calculator failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Token calculator error: {e}")
    
    # Test 4: Sample Problem Solver
    print("\n4. Testing Sample Problem Solver...")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/solve-sample-problem", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sample problem solver works!")
            print(f"   Solution preview: {data['solution'][:200]}...")
        else:
            print(f"❌ Sample problem solver failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample problem solver error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Your TDS Virtual TA is live and working!")
    print(f"📱 Access it at: {RAILWAY_URL}")
    print("🔗 API endpoints available:")
    print(f"   - Health: {RAILWAY_URL}/health")
    print(f"   - Ask questions: {RAILWAY_URL}/api/")
    print(f"   - Calculate tokens: {RAILWAY_URL}/api/calculate-tokens")
    print(f"   - Solve sample: {RAILWAY_URL}/api/solve-sample-problem")
    
    return True

if __name__ == "__main__":
    print("🔧 SETUP REQUIRED:")
    print("1. Replace RAILWAY_URL with your actual Railway deployment URL")
    print("2. Find your URL at: https://railway.app/dashboard")
    print("3. It should look like: https://your-app-name.up.railway.app")
    print("\nThen run this script to test your deployment!")
    print("\n" + "=" * 60)
    
    # Now test your deployed API
    test_deployed_api() 