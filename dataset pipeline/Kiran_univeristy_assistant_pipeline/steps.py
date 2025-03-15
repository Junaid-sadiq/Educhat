import os
import sys
import yaml
import nltk
import time
import asyncio
import random

def count_tokens(text):
    """Simple token counter - estimates token count from text"""
    # A simple approximation: split by whitespace
    return len(text.split())

def chunk_by_token_length(text, max_token_length=1500):
    """Split text into chunks by token length"""
    tokens = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for token in tokens:
        if current_length + 1 > max_token_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [token]
            current_length = 1
        else:
            current_chunk.append(token)
            current_length += 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Load configuration
config_path = os.environ.get("CONFIG_PATH", "config.yaml")
with open(config_path, "r") as file:
    obj_conf = yaml.safe_load(file)

# Extract API configurations
try:
    # Check API section exists
    if "API" not in obj_conf:
        print(f"Warning: 'API' section not found in config. Using default values.")
        API_KEY_A = "dummy-key"
        API_KEY_B = "dummy-key"
        BASE_URL_A = "http://localhost:11434/v1"
        BASE_URL_B = "http://localhost:11434/v1"
        LOGICAL_MODEL_A = "phi4:latest"
        LOGICAL_MODEL_B = "phi4:latest"
        MODE_A = "api"
        MODE_B = "api"
    else:
        # Use the SMALL_MODEL and LARGE_MODEL names instead
        API_KEY_A = obj_conf["API"].get("SMALL_API_KEY", "dummy-key")
        API_KEY_B = obj_conf["API"].get("LARGE_API_KEY", "dummy-key")
        BASE_URL_A = obj_conf["API"].get("SMALL_BASE_URL", "http://localhost:11434/v1")
        BASE_URL_B = obj_conf["API"].get("LARGE_BASE_URL", "http://localhost:11434/v1")
        LOGICAL_MODEL_A = obj_conf["API"].get("SMALL_MODEL", "phi4:latest")
        LOGICAL_MODEL_B = obj_conf["API"].get("LARGE_MODEL", "phi4:latest")
        MODE_A = obj_conf["API"].get("SMALL_MODE", "api")
        MODE_B = obj_conf["API"].get("LARGE_MODE", "api")
        
    # Get concurrency limit
    CONCURRENCY_LIMIT = int(obj_conf.get("SYSTEM", {}).get("CONCURRENCY_LIMIT", 2))
    
    print(f"Config loaded successfully: Using models {LOGICAL_MODEL_A} and {LOGICAL_MODEL_B}")
except Exception as e:
    print(f"Error loading configuration: {e}")
    print(f"Using default values instead.")
    API_KEY_A = "dummy-key"
    API_KEY_B = "dummy-key"
    BASE_URL_A = "http://localhost:11434/v1"
    BASE_URL_B = "http://localhost:11434/v1"
    LOGICAL_MODEL_A = "phi4:latest"
    LOGICAL_MODEL_B = "phi4:latest"
    MODE_A = "api"
    MODE_B = "api"
    CONCURRENCY_LIMIT = 2

def make_id(length=10):
    """Generate a random ID string of specified length"""
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))

async def add_key(input_data, engine_wrapper, idx, output_list):
    """Generate a key for the input data and add it to the output list"""
    try:
        key = make_id()
        new_obj = {
            "key": key,
            "chunk_idx": idx,
            "input_data": input_data,
        }
        output_list.append(new_obj)
        return new_obj
    except Exception as e:
        print(f"Error in add_key: {e}")
        return None

def chunking_algorithm(text_file_path, max_token_length=1500):
    """Process a text file into chunks of specified maximum token length"""
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Download NLTK resources if they don't exist
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        # Split text into sentences
        sentences = nltk.sent_tokenize(text)
        
        # Combine sentences into chunks of specified maximum token length
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            if count_tokens(potential_chunk) <= max_token_length:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
                
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        # If file is too small, just use it as is
        if not chunks:
            chunks = [text]
            
        return chunks
    except Exception as e:
        print(f"Error processing {text_file_path}: {e}")
        return []