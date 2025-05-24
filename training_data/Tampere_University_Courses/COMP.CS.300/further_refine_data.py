import json
import os


def restructure_dataset(input_file, output_file):
    # Read the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found")
        return 0
    except json.JSONDecodeError:
        print(f"Error: {input_file} contains invalid JSON")
        return 0
    
    # Create the new structure
    new_data = []
    
    for item in data:
        # Skip empty items or those without proper structure
        if not isinstance(item, dict) or "system" not in item or "conversations" not in item:
            continue
        
        # Check if conversations array has at least host and assistant
        conversations = item.get("conversations", [])
        if len(conversations) < 2:
            continue
        
        # Find host and assistant messages
        host_content = None
        assistant_content = None
        
        for conv in conversations:
            if conv.get("role") == "host":
                host_content = conv.get("content", "")
            elif conv.get("role") == "assistant":
                assistant_content = conv.get("content", "")
        
        # Skip if missing required content
        if not host_content or not assistant_content:
            continue
        
        # Create the new format
        new_item = {
            "messages": [
                {"role": "system", "content": item.get("system", "")},
                {"role": "user", "content": f"Please summarize the following text:\n\n{host_content}"},
                {"role": "assistant", "content": assistant_content}
            ]
        }
        
        new_data.append(new_item)
    
    # Write the output file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 0
    
    return len(new_data)

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "./FINE_TUNING_SHAREGPT_CLEANED.json")
output_file = os.path.join(current_dir, "FINE_TUNING_UNSLOTH_READY.json")
count = restructure_dataset(input_file, output_file)
print(f"Successfully restructured {count} examples into Unsloth format")