# MODULES 
import re
import os
import time
import numpy as np
from collections import Counter
from tools import (load_stpwords, clean_texts, save_text, n_gramm, save_freq,
                   create_comparison_matrix, compare_files, 
                   biblio, generate_report)

# from scatter_plot import (similarities_genre, similarities_authors, similarities_dates)

if __name__ == "__main__":

    # PATHS
    raw_txt_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt"
    clean_txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"
    filter_txt_dir = r"/workspaces/medFR-paleao-NLP/data/filtered-txt"
    freq_folder = r"/workspaces/medFR-paleao-NLP/results/frequencies"
    
    stopwords_dir = r"/workspaces/medFR-paleao-NLP/data/stopwords/300stopwordsMF"
    biblio_genre__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
    biblio_author__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
    biblio_date__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"

    output_matrix = r"/workspaces/medFR-paleao-NLP/results/matrix/matrix.tsv"
    genre_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-genre.txt"
    auteurs_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-auteurs.txt"
    dates_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-date.txt"
    compare_out_dir =r"/workspaces/medFR-paleao-NLP/results/matrix/compare-files.tsv"

    # Chargement en mémoire 
    stopwords = load_stpwords(stopwords_dir)
    dico_genre = biblio(biblio_genre__dir)
    dico_author = biblio(biblio_author__dir)
    dico_date = biblio(biblio_date__dir)

    # MAIN 
    # E1 : Nettoyage des textes 
    if not os.path.exists(raw_txt_dir):
        print(f'Erreur : le dossier {raw_txt_dir} est introuvable.')
    else:

        files = os.listdir(raw_txt_dir)
        for filename in files:

            if filename.endswith(".txt"):
                input_path = os.path.join(raw_txt_dir, filename)
                with open(input_path, 'r', encoding='utf-8') as f:
                    contenu_brut = f.read()
            
                clean_content = clean_texts(contenu_brut, regex_file=None)
                save_text(clean_content, input_path, clean_txt_dir, prefix="clean")
                
                frequences = n_gramm(clean_content)
                save_freq(frequences, filename, freq_folder)

    print("Etape 1 : Nettoyage des textes et extraction de fréquences terminés.")

    # E2 : Création de la matrice et comparaison des fichiers
    print("\n Début E2 : Matrice et analyse.")
    matrix, lexique, txt_names = create_comparison_matrix(freq_folder, output_matrix)
    
    compare_files(matrix, txt_names, compare_out_dir)

    # E3 : LCS

    # E4 : Génération d'un rapport
    generate_report(matrix, txt_names, dico_genre, lexique, genre_report_dir)
    generate_report(matrix, txt_names, dico_author, lexique, auteurs_report_dir)
    generate_report(matrix, txt_names, dico_date, lexique, dates_report_dir)