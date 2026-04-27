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
from analyse import cos_np


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
        for j in range(i + 1,nb_txt):
                v1 = matrix[:,i]
                v2 = matrix[:,j]
                
                dist = max(0.0, 1.0 - cos_np(v1,v2))
                dissimilarity[i,j] = dist
                dissimilarity[j,i] = dist
 
    # Configuration esthétique
    configs = {
        'genre':  {'title': 'par genres', 'file': 'genre.png', 'legend': 'Genres'},
        'dates':  {'title': 'par dates', 'file': 'dates.png', 'legend': 'Dates'},
        'auteurs':{'title': 'par auteurs', 'file': 'auteurs.png', 'legend': 'Auteurs'}
    }
   
    
    if mode not in configs:
        print(f"generate_similarity_plot : mode '{mode}' invalide. Choix : genre, dates, auteurs.")
        return
    conf = configs[mode]

    if nb_txt < 3:
        print(f"generate_similarity_plot : pas assez de textes ({nb_txt}) pour un MDS (minimum 3).")
        return
    try:
        mds = MDS(n_components=2, metric='precomputed', init='classical_mds', metric_mds=True, n_init=1, random_state=42, )
        pos = mds.fit_transform(dissimilarity)
    except Exception as e:
        print(f"Erreur MDS ({mode}) : {e}")
        return
    
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
    #  Nuage de points
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

 
def export_gephi_files(compare_tsv_path, biblio_list, output_dir,
                       threshold_cos=0.3, threshold_jac=0.0):
    """
    Génère deux fichiers CSV pour Gephi depuis le .tsv de comparaison par paires.
    
    Le fichier nodes.csv associe chaque texte à ses métadonnées (une ligne par nœud).
    Le fichier edges.csv liste les arêtes filtrées par seuil (une ligne par paire).
    
    Les arêtes sont filtrées pour ne conserver que les liens significatifs,
    afin d'éviter un graphe trop dense (25 nœuds = 300 arêtes potentielles).
    
    Entrées :
        compare_tsv_path (str) : chemin vers le .tsv produit par compare_files()
                                colonnes attendues : Texte A | Texte B | Cosinus | Jaccard
        biblio_list (list[dict]) : liste de dicts {nom_texte: catégorie} pour les métadonnées ex : [dico_genre, dico_author, dico_date]
                                    chaque dict ajoute une colonne dans nodes.csv
        output_dir (str) : dossier de sortie pour nodes.csv et edges.csv
        threshold_cos (float): seuil minimum de similarité cosinus (défaut : 0.3) les arêtes en dessous sont ignorées
        threshold_jac (float) : seuil minimum pour Jaccard (défaut : 0.0, pas de filtre)
    
    Sorties :
        fichier nodes.csv : Id | Label | genre | auteur | date  (selon biblio_list)
        fichier edges.csv : Source | Target | Weight | jaccard | Type
    """
    if not os.path.exists(compare_tsv_path):
        print(f"export_gephi_files : fichier introuvable ({compare_tsv_path})")
        return
    
        # Lecture du .tsv
    paires = []
    noms   = set()
    
    with open(compare_tsv_path, mode='r', encoding='utf-8') as f:
        next(f)    # skip header
        for ligne in f:
            parts = ligne.strip().split('\t')
            if len(parts) < 4:
                continue
            t1, t2 = parts[0].strip(), parts[1].strip()
            try:
                cos = float(parts[2].strip())
                jac = float(parts[3].strip())
            except ValueError:
                continue
    
            noms.add(t1)
            noms.add(t2)
    
            # Filtre par seuil
            if cos >= threshold_cos and jac >= threshold_jac:
                paires.append((t1, t2, cos, jac))
    
        if not paires:
            print(f"export_gephi_files : aucune arête après filtrage "
                f"(seuil cosinus={threshold_cos}, jaccard={threshold_jac}). "
                f"Essaie un seuil plus bas.")
            return
    
        os.makedirs(output_dir, exist_ok=True)
    
        # Préparation du fichier nodes.csv 
        # En-tête dynamique selon les dicts fournis dans biblio_list
        col_names = ['genre', 'auteur', 'date'][:len(biblio_list)]
        nodes_path = os.path.join(output_dir, 'nodes.csv')
    
        with open(nodes_path, mode='w', encoding='utf-8') as f:
            header = 'Id;Label;' + ';'.join(col_names)
            f.write(header + '\n')
    
            for nom in sorted(noms):
                meta = [d.get(nom, 'Inconnu') for d in biblio_list]
                ligne = f'{nom};{nom};' + ';'.join(meta)
                f.write(ligne + '\n')
    
        print(f"nodes.csv généré : {nodes_path} ({len(noms)} nœuds)")
    
        # Préparation du fichier edges.csv 
        edges_path = os.path.join(output_dir, 'edges.csv')
    
        with open(edges_path, mode='w', encoding='utf-8') as f:
            f.write('Source;Target;Weight;jaccard;Type\n')
            for t1, t2, cos, jac in paires:
                f.write(f'{t1};{t2};{cos:.4f};{jac:.4f};Undirected\n')
    
        print(f"edges.csv généré  : {edges_path} ({len(paires)} arêtes, "
            f"seuil cosinus >= {threshold_cos})")

        




