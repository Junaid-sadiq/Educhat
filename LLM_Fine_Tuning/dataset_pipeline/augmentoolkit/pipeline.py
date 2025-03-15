def find_text_files(directory):
    """Find all text files in directory and subdirectories"""
    text_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                text_files.append(os.path.join(root, file))
    return text_files

async def load_chunks(self):
    """Load text chunks from files in the input directory"""
    self.info("Loading text chunks...")
    
    input_dir = getattr(self.config.PATH, "INPUT", "./input")
    chunks = []
    
    try:
        # Check if directory exists
        if not os.path.exists(input_dir):
            self.error(f"Input directory does not exist: {input_dir}")
            return []
        
        # Find all text files recursively
        text_files = find_text_files(input_dir)
        self.info(f"Found {len(text_files)} text files in input directory and subdirectories")
        
        # Process text files
        for file_path in text_files:
            self.info(f"Processing file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Rest of your chunking code...
    except Exception as e:
        self.error(f"Error loading chunks: {e}")
    
    self.info(f"Loaded {len(chunks)} chunks")
    return chunks