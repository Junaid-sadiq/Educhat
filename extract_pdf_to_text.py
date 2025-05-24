import os
import re
import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extract_logs.log"),
        logging.StreamHandler()
    ]
)


def clean_text(text):
    """Clean text by removing extra whitespace, newlines, and artifacts."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF file using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(pdf_path)
        raw_text = "\n\n".join(page.get_text("text")
                               for page in doc if page.get_text("text"))
        return clean_text(raw_text)
    except Exception as e:
        logging.error(f"Error extracting PDF {pdf_path}: {str(e)}")
        raise Exception(f"Error extracting PDF {pdf_path}: {str(e)}")


def extract_text_from_html(html_path):
    """Extract text from a given HTML file using BeautifulSoup."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        return clean_text(soup.get_text())
    except Exception as e:
        logging.error(f"Error extracting HTML {html_path}: {str(e)}")
        raise Exception(f"Error extracting HTML {html_path}: {str(e)}")


def save_text_file(filename, content, output_dir, source_subdir=None):
    """Save extracted text to a plain text file, preserving source directory structure."""
    # Clean filename for use as a file
    clean_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    clean_filename = clean_filename.replace(
        '.pdf', '').replace('.html', '').replace('.htm', '')
    clean_filename = clean_filename + '.txt'

    # If we have subdir information, create that structure in the output
    if source_subdir:
        subdir_path = os.path.join(output_dir, source_subdir)
        os.makedirs(subdir_path, exist_ok=True)
        output_path = os.path.join(subdir_path, clean_filename)
    else:
        output_path = os.path.join(output_dir, clean_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path


def process_files_to_text(root_dir, output_dir):
    """Process all PDFs and HTML files in the directory and save as text files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    processed_files = 0
    skipped_files = 0
    error_log = []
    total_files = 0
    
    # Count total files first for better progress tracking
    for dirpath, dirnames, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.pdf', '.html', '.htm')):
                total_files += 1
    
    logging.info(f"Found a total of {total_files} PDF/HTML files to process")
    
    # Now process the files
    with tqdm(total=total_files, desc="Overall progress") as pbar:
        for dirpath, dirnames, files in os.walk(root_dir):
            # Get the relative path from the root_dir to preserve directory structure
            rel_path = os.path.relpath(dirpath, root_dir) if dirpath != root_dir else ""
            if rel_path == ".":
                rel_path = ""
                
            pdf_html_files = [f for f in files if f.lower().endswith(('.pdf', '.html', '.htm'))]
            
            if not pdf_html_files:
                continue
                
            logging.info(f"Processing {len(pdf_html_files)} files in: {dirpath}")
            
            for file in pdf_html_files:
                file_lower = file.lower()
                file_path = os.path.join(dirpath, file)
                
                # Check if output file already exists
                clean_filename = re.sub(r'[^\w\-_\.]', '_', file)
                clean_filename = clean_filename.replace('.pdf', '').replace('.html', '').replace('.htm', '') + '.txt'
                
                # Determine output path for this file
                if rel_path:
                    output_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_file_path = os.path.join(output_subdir, clean_filename)
                else:
                    output_file_path = os.path.join(output_dir, clean_filename)
                
                # Skip if file already exists
                if os.path.exists(output_file_path):
                    logging.info(f"Skipping already processed file: {file_path}")
                    skipped_files += 1
                    pbar.update(1)
                    continue
                
                try:
                    if file_lower.endswith('.pdf'):
                        text = extract_text_from_pdf(file_path)
                    elif file_lower.endswith(('.html', '.htm')):
                        text = extract_text_from_html(file_path)
                    else:
                        pbar.update(1)
                        continue

                    # Save as text file, preserving directory structure
                    output_path = save_text_file(file, text, output_dir, rel_path if rel_path else None)
                    logging.info(f"Saved: {output_path}")
                    processed_files += 1
                            
                except Exception as e:
                    error_log.append({
                        "file": file_path,
                        "error": str(e)
                    })
                    logging.error(f"Error processing {file_path}: {e}")
                
                pbar.update(1)
    
    # Return statement should be HERE, aligned with the function definition 
    # (not inside any loops)
    return processed_files, skipped_files, error_log


if __name__ == '__main__':
    # Get the base directory - this is where the script is running from
    current_dir = Path(__file__).parent.absolute()

    # Source directory containing PDFs and HTMLs
    source_directory = os.path.join(current_dir, "training_data")

    # Output directory for text files
    output_directory = os.path.join(current_dir, "LLM_Fine_Tuning", "dataset_pipeline",
                                   "Kiran_univeristy_assistant_pipeline", "raw_txt_input")

    logging.info(f"Current directory: {current_dir}")
    logging.info(f"Source directory: {source_directory}")
    logging.info(f"Output directory: {output_directory}")

    # Verify the source directory structure
    if os.path.exists(source_directory):
        logging.info("Main subdirectories in source:")
        for item in os.listdir(source_directory):
            item_path = os.path.join(source_directory, item)
            if os.path.isdir(item_path):
                logging.info(f"  - {item}/")
                sub_items = os.listdir(item_path)
                logging.info(f"    Contains {len(sub_items)} items")
    else:
        logging.error(f"Source directory does not exist: {source_directory}")
        exit(1)

    # Process files and save directly as text
    processed_count, skipped_count, errors = process_files_to_text(
        source_directory, output_directory)

    logging.info(f"Processed {processed_count} new files to text format.")
    logging.info(f"Skipped {skipped_count} already processed files.")
    logging.info(f"Encountered {len(errors)} errors.")
    # Save error log
    import json
    error_log_path = os.path.join(current_dir, "extraction_errors.json")
    with open(error_log_path, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=4, ensure_ascii=False)
    logging.info(f"Error log saved to {error_log_path}")