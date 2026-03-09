import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import MDS
from adjustText import adjust_text
import numpy as np
from metrics import cos_np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

def clean_label(name):
    for prefix in ['freq-filtered-', 'freq-', 'filtered-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def generate_similarity_plot(matrix_path, dico_path, output_dir, mode='genre'):
    # 1. Chargement des métadonnées
    biblio = {}
    try:
        with open(dico_path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
    except Exception as e:
        print(f"Erreur lecture dico: {e}")
        return

    # 2. Traitement des données
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    df = df.dropna(axis=1, how="all")
    df = df.fillna(0)
    df.columns = [clean_label(col) for col in df.columns]
    
    # Calcul MDS
    nb_txt = len(df.columns)
    dissimilarity = np.zeros((nb_txt, nb_txt))

    for i in range(nb_txt):
        for j in range(nb_txt):
            if i!=j:
                v1 = df.iloc[:,i].values
                v2 = df.iloc[:,j].values
                
                dist = max(0.0, 1.0 - cos_np(v1,v2))
                dissimilarity[i,j] = dist
                dissimilarity[j,i] = dist
    
    mds = MDS(n_components=2, metric=True, n_init=4, random_state=42, dissimilarity='precomputed' )
    pos = mds.fit_transform(dissimilarity)
    """
    df_transposed = df.T
    sim_matrix = cosine_similarity(df_transposed)
    dissimilarity = 1 - sim_matrix
    mds = MDS(n_components=2, metric=True, n_init=4, init='random', random_state=42)
    pos = mds.fit_transform(dissimilarity)
    """

    # 3. Configuration esthétique
    configs = {
        'genre':  {'title': 'par genres', 'file': 'genre.png', 'legend': 'Genres'},
        'dates':  {'title': 'par dates', 'file': 'dates.png', 'legend': 'Dates'},
        'auteurs':{'title': 'par auteurs', 'file': 'auteurs.png', 'legend': 'Auteurs'}
    }
    conf = configs.get(mode)
    
    color_maps = {
        'genre': {'Didactique': '#E74C3C', 'Roman courtois': '#3498DB', 'Antique': "#FCD435", 
                  'Hagiographie': '#2ECC71', 'Epique': '#9B59B6', 'Prose': "#FA8806", "Jugement d'amour": "#FC4EA5"},
        'dates': {'XIe siècle': '#E74C3C', 'XIIe siècle': '#3498DB', 'XIIIe siècle': "#FCD435", 'XIVe siècle': '#2ECC71', 'XVe siècle': '#9B59B6'},
        'auteurs': {'Anonyme': '#E74C3C', 'Benoît de Saint-Maure': '#3498DB', 'Adenet le Roi': "#FCD435", 
                    'Chrétien de Troyes': '#2ECC71', 'Raoul de Houdenc': '#9B59B6', 'Jean Renart': "#FA8806", 'Jacques de Vitry': "#FC4EA5"}
    }
    current_map = color_maps.get(mode, {})

    # 4. Création du graphique avec marges forcées
    fig, ax = plt.subplots(figsize=(14, 9), dpi=100)
    
    # On bloque les marges : right=0.75 laisse 25% de l'image à la légende
    fig.subplots_adjust(right=0.75, left=0.1, top=0.88, bottom=0.1)
    
    ax.spines[['top', 'right']].set_visible(False)
    
    texts = []
    handles_labels = {} 

    for i, txt in enumerate(df.columns):
        cat = biblio.get(txt, 'Inconnu')
        couleur = current_map.get(cat, '#BDC3C7')

        scatter = ax.scatter(pos[i, 0], pos[i, 1], c=couleur, s=180, 
                             edgecolors='white', linewidth=0.8, alpha=0.85)
        
        if cat not in handles_labels:
            handles_labels[cat] = scatter

        texts.append(ax.text(pos[i, 0], pos[i, 1], txt, fontsize=9, fontweight='medium'))

    # 5. Ajustement des labels
    adjust_text(texts, 
                x = pos[:,0],
                y = pos[:,1],
                force_text=(1.5, 2.0),
                force_points=(2.0, 2.5),
                expand_points = (1.8, 1.8))
    
    # Paramètre légende
    ordered_labels = [cat for cat in current_map.keys() if cat in handles_labels]
    ordered_labels += [cat for cat in handles_labels.keys() if cat not in current_map]
    ordered_handels = [handles_labels[cat] for cat in ordered_labels] 

    ax.legend(ordered_handels, ordered_labels,
              title=conf['legend'], 
              title_fontsize='12',
              fontsize='10',
              loc='center left', 
              bbox_to_anchor=(1.05, 0.5),
              frameon=False,
              labelspacing=1.5)

    # Titre 
    ax.set_title(f"Proximité des textes {conf['title']} - Similarité Cosinus", 
                 loc='left', fontsize=16, pad=25, color='#333333', fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.2)

    # 6. Sauvegarde
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"nuage_points_{conf['file']}")
    
    # On NE met PAS bbox_inches='tight' pour garder nos marges de subplots_adjust
    fig.savefig(output_path, dpi=300)
    plt.close(fig) 
    print(f"Scatter Plot généré avec succès : {output_path}")


def generate_dendogramme(matrix_path,dico_path, output_dir):
    """
    """
    biblio = {}
    try:
        with open(dico_path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
    except Exception as e:
        print(f"Erreur lecture dico: {e}")
        return
    
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    df = df.dropna(axis=1, how="all")
    df = df.fillna(0)
    df.columns = [clean_label(col) for col in df.columns]

    anonym = [col for col in df.columns if biblio.get(col) == 'Anonyme']
    if len(anonym) <2:
        print("Pas assez de textes d'auteus anonyms pour faire un arbre")
        return
    
    df_anonym = df[anonym]
    nb_txt = len(df_anonym.columns)
    dissimilarity = np.zeros((nb_txt, nb_txt))

    for i in range(nb_txt):
        for j in range(nb_txt):
            if i!=j:
                v1 = df.iloc[:,i].values
                v2 = df.iloc[:,j].values
                
                dist = max(0.0, 1.0 - cos_np(v1,v2))
                dissimilarity[i,j] = dist
                dissimilarity[j,i] = dist
    condensed_dist = squareform(dissimilarity)
    z = linkage(condensed_dist, method='average')

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    dendro = dendrogram(z,
                        labels = df_anonym.columns,
                        orientation = 'top',
                        leaf_rotation=90,
                        leaf_font_size=11,
                        color_threshold=0.15,
                        ax=ax)
    
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    ax.set_title(f"Dendogramme des textes d'auteurs anonymes", loc='left', fontsize=16, pad=20, color='#333333', fontweight='bold')

    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"dendogramme_anonymes.png")
    fig.subplots_adjust(left=0.08, right=0.95, top=0.85, bottom=0.25)
    fig.savefig(output_path, dpi=300)
    plt.close(fig) 
    print(f"Dendogramme généré avec succès : {output_path}")



# Exemple d'appel pour tes 3 fonctions d'origine :
path_matrix = "/workspaces/medFR-paleao-NLP/results/matrix/matrix.tsv"
path_dic_genre ="/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
path_dic_dates = "/workspaces/medFR-paleao-NLP/data/metadata/dico_date.txt"
path_dic_authors = "/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
path_out_dir = "/workspaces/medFR-paleao-NLP/results/scatter-plots"


"""generate_similarity_plot(path_matrix, path_dic_genre, path_out_dir, mode='genre')
generate_similarity_plot(path_matrix, path_dic_dates, path_out_dir, mode='dates')
generate_similarity_plot(path_matrix, path_dic_authors, path_out_dir, mode='auteurs')"""
generate_dendogramme(path_matrix, path_dic_authors, path_out_dir)