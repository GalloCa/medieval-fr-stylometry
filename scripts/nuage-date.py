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


def analyze_similarities(matrix_path, dico_path, output_dir):
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

# MAIN 


analyze_similarities("/workspaces/medFR-paleao-NLP/data/matrice.tsv", 
                     "/workspaces/medFR-paleao-NLP/data/dico_date.txt",
                              "/workspaces/medFR-paleao-NLP/data")