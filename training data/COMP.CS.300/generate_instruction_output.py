import json
import subprocess
import random
import ollama

# File paths
input_file = "fine_tuning_dataset.json"
output_file = "finetune_dataset_with_ollama.json"

def detect_ollama_model():
    """
    Detect available LLM models in Ollama.
    """
    try:
        models = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        models = models.stdout.strip().split("\n")[1:]  # Ignore header row
        available_models = [m.split()[0] for m in models if m]  # Extract model names
        if available_models:
            print(f"Detected Ollama Models: {available_models}")
            return available_models[0]  # Use the first available model
    except Exception as e:
        print(f"Error detecting Ollama models: {e}")
    return None

def generate_instruction_and_output(model, text):
    """
    Use Ollama LLM to generate an instruction (question/task) and output (answer).
    """
    prompt = f"""
    Based on the following text, generate:
    - An instruction (question or task).
    - A relevant answer.

    Text: {text}

    Format output as:
    Instruction: <generated instruction>
    Output: <generated output>
    """
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        response_text = response["message"]["content"]

        # Extract instruction and output from response
        instruction = "Unknown Instruction"
        output = "Unknown Output"

        if "Instruction:" in response_text and "Output:" in response_text:
            parts = response_text.split("Output:")
            instruction = parts[0].replace("Instruction:", "").strip()
            output = parts[1].strip()

        return instruction, output

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Could not generate instruction.", "Could not generate output."

# Detect the Ollama model
ollama_model = detect_ollama_model()
if not ollama_model:
    print("No Ollama model found. Please install one (e.g., 'ollama pull llama3').")
    exit(1)

# Load dataset
with open(input_file, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Process dataset using the LLM
for entry in dataset:
    instruction, output = generate_instruction_and_output(ollama_model, entry["input"])
    entry["instruction"] = instruction
    entry["output"] = output

# Save the updated dataset
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4, ensure_ascii=False)

print(f"✅ Fine-tuning dataset with Ollama LLM saved to {output_file}")
