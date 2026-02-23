import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import MDS

def clean_label(name):
    """
    Nettoyage des labels de fichiers pour isoler le nom du texte.
    Suppression des préfixes techniques liés au filtrage des fréquences et des extensions
    de fichiers.

    Entrée:
        name (str) : Le nom original de la colone ou du fichier à nettoyer.

    Sortie :
        str : Le nom du texte nettoyé 
    """
    for prefix in ['freq-filtered-', 'freq-', 'filtered-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def similarities_genre(matrix_path, dico_path, output_dir):
    """
    Analyse et visualisations des similarités des textes avec cosinus.
    Calcul de la similarité cosinus entre les vecteurs de n-grammes des textes. 
    Génération d'un nuage de point coloré par catégorie.

    Entrées :
        matrix_path (str) : chemin vers la matrice de fréquence (format TSV)
        dico_path (str) : chemin du fichier texte des métadonnées
        output_dir (str) : dossier de sortie pour la sauvegarde de l'image   
    Sortie :
        image : nuage de point des similarités en cosinus
    """
    # Création du dictionnaire clé = texte : valeur = genre
    biblio = {}
    try:
        with open(dico_path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
    except Exception as e:
        return
    
    # Calcul du positionnement 2D (MDS)
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    # Appel de la fonction de nettoayge des labels
    df.columns = [clean_label(col) for col in df.columns]

    df_transposed = df.T
    sim_matrix = cosine_similarity(df_transposed)
    dissimilarity = 1 - sim_matrix

    mds = MDS(n_components=2, metric=True, n_init=4, init='random', random_state=42)
    pos = mds.fit_transform(dissimilarity)
    
    color_map = {
    'Didactique': '#E74C3C',      
    'Roman courtois': '#3498DB',        
    'Antique': "#FCD435",        
    'Hagiographie': '#2ECC71', 
    'Epique': '#9B59B6',
    'Prose': "#FA8806",
    'Jugement d\'amour': "#FC4EA5",         
    }

    # Création du Nuage de Points
    plt.figure(figsize=(15, 10))
    
    for i, txt in enumerate(df.columns):
        cat = biblio.get(txt, 'Genre inconnu')
        couleur = color_map.get(cat, '#BDC3C7')

        plt.scatter(pos[i, 0], pos[i, 1], c=couleur, 
            s=150, edgecolors='black', 
            label=cat if cat not in plt.gca().get_legend_handles_labels()[1] else "")
        
        plt.annotate(txt, 
                     (pos[i, 0], 
                      pos[i, 1]), 
                      xytext=(7, 7), 
                      textcoords='offset points', 
                      fontsize=11, 
                      fontweight='bold')

    plt.title("Proximité des textes par genres - Similarité Cosinus")
    plt.legend(title='Genres', loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(True, linestyle='--', alpha=0.6)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "nuage_points_genre.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graphique généré avec succès : {output_path}")



def similarities_dates(matrix_path, dico_path, output_dir):
    # Création du dictionnaire clé = texte : valeur = genre
    biblio = {}
    try:
        with open(dico_path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
    except Exception as e:
        return
    
    # Calcul du positionnement 2D (MDS)
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    df.columns = [clean_label(col) for col in df.columns]

    df_transposed = df.T
    sim_matrix = cosine_similarity(df_transposed)
    dissimilarity = 1 - sim_matrix

    mds = MDS(n_components=2, metric=True, n_init=4, init='random', random_state=42)
    pos = mds.fit_transform(dissimilarity)
    
    color_map = {
    '11e': '#E74C3C',      
    '12e': '#3498DB',        
    '13e': "#FCD435",        
    '14e': '#2ECC71', 
    '15e': '#9B59B6',       
    }

    # Création du Nuage de Points
    plt.figure(figsize=(15, 10))
    
    for i, txt in enumerate(df.columns):
        cat = biblio.get(txt, 'Genre inconnu')
        couleur = color_map.get(cat, '#BDC3C7')

        plt.scatter(pos[i, 0], pos[i, 1], c=couleur, 
            s=150, edgecolors='black', 
            label=cat if cat not in plt.gca().get_legend_handles_labels()[1] else "")
        
        plt.annotate(txt, 
                     (pos[i, 0], 
                      pos[i, 1]), 
                      xytext=(7, 7), 
                      textcoords='offset points', 
                      fontsize=11, 
                      fontweight='bold')

    plt.title("Proximité des textes par dates - Similarité Cosinus")
    # plt.xlabel("Dimension 1")
    # plt.ylabel("Dimension 2")
    plt.legend(title='Dates', loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(True, linestyle='--', alpha=0.6)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "nuage_points_dates.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graphique généré avec succès : {output_path}")

def similarities_authors(matrix_path, dico_path, output_dir):
    # Création du dictionnaire clé = texte : valeur = genre
    biblio = {}
    try:
        with open(dico_path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
    except Exception as e:
        return
    
    # Calcul du positionnement 2D (MDS)
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    df.columns = [clean_label(col) for col in df.columns]

    df_transposed = df.T
    sim_matrix = cosine_similarity(df_transposed)
    dissimilarity = 1 - sim_matrix

    mds = MDS(n_components=2, metric=True, n_init=4, init='random', random_state=42)
    pos = mds.fit_transform(dissimilarity)
    
    color_map = {
    'Anonyme': '#E74C3C',      
    'Benoît de Saint-Maure': '#3498DB',        
    'Adenet le Roi': "#FCD435",        
    'Chrétien de Troyes': '#2ECC71', 
    'Raoul de Houdenc': '#9B59B6',
    'Jean Renart': "#FA8806",
    'Jacques de Vitry': "#FC4EA5",         
    }

    # Création du Nuage de Points
    plt.figure(figsize=(15, 10))
    
    for i, txt in enumerate(df.columns):
        cat = biblio.get(txt, 'Genre inconnu')
        couleur = color_map.get(cat, '#BDC3C7')

        plt.scatter(pos[i, 0], pos[i, 1], c=couleur, 
            s=150, edgecolors='black', 
            label=cat if cat not in plt.gca().get_legend_handles_labels()[1] else "")
        
        plt.annotate(txt, 
                     (pos[i, 0], 
                      pos[i, 1]), 
                      xytext=(7, 7), 
                      textcoords='offset points', 
                      fontsize=11, 
                      fontweight='bold')

    plt.title("Proximité des textes par auteurs - Similarité Cosinus")
    # plt.xlabel("Dimension 1")
    # plt.ylabel("Dimension 2")
    plt.legend(title='Auteurs', loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(True, linestyle='--', alpha=0.6)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "nuage_points_auteurs.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graphique généré avec succès : {output_path}")



# MAIN 
path_matrix = "/workspaces/medFR-paleao-NLP/results/np_matrix.tsv"
path_dic_genre ="/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
path_dic_dates = "/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"
path_dic_authors = "/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
path_out_dir = "/workspaces/medFR-paleao-NLP/results/scatter-plots"

similarities_genre(path_matrix, path_dic_genre, path_out_dir)
similarities_dates(path_matrix,path_dic_dates, path_out_dir)
similarities_authors(path_matrix, path_dic_authors, path_out_dir)