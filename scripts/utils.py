"""
Module utilitaire pour le traitement des métadonnées et la gestion des fichiers

Ce script contient des fonctions auxiliaires utilisées à travers l'ensemble de la pipeline
pour charger les dictionnaires, nettoyer les étiquettes ou exporter des matrices au format .tsv.
"""


# MODULE
import os

# FONCTIONS
def load_biblio(path):
   """
   Charge un fichier de metadonnées et le transforme en dictionnaire.
   Le fichier est formaté comme ceci : NomDuTexte : Catégorie

   Entrée : 
        path (str) : le chemin absolu ou relatif du fichier de métadonnées

   Sortie : 
        dict : une dictionnaire  associant le nom de l'oeuvre à sa métadonnées{ 'Oeuvre' : 'Genre'}

   """
   biblio = {}
   with open(path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
   return biblio

def clean_label(name):
    """
    Nettoyage des étiquettes de fichiers pour isoler le nom du texte.
    Suppression des préfixes techniques liés au filtrage des fréquences et des extensions
    de fichiers.

    Entrée :
        name (str) : Le nom original de la colonne ou du fichier à nettoyer.

    Sortie :
        str : Le nom du texte nettoyé (ex : 'clean-Yvain.txt' devient 'Yvain')
    """
    for prefix in ['freq-', 'clean-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def save_matrix_tsv(matrix, lexique, txt_names, output_path):
    """
    Sauvegarde la matrice Numpy en mémoire vers un fichier TSV. Structuré sous la forme
    noms de textes pour les colonnes et n-grammes sur les lignes.

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        lexique (list): la liste ordonnée de tous les n-grammes du corpus
        txt_names (list) : liste des noms de textes 
        output_path (str) : le chemin de sauvegarde du fichier .tsv
         
    Sortie : 
        Génération et sauvegarde du fichier .tsv
    """
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write("ngramme\t" + "\t".join(txt_names) + "\n")
        
        for i, ngram in enumerate(lexique):
            values = "\t".join(map(str, matrix[i, :]))
            f.write(f"{ngram}\t{values}\n")
            
    print(f"Matrice globale sauvegardée avec succès dans : {output_path}")