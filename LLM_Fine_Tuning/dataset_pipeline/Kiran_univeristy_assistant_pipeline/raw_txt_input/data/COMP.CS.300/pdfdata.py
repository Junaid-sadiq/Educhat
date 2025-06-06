import json

def remove_keys(data, keys_to_remove=("instruction", "output")):
    """
    Recursively remove the specified keys from dictionaries.
    Assumes that the top-level JSON is either a list or a dict.
    """
    if isinstance(data, list):
        return [remove_keys(item, keys_to_remove) for item in data]
    elif isinstance(data, dict):
        # Remove each key in the keys_to_remove list if present.
        for key in keys_to_remove:
            data.pop(key, None)
        # Recursively process all values.
        for key, value in data.items():
            data[key] = remove_keys(value, keys_to_remove)
        return data
    else:
        return data

def main():
    input_file = "./fine_tuning_dataset.json"   # Adjust the path as needed.
    output_file = "./fine_tuning_dataset_cleaned.json"  # Adjust the path as needed.

    # Load the JSON dataset.
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Remove all "instruction" and "output" key/value pairs.
    cleaned_data = remove_keys(data)
    
    # Save the cleaned dataset.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned dataset written to {output_file}")

if __name__ == "__main__":
    main()