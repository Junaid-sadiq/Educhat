import os
import re
import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path

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

def save_text_file(filename, content, output_dir):
    """Save extracted text to a plain text file."""
    # Clean filename for use as a file
    clean_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    clean_filename = clean_filename.replace('.pdf', '').replace('.html', '').replace('.htm', '')
    clean_filename = clean_filename + '.txt'
    
    output_path = os.path.join(output_dir, clean_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path

def process_files_to_text(root_dir, output_dir):
    """Process all PDFs and HTML files in the directory and save as text files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    processed_files = 0
    error_log = []
    
    # Print directory content to debug
    print(f"Looking for files in: {root_dir}")
    print(f"Directory exists: {os.path.exists(root_dir)}")
    if os.path.exists(root_dir):
        print("Files in directory:")
        for item in os.listdir(root_dir):
            print(f"  - {item}")
    
    for dirpath, dirnames, files in os.walk(root_dir):
        print(f"Checking directory: {dirpath}")
        print(f"Found {len(files)} files")
        
        for file in tqdm(files, desc=f"Processing files in {dirpath}"):
            file_lower = file.lower()
            file_path = os.path.join(dirpath, file)
            print(f"Checking file: {file_path}")
            
            try:
                if file_lower.endswith('.pdf'):
                    print(f"Processing PDF: {file_path}")
                    text = extract_text_from_pdf(file_path)
                    source_type = "pdf"
                elif file_lower.endswith(('.html', '.htm')):
                    print(f"Processing HTML: {file_path}")
                    text = extract_text_from_html(file_path)
                    source_type = "html"
                else:
                    print(f"Skipping non-PDF/HTML file: {file_path}")
                    continue

                if not text:
                    error_log.append({
                        "file": file_path,
                        "error": "Empty text extracted."
                    })
                    print(f"Empty text extracted from {file_path}")
                    continue
                
                # Save as text file
                output_path = save_text_file(file, text, output_dir)
                print(f"Saved: {output_path}")
                processed_files += 1
                        
            except Exception as e:
                error_log.append({
                    "file": file_path,
                    "error": str(e)
                })
                print(f"Error processing {file_path}: {e}")
    
    return processed_files, error_log

if __name__ == '__main__':
    # Use absolute paths
    base_dir = Path.home() / "Educhat"
    
    # Source directory containing PDFs and HTMLs
    source_directory = base_dir / "training" / "COMP.CS.300"
    
    # AugmenToolkit output directory for text files
    output_directory = base_dir / "augmentoolkit" / "data" / "raw_txt_input"
    
    print(f"Base directory: {base_dir}")
    print(f"Source directory: {source_directory}")
    print(f"Output directory: {output_directory}")
    
    # Process files and save directly as text
    processed_count, errors = process_files_to_text(source_directory, output_directory)
    
    print(f"Processed {processed_count} files to text format.")
    print(f"Encountered {len(errors)} errors.")
    
    # Optionally save error log
    if errors:
        import json
        with open(base_dir / "extraction_errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=4, ensure_ascii=False)
        print("Error log saved to extraction_errors.json")
    
    # If no files were processed, check raw_dataset.json
    if processed_count == 0:
        raw_json_path = base_dir / "raw_dataset.json"
        if os.path.exists(raw_json_path):
            print(f"\nFound raw_dataset.json. You can use text_processing.py to convert this to text files.")