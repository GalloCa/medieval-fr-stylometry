import os 
import time

from utils import load_biblio, clean_label, save_matrix_tsv
from text_processor import TextProcessor
from analyse import create_comparison_matrix, generate_report, compare_files
# scatterplot 
# lcs

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

    dico_genre = load_biblio(biblio_genre__dir)
    dico_author = load_biblio(biblio_author__dir)
    dico_date = load_biblio(biblio_date__dir)

    print("\n E1...")
    my_corpus = []

    if not os.path.exists(raw_txt_dir):
        print(f'Erreur : le dossier {raw_txt_dir} est introuvable.')
    else:
        files = [f for f in os.listdir(raw_txt_dir) if f.endswith(".txt")]

        for filename in files : 
            input_path = os.path.join(raw_txt_dir, filename)
            file_name_clean = clean_label(filename)

            doc = TextProcessor(filepath = input_path, clean_name = file_name_clean)

            doc.clean_txt()
            doc.n_gramm(n=3)

            doc.save_clean_txt(clean_txt_dir, prefix = "clean")
            doc.save_freq(freq_folder)

            my_corpus.append(doc)
    print(f"{len(my_corpus)} textes traités")

    print("\n Début E2 : Matrice et analyse.")
    matrix, lexique, txt_names = create_comparison_matrix(my_corpus)
    save_matrix_tsv(matrix, lexique, txt_names, output_matrix)
    compare_files(matrix, txt_names, compare_out_dir)

    # E3 : LCS
    
    # E4 : Scatter plot

    # E5 : Génération d'un rapport
    generate_report(matrix, txt_names, dico_genre, lexique, genre_report_dir, titre="Analyse par Genres Littéraires")
    generate_report(matrix, txt_names, dico_author, lexique, auteurs_report_dir, titre="Analyse par Auteurs")
    generate_report(matrix, txt_names, dico_date, lexique, dates_report_dir, titre="Analyse par Epoques")