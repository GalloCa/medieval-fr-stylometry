import os
import re


def load_biblio(path):
   """
   Charge un fichier de metadonné et le transforme en dictionnaire

   Arguments : 
    path (str) : le chemin du fichier de métadonnée

   Return : 
    dict : une dictionnaire { 'Oeuvre' : 'Genre'}

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
    Nettoyage des labels de fichiers pour isoler le nom du texte.
    Suppression des préfixes techniques liés au filtrage des fréquences et des extensions
    de fichiers.

    Entrée:
        name (str) : Le nom original de la colonne ou du fichier à nettoyer.

    Sortie :
        str : Le nom du texte nettoyé (ex : )
    """
    for prefix in ['freq-', 'clean-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def save_matrix_tsv(matrix, lexique, txt_names, output_path):
    """
    Sauvegarde la matrice Numpy en mémoire vers un fichier TSV 

    Arguments :

    Returns : 
    """
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    with open(output_path, mode='w', encoding='utf-8') as f:
        # 1. L'en-tête (Les noms des textes en colonnes)
        f.write("ngramme\t" + "\t".join(txt_names) + "\n")
        
        # 2. Les lignes (Le n-gramme + ses fréquences pour chaque texte)
        for i, ngram in enumerate(lexique):
            values = "\t".join(map(str, matrix[i, :]))
            f.write(f"{ngram}\t{values}\n")
            
    print(f"Matrice globale sauvegardée avec succès dans : {output_path}")