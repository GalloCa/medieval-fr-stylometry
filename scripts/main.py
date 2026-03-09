import os 
import time

from utils import load_biblio, clean_label, save_matrix_tsv
from text_processor import TextProcessor
from analyse import create_comparison_matrix, generate_report, compare_files
from plots_generator import generate_similarity_plot, generate_dendogramme
from lcs_analyse import analyse_auteur

if __name__ == "__main__":

    # PATHS
    raw_txt_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt"
    clean_txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"
    filter_txt_dir = r"/workspaces/medFR-paleao-NLP/data/filtered-txt"
    freq_folder = r"/workspaces/medFR-paleao-NLP/results/frequencies"
    
    biblio_genre__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
    biblio_author__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
    biblio_date__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"

    scatter_plot_genre = "../scatter-plots/nuage_points_genre.png"
    scatter_plot_author = "../scatter-plots/nuage_points_auteurs.png"
    scatter_plot_date = "../scatter-plots/nuage_points_dates.png"

    output_matrix = r"/workspaces/medFR-paleao-NLP/results/matrix/matrix.tsv"
    plot_output_dir = r"/workspaces/medFR-paleao-NLP/results/scatter-plots"
    genre_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-genre.md"
    auteurs_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-auteurs.md"
    dates_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-epoques.md"
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

    # E4 : Scatter plot
    generate_similarity_plot(matrix, txt_names, dico_genre, plot_output_dir, mode='genre')
    generate_similarity_plot(matrix, txt_names, dico_date, plot_output_dir, mode='dates')
    generate_similarity_plot(matrix, txt_names, dico_author, plot_output_dir, mode='auteurs')
    generate_dendogramme(matrix, txt_names, dico_author, plot_output_dir)

    # E5 : Génération d'un rapport
    generate_report(matrix, txt_names, 
                    dico_genre, lexique, genre_report_dir, 
                    scatter_plot_genre, titre="Analyse par Genres Littéraires")
    
    generate_report(matrix, txt_names, 
                    dico_author, lexique, auteurs_report_dir, 
                    scatter_plot_author, titre="Analyse par Auteurs")
    
    generate_report(matrix, txt_names, 
                    dico_date, lexique, dates_report_dir, 
                    scatter_plot_date, titre="Analyse par Epoques")
    
    # E5 : LCS
    add_lcs_report_author = analyse_auteur('Chrétien de Troyes', clean_txt_dir, dico_author)

    with open(auteurs_report_dir, mode='a', encoding='utf-8') as f:
        f.write("\n" + "="*50 + "\n")
        f.write(add_lcs_report_author)
    print("Analyse LCS ajoutée au rapport global des auteurs")