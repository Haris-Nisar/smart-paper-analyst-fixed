#!/usr/bin/env python3
"""
List Available OpenRouter Models
Fetches and displays available models from OpenRouter API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

print("🔍 Fetching available models from OpenRouter...")
print()

try:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }
    
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        exit(1)
    
    data = response.json()
    models = data.get("data", [])
    
    print(f"📊 Total models available: {len(models)}")
    print()
    
    # Filter for free and cheap models
    free_models = []
    cheap_models = []
    
    for model in models:
        model_id = model.get("id", "")
        pricing = model.get("pricing", {})
        prompt_price = float(pricing.get("prompt", 0))
        
        # Look for free and cheap models
        if prompt_price == 0:
            free_models.append(model)
        elif prompt_price < 0.0001:  # Less than $0.0001 per 1K tokens
            cheap_models.append(model)
    
    print("=" * 100)
    print("🆓 FREE MODELS (No cost)")
    print("=" * 100)
    for model in free_models[:10]:  # Show first 10
        model_id = model.get("id", "")
        print(f"  • {model_id}")
    
    print()
    print("=" * 100)
    print("💰 CHEAP MODELS (< $0.0001 per 1K tokens)")
    print("=" * 100)
    for model in cheap_models[:10]:  # Show first 10
        model_id = model.get("id", "")
        pricing = model.get("pricing", {})
        prompt_price = float(pricing.get("prompt", 0))
        print(f"  • {model_id:<50} ${prompt_price:.6f}/1K tokens")
    
    print()
    print("=" * 100)
    print("✨ RECOMMENDED MODELS")
    print("=" * 100)
    
    # Look for specific recommended models
    recommended = [
        "openai/gpt-4o-mini",  # Cheap and good
        "mistralai/mistral-nemo",  # Free tier friendly
        "meta-llama/llama-3.2-1b-instruct",  # Free
        "openai/gpt-3.5-turbo",  # Reliable
        "google/gemini-pro",  # Good option
        "anthropic/claude-3-5-haiku",  # Cheap Claude
    ]
    
    for model_id in recommended:
        for model in models:
            if model.get("id") == model_id:
                pricing = model.get("pricing", {})
                prompt_price = float(pricing.get("prompt", 0))
                completion_price = float(pricing.get("completion", 0))
                if prompt_price == 0:
                    cost_str = "FREE"
                else:
                    cost_str = f"${prompt_price:.6f}/1K"
                print(f"  • {model_id:<40} {cost_str}")
                break
    
    print()
    print("=" * 100)
    print("💡 SUGGESTED FIX")
    print("=" * 100)
    print()
    print("Add this to your .env file:")
    print("  OPENROUTER_MODEL=openai/gpt-4o-mini")
    print()
    print("Or use a free model:")
    print("  OPENROUTER_MODEL=meta-llama/llama-3.2-1b-instruct")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
