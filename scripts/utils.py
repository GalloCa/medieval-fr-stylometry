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