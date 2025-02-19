import os
import json
import re
import fitz  
from tqdm import tqdm  
from bs4 import BeautifulSoup
import requests
import time

# Add Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:14b"

def generate_response_with_ollama(text, max_length=250, delay=0.1):
    """Generate a response using local Ollama model."""
    time.sleep(delay)  # Rate limiting
    data = {
        "model": MODEL_NAME,
        "prompt": (
            "You are an AI teaching assistant. Based on the following lecture content, "
            "provide a comprehensive but concise summary of the key topics and concepts covered.\n\n"
            f"Lecture content: {text}\n\n"
            "Summary:"
        ),
        "max_tokens": max_length,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=data, stream=False)
        response.raise_for_status()
        json_response = response.json()
        generated_response = json_response.get("response", "").strip()
        return generated_response if generated_response else None
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

# ... existing clean_text, extract_text_from_pdf, and extract_text_from_html functions ...

def convert_to_sharegpt_format(extracted_text):
    """Convert extracted lecture text into ShareGPT format with generated response."""
    # Clean the extracted text first
    cleaned_text = clean_text(extracted_text)
    
    # Generate response using Ollama
    generated_response = generate_response_with_ollama(cleaned_text)
    
    return {
        "system": "Hello! I am Kiran, an AI assistant from Tampere University, dedicated to providing you with accurate and insightful assistance. My goal is to help you understand concepts, summarize lectures, and answer questions effectively.",
        "conversations": [
            {
                "role": "host",
                "content": cleaned_text
            },
            {
                "role": "user",
                "content": "Can you summarize the key topics covered in this lecture?"
            },
            {
                "role": "assistant",
                "content": generated_response if generated_response else "Unable to generate summary for this lecture."
            }
        ]
    }

def process_files(root_dir):
    """Process all PDFs and HTML files and convert them into ShareGPT format."""
    dataset = []
    error_log = []
    
    for dirpath, _, files in os.walk(root_dir):
        for file in tqdm(files, desc="Processing files"):
            file_lower = file.lower()
            file_path = os.path.join(dirpath, file)
            try:
                if file_lower.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                elif file_lower.endswith(('.html', '.htm')):
                    text = extract_text_from_html(file_path)
                else:
                    continue

                if not text:
                    error_log.append({"file": file_path, "error": "Empty text extracted."})
                    continue

                print(f"\nProcessing: {file_path}")
                sharegpt_entry = convert_to_sharegpt_format(text)
                dataset.append(sharegpt_entry)

            except Exception as e:
                error_log.append({"file": file_path, "error": str(e)})
                print(f"Error processing {file_path}: {e}")

    return dataset, error_log

# ... rest of the existing code ...