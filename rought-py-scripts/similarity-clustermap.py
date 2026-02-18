import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

def generate_cluster_analysis(matrix_path, output_image_path):
    # 1. Chargement de la matrice comparative
    # On met l'index sur 'ngramme'
    df = pd.read_csv(matrix_path, sep='\t', index_col='ngramme')
    
    # 2. Transposition de la matrice
    # On veut comparer les fichiers (colonnes), donc on transpose pour les avoir en lignes
    # Car cosine_similarity compare les lignes d'un tableau
    df_transposed = df.T
    
    # 3. Calcul de la similarité cosinus
    # On obtient une matrice carrée (fichiers x fichiers)
    sim_matrix = cosine_similarity(df_transposed)
    
    # Transformation en DataFrame pour la lisibilité
    sim_df = pd.DataFrame(sim_matrix, index=df_transposed.index, columns=df_transposed.index)
    
    # 4. Génération de la Clustermap
    # On utilise 'viridis' ou 'YlGnBu' pour une bonne lisibilité en BioNLP
    plt.figure(figsize=(12, 10))
    g = sns.clustermap(sim_df, 
                       cmap='viridis', 
                       annot=True, # Affiche les scores de 0 à 1
                       fmt=".2f",
                       linewidths=.5,
                       figsize=(12, 12))
    
    plt.title("Cluster Map des Similarités Cosinus (N-grammes)")
    
    # 5. Sauvegarde de l'image
    plt.savefig(output_image_path)
    print(f"✅ Cluster Map générée : {output_image_path}")
    return sim_df

# --- EXÉCUTION ---
matrix_file = r"/workspaces/medFR-paleao-NLP/data/matrice.tsv"
output_viz = r"/workspaces/medFR-paleao-NLP/data/cluster_map_similarites.png"

# On lance l'analyse
similarity_results = generate_cluster_analysis(matrix_file, output_viz)