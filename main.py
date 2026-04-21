"""
Pipeline global d'Analyse d'un corpus de l'Ancien Français.
Mode : Multi-expérimentations (Caractères vs Mots)
"""

# MODULES
import os 
import time
import sys

from download_data import download_github_data
from text_processor import TextProcessor
from analyse import create_comparison_matrix, compare_files, load_biblio, clean_label, save_matrix_tsv, analyse_auteur, gexf
from plots_generator import generate_similarity_plot
from generate_report_html import generate_combined_report_html


# MAIN
if __name__ == "__main__":

    # CONFIGURATION DES METADONNEE 
    # DEFINIR SI NGRAMS CARACTERES OU MOTS TAILLE ET METRIQUE UTILISEE
    
    experiences = [
        {'nom': 'morpho', 'n': 3, 'niveau': 'char', 'metric' : 'cosinus'},
        {'nom': 'lexical', 'n': 2, 'niveau': 'word', 'metric' : 'cosinus'}
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
    result_auteurs = {}
    result_genre = {}
    result_epoque = {}

    for exp in experiences:
        suffixe = exp['nom']

        # Création des sous-dossiers spécifiques à cette expérience
        exp_matrix_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/matrix", suffixe)
        exp_plot_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/scatter-plots", suffixe)
        exp_freq_dir = os.path.join(r"/workspaces/medFR-paleao-NLP/results/frequencies", suffixe)

        os.makedirs(exp_matrix_dir, exist_ok=True)
        os.makedirs(exp_plot_dir, exist_ok=True)

        # Chemins de sortie dynamiques
        output_matrix = os.path.join(exp_matrix_dir, "matrix.tsv")
        compare_out_dir = os.path.join(exp_matrix_dir, "compare-files.tsv")

        # Chemins absolus pour insérer les images
        scatter_plot_genre  = os.path.join(exp_plot_dir, "nuage_points_genre.png")
        scatter_plot_author = os.path.join(exp_plot_dir, "nuage_points_auteurs.png")
        scatter_plot_date   = os.path.join(exp_plot_dir, "nuage_points_dates.png")

        results_dir = r"/workspaces/medFR-paleao-NLP/results"

        # ETAPE 2 : NETTOYAGE ET FRÉQUENCES 
        print(f"\nÉtape 2 : Nettoyage et extraction des n-grammes ({exp['niveau']}, n={exp['n']})...")
        my_corpus = []
        files = [f for f in os.listdir(raw_txt_dir) if f.endswith(".txt")]

        for filename in files:
            input_path = os.path.join(raw_txt_dir, filename)
            file_name_clean = clean_label(filename)
            
            try:
                doc = TextProcessor(filepath=input_path, clean_name=file_name_clean)
                doc.clean_txt()
                
                
                doc.n_gramm(n=exp['n'], niveau=exp['niveau']) 

                if not doc.frequences:
                    print(f"⏩ Texte ignoré (vide ou invalide) : {filename}")
                    continue

                # Sauvegarde avec le préfixe de l'expérience (ex: lexical-Yain.tsv)
                doc.save_freq(exp_freq_dir, prefix=suffixe)
                doc.save_clean_txt(clean_txt_dir, prefix="clean")

                my_corpus.append(doc)
            except Exception as e:
                print(f"Échec sur {filename} : erreur {e}")
                continue
                
        print(f"{len(my_corpus)} textes traités pour l'expérience {suffixe}.")


        # ETAPE 3 : MATRICE DE COMPARAISON
        print("\nÉtape 3 : Création de la matrice Termes-Documents...")
        
        matrix, lexique, txt_names = create_comparison_matrix(my_corpus)
        save_matrix_tsv(matrix, lexique, txt_names, output_matrix)
        compare_files(matrix, txt_names, compare_out_dir)

        # TEST 
        print("Archivage global des comparaisons...")
        chemin_tsv = os.path.join(results_dir, "matrix", "morpho/compare-files.tsv")
        compare_files(matrix, txt_names, chemin_tsv)

        print("Génération des fichiers réseaux Gephi...")
        chemin_gexf_cos = os.path.join(results_dir, "gephi", "reseau_cosinus.gexf")
        chemin_gexf_jac = os.path.join(results_dir, "gephi", "reseau_jaccard.gexf")

        # cos
        gexf(matrix, txt_names, dico_author, chemin_gexf_cos, metric='cosinus')

        # jac
        gexf(matrix, txt_names, dico_author, chemin_gexf_jac, metric='jaccard')

        # ETAPE 4 : VISUALISATION
        print("\nEtape 4 : Génération des visualisations (scatter plot) ... ")
        
        generate_similarity_plot(matrix, txt_names, dico_genre, exp_plot_dir, mode='genre')
        generate_similarity_plot(matrix, txt_names, dico_date, exp_plot_dir, mode='dates')
        generate_similarity_plot(matrix, txt_names, dico_author, exp_plot_dir, mode='auteurs')
      

        # ETAPE 5 : PREPARATION DES RAPPORTS HTML
        print("\nÉtape 5 : Préparation des rapports")
       
        metric_use = exp['metric']
        
        result_auteurs[suffixe] = {
            'matrix' : matrix,
            'txt_names' : txt_names,
            'lexique' :   lexique,
            'img_path' :  os.path.join(exp_plot_dir, "nuage_points_auteurs.png"),
            'metric' :    metric_use,
        }
        
        result_genre[suffixe] = {
            'matrix':    matrix,
            'txt_names': txt_names,
            'lexique':   lexique,
            'img_path':  os.path.join(exp_plot_dir, "nuage_points_genre.png"),   # chemin absolu
            'metric':    metric_use,
        }

        result_epoque[suffixe] = {
            'matrix':    matrix,
            'txt_names': txt_names,
            'lexique':   lexique,
            'img_path':  os.path.join(exp_plot_dir, "nuage_points_dates.png"),
            'metric':    metric_use,
        }

        rapports_dir = r"/workspaces/medFR-paleao-NLP/results/rapports"
        os.makedirs(rapports_dir, exist_ok=True)
        
        genre_report_path   = os.path.join(rapports_dir, "rapport-genre.html")
        auteurs_report_path = os.path.join(rapports_dir, "rapport-auteurs.html")
        dates_report_path   = os.path.join(rapports_dir, "rapport-epoques.html")


        print(f"Fin du traitement pour {suffixe} !")


    # Etape 6 : LCS et rajout au rapport 'auteurs'
    print("Étape 6 : Recherche de séquences récurrentes (LCS) pour Chrétien de Troyes et génération des rapports finaux")
    
   # Construction du rapport final
    lcs_content = analyse_auteur('Chrétien de Troyes', clean_txt_dir, dico_author)
    rapport_auteurs_final = r"/workspaces/medFR-paleao-NLP/results/rapports/rapport-auteurs.html"
   
    print("Expériences dans result_auteurs :", list(result_auteurs.keys())) # trace à effacer 

    generate_combined_report_html(
        resultats=result_genre,
        biblio=dico_genre,
        output_path=genre_report_path,
        mode='genre',
        titre='Analyse par Genre'
        )
    
    generate_combined_report_html(
        resultats=result_auteurs,
        biblio=dico_author,
        output_path=rapport_auteurs_final,
        mode='auteurs',
        lcs_content=lcs_content,
        titre='Analyse par Auteurs'
        )
    
    generate_combined_report_html(
        resultats=result_epoque,
        biblio=dico_date,
        output_path=dates_report_path,
        mode='dates',
        titre='Analyse par Epoques'
        )


    print("Fin de la pipeline d'analyse de corpus médiévaux.")
    
 
