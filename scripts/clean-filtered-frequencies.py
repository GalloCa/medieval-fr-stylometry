# MODULES

import re
import os 
from collections import Counter

# FUNCTIONS 

def load_stpwords(stopwords_filepath):
    """
    """
    with open(stopwords_filepath) as f:
        content = f.read()
    lines = [re.escape(l.strip()) for l in content.split('\n') if l.strip() and not l.startswith('#')]
    
    if not lines:
        return None
    
    pattern = r"\b(?:" + "|".join(lines)+ r")\b"

    return re.compile(pattern, flags=re.I)

def clean_texts(text, regex_file):
    """

    """
    text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
    if 'start' in text:
        text = text.split('start', 1)[1]
    else :
        text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
    
    if regex_file:
        text = regex_file.sub('', text)

    lines = text.split('\n')
    clean_lines = []
    ban_words = ['meta', 'texturi', 'deaf', 'arlima', 'texttitle', 'textdate', 
        'ededitor', 'msbase', 'http', 'www', 'orcid', 'cclicense', 
        'ici commence', 'prologue', 'or commence', 'author', 'start', 'folio', 'version']

    for line in lines:
        line_content = line.lower().strip()
        
        if any(word in line_content for word in ban_words):
            continue

        line_content = re.sub(r'\b[a-z]*\d+[a-z\d]*\b', '', line_content)
        line_content = re.sub(r'\b\d+[a-d]?\b', '', line_content)
        
        line_content = re.sub(r'[^\w\s7&ç]', '', line_content)
        
        line_content = re.sub(r'\s+', ' ', line_content).strip()
        
    
        if line_content:
            clean_lines.append(line_content)

    return "\n".join(clean_lines)

def save_text(text, original_filename, output_dir, prefix):
    """
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name_only = os.path.basename(original_filename)
    new_filename = f'{prefix}-{file_name_only}'
    path = os.path.join(output_dir, new_filename)

    with open(path, 'w', encoding="utf-8") as f:
        f.write(text)

def n_gramm(text,n=3):
    """
    """
    clean_text = clean_texts(text, regex_file=stop_re)
    ngrams = [clean_text[i:i+n] for i in range(len(clean_text)-n+1)]
    return Counter(ngrams)

def save_freq(frequences, original_filename, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_name_only = os.path.basename(original_filename)
    new_filename = f'freq-{file_name_only.replace(".txt", ".tsv")}'
    path = os.path.join(output_dir, new_filename)
    
    sorted_ngrams = sorted(frequences.keys(), key=lambda v:frequences[v], reverse = True)
    with open(path, mode='w', encoding="utf-8") as f:
        f.write("ngramme\tfrequence\n")
        for ngram in sorted_ngrams:
            f.write(f"{ngram}\t{frequences[ngram]}\n")


# Main 
raw_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt/"
out_dir = r'/workspaces/medFR-paleao-NLP/data/clean-txt'
out_dir_filter = r"/workspaces/medFR-paleao-NLP/data/filtered-txt"
stop_re = load_stpwords(r'/workspaces/medFR-paleao-NLP/data/grammar/300stopwordsMF')

if os.path.exists(raw_dir):
    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            path_src = os.path.join(raw_dir, filename)
            with open(path_src, mode='r', encoding='utf-8') as f:
                content = f.read()

            filtered_txt = clean_texts(content, regex_file=stop_re)
            save_text(filtered_txt, filename, out_dir_filter, prefix="filtered")
            print(f' Fichier filtré : {filename}')


            frequences = n_gramm(filtered_txt)
            save_freq(frequences, filename, r"/workspaces/medFR-paleao-NLP/data/frequencies" )
else:
    print(f"Erreur : {raw_dir} n'existe pas")

