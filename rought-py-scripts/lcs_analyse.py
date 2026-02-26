from tools import (biblio)
import os 
from difflib import SequenceMatcher

biblio_author_dir = r"/workspaces/medFR-paleao-NLP/data/metadata/dico_auteur.txt"
txt_dir = r"/workspaces/medFR-paleao-NLP/data/clean-txt"

def lcs(t1,t2):
    m = [[0] * (1+len(t2)) for _ in range(1 + len(t1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(t1)):
        for y in range(1, 1 + len(t2)):
            if t1[x-1] == t2[y-1]:
                m[x][y] = m[x-1][y-1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return t1[x_longest - longest: x_longest]

def analyse_auteur(auteur, texte_dir, biblio_author_dir):
    dico_author = biblio(biblio_author_dir)
    fichiers_auteur = []

    for filename in os.listdir(texte_dir):
        if filename.endswith(".txt"):   
            nom_original = filename.replace("clean-", "").replace(".txt", "")
            auteur_trouve = dico_author.get(nom_original, "").strip()
            if auteur_trouve == auteur.strip():
                fichiers_auteur.append(filename)
    if len(fichiers_auteur) < 2:
        print("❌ Il faut au moins 2 textes pour faire une comparaison !")
        return

    # 3. Charger le contenu des textes en mémoire
    textes = {}
    for f in fichiers_auteur:
        chemin = os.path.join(texte_dir, f)
        with open(chemin, 'r', encoding='utf-8') as file:
            textes[f] = file.read()
            
    # 4. Comparer les textes 2 à 2
    print("\n⏳ Début du calcul LCS (cela peut prendre quelques minutes)...")
    for i in range(len(fichiers_auteur)):
        for j in range(i + 1, len(fichiers_auteur)):
            nom1 = fichiers_auteur[i]
            nom2 = fichiers_auteur[j]
            
            print(f"\n⚔️  Comparaison : {nom1} vs {nom2}")
            lcs_ct = lcs_maison(textes[nom1], textes[nom2])
            
            print(f"   -> Séquence commune ({len(lcs_ct)} caractères) :")
            print(f"   « {lcs_ct} »")


def lcs_optimise(t1, t2):
    """
    Trouve la plus longue séquence commune en comparant des mots entiers.
    """
    # 1. On découpe les textes en listes de MOTS
    mots1 = t1.split()
    mots2 = t2.split()
    
    # 2. On compare les listes avec autojunk=False pour ne rien ignorer
    match = SequenceMatcher(None, mots1, mots2, autojunk=False).find_longest_match(0, len(mots1), 0, len(mots2))
    
    # 3. On recolle les mots correspondants pour former une vraie phrase
    phrase_commune = " ".join(mots1[match.a : match.a + match.size])
    
    return phrase_commune

def lcs_maison(t1, t2):
    """
    Algorithme LCS ultra-optimisé en RAM et en temps de calcul, 
    sans aucune librairie externe. Compare des mots entiers.
    """
    mots1 = t1.split()
    mots2 = t2.split()
    
    # Étape 1 : On crée un "index" des positions des mots du Texte 2.
    # C'est comme l'index à la fin d'un livre, ça permet de chercher très vite.
    positions_t2 = {}
    for i, mot in enumerate(mots2):
        if mot not in positions_t2:
            positions_t2[mot] = []
        positions_t2[mot].append(i)
        
    longest = 0
    end_idx = 0
    
    # Ce dictionnaire ne garde en mémoire QUE la longueur des phrases 
    # en cours de correspondance. Adieu la matrice géante !
    suivi_longueurs = {} 
    
    # Étape 2 : On lit le Texte 1 mot par mot
    for i, mot in enumerate(mots1):
        nouveau_suivi = {}
        # Si le mot existe dans le Texte 2
        if mot in positions_t2:
            # On regarde toutes ses positions dans le Texte 2
            for j in positions_t2[mot]:
                # Si le mot PRÉCÉDENT correspondait aussi, on prolonge la chaîne de +1
                longueur_actuelle = suivi_longueurs.get(j - 1, 0) + 1
                nouveau_suivi[j] = longueur_actuelle
                
                # On met à jour le record si on a trouvé une phrase plus longue
                if longueur_actuelle > longest:
                    longest = longueur_actuelle
                    end_idx = i
                    
        # On passe à la ligne suivante en écrasant l'ancienne (libère la RAM)
        suivi_longueurs = nouveau_suivi
        
    # Étape 3 : On extrait la phrase gagnante
    if longest == 0:
        return ""
        
    mots_communs = mots1[end_idx - longest + 1 : end_idx + 1]
    return " ".join(mots_communs)


auteur_cible = 'Chrétien de Troyes'
analyse_auteur(auteur_cible, txt_dir, biblio_author_dir)

