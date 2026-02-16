# MODULES

import re
import os 
from collections import Counter

def clean_texts(text):
    """
    Docstring for clean_texts
    
    :param text: Description
    """
    text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
    text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
    text = re.sub(r'\b\d+[a-d]\b', '', text)
    text = re.sub(r'[^\w\s7&ç]', '', text)
    return text.lower().strip()

def save_text(text, original_filename, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name_only = os.path.basename(original_filename)
    new_filename = f'clean_{file_name_only}'
    path = os.path.join(output_dir, new_filename)

    with open(path, 'w', encoding="utf-8") as f:
        f.write(text)

def n_gramm(text,n=3):
    clean_text = clean_texts(text)
    ngrams = [clean_text[i:i+n] for i in range(len(clean_text)-n+1)]
    return Counter(ngrams)

raw_dir = r"/workspaces/medFR-paleao-NLP/data/raw-texts/"
out_dir = r'/workspaces/medFR-paleao-NLP/data/clean-texts'

if os.path.exists(raw_dir):
    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            path_src = os.path.join(raw_dir, filename)
            with open(path_src, mode='r', encoding='utf-8') as f:
                content = f.read()
            
            clean_txt = clean_texts(content)
            save_text(clean_txt, filename, out_dir)

            print(f' Fichier traité : {filename}')
else:
    print(f"Erreur : {raw_dir} n'existe pas")


