import os
import re
from langdetect import detect
from difflib import SequenceMatcher

def text_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_raw_text_files(directory):
    issues = {
        "duplicated_content": [],
        "mixed_language": [],
        "external_sources": []
    }
    
    external_keywords = ["MIT", "Cormen", "Leiserson", "Rivest", "Stein", 
                         "Levitin", "Introduction to Algorithms"]
    
    files = os.listdir(directory)
    for filename in files:
        if not filename.endswith('.txt'):
            continue
            
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for duplicated paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        for i in range(len(paragraphs)):
            for j in range(i+1, len(paragraphs)):
                if text_similarity(paragraphs[i], paragraphs[j]) > 0.8:
                    issues["duplicated_content"].append(filename)
                    break
            if filename in issues["duplicated_content"]:
                break
        
        # Check for mixed language
        try:
            # Divide text into chunks and check language of each
            chunks = [content[i:i+100] for i in range(0, len(content), 100) if content[i:i+100].strip()]
            langs = [detect(chunk) for chunk in chunks[:10] if len(chunk) > 20]
            if 'fi' in langs and 'en' in langs:
                issues["mixed_language"].append(filename)
        except:
            pass
            
        # Check for external sources
        for keyword in external_keywords:
            if keyword.lower() in content.lower():
                issues["external_sources"].append((filename, keyword))
                break
    
    return issues