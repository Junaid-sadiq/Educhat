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
    
    # Process each subdirectory specifically
    pdf_dir = os.path.join(root_dir, "pdf")
    html_dir = os.path.join(root_dir, "html")
    
    # Process PDFs
    if os.path.exists(pdf_dir):
        print(f"Found PDF directory: {pdf_dir}")
        for dirpath, dirnames, files in os.walk(pdf_dir):
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            print(f"Found {len(pdf_files)} PDF files in {dirpath}")
            
            for file in tqdm(pdf_files, desc=f"Processing PDFs in {dirpath}"):
                file_path = os.path.join(dirpath, file)
                try:
                    print(f"Processing PDF: {file_path}")
                    text = extract_text_from_pdf(file_path)
                    
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
    else:
        print(f"PDF directory not found: {pdf_dir}")
    
    # Process HTMLs
    if os.path.exists(html_dir):
        print(f"Found HTML directory: {html_dir}")
        for dirpath, dirnames, files in os.walk(html_dir):
            html_files = [f for f in files if f.lower().endswith(('.html', '.htm'))]
            print(f"Found {len(html_files)} HTML files in {dirpath}")
            
            for file in tqdm(html_files, desc=f"Processing HTMLs in {dirpath}"):
                file_path = os.path.join(dirpath, file)
                try:
                    print(f"Processing HTML: {file_path}")
                    text = extract_text_from_html(file_path)
                    
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
    else:
        print(f"HTML directory not found: {html_dir}")
    
    return processed_files, error_log

if __name__ == '__main__':
    # Current directory approach - better for your specific setup
    current_dir = os.path.dirname(os.path.abspath(__file__))  # COMP.CS.200 directory
    
    # Output directory inside COMP.CS.200
    output_directory = os.path.join(current_dir, "raw_txt_input")
    
    print(f"Current directory: {current_dir}")
    print(f"Output directory: {output_directory}")
    
    # Process files and save directly as text
    processed_count, errors = process_files_to_text(current_dir, output_directory)
    
    print(f"Processed {processed_count} files to text format.")
    print(f"Encountered {len(errors)} errors.")
    
    # Optionally save error log
    if errors:
        import json
        with open(os.path.join(current_dir, "extraction_errors.json"), "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=4, ensure_ascii=False)
        print("Error log saved to extraction_errors.json")