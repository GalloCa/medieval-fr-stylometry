import re
import os
from collections import Counter

class Test: 

    def __init__(self, filepath, clean_name, genre="Inconnu"):
        self.filepath = filepath
        self.nom = clean_name
        self.genre = genre
        self.clean_text = ""
        self.frequences = {}

    def clean_txt(self):
        """
        Nettoie le texte en retirant les métadonnées, la ponctuation et les chiffres.
        """
        with open(self.filepath, mode = 'r', encoding='utf-8') as f:
            raw_txt = f.read()

        text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
        if 'start' in text:
            text = text.split('start', 1)[1]
        else :
            text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
    
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

        self.clean_text =  "\n".join(clean_lines)
        
    def n_gramm(self,n=3):
        """
        Génère un dictionnaire de fréquences de n-grammes de caractères.

        Arguments : 
           
            n (int) : taille des n-grammes (par défaut n=3, mais peut être changé)

        """
        if not self.clean_text : 
            self.frequences = Counter()
            return
        
        ngrams = [self.clean_text[i:i+n] for i in range(len(self.clean_text)-n+1)]
        self.frequences = dict(Counter(ngrams))

    # Fonctions de sauvegarde
    def save_clean_txt(self, output_dir, prefix):
        """
        Sauvegarde des textes nettoyés.

        """
        if not self.clean_text:
            print(f"Le fichier {self.nom} n'est pas nettoyé.")
            return
                
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_name_only = os.path.basename(self.filepath)
        new_filename = f'{prefix}-{file_name_only}'
        path = os.path.join(output_dir, new_filename)

        with open(path, 'w', encoding="utf-8") as f:
            f.write(self.clean_text)

    def save_freq(self, output_dir):
        """
        Sauvegarde les fréquences des n-grammes dans un fichier TSV.

        """
        if not self.frequences:
            print(f'Les fréquences du fichier {self.nom} n\'existent pas')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        file_name_only = os.path.basename(self.filepath)
        new_filename = f'freq-{file_name_only.replace(".txt", ".tsv")}'
        path = os.path.join(output_dir, new_filename)
        
        sorted_ngrams = sorted(self.frequences.keys(), key=lambda v: self.frequences[v], reverse = True)
        
        with open(path, mode='w', encoding="utf-8") as f:
            f.write("Ngramme\tFrequence\n")
            for ngram in sorted_ngrams:
                f.write(f"{ngram}\t{self.frequences[ngram]}\n")
                