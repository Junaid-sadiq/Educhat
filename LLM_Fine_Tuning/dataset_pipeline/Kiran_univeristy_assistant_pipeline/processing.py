import requests
import os
import json
import sys
import logging
import yaml
import re
import time
import glob
from tqdm import tqdm
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AlpacaGenerator")

# Load configuration
config_path = os.environ.get("CONFIG_PATH", "config.yaml")
try:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
    logger.error(f"Error loading config from {config_path}: {e}")
    config = {}

# Config parsing
INPUT = config.get("PATH", {}).get("INPUT", "./raw_txt_input")
OUTPUT = config.get("PATH", {}).get("OUTPUT", "./output")
MODEL = config.get("API", {}).get("LARGE_MODEL", "phi4:latest")

# Ensure output directory exists
os.makedirs(OUTPUT, exist_ok=True)

def find_text_files(input_dir):
    """Find all text files in the input directory"""
    text_files = []
    # Try direct .txt files
    text_files.extend(glob.glob(os.path.join(input_dir, "*.txt")))
    # Try recursive search
    text_files.extend(glob.glob(os.path.join(input_dir, "**", "*.txt"), recursive=True))
    # Add markdown files too
    text_files.extend(glob.glob(os.path.join(input_dir, "*.md")))
    text_files.extend(glob.glob(os.path.join(input_dir, "**", "*.md"), recursive=True))
    
    return sorted(set(text_files))  # Remove duplicates and sort

def ollama_generate(prompt, model=MODEL):
    """Generate text using Ollama API directly"""
    try:
        print(f"Sending request to Ollama...")
        response = requests.post(
            "http://localhost:11434/v1/completions", 
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("choices", [{}])[0].get("text", "")
            word_count = len(response_text.split())
            print(f"Received response ({word_count} words)")
            return response_text
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return f"Error: API returned status code {response.status_code}"
    except Exception as e:
        logger.error(f"Exception calling Ollama: {e}")
        return f"Error: {str(e)}"

def clean_question(question):
    """Clean up question to ensure it's concise and focused"""
    # Extract just the first question if multiple are generated
    match = re.search(r'^([^.!?]+[.!?])', question.strip())
    if match:
        return match.group(1).strip()
    
    # If no punctuation found, just return the first 25 words max
    words = question.split()
    if len(words) > 25:
        return " ".join(words[:25]) + "?"
        
    return question.strip()

def generate_question(content):
    """Generate a focused, concise question about the content"""
    prompt = f"""You are a university student. Generate a concise, focused question about this educational material:

{content[:1500]}

IMPORTANT REQUIREMENTS:
1. Return ONLY the question itself - no explanations, no commentary
2. Question should be single sentence and direct
3. Focus on conceptual understanding, not just facts
4. Maximum 15 words
5. Do not use quotation marks around your question

Example good questions:
- How do abstract data types help separate interface from implementation?
- What are the advantages of using linked lists over arrays?
- Why is encapsulation important for data structure design?
"""
    
    question = ollama_generate(prompt)
    # Clean up the question to ensure it's concise
    return clean_question(question)

def generate_answer(question, content):
    """Generate a helpful, concise answer to the question"""
    prompt = f"""You are Kiran, an AI assistant for Tampere University students. A student has asked this question:

{question}

Use this educational content to provide a helpful answer:

{content[:2000]}

IMPORTANT REQUIREMENTS:
1. Start with a brief greeting
2. Be clear and direct - aim for EXACTLY 200-250 words total
3. Use markdown formatting for structure (headers, bullet points, bold for key terms)
4. Include 1 specific example to illustrate the concept
5. End with a friendly closing like "Hope this helps!" or "Let me know if you have any questions!"
6. STRICT WORD COUNT: 200-250 words, no longer

Your answer should be helpful, accurate, and concise.
"""
    
    return ollama_generate(prompt)

def process_file(file_path, pairs_per_file=2):
    """Process a single file and return Alpaca data pairs"""
    file_name = os.path.basename(file_path)
    logger.info(f"Processing file: {file_name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        file_alpaca_data = []
        
        for i in range(pairs_per_file):
            # Generate question
            question = generate_question(content)
            logger.info(f"  Generated Q{i+1}: {question}")
            
            # Generate answer
            answer = generate_answer(question, content)
            answer_length = len(answer.split())
            logger.info(f"  Generated A{i+1}: {answer_length} words")
            
            # Add to Alpaca data
            file_alpaca_data.append({
                "instruction": "You are Kiran, an AI assistant from Tampere University. Answer the following question from a student:",
                "input": question,
                "output": answer
            })
        
        return file_alpaca_data
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []

def main():
    start_time = time.time()
    logger.info("Starting Alpaca dataset generation for all input files")
    
    # Find all text files
    text_files = find_text_files(INPUT)
    if not text_files:
        logger.error(f"No text files found in {INPUT}")
        return
    
    logger.info(f"Found {len(text_files)} text files")
    
    # Process each file with progress bar
    all_alpaca_data = []
    pairs_per_file = 2
    total_pairs = len(text_files) * pairs_per_file
    
    print(f"\nProcessing {len(text_files)} files ({total_pairs} total QA pairs)...")
    
    # Use tqdm for progress tracking
    for file_path in tqdm(text_files, desc="Files", unit="file"):
        file_data = process_file(file_path, pairs_per_file)
        all_alpaca_data.extend(file_data)
        
        # Calculate progress
        processed_pairs = len(all_alpaca_data)
        elapsed = time.time() - start_time
        pairs_per_second = processed_pairs / elapsed if elapsed > 0 else 0
        
        # Estimated time remaining
        remaining_pairs = total_pairs - processed_pairs
        estimated_seconds = remaining_pairs / pairs_per_second if pairs_per_second > 0 else 0
        
        print(f"\rProcessed: {processed_pairs}/{total_pairs} QA pairs | "
              f"Est. remaining: {str(timedelta(seconds=int(estimated_seconds)))}")
    
    # Save ONLY Alpaca format
    alpaca_path = os.path.join(OUTPUT, "kiran_alpaca_dataset_for_comp200.json")
    with open(alpaca_path, "w", encoding="utf-8") as f:
        json.dump(all_alpaca_data, f, ensure_ascii=False, indent=2)
    
    # Log completion
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    logger.info(f"Completed in {minutes}m {seconds}s")
    logger.info(f"Generated {len(all_alpaca_data)} total QA pairs from {len(text_files)} files")
    logger.info(f"Saved Alpaca dataset to {alpaca_path}")

if __name__ == "__main__":
    main()