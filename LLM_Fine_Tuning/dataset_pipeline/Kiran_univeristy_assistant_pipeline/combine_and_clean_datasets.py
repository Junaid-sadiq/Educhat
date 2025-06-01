import os
import json
import glob

def combine_and_clean_datasets(output_dir):
    """
    Combines all JSON datasets in the specified output directory,
    removes 'source_file' and 'context_snippet' from each entry,
    and saves the result to a new file.
    """
    combined_data = []
    # Correctly specify the path to the output directory
    # This assumes the script is run from Kiran_univeristy_assistant_pipeline directory
    # or that output_dir is an absolute path.
    # For robustness, let's construct the path relative to this script's location if it's in the same parent.
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # If output_dir is just "output", it will be relative to where the script is run.
    # To make it relative to the script's location:
    if not os.path.isabs(output_dir):
        output_dir_path = os.path.join(script_dir, output_dir)
    else:
        output_dir_path = output_dir

    if not os.path.isdir(output_dir_path):
        print(f"Error: Output directory '{output_dir_path}' not found.")
        return

    json_files = glob.glob(os.path.join(output_dir_path, "alpaca_dataset_*.json"))
    # Exclude the potential output file of this script itself if it's run multiple times
    output_filename = "combined_dataset_cleaned.json"
    json_files = [f for f in json_files if os.path.basename(f) != output_filename]

    if not json_files:
        print(f"No 'alpaca_dataset_*.json' files found in '{output_dir_path}'.")
        return

    print(f"Found {len(json_files)} dataset files to process.")

    for file_path in json_files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict):
                            entry.pop("source_file", None)
                            entry.pop("context_snippet", None)
                            combined_data.append(entry)
                        else:
                            print(f"Warning: Found non-dictionary item in list in {file_path}: {type(entry)}")
                else:
                    print(f"Warning: File {file_path} does not contain a JSON list. Skipping.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}. Skipping.")
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}. Skipping.")

    output_file_path = os.path.join(output_dir_path, output_filename)
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"\nSuccessfully combined {len(combined_data)} entries into {output_file_path}")
    except Exception as e:
        print(f"Error writing combined data to {output_file_path}: {e}")

if __name__ == "__main__":
    # The script is located in:
    # c:\Users\Lenovo\experiments\Creative\Thesis\Educhat\LLM_Fine_Tuning\dataset_pipeline\Kiran_univeristy_assistant_pipeline\
    # The output directory is a subdirectory of this path.
    current_script_directory = os.path.dirname(os.path.abspath(__file__))
    target_output_directory = os.path.join(current_script_directory, "output")
    
    combine_and_clean_datasets(target_output_directory)