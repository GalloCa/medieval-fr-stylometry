"""

"""
# MODULES
import os 
import time

from download_data import download_github_data
from utils import load_biblio, clean_label, save_matrix_tsv
from text_processor import TextProcessor
from analyse import create_comparison_matrix, generate_report, compare_files
from plots_generator import generate_similarity_plot, generate_dendogramme
from lcs_analyse import analyse_auteur


# MAIN
if __name__ == "__main__":

    # PATHS
    # Répertoires de travail
    raw_txt_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt"
    clean_txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"
    filter_txt_dir = r"/workspaces/medFR-paleao-NLP/data/filtered-txt"
    freq_folder = r"/workspaces/medFR-paleao-NLP/results/frequencies"
    
    # Fichiers de métadonnées
    biblio_genre__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
    biblio_author__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
    biblio_date__dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"

    # Chemins relatifs des images pour génération du rapport
    scatter_plot_genre = "../scatter-plots/nuage_points_genre.png"
    scatter_plot_author = "../scatter-plots/nuage_points_auteurs.png"
    scatter_plot_date = "../scatter-plots/nuage_points_dates.png"

    # Fichiers de résultats
    output_matrix = r"/workspaces/medFR-paleao-NLP/results/matrix/matrix.tsv"
    plot_output_dir = r"/workspaces/medFR-paleao-NLP/results/scatter-plots"
    genre_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-genre.md"
    auteurs_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-auteurs.md"
    dates_report_dir = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-epoques.md"
    compare_out_dir =r"/workspaces/medFR-paleao-NLP/results/matrix/compare-files.tsv"

    # Chargement en mémoire des dictionnaires
    dico_genre = load_biblio(biblio_genre__dir)
    dico_author = load_biblio(biblio_author__dir)
    dico_date = load_biblio(biblio_date__dir)

    # Etape 1 : Téléchargement des données 
    print("\nEtape 1 : Téléchargement des données brutes depuis le répertoire Open Medieval French...")
    repo_api_url = "https://api.github.com/repos/OpenMedFr/texts/contents"

    if not os.path.exists(raw_txt_dir) or len(os.listdir(raw_txt_dir)) == 0:
        print("\nLe dossier des textes brutes est vide, lancement du téléchargement...")
        reussit = download_github_data(repo_api_url, raw_txt_dir)

        if reussit :
            print("\nTéléchargement terminé avec succès")
        else :
            print("\nEchec du téléchargement (problème d'API ou de token GitHub)")
            exit()
    else :
        print(f"\nLes textes sont déjà présents dans {raw_txt_dir}. Pas besoin de les re-télécharger")

    # Etape 2 : Nettoyage des textes et calculs des fréquences    
    print("\nEtape 2 : nettoyage des textes et calcul des n-grammes...")
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

    # Etape 3 : Matrice de comparaison
    print("\nEtape 3 : création de la matrice et analyse.")
    matrix, lexique, txt_names = create_comparison_matrix(my_corpus)
    save_matrix_tsv(matrix, lexique, txt_names, output_matrix)
    compare_files(matrix, txt_names, compare_out_dir)

    # Etape 4 : visualisation graphique
    print("\nEtape 4 :.Génération des visualisation (scatter plot et dendogramme)... ")
    generate_similarity_plot(matrix, txt_names, dico_genre, plot_output_dir, mode='genre')
    generate_similarity_plot(matrix, txt_names, dico_date, plot_output_dir, mode='dates')
    generate_similarity_plot(matrix, txt_names, dico_author, plot_output_dir, mode='auteurs')
    generate_dendogramme(matrix, txt_names, dico_author, plot_output_dir)

    # Etape 5 : Génération des rapports
    print("\nEtape 5 : Génération des rapport Markdown d'analyse")
    generate_report(matrix, txt_names, 
                    dico_genre, lexique, genre_report_dir, 
                    scatter_plot_genre, titre="Analyse par Genres Littéraires")
    
    generate_report(matrix, txt_names, 
                    dico_author, lexique, auteurs_report_dir, 
                    scatter_plot_author, titre="Analyse par Auteurs")
    
    generate_report(matrix, txt_names, 
                    dico_date, lexique, dates_report_dir, 
                    scatter_plot_date, titre="Analyse par Epoques")
    
    # Etape 6 : LCS et rajout au rapport 'auteurs'
    print("\nEtape 6 : Recherche de séquences récurrentes pour Chrétien de Troyes")
    add_lcs_report_author = analyse_auteur('Chrétien de Troyes', clean_txt_dir, dico_author)

    with open(auteurs_report_dir, mode='a', encoding='utf-8') as f:
        f.write("\n" + "="*50 + "\n")
        f.write(add_lcs_report_author)
    print("Analyse LCS ajoutée au rapport global des auteurs")
    
