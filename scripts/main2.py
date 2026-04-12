"""
Pipeline global d'Analyse Stylométrique de l'Ancien Français.
Mode : Multi-expérimentations (Caractères vs Mots)
"""

# MODULES
import os 
import time
import sys

from download_data import download_github_data
from utils import load_biblio, clean_label, save_matrix_tsv
from text_processor import TextProcessor
from analyse import create_comparison_matrix, generate_report, compare_files
from plots_generator import generate_similarity_plot, generate_dendogramme
from lcs_analyse import analyse_auteur


# MAIN
if __name__ == "__main__":

    # CONFIGURATION DES METADONNEE 
    # DEFINIR SI NGRAMS CARACTERES OU MOTS TAILLE ET METRIQUE UTILISEE
    
    experiences = [
        {'nom': 'caracteres3', 'n': 3, 'niveau': 'char', 'metric' : 'cosinus'},
        {'nom': 'mots2', 'n': 2, 'niveau': 'word', 'metric' : 'cosinus'}
    ]

    # Répertoires de travail globaux
    raw_txt_dir = r"/workspaces/medFR-paleao-NLP/data/raw-txt"
    clean_txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"
    freq_folder = r"/workspaces/medFR-paleao-NLP/results/frequencies"
    
    # Fichiers de métadonnées
    biblio_genre_dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
    biblio_author_dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
    biblio_date_dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"

    # Chargement sécurisé des dictionnaires
    dico_genre = load_biblio(biblio_genre_dir)
    dico_author = load_biblio(biblio_author_dir)
    dico_date = load_biblio(biblio_date_dir)

        dicos = {
        'dico_genre':  (dico_genre,  biblio_genre_dir),
        'dico_author': (dico_author, biblio_author_dir),
        'dico_date':   (dico_date,   biblio_date_dir),
    }
    for nom, (dico, chemin) in dicos.items():
        if not dico:
            print(f"Erreur : {nom} est vide ou introuvable ({chemin}). Vérifier le fichier.")
            sys.exit(1)
    print(f"Métadonnées chargées : {len(dico_genre)} genres, {len(dico_author)} auteurs, {len(dico_date)} dates.")


    # ÉTAPE 1 : TÉLÉCHARGEMENT DES DONNÉES

    print("\nEtape 1 : Téléchargement des données brutes depuis le répertoire Open Medieval French...")
    repo_api_url = "https://api.github.com/repos/OpenMedFr/texts/contents"

    if not os.path.exists(raw_txt_dir) or len(os.listdir(raw_txt_dir)) == 0:
        print("\nLe dossier des textes brutes est vide, lancement du téléchargement...")
        reussit = download_github_data(repo_api_url, raw_txt_dir)

        if reussit :
            print("\nTéléchargement terminé avec succès")
        else :
            print("\nEchec du téléchargement (problème d'API ou de token GitHub)")
            sys.exit(1)
    else :
        print(f"\nLes textes sont déjà présents dans {raw_txt_dir}. Pas besoin de les re-télécharger")

    
    # START 
    
    for exp in experiences:
        suffixe = exp['nom']

        # Création des sous-dossiers spécifiques à cette expérience
        exp_matrix_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/matrix", suffixe)
        exp_plot_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/scatter-plots", suffixe)
        exp_report_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/rapports", suffixe)

        os.makedirs(exp_matrix_dir, exist_ok=True)
        os.makedirs(exp_plot_dir, exist_ok=True)
        os.makedirs(exp_report_dir, exist_ok=True)

        # Chemins de sortie dynamiques
        output_matrix = os.path.join(exp_matrix_dir, "matrix.tsv")
        compare_out_dir = os.path.join(exp_matrix_dir, "compare-files.tsv")
        genre_report_dir = os.path.join(exp_report_dir, "rapport-genre.md")
        auteurs_report_dir = os.path.join(exp_report_dir, "rapport-auteurs.md")
        dates_report_dir = os.path.join(exp_report_dir, "rapport-epoques.md")

        # Chemins relatifs pour insérer les images dans le Markdown
        # Depuis results/rapports/char3/ vers results/scatter-plots/char3/
        scatter_plot_genre = f"../../scatter-plots/{suffixe}/nuage_points_genre.png"
        scatter_plot_author = f"../../scatter-plots/{suffixe}/nuage_points_auteurs.png"
        scatter_plot_date = f"../../scatter-plots/{suffixe}/nuage_points_dates.png"


        # --- ÉTAPE 2 : NETTOYAGE ET FRÉQUENCES ---
        print(f"\nÉtape 2 : Nettoyage et extraction des n-grammes ({exp['niveau']}, n={exp['n']})...")
        my_corpus = []
        files = [f for f in os.listdir(raw_txt_dir) if f.endswith(".txt")]

        for filename in files:
            input_path = os.path.join(raw_txt_dir, filename)
            file_name_clean = clean_label(filename)
            
            try:
                doc = TextProcessor(filepath=input_path, clean_name=file_name_clean)
                doc.clean_txt()
                
                # C'est ici que la magie opère selon l'expérience en cours !
                doc.n_gramm(n=exp['n'], niveau=exp['niveau']) 

                if not doc.frequences:
                    print(f"⏩ Texte ignoré (vide ou invalide) : {filename}")
                    continue

                # Sauvegarde avec le préfixe de l'expérience (ex: freq-word1-Yvain.tsv)
                doc.save_freq(freq_folder, prefix=suffixe)
                doc.save_clean_txt(clean_txt_dir, prefix="clean")

                my_corpus.append(doc)
            except Exception as e:
                print(f"Échec sur {filename} : erreur {e}")
                continue
                
        print(f"{len(my_corpus)} textes traités pour l'expérience {suffixe}.")


        # Etape 3 : Matrice de comparaison
        print("\nÉtape 3 : Création de la matrice Termes-Documents...")
        matrix, lexique, txt_names = create_comparison_matrix(my_corpus)
        save_matrix_tsv(matrix, lexique, txt_names, output_matrix)
        compare_files(matrix, txt_names, compare_out_dir)


        # Etape 4 : visualisation graphique
        print("\nEtape 4 : génération des visualisations (scatter plot) ... ")
        generate_similarity_plot(matrix, txt_names, dico_genre, exp_plot_dir, mode='genre')
        generate_similarity_plot(matrix, txt_names, dico_date, exp_plot_dir, mode='dates')
        generate_similarity_plot(matrix, txt_names, dico_author, exp_plot_dir, mode='auteurs')
      

        # Etape 5 : Génération des rapports
        print("\nÉtape 5 : Génération des rapports Markdown...")
        metric_use = exp['metric']
        generate_report(matrix, txt_names, dico_genre, lexique, genre_report_dir, scatter_plot_genre, titre="Analyse par Genres Littéraires", metric=metric_use)
        generate_report(matrix, txt_names, dico_author, lexique, auteurs_report_dir, scatter_plot_author, titre="Analyse par Auteurs", metric=metric_use)
        generate_report(matrix, txt_names, dico_date, lexique, dates_report_dir, scatter_plot_date, titre="Analyse par Époques", metric=metric_use)

        print(f"Fin du traitement pour {suffixe} !")


    # Etape 6 : LCS et rajout au rapport 'auteurs'
    print("Étape 6 : Recherche de séquences récurrentes (LCS) pour Chrétien de Troyes...")
    

   # Construction du rapport final : MD ou HTML ? 
    rapport_cible = r"/workspaces/medFR-paleao-NLP/results/rapports/caracteres3/rapport-auteurs.md"
    add_lcs_report_author = analyse_auteur('Chrétien de Troyes', clean_txt_dir, dico_author)

    try:
        with open(rapport_cible, mode='a', encoding='utf-8') as f:
            f.write("\n" + "="*50 + "\n\n")
            f.write(add_lcs_report_author)
        print("Analyse LCS ajoutée au rapport global des auteurs (caracteres3).")
    except Exception as e:
        print(f"Impossible d'ajouter le LCS au rapport : {e}")
        
    print("\nFin de l'étape 6")
 
