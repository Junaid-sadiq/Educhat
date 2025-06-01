import os
import logging
import json
import glob
import sys
import time
import httpx  # Required for Ollama communication
import re  # For cleaning questions
import random  # For randomizing questions

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Constants ---
CACHE_DIR = "/scratch/project_2012879/model_cache" # Or your local cache if not on Puhti
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OLLAMA_API_BASE_URL = "http://127.0.0.1:11434"
QUESTION_MODEL = "qwen3:32b"
ANSWER_MODEL = "qwen3:32b"
DEFAULT_PAIRS_PER_FILE = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_qwen_response(response_text):
    if not response_text:
        return response_text
    think_pattern = r'<think>.*?</think>'
    cleaned_text = re.sub(think_pattern, '', response_text, flags=re.DOTALL | re.IGNORECASE)
    thinking_pattern = r'<thinking>.*?</thinking>'
    cleaned_text = re.sub(thinking_pattern, '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text

def generate_with_ollama(prompt, model_name, num_predict=512, max_retries=3, timeout=180):
    logger.debug(f"Attempting Ollama generation with model: {model_name}")
    for attempt in range(max_retries):
        try:
            logger.debug(
                f"Attempt {attempt+1} to connect to Ollama at {OLLAMA_API_BASE_URL}")
            client = httpx.Client(
                base_url=OLLAMA_API_BASE_URL, timeout=timeout)

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "num_predict": num_predict,
                    "repetition_penalty": 1.1
                }
            }
            start_time = time.time()
            response = client.post("/api/generate", json=payload)
            end_time = time.time()
            logger.debug(
                f"Ollama API call took: {end_time - start_time:.2f} seconds")

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                generated_text = clean_qwen_response(generated_text)
                if not generated_text.strip():
                    logger.warning(
                        f"Ollama model {model_name} returned an empty response after cleaning for prompt: {prompt[:100]}...")
                    raise ValueError("Empty response received from Ollama after cleaning")
                logger.debug(
                    f"Ollama response received (first 100 chars): {generated_text[:100]}...")
                if "error" in generated_text.lower() and len(generated_text) < 100:
                    logger.error(
                        f"Ollama model {model_name} may have encountered an internal error: {generated_text}")
                    raise ValueError(
                        f"Ollama internal error suspected: {generated_text}")
                return generated_text
            elif response.status_code == 404:
                logger.error(
                    f"Ollama API error (attempt {attempt+1}): Model '{model_name}' not found. Status 404.")
                return None
            else:
                logger.error(
                    f"Ollama API error (attempt {attempt+1}): {response.status_code} - {response.text}")
                time.sleep(5 * (attempt + 1))
        except httpx.ConnectError as e:
            logger.error(
                f"Ollama connection error (attempt {attempt+1}): {str(e)}. Is the Ollama server running at {OLLAMA_API_BASE_URL}?")
            time.sleep(10 * (attempt + 1))
        except httpx.ReadTimeout as e:
            logger.error(
                f"Ollama read timeout (attempt {attempt+1}) for model {model_name}: {str(e)}. Generation might be too long or server busy/crashed.")
            break
        except ValueError as e:
            logger.warning(
                f"Ollama generation issue (attempt {attempt+1}): {e}")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.error(
                f"Ollama API request failed (attempt {attempt+1}): {str(e)}")
            time.sleep(2 * (attempt + 1))
    logger.error(
        f"All {max_retries} attempts to generate with Ollama model {model_name} failed.")
    return None

