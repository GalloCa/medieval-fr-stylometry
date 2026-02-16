import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import MDS

def clean_label(name):
    for prefix in ['freq-filtered-', 'freq-', 'filtered-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def analyze_similarities(matrix_path, output_dir):
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    df.columns = [clean_label(col) for col in df.columns]

    groups = {
    'DancusM': 'Médical',
    'AlexisOctP': 'Hagiographie', 'AlexisP11': 'Hagiographie', 
    'AlexisP13': 'Hagiographie', 'AlexisPQ': 'Hagiographie', 
    'AlexisPRI': 'Hagiographie', 'SGeorgDeG': 'Hagiographie',
    'SGeorgVosL': 'Hagiographie',
    'ThebesC': 'Antique', 'BenTroieC_1partial': 'Antique', 
    'BenTroieC_4partial': 'Antique',
    'Yvain': 'Roman', 'Cliges': 'Roman', 'ErecF': 'Roman', 
    'LancJ': 'Roman', 'PercevalKu': 'Roman', 'MeraugisF': 'Roman', 
    'JugAmD': 'Roman', 'OmbreB2': 'Roman',
    'UnicornecW': 'Didactique', 'AigarB': 'Epique'
    }

    color_map = {
    'Médical': '#E74C3C',      
    'Roman': '#3498DB',        
    'Antique': '#F1C40F',        
    'Hagiographie': '#2ECC71', 
    'Epique': '#9B59B6',
    'Didactique': '#9B59B6'         
    }

    df_transposed = df.T
    sim_matrix = cosine_similarity(df_transposed)
    dissimilarity = 1 - sim_matrix
    
    # Calcul du positionnement 2D (MDS)
    
    mds = MDS(n_components=2, metric=True, n_init=4, init='random', random_state=42)
    pos = mds.fit_transform(dissimilarity)
    
    # Création du Nuage de Points
    plt.figure(figsize=(15, 10))
    
    for i, txt in enumerate(df.columns):
        cat = groups.get(txt, 'Genre')
        couleur = color_map.get(cat)

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

    plt.title("Nuage de points : Proximité des textes (MDS sur Similarité Cosinus)")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.legend(title='Genres', loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.6)

    
    output_path = os.path.join(output_dir, "nuage_points_noms_propres.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Graphique généré avec succès : {output_path}")

# MAIN 

analyze_similarities("/workspaces/medFR-paleao-NLP/data/matrice.tsv", 
                              "/workspaces/medFR-paleao-NLP/data")