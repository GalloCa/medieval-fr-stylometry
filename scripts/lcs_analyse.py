from utils import load_biblio
import os 
from difflib import SequenceMatcher

biblio_author_dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"

def lcs(t1, t2):
    """
    Algorithme LCS ultra-optimisé en RAM et en temps de calcul, 
    sans aucune librairie externe. Compare des mots entiers.
    """
    mots1 = t1.split()
    mots2 = t2.split()
    
    positions_t2 = {}
    for i, mot in enumerate(mots2):
        if mot not in positions_t2:
            positions_t2[mot] = []
        positions_t2[mot].append(i)
        
    longest = 0
    end_idx = 0
    
    suivi_longueurs = {} 
    
    
    for i, mot in enumerate(mots1):
        nouveau_suivi = {}
        if mot in positions_t2:
            for j in positions_t2[mot]:
                longueur_actuelle = suivi_longueurs.get(j - 1, 0) + 1
                nouveau_suivi[j] = longueur_actuelle
                
                if longueur_actuelle > longest:
                    longest = longueur_actuelle
                    end_idx = i
                    
        suivi_longueurs = nouveau_suivi

    if longest == 0:
        return ""
  
    mots_communs = mots1[end_idx - longest + 1 : end_idx + 1]
    return " ".join(mots_communs)


def analyse_auteur(auteur, texte_dir, dico_author):
    fichiers_auteur = []

    for filename in os.listdir(texte_dir):
        if filename.endswith(".txt"):   
            nom_original = filename.replace("clean-", "").replace(".txt", "")
            auteur_trouve = dico_author.get(nom_original, "").strip()
            if auteur_trouve == auteur.strip():
                fichiers_auteur.append(filename)

    if len(fichiers_auteur) < 2:
        return f"Il faut au moins 2 textes pour faire une comparaison !"
    
    # Chargement des fichiers    
    textes = {}
    for f in fichiers_auteur:
        chemin = os.path.join(texte_dir, f)
        with open(chemin, 'r', encoding='utf-8') as file:
            textes[f] = file.read()

    report_lignes = [f"## 5. LCS - Séquences récurrentes de {auteur} \n"]  
    report_lignes.append(f"Séquences de mots exactes partagées entre ses oeuvres : \n")  

    # Comparaison des textes 2 à 2
    for i in range(len(fichiers_auteur)):
        for j in range(i + 1, len(fichiers_auteur)):
            file1 = fichiers_auteur[i]
            file2 = fichiers_auteur[j]
            nom1 = file1.replace("clean-", "").replace(".txt", "")
            nom2 = file2.replace("clean-", "").replace(".txt", "")
            
            lcs_ct = lcs(textes[file1], textes[file2])

            if len(lcs_ct) > 10:
                report_lignes.append(f"- **{nom1}** et **{nom2}** ({len(lcs_ct)} caractères) :")
                report_lignes.append(f" > «  *{lcs_ct}* »\n")

    return "\n".join(report_lignes)    


