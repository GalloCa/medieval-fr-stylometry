"""
Génération de graphique et visualisation du corpus 

Ce script prend en charge la représentation visuelle des résultats de l'analyse.
Il transforme les matrices de distances mathématiques en graphiques.

Il génère :
    1. des nuages de points via MDS, afin d'observer la proximité des textes selon le 
        genres, époque ou auteurs.
    2. Des dendogrammespour analyser les regroupements spécifiques en fonction des auteurs anomynes.

Dépendances :
    - matplotlib.pyplot : création, mise en forme et sauvegarde des graphes.
    - sklearn.manifold (MDS) : réduction de dimension (passage de N-dimensions à 2D)
    - scipy.cluster  / scipy.spatial : outils pour le clustering hiérarchique
    - adjustText : optimisation de l'affichage des étiquettes (anti-chevauchement)
    - metrics : script contenant la fonctions personnalisée de calcul de 
                similarité (cos_np)
"""
# MODULES
import os
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from adjustText import adjust_text
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from metrics import cos_np


# FONCTIONS
def generate_similarity_plot(matrix, txt_names, biblio, output_dir, mode='genre'):
    """
    Génère un nuage de points en deux dimensions illustrant la proximité
    stylistique entre deux textes du corpus.

    Entrées : 
        matrix(np.ndarray) : matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}
        output_dir (str) : le chemin du dossier où sauvegarder l'image générée
        mode (str, optionnel) : mode de coloration des points. 
                                Accepte 'genre', 'dates' ou 'auteurs'.
                                Par défaut 'genre'.
    Sortie : 
        image (.png) : nuage de point dans le répertoire cible
    """
    # Calcul MDS
    nb_txt = len(txt_names)
    dissimilarity = np.zeros((nb_txt, nb_txt))

    for i in range(nb_txt):
        for j in range(nb_txt):
                v1 = matrix[:,i]
                v2 = matrix[:,j]
                
                dist = max(0.0, 1.0 - cos_np(v1,v2))
                dissimilarity[i,j] = dist
                dissimilarity[j,i] = dist
    
    mds = MDS(n_components=2, metric=True, n_init=4, random_state=42, dissimilarity='precomputed' )
    pos = mds.fit_transform(dissimilarity)
  
    # Configuration esthétique
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

    # Marges forcées
    fig, ax = plt.subplots(figsize=(14, 9), dpi=100)
    fig.subplots_adjust(right=0.75, left=0.1, top=0.88, bottom=0.1)
    
    ax.spines[['top', 'right']].set_visible(False)
    
    texts = []
    handles_labels = {} 

    for i, txt in enumerate(txt_names):
        cat = biblio.get(txt, 'Inconnu')
        couleur = current_map.get(cat, '#BDC3C7')

        scatter = ax.scatter(pos[i, 0], pos[i, 1], c=couleur, s=180, 
                             edgecolors='white', linewidth=0.8, alpha=0.85)
        
        if cat not in handles_labels:
            handles_labels[cat] = scatter

        texts.append(ax.text(pos[i, 0], pos[i, 1], txt, fontsize=9, fontweight='medium'))

    # Ajustement des labels
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

    # Sauvegarde
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"nuage_points_{conf['file']}")
    
    fig.savefig(output_path, dpi=300)
    plt.close(fig) 
    print(f"Scatter Plot généré avec succès : {output_path}")


def generate_dendogramme(matrix, txt_names, biblio, output_dir):    
    """
    Génère un dendogramme illustrant les regroupements stylistiques 
    au sein du sous-corpus des textes d'auteurs 'Anonyme'

    Calcule leur matrice de dissimilarité, puis applique un algorithme de clustering 
    ascendant.

    Entrées : 
        matrix(np.ndarray) : matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}
        output_dir (str) : le chemin du dossier où sauvegarder l'image générée
    Sortie : 
        image (.png) : le dendogramme dans le répertoire cible

    """
    # Cherche les textes avec l'étiquette "Anonyme"
    anonym = [i for i, name in enumerate(txt_names) if biblio.get(name) == 'Anonyme']
    anonym_names = [txt_names[i] for i in anonym]

    if len(anonym) <2:
        print("Pas assez de textes d'auteus anonymes pour faire un arbre")
        return
    
    nb_txt = len(anonym)
    dissimilarity = np.zeros((nb_txt, nb_txt))

    for i in range(nb_txt):
        for j in range(nb_txt):
            if i!=j:
                v1 = matrix[:,anonym[i]]
                v2 = matrix[:,anonym[j]]
                dist = max(0.0, 1.0 - cos_np(v1,v2))
                dissimilarity[i,j] = dist
                dissimilarity[j,i] = dist

    condensed_dist = squareform(dissimilarity)
    z = linkage(condensed_dist, method='average')

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    dendro = dendrogram(z,
                        labels = anonym_names,
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