def generate_questions(text_content, num_questions=5):
    logger.info(
        f"Generating {num_questions} questions using Ollama model: {QUESTION_MODEL}...")
    if len(text_content) > 15000: # Adjusted for potentially larger context windows of Qwen
        logger.info(
            f"Text potentially too long ({len(text_content)} chars), truncating to ~15K characters for question generation...")
        text_content = text_content[:15000]

    prompt = f"""Generate exactly {num_questions} unique, insightful, university-level questions based *only* on the following text.
Focus on questions that require analytical thinking or synthesis of information present in the text.
Return ONLY the questions, numbered from 1 to {num_questions}. Do not include any preamble, introduction, explanation, or thinking process.

IMPORTANT: Do not include any <think> or <thinking> sections. Provide only the final questions.

Text:
{text_content}

Questions:
"""
    response_text = generate_with_ollama(
        prompt, model_name=QUESTION_MODEL, num_predict=512) # num_predict can be adjusted
    if response_text is None:
        logger.error("Failed to generate questions using Ollama.")
        return []

    questions = []
    current_q = ""
    logger.debug(f"Raw response for question parsing:\n{response_text}")
    lines = response_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^\s*([\d\.\)\-\*]+)\s*(.*)", line)
        if match and match.group(2):
            if current_q:
                questions.append(current_q.strip())
            current_q = match.group(2)
        elif current_q:
            current_q += " " + line
        elif line.endswith('?'): # Handle case where first line isn't numbered but looks like a question
            current_q = line
    if current_q:
        questions.append(current_q.strip())

    clean_questions = [q for q in questions if len(q) > 10 and '?' in q]
    final_questions = clean_questions[:num_questions]
    if len(final_questions) < num_questions:
        logger.warning(
            f"Could only parse {len(final_questions)} valid questions out of {num_questions} requested.")
    logger.info(
        f"Successfully generated and parsed {len(final_questions)} questions.")
    return final_questions

def generate_answers(questions, context):
    answers = []
    logger.info(
        f"Generating answers for {len(questions)} questions using Ollama model: {ANSWER_MODEL}...")
    if len(context) > 15000: # Adjusted for Qwen
        logger.info(
            f"Context potentially too long ({len(context)} chars), truncating to ~15K characters for answer generation...")
        context_truncated = context[:15000]
    else:
        context_truncated = context

    for i, question in enumerate(questions):
        logger.info(
            f"Generating answer for question {i+1}/{len(questions)}: {question[:80]}...")
        prompt = f"""You are Kiran, an AI assistant created by Tampere University. Answer the following student question thoroughly and accurately based ONLY on the context provided below.
Provide a detailed answer of approximately 200-300 words.
If the context does not contain the information needed to answer the question, state that clearly and do not invent information.

IMPORTANT: Do not include any <think> or <thinking> sections. Provide only the final answer.

Context:
{context_truncated}

Question: {question}

Answer:"""
        answer_text = generate_with_ollama(
            prompt, model_name=ANSWER_MODEL, num_predict=1024, timeout=300) # Increased num_predict for answers
        if answer_text is None:
            logger.error(
                f"Failed to generate answer for question: {question[:80]}...")
            answer_text = "I apologize, but I encountered an error trying to generate an answer for this question."
        elif len(answer_text.split()) < 50: # Check if answer is too short
             logger.warning(
                f"Generated answer is very short ({len(answer_text.split())} words) for question: {question[:80]}...")
        answers.append(answer_text.strip())
    return answers

