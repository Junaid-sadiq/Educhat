import requests
import time

# Ollama API details
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "deepseek-r1:14b"  # Default model to test

def test_ollama_api(prompt="Why is the sky blue?", model=DEFAULT_MODEL, delay=0.1):
    """Test Ollama API with a simple prompt"""
    time.sleep(delay)  # Rate limiting
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print(f"Sending test prompt to Ollama ({model})...")
        response = requests.post(OLLAMA_API_URL, json=data)
        response.raise_for_status()
        
        json_response = response.json()
        return json_response.get("response", "No response in API output")
        
    except requests.exceptions.RequestException as e:
        return f"API call failed: {str(e)}"
    except json.JSONDecodeError:
        return "Received invalid JSON response"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ollama API connection")
    parser.add_argument("--model", default=DEFAULT_MODEL, 
                       help="Model name to test")
    parser.add_argument("--prompt", default="Explain quantum computing in simple terms",
                       help="Test prompt to send")
    args = parser.parse_args()

    result = test_ollama_api(prompt=args.prompt, model=args.model)
    
    print("\nTest results:")
    print("=" * 40)
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt}")
    print("-" * 40)
    print("Response:")
    print(result)
    print("=" * 40)