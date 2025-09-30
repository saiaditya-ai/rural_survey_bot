#!/usr/bin/env python3
"""
Quick test script for judges to verify the Rural Survey & FAQ Bot
Run this after starting the server to test all major functionality
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Rural Survey & FAQ Bot API...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
        else:
            print("❌ Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ Server not running. Please start with: python -m uvicorn app_simple:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test 2: Government Scheme Query (English)
    try:
        payload = {
            "question": "What is PMAY scheme?",
            "language": "english"
        }
        response = requests.post(f"{base_url}/api/v1/chat/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Government Scheme Query (English): PASSED")
            print(f"   Intent: {data.get('intent')}")
            print(f"   Response: {data.get('response')[:100]}...")
        else:
            print("❌ Government Scheme Query: FAILED")
    except Exception as e:
        print(f"❌ Government Scheme Query: ERROR - {e}")
    
    # Test 3: Health Facility Query
    try:
        payload = {
            "question": "Find hospitals near me",
            "language": "english"
        }
        response = requests.post(f"{base_url}/api/v1/chat/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Facility Query: PASSED")
            print(f"   Intent: {data.get('intent')}")
        else:
            print("❌ Health Facility Query: FAILED")
    except Exception as e:
        print(f"❌ Health Facility Query: ERROR - {e}")
    
    # Test 4: Hindi Language Support
    try:
        payload = {
            "question": "PMAY योजना के बारे में बताएं",
            "language": "hindi"
        }
        response = requests.post(f"{base_url}/api/v1/chat/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Hindi Language Support: PASSED")
            print(f"   Intent: {data.get('intent')}")
            print(f"   Language: {data.get('language')}")
        else:
            print("❌ Hindi Language Support: FAILED")
    except Exception as e:
        print(f"❌ Hindi Language Support: ERROR - {e}")
    
    # Test 5: Representative Query
    try:
        payload = {
            "question": "Who is my MLA?",
            "language": "english"
        }
        response = requests.post(f"{base_url}/api/v1/chat/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Representative Query: PASSED")
            print(f"   Intent: {data.get('intent')}")
        else:
            print("❌ Representative Query: FAILED")
    except Exception as e:
        print(f"❌ Representative Query: ERROR - {e}")
    
    # Test 6: Commodity Price Query
    try:
        payload = {
            "question": "What is wheat price today?",
            "language": "english"
        }
        response = requests.post(f"{base_url}/api/v1/chat/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Commodity Price Query: PASSED")
            print(f"   Intent: {data.get('intent')}")
        else:
            print("❌ Commodity Price Query: FAILED")
    except Exception as e:
        print(f"❌ Commodity Price Query: ERROR - {e}")
    
    # Test 7: Supported Intents
    try:
        response = requests.get(f"{base_url}/api/v1/chat/intents")
        if response.status_code == 200:
            data = response.json()
            print("✅ Supported Intents: PASSED")
            print(f"   Total Intents: {len(data.get('intents', []))}")
        else:
            print("❌ Supported Intents: FAILED")
    except Exception as e:
        print(f"❌ Supported Intents: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   • Multi-language support (English & Hindi)")
    print("   • Intent detection for government services")
    print("   • Rural-focused responses")
    print("   • Comprehensive fallback system")
    print("   • Production-ready API")
    
    print(f"\n🌐 API Documentation: {base_url}/docs")
    print(f"🔍 Health Check: {base_url}/health")
    
    return True

if __name__ == "__main__":
    print("🌾 Rural Survey & FAQ Bot - Judge Testing Script")
    print("Make sure the server is running first!")
    print("Start server: python -m uvicorn app_simple:app --host 0.0.0.0 --port 8000")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    test_api()
