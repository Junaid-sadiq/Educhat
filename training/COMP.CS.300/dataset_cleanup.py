import requests
import json
import os
import time
from tqdm import tqdm

# Ollama API details
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:14b"  # Adjust to match your installed model name

def summarize_with_rate_limit(text, max_length=150, delay=0.1):
    """Summarize text with rate limiting to prevent overwhelming Ollama."""
    time.sleep(delay)
    data = {
        "model": MODEL_NAME,
        "prompt": (
            "Summarize the following text in a clear and concise way, focusing on key concepts "
            "and maintaining technical accuracy. Remove any code examples or file paths.\n\n"
            f"Text: {text}\n\n"
            "Summary:"
        ),
        "max_tokens": max_length,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=data, stream=False)
        response.raise_for_status()
        json_response = response.json()
        summary = json_response.get("response")
        if summary:
            return summary.strip()
        else:
            print("Ollama API returned an unexpected response format.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama API call: {e}")
        return None

def clean_text(text):
    """Cleans the text by removing unwanted elements and standardizing format."""
    import re
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # Remove code block markers and their contents
    text = re.sub(r'```[\w\s]*\n[\s\S]*?```', '', text)
    
    # Remove file path comments
    text = re.sub(r'// filepath:.*\n', '', text)
    
    # Remove special characters but keep essential punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,?!():-]', ' ', text)
    
    # Handle Finnish/English mixed content (keep both languages)
    text = re.sub(r'[^a-zA-ZäöåÄÖÅ0-9\s.,?!():-]', ' ', text)
    
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove very short lines (likely noise)
    text = '\n'.join(line for line in text.split('\n') if len(line.strip()) > 5)
    
    return text

def process_json_content(data):
    """Process JSON data with better error handling and structure preservation."""
    if isinstance(data, list):
        return [process_json_content(item) for item in data]
    
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == "content" and isinstance(value, str):
                cleaned_text = clean_text(value)
                if len(cleaned_text) > 50:  # Only summarize longer content
                    summary = summarize_with_rate_limit(cleaned_text)
                    result[key] = summary if summary else cleaned_text
                else:
                    result[key] = cleaned_text
            elif key == "conversations":
                result[key] = process_json_content(value)
            else:
                result[key] = value
        return result
    
    return data

def process_with_progress(data):
    """Process data with progress bar."""
    if isinstance(data, list):
        return [process_json_content(item) for item in tqdm(data, desc="Processing items")]
    return process_json_content(data)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean and summarize JSON content using Ollama")
    parser.add_argument("--input", default="FINE_TUNING_SHAREGPT.JSON", 
                       help="Input JSON file path")
    parser.add_argument("--output", default="FINE_TUNING_SHAREGPT_REFINED.JSON",
                       help="Output JSON file path")
    parser.add_argument("--model", default="deepseek-r1:14b", 
                       help="Ollama model name")
    parser.add_argument("--delay", type=float, default=0.1,
                       help="Delay between API calls in seconds")
    args = parser.parse_args()

    global MODEL_NAME
    MODEL_NAME = args.model
    
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Processing {args.input}...")
        processed_data = process_with_progress(data)
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved processed data to {args.output}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
    except json.JSONDecodeError:
        print(f"Error: '{args.input}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()