# MODULES

import re
import os 
from collections import Counter


def load_grm(filepath):
    with open(filepath, mode='r', encoding='utf-8') as f:
        regles = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    regles = [r.replace("'", "").replace('"', "") for r in regles]
    return re.compile("|".join(regles), flags = re.I)

def load_list(filepath):
    with open(filepath, mode='r', encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]

def clean_texts(text, regex_file, stopwords, blacklist):

    text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
    if 'start' in text:
        text = text.split('start', 1)[1]
    else :
        text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
    
    lines = text.split('\n')
    clean_lines = []

    stop_set = set(stopwords) if stopwords else set()
    black_set = set(blacklist) if blacklist else set()

    for line in lines:
        line_content = line.lower().strip()

        if regex_file:
            line_content = regex_file.sub(' ', line_content)
        
        words = line_content.split()
        filtered_words = [w for w in words if w not in stop_set and w not in black_set]

        final_line_content = " ".join(filtered_words).strip()

        if final_line_content:
            clean_lines.append(final_line_content)
    return "\n".join(clean_lines)

def save_text(text, original_filename, output_dir, prefix):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name_only = os.path.basename(original_filename)
    new_filename = f'{prefix}-{file_name_only}'
    path = os.path.join(output_dir, new_filename)

    with open(path, 'w', encoding="utf-8") as f:
        f.write(text)

def n_gramm(text,n=3):
    clean_text = clean_texts(text, regex_file=regex_mf)
    ngrams = [clean_text[i:i+n] for i in range(len(clean_text)-n+1)]
    return Counter(ngrams)


# MAIN 
regex_mf = load_grm(r'/workspaces/medFR-paleao-NLP/data/grammar/re-txt')
path_stpwords = load_list(r'/workspaces/medFR-paleao-NLP/data/grammar/300stopwordsMF')
path_blist = load_list(r'/workspaces/medFR-paleao-NLP/data/grammar/blacklist-words')
raw_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt/"
out_dir_filter = r"/workspaces/medFR-paleao-NLP/data/filtered-txt"

if os.path.exists(raw_dir):
    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            path_src = os.path.join(raw_dir, filename)
            with open(path_src, mode='r', encoding='utf-8') as f:
                content = f.read()
            
            filtered_txt = clean_texts(content, regex_file=regex_mf, stopwords=path_stpwords, blacklist=path_blist)
            save_text(filtered_txt, filename, out_dir_filter, prefix="filtered")
            print(f' Fichier traité : {filename}')


            frequences = n_gramm(filtered_txt)
            save_text(str(frequences), filename, r"/workspaces/medFR-paleao-NLP/data/frequencies", prefix="freq")
else:
    print(f"Erreur : {raw_dir} n'existe pas")