def process_file(file_path, base_input_dir, pairs_per_file=DEFAULT_PAIRS_PER_FILE):
    # Use relative path for unique identification in dataset and for logging
    relative_file_path = os.path.relpath(file_path, base_input_dir)
    logger.info(f"Processing file: {relative_file_path} (Full path: {file_path})")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if not content.strip():
            logger.warning(
                f"File {relative_file_path} is empty or contains only whitespace. Skipping.")
            return []
        
        logger.info(f"Planning to generate {pairs_per_file} questions and answers for {relative_file_path}")
        questions = generate_questions(content, num_questions=pairs_per_file)
        if not questions:
            logger.error(f"No questions generated for {relative_file_path}.")
            return []
        logger.info(f"  Generated {len(questions)} questions for {relative_file_path}.")
        
        answers = generate_answers(questions, content)
        logger.info(f"  Generated {len(answers)} answers for {relative_file_path}.")

        file_alpaca_data = []
        for i, (question, answer) in enumerate(zip(questions, answers)):
            if not question or not answer or "I apologize" in answer or len(answer.split()) < 20:
                logger.warning(
                    f"Skipping invalid or short Q&A pair for {relative_file_path}: Q='{question[:50]}...' A='{answer[:50]}...'")
                continue
            file_alpaca_data.append({
                "instruction": "You are Kiran, an AI assistant from Tampere University. Answer the following question from a student based on the provided context:",
                "input": question,
                "output": answer,
                "source_file": relative_file_path, # Store relative path
                "context_snippet": content[:200]
            })
        logger.info(f"Created {len(file_alpaca_data)} total Q&A pairs for {relative_file_path}")
        return file_alpaca_data
    except Exception as e:
        logger.error(f"Error processing {relative_file_path} (Full path: {file_path}): {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def main():
    start_time = time.time()
    base = os.path.dirname(os.path.abspath(__file__))

    # --- Configuration for targeting a specific subfolder (e.g., "resources") ---
    # Set this to the specific subfolder you want to process within the course.
    # If you want to process the entire course again, remove ", \"resources\"" from the path.
    target_subfolder = "static_resources" # CHANGE THIS if you want a different subfolder or the whole course

    course_base_name = "14.126_Spring_2024_Game_Theory"

    if target_subfolder:
        input_dir = os.path.join(base, "raw_txt_input",
                                 "Other_Unversities_Courses",
                                 "MIT_Open_courseware",
                                 course_base_name,
                                 target_subfolder)
        # Adjust test_course to reflect that only a subfolder is processed, for unique output files
        test_course_identifier = f"{course_base_name}_{target_subfolder}"
    else:
        input_dir = os.path.join(base, "raw_txt_input",
                                 "Other_Unversities_Courses",
                                 "MIT_Open_courseware",
                                 course_base_name)
        test_course_identifier = course_base_name
    # --- End of subfolder configuration ---


    sanitized_course_name = re.sub(r'\W+', '_', test_course_identifier)
    if not sanitized_course_name:
        sanitized_course_name = "default_course"

    output_file = os.path.join(
        OUTPUT_DIR, f"alpaca_dataset_{sanitized_course_name}_ollama_sequential.json")
    progress_file = os.path.join(
        OUTPUT_DIR, f"progress_{sanitized_course_name}_ollama_sequential.json")

    logger.info(f"Targeting course/subfolder identifier: '{test_course_identifier}'")
    logger.info(f"Input directory for os.walk: '{input_dir}'")
    logger.info(f"Using output file: {output_file}")
    logger.info(f"Using progress file: {progress_file}")

    try:
        client = httpx.Client(base_url=OLLAMA_API_BASE_URL, timeout=10.0)
        response = client.get("/")
        if response.status_code == 200 and "Ollama is running" in response.text:
            logger.info(
                f"Successfully connected to Ollama server at {OLLAMA_API_BASE_URL}")
        else:
            logger.warning(
                f"Connected to {OLLAMA_API_BASE_URL}, but response was unexpected: {response.text[:100]}")
    except Exception as e:
        logger.error(
            f"FATAL: Could not connect to Ollama server at {OLLAMA_API_BASE_URL}. Please ensure it is running. Error: {e}")
        return

    dataset = []
    processed_files = set() # Will store relative paths

    # Load progress using relative paths
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            loaded_progress_files = {item.get('source_file') for item in dataset if 'source_file' in item}
            processed_files.update(loaded_progress_files)
            logger.info(
                f"Loaded progress with {len(dataset)} examples from {len(processed_files)} unique relative file paths.")
        except json.JSONDecodeError:
            logger.warning(
                f"Progress file {progress_file} is corrupted. Starting fresh.")
            dataset = []
        except Exception as e:
            logger.error(f"Error loading progress file {progress_file}: {e}")
            dataset = []

    # Load existing output file (if any) using relative paths
    if os.path.exists(output_file) and output_file != progress_file:
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                output_dataset = json.load(f)
            loaded_output_files = {item.get('source_file') for item in output_dataset if 'source_file' in item}
            if len(output_dataset) > len(dataset): # Basic check, could be more sophisticated
                logger.info(
                    f"Found more examples in output file ({len(output_dataset)}) than progress file ({len(dataset)}). Considering output file data.")
                dataset = output_dataset
                processed_files.update(loaded_output_files)
            logger.info(
                f"Combined with output file, found {len(processed_files)} total processed relative file paths initially.")
        except json.JSONDecodeError:
            logger.warning(
                f"Output file {output_file} exists but is corrupted. Using progress data only (if any).")
        except Exception as e:
            logger.error(f"Error loading output file {output_file}: {e}")

    extensions = ['.txt', '.md']
    file_paths = [] # Will store full absolute paths

    logger.info(f"Starting os.walk in directory: {input_dir}")
    if not os.path.isdir(input_dir):
        logger.error(f"Input directory does not exist or is not a directory: {input_dir}")
        logger.error(f"Please check the 'target_subfolder' variable and the base course path.")
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))

    logger.info(f"Found {len(file_paths)} files with extensions {extensions} in '{input_dir}' before any further filtering. First 5: {file_paths[:5]}")

    # The `test_course_identifier` (which might include the subfolder name) is used for output file naming.
    # The actual filtering of files to process is now implicitly handled by `input_dir` pointing to the specific subfolder.
    # If `input_dir` points to the whole course, and `test_course_identifier` is just the course name,
    # then the old filter `if course_base_name in fp` would be relevant.
    # For simplicity, if `input_dir` is already specific, we don't need an additional path string filter.
    
    # The `file_paths` list now contains all relevant files from the (potentially specific) `input_dir`.
    # No additional string-based filtering on `file_paths` is strictly necessary here if `input_dir` is already narrowed down.
    # However, if `target_subfolder` was empty, you might want to re-introduce a filter based on `course_base_name`.
    # For now, we assume `input_dir` is the definitive source.

    unique_file_paths = sorted(list(set(file_paths))) # Ensure uniqueness of full paths
    logger.info(f"Found {len(unique_file_paths)} unique files to potentially process from '{input_dir}'. First 5: {unique_file_paths[:5]}")

    total_files_to_process = len(unique_file_paths)

    if not unique_file_paths:
        logger.error(
            f"No text files found in the input directory: {input_dir}")
        return

    # Use relative paths for checking against `processed_files`
    remaining_files_to_process_list = [
        os.path.relpath(fp, input_dir) for fp in unique_file_paths if os.path.relpath(fp, input_dir) not in processed_files
    ]
    count_remaining_files = len(remaining_files_to_process_list)

    logger.info(
        f"Already processed {len(processed_files)} files (relative paths, based on loaded progress/output). {count_remaining_files} files remaining to process.")

    if count_remaining_files > 0:
        logger.info(f"First 5 relative file paths to process: {remaining_files_to_process_list[:5]}")
    elif total_files_to_process > 0 :
        logger.info(f"All {total_files_to_process} found files have already been processed according to progress/output files.")
    else:
        logger.info("No files to process.")

    skipped_files_count = 0
    # Iterate using the full unique_file_paths
    for i, file_path_to_process in enumerate(unique_file_paths):
        # Get relative path for checking against processed_files and for storing in JSON
        relative_path_for_processing = os.path.relpath(file_path_to_process, input_dir)

        if relative_path_for_processing in processed_files:
            logger.info(f"Skipping already processed file: {relative_path_for_processing} (Full path: {file_path_to_process})")
            skipped_files_count += 1
            continue
        
        # For logging remaining count, it's a bit trickier now since we iterate all unique_file_paths
        # and skip. A simple decreasing counter is easier.
        logger.info(
            f"Processing {relative_path_for_processing} (Full path: {file_path_to_process}). Approx. {count_remaining_files - (i - skipped_files_count)} actual new files remaining in this run.")
        
        # Pass the original input_dir (which might be the subfolder path) as base_input_dir
        file_data = process_file(file_path_to_process, input_dir, pairs_per_file=DEFAULT_PAIRS_PER_FILE)

        if file_data:
            dataset.extend(file_data)
            processed_files.add(relative_path_for_processing) # Add relative path to set

            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(dataset, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(
                    f"Failed to save progress to {progress_file}: {e}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved final dataset to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save final dataset to {output_file}: {e}")

    end_time = time.time()
    logger.info(
        f"Dataset generation complete. Total time: {end_time - start_time:.2f} seconds")
    logger.info(
        f"Final dataset contains {len(dataset)} examples from {len(processed_files)} processed relative file paths (this session or loaded).")
    logger.info(f"Skipped {skipped_files_count} files that were already processed (according to loaded data).")

if __name__ == "__main__":
    main()