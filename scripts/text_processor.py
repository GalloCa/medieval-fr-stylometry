"""
Module de prétraitement et de tokénisation des textes

Ce script contient la classe TextProcessor, elle est responsable du chargement des textes bruts, 
de leur nettoyage (suppression des métadonnées originales, de la ponctuation ou autres marques) 
et de l'extraction des fréquences de n-grammes de caractères.

"""

# MODULES
import re
import os
from collections import Counter

# CLASSE
class TextProcessor: 
    """
    Objet représentant un document textuel du corpus et gère son traitement
    """

    def __init__(self, filepath, clean_name, genre="Inconnu"):
        """
        Initialise le processeur de texte

        Entrées : 
            filepath (str) : le chemin absolu ou relatif vers le fichier brut du texte
            clean_name (str) : le nom du texte nettoyé
            genre (str, optionnel) : le genre littéraire du texte, par défaut 'Inconnu'
        """
        self.filepath = filepath
        self.nom = clean_name
        self.genre = genre
        self.clean_text = ""
        self.frequences = {}

    def clean_txt(self):
        """
        Nettoie le texte en retirant les métadonnées, la ponctuation et les chiffres

        Etapes : 
            - Suppression des en-têtes et marqueurs de métadonnées
            - Filtrage des lignes contenant des mots-clés parasites ('meta', 'http', etc)
            - Suppresion des chiffres et mots alphanumériques 
            - Suppression de la ponctuation
            - Normalisation des espaces
        
        Modifie :
            self.clean_text (str) : stockage du texte nettoyé en mémoire
        """
        try : 
            with open(self.filepath, mode = 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError : 
            print(f"Le fichier {self.filepath} n'exite pas")
            self.clean_text = ""
            return
        except UnicodeDecodeError:
            print(f"Erreur d'encodage : le fichier {self.nom} n'est pas en UTF-8")

        # Suppression des en-têtes et marqueurs de métadonnées
        text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
        if 'start' in text:
            text = text.split('start', 1)[1]
        else :
            text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
        
        lines = text.split('\n')
        clean_lines = []
        ban_words = ['meta', 'texturi', 'deaf', 'arlima', 'texttitle', 'textdate', 
            'ededitor', 'msbase', 'http', 'www', 'orcid', 'cclicense', 
            'ici commence', 'prologue', 'or commence', 'author', 'start', 'folio', 'version', 'end']
        
        # Filtrage des lignes contenant des mots-clés parasites
        for line in lines:
            line_content = line.lower().strip()
            if any(word in line_content for word in ban_words):
                continue
            # Suppresion des chiffres et mots alphanumériques         
            line_content = re.sub(r'\b[a-z]*\d+[a-z\d]*\b', '', line_content)
            line_content = re.sub(r'\b\d+[a-d]?\b', '', line_content)
            # Suppression de la ponctuation
            line_content = re.sub(r'[^\w\s7&ç]', '', line_content)
            # Normalisation des espaces
            line_content = re.sub(r'\s+', ' ', line_content).strip()

            if line_content:
                clean_lines.append(line_content)

        self.clean_text =  "\n".join(clean_lines)
        
    def n_gramm(self,n=3, niveau='char'):
        """
        Génère un dictionnaire de fréquences de n-grammes de caractères 
        ou de mots à partir du texte nettoyé

        Entrées : 
            n (int, optionnel) : taille des n-grammes, par défaut n = 3
            niveau (str) : niveau d'analyse, accepte 'char' ou 'word'
        Modifie : 
            self.frequences (dict) : stocke les n-grammes et leur occurences : {'ngramme' : 'frequence}
        """
        if not self.clean_text : 
            self.frequences = Counter()
            return
        
        if niveau == 'char':
            ngrams = [self.clean_text[i:i+n] for i in range(len(self.clean_text)-n+1)]
        elif niveau == 'word':
            words = self.clean_text.split()
            ngrams = [" ".join(words[i:i+n]) for i in range(len(words)- n + 1)]
        self.frequences = dict(Counter(ngrams))

    def save_clean_txt(self, output_dir, prefix):
        """
        Sauvegarde des textes nettoyés dans un fichier

        Entrées : 
            output_dir (str) : le chemin du répertoire de destination
            prefix (str) : le préfixe à ajouter au nom de fichier (ex : 'clean')
        Sorties :
            Génère et sauvegarde un fichier texte (.txt) dans le répertoire cible
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

    def save_freq(self, output_dir, prefix):
        """
        Sauvegarde les fréquences des n-grammes dans un fichier TSV, les n-grammes sont 
        triés par ordre décroissant.

        Entrées : 
            output_dir (str) : le chemin du répertoire de destination
        Sorties :
            Génère et sauvegarde un fichier TSV(.tsv) dans le répertoire cible


        """
        if not self.frequences:
            print(f'Les fréquences du fichier {self.nom} n\'existent pas')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        file_name_only = os.path.basename(self.filepath)
        new_filename = f'{prefix}-{file_name_only.replace(".txt", ".tsv")}'
        path = os.path.join(output_dir, new_filename)
        
        sorted_ngrams = sorted(self.frequences.keys(), key=lambda v: self.frequences[v], reverse = True)
        
        with open(path, mode='w', encoding="utf-8") as f:
            f.write("Ngramme\tFrequence\n")
            for ngram in sorted_ngrams:
                f.write(f"{ngram}\t{self.frequences[ngram]}\n")
                
