#!/usr/bin/env python3
"""
Test script for TDS Virtual TA API
"""

import requests
import json
import time
import base64
from typing import Dict, Any

def test_api_endpoint(base_url: str = "http://localhost:8000") -> None:
    """Test the TDS Virtual TA API endpoint"""
    
    api_url = f"{base_url}/api/"
    
    # Test cases
    test_cases = [
        {
            "name": "GPT Model Question",
            "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
            "expected_keywords": ["gpt-3.5-turbo-0125", "OpenAI API"]
        },
        {
            "name": "Python Setup Question",
            "question": "How do I set up my Python environment for TDS?",
            "expected_keywords": ["Python 3.8", "pip"]
        },
        {
            "name": "Visualization Question",
            "question": "What are the best practices for data visualization?",
            "expected_keywords": ["chart", "labels"]
        },
        {
            "name": "Assignment Question",
            "question": "How should I submit my assignment?",
            "expected_keywords": ["file formats", "documentation"]
        },
        {
            "name": "General Question",
            "question": "What is machine learning?",
            "expected_keywords": ["machine learning", "TDS"]
        }
    ]
    
    print(f"Testing TDS Virtual TA API at {api_url}")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        # Prepare request
        payload = {
            "question": test_case["question"],
            "image": None
        }
        
        try:
            # Make request
            start_time = time.time()
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=35  # Slightly more than 30s limit
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"⏱️  Response time: {response_time:.2f}s")
                
                # Validate response format
                if "answer" in data and "links" in data:
                    print("✅ Response format valid")
                    
                    # Check answer content
                    answer = data["answer"]
                    print(f"📝 Answer: {answer[:100]}...")
                    
                    # Check for expected keywords
                    found_keywords = []
                    for keyword in test_case["expected_keywords"]:
                        if keyword.lower() in answer.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"✅ Found keywords: {found_keywords}")
                    else:
                        print(f"⚠️  Expected keywords not found: {test_case['expected_keywords']}")
                    
                    # Check links
                    links = data["links"]
                    if links and len(links) > 0:
                        print(f"✅ Links provided: {len(links)}")
                        for link in links[:2]:  # Show first 2 links
                            print(f"   🔗 {link['url']}")
                    else:
                        print("⚠️  No links provided")
                    
                    # Check response time
                    if response_time <= 30:
                        print("✅ Response within 30s limit")
                    else:
                        print(f"❌ Response too slow: {response_time:.2f}s > 30s")
                        
                else:
                    print("❌ Invalid response format")
                    print(f"Response: {data}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (>35s)")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing completed!")

def test_with_image():
    """Test API with a sample base64 image"""
    # Create a simple test image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    payload = {
        "question": "I have an error in my code, can you help?",
        "image": test_image_b64
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=35
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Image test passed")
            print(f"Answer: {data['answer'][:100]}...")
        else:
            print(f"❌ Image test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Image test error: {e}")

if __name__ == "__main__":
    import sys
    
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("TDS Virtual TA API Test Suite")
    print("=" * 50)
    
    # Run main tests
    test_api_endpoint(base_url)
    
    # Test with image if running locally
    if "localhost" in base_url:
        print("\nTesting with image attachment...")
        test_with_image() 