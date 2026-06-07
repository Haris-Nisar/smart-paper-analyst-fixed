#!/usr/bin/env python3
"""
OpenRouter API Connection Test
Tests the OpenRouter API configuration and connectivity
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

print("=" * 80)
print("🧪 OpenRouter API Connection Test")
print("=" * 80)

# 1. Check configuration
print("\n1️⃣  Configuration Check")
print("-" * 80)

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not set in .env")
    sys.exit(1)

api_key_display = OPENROUTER_API_KEY[:20] + "..." if len(OPENROUTER_API_KEY) > 20 else "***"
print(f"✅ API Key: {api_key_display}")
print(f"✅ Model: {OPENROUTER_MODEL}")
print(f"✅ Base URL: {OPENROUTER_BASE_URL}")

# 2. Prepare request
print("\n2️⃣  Request Preparation")
print("-" * 80)

url = f"{OPENROUTER_BASE_URL}/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://smart-paper-analyst.app",
    "X-OpenRouter-Title": "Smart Academic Paper Analyst",
}
payload = {
    "model": OPENROUTER_MODEL,
    "messages": [
        {"role": "user", "content": "Respond with exactly 'test successful' and nothing else."}
    ],
    "max_tokens": 50,
    "temperature": 0.3,
}

print(f"URL: {url}")
print(f"Headers: {json.dumps({k: v if k != 'Authorization' else '***' for k, v in headers.items()}, indent=2)}")
print(f"Payload:\n{json.dumps(payload, indent=2)}")

# 3. Make request
print("\n3️⃣  Sending Request")
print("-" * 80)

try:
    print(f"📤 POST {url}")
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    print(f"📬 Status Code: {response.status_code}")
    print(f"📬 Content-Type: {response.headers.get('Content-Type')}")
except Exception as e:
    print(f"❌ Request failed: {e}")
    sys.exit(1)

# 4. Parse response
print("\n4️⃣  Response Parsing")
print("-" * 80)

try:
    data = response.json()
    print(f"✅ Valid JSON response")
    print(f"Response keys: {list(data.keys())}")
except Exception as e:
    print(f"❌ Cannot parse response as JSON: {e}")
    print(f"Response text:\n{response.text}")
    sys.exit(1)

# 5. Check status code
print("\n5️⃣  Status Code Handling")
print("-" * 80)

if response.status_code == 200:
    print("✅ Status 200 OK")
elif response.status_code == 401:
    print("❌ Status 401 Unauthorized - Check your API key")
    if "error" in data:
        print(f"   Error: {data['error'].get('message', 'Unknown')}")
    sys.exit(1)
elif response.status_code == 404:
    print("❌ Status 404 Not Found")
    if "error" in data:
        print(f"   Error: {data['error'].get('message', 'Unknown')}")
    print(f"   Check that model '{OPENROUTER_MODEL}' exists")
    print(f"   Available models: https://openrouter.ai/models")
    sys.exit(1)
elif response.status_code == 429:
    print("❌ Status 429 Rate Limited")
    sys.exit(1)
elif response.status_code >= 500:
    print(f"❌ Status {response.status_code} Server Error")
    sys.exit(1)
else:
    print(f"⚠️  Status {response.status_code}")

# 6. Check for error in response
print("\n6️⃣  Error Handling")
print("-" * 80)

if "error" in data:
    error = data["error"]
    print(f"❌ API Error: {error.get('message', 'Unknown error')}")
    if "metadata" in error:
        print(f"   Metadata: {error['metadata']}")
    sys.exit(1)
else:
    print("✅ No error in response")

# 7. Validate response structure
print("\n7️⃣  Response Structure")
print("-" * 80)

required_fields = ["choices", "model", "usage"]
for field in required_fields:
    if field in data:
        print(f"✅ {field}: present")
    else:
        print(f"❌ {field}: missing")

if "choices" in data:
    choices = data["choices"]
    print(f"   Choices count: {len(choices)}")
    if len(choices) > 0:
        choice = choices[0]
        print(f"   Choice 0 keys: {list(choice.keys())}")
        if "message" in choice:
            message = choice["message"]
            print(f"      Message keys: {list(message.keys())}")
            if "content" in message:
                content = message["content"]
                print(f"      Content: {content[:100]}...")

# 8. Extract response content
print("\n8️⃣  Response Content")
print("-" * 80)

try:
    choices = data.get("choices", [])
    if not choices:
        print("❌ Empty choices array")
        sys.exit(1)
    
    content = choices[0].get("message", {}).get("content", "").strip()
    if not content:
        print("❌ Empty response content")
        sys.exit(1)
    
    print(f"✅ Content received ({len(content)} chars):")
    print(f"   {content}")
except Exception as e:
    print(f"❌ Cannot extract content: {e}")
    sys.exit(1)

# 9. Usage statistics
print("\n9️⃣  Usage Statistics")
print("-" * 80)

if "usage" in data:
    usage = data["usage"]
    print(f"✅ Prompt tokens: {usage.get('prompt_tokens', '?')}")
    print(f"✅ Completion tokens: {usage.get('completion_tokens', '?')}")
    print(f"✅ Total tokens: {usage.get('total_tokens', '?')}")
    if "cost" in usage:
        print(f"✅ Cost: ${usage.get('cost', '?')}")

# Final result
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\n✨ OpenRouter API is working correctly.")
print("   Your chatbot should now be able to generate responses.")
print("\nNext: Run `streamlit run app.py` to start the application.")
print("=" * 80)
