import json
import os
from pathlib import Path

# Define paths
base_dir = Path.cwd()  # Current working directory
raw_dataset_path = base_dir / "raw_dataset.json"
output_dir = base_dir / "augmentoolkit" / "data" / "raw_txt_input"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

print(f"Reading data from: {raw_dataset_path}")
print(f"Writing files to: {output_dir}")

# Read your JSON data
with open(raw_dataset_path, "r") as f:
    data = json.load(f)

# For each document, write it to a separate file
for i, doc in enumerate(data):
    try:
        # Clean filename
        if "file_name" in doc:
            filename = doc["file_name"].replace(".pdf", "").replace(" ", "_")
        else:
            filename = f"document_{i+1}"
        
        output_file = output_dir / f"{filename}.txt"
        
        # Write the content to a plain text file
        with open(output_file, "w", encoding="utf-8") as outfile:
            if "content" in doc:
                # Join all content chunks
                content = "\n\n".join(doc["content"]) if isinstance(doc["content"], list) else doc["content"]
                outfile.write(content)
            else:
                # If the document structure is different
                outfile.write(str(doc))
        
        print(f"Processed {filename}")
    except Exception as e:
        print(f"Error processing document {i}: {e}")

print(f"Processing complete. {len(data)} documents processed.")