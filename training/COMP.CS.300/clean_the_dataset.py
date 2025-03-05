import json
import re
import os
from datasets import Dataset  # pip install datasets
import pandas as pd

def remove_think_blocks(text):
    """
    Remove all text between <think> and </think> tags.
    """
    # Remove all <think>...</think> blocks using DOTALL flag.
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

def process_item(item):
    """
    Recursively process dictionary or list items.
    If the key is 'content' and its value is a string, remove any <think> blocks.
    """
    if isinstance(item, dict):
        new_item = {}
        for key, value in item.items():
            if key == "content" and isinstance(value, str):
                new_item[key] = remove_think_blocks(value)
            else:
                new_item[key] = process_item(value)
        return new_item
    elif isinstance(item, list):
        return [process_item(elem) for elem in item]
    else:
        return item

def main():
    # File paths (adjust as necessary)
    input_file = "./FINE_TUNING_SHAREGPT_REFINED.json"
    output_file = "./FINE_TUNING_SHAREGPT_CLEANED.json"
    
    # Load the JSON dataset
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Process the data to remove <think> blocks
    cleaned_data = process_item(data)
    
    # Save the cleaned dataset
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned dataset saved to {output_file}")
    
    # Arrange like an SQL table using HuggingFace Datasets
    # Assuming the top-level is a list of examples.
    hf_dataset = Dataset.from_list(cleaned_data)
    df = hf_dataset.to_pandas()
    
    # For SQL-like display, you might want to print selected columns.
    # For example, if your dataset has 'system' and 'conversations', you can explode them
    # or simply display the first few rows.
    print("\nSQL-like table view (first 5 records):")
    print(df.head())

if __name__ == "__main__":
    main()