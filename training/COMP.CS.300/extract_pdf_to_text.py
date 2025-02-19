import os
import json
import re
import fitz  
from tqdm import tqdm  
from bs4 import BeautifulSoup  

def clean_text(text):
    """Clean text by removing extra whitespace, newlines, and artifacts."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF file using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(pdf_path)
        raw_text = "\n\n".join(page.get_text("text") for page in doc if page.get_text("text"))
        return clean_text(raw_text)
    except Exception as e:
        raise Exception(f"Error extracting PDF {pdf_path}: {str(e)}")

def extract_text_from_html(html_path):
    """Extract text from a given HTML file using BeautifulSoup."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        return clean_text(soup.get_text())
    except Exception as e:
        raise Exception(f"Error extracting HTML {html_path}: {str(e)}")

def process_files(root_dir):
    """Process all PDFs and HTML files in the directory and format in Alpaca-style instruct format."""
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
                    error_log.append({
                        "file": file_path,
                        "error": "Empty text extracted."
                    })
                    continue

                # Split text into chunks based on double newlines.
                chunks = text.split("\n\n")
                for chunk in chunks:
                    chunk_clean = clean_text(chunk)
                    if len(chunk_clean) > 50:  # Ignore very short chunks
                        dataset.append({
                            "instruction": "Summarize the following text:",
                            "input": chunk_clean,
                            "output": "Summary will go here (auto-generate or manually edit)."
                        })
            except Exception as e:
                error_log.append({
                    "file": file_path,
                    "error": str(e)
                })
                print(f"Error processing {file_path}: {e}")
    return dataset, error_log

# Stub for local LLM integration – replace with your actual call if needed
def run_local_llm(input_text):
    """Call your local LLM to generate a summary; modify this function accordingly."""
    return "Auto-generated summary from local LLM."

def generate_outputs_with_local_llm(dataset):
    """Iterate over the dataset and update the output field using the local LLM."""
    for example in dataset:
        if "auto-generate" in example["output"]:
            generated = run_local_llm(example["input"])
            example["output"] = generated.strip()
    return dataset

def save_to_json(data, output_file):
    """Save data to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {output_file}")

if __name__ == '__main__':
    root_directory = r"./training/COMP.CS.300/"  # This root directory contains PDFs and HTMLs
    dataset_output_file = "fine_tuning_dataset.json"
    error_log_file = "extraction_errors.json"
    
    dataset, error_log = process_files(root_directory)
    
    # Uncomment the next line if you want to auto-generate outputs with the local LLM.
    # dataset = generate_outputs_with_local_llm(dataset)
    
    save_to_json(dataset, dataset_output_file)
    save_to_json(error_log, error_log_file)