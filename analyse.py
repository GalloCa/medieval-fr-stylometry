
"""
Module central d'analyse stylométrique de l'Ancien Français.

Regroupe l'ensemble des fonctions analytiques du pipeline :
    — Utilitaires        : chargement des métadonnées, nettoyage des labels,
                           export de la matrice TSV
    — Métriques          : similarité cosinus, distance de Manhattan
                           (implémentées manuellement sans scikit-learn)
    — Analyse vectorielle : construction de la matrice Termes-Documents,
                            comparaison par paires (cosinus + Jaccard)
    — Classification     : KNN (k=1) avec évaluation de précision,
                           support des métriques cosinus, Jaccard et Manhattan
    — Cohésion interne   : similarité moyenne intra-catégorie
    — Signatures         : n-grammes sur-représentés par catégorie (ratio TF)
    — LCS                : plus longue sous-séquence commune de mots entre textes,
                           comptage des occurrences de la séquence dans chaque texte

Expériences disponibles (configurées dans main.py) :
    morpho  — trigrammes de caractères, cosinus  → niveau morphologique
    lexical — bigrammes de mots, cosinus          → niveau lexical
    
Dépendances :
    - numpy : matrices et calculs vectoriels
"""
# MODULES
import os
import numpy as np
import datetime 

# UTILITAIRES
# Chargement des métadonnées, nettoyage des labels, export TSV
def load_biblio(path):
   """
   Charge un fichier de métadonnées et le transforme en dictionnaire.

   Format attendu (une entrée par ligne) :
       NomDuFichierSansExtension : Catégorie

   Entrée :
       path (str) : chemin vers le fichier de métadonnées

   Sortie :
       dict : {'NomTexte': 'Catégorie'} — retourne {} si le fichier est absent
   """
   biblio = {}
   try : 
       
    with open(path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
   except FileNotFoundError:
       print(f"Erreur, le chemin du dictionnaire {path} est introuvable")
   except Exception as e : 
       print(f"Erreur lors de la lecture de {path} : {e}")
       
   return biblio

def clean_label(name):
    """
    Isole le nom du texte en supprimant les préfixes et extensions techniques.

    Entrée :
        name (str) : nom brut du fichier (ex : 'clean-Yvain.txt')

    Sortie :
        str : nom nettoyé (ex : 'Yvain')
    """
    for prefix in ['freq-', 'clean-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def save_matrix_tsv(matrix, lexique, txt_names, output_path):
    """
    Exporte la matrice Termes-Documents au format TSV.

    Structure du fichier :
        — 1ère ligne  : en-tête avec les noms de textes (colonnes)
        — lignes N+1  : un n-gramme par ligne, suivi de ses fréquences

    Entrées :
        matrix (np.ndarray) : matrice de fréquences (n-grammes × textes)
        lexique (list)       : n-grammes ordonnés (index des lignes)
        txt_names (list)     : noms des textes (index des colonnes)
        output_path (str)    : chemin de sortie (.tsv)

    Sortie :
        fichier .tsv écrit dans output_path
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

# MÉTRIQUES
# Trois mesures de similarité/distance implémentées sans scikit-learn.
# Toutes lèvent ValueError si les vecteurs n'ont pas la même dimension.

def cos_np(v1, v2):
   """
   Similarité cosinus entre deux vecteurs de fréquences.

   Mesure l'angle entre les vecteurs — indépendante de leur norme,
   donc robuste aux différences de longueur entre textes.
   Formule : (A · B) / (‖A‖ × ‖B‖)

   Entrées :
       v1, v2 (np.ndarray) : vecteurs de même dimension

   Sortie :
       float : score dans [0, 1] — 0 si l'un des vecteurs est nul

   Lève :
       ValueError : si v1 et v2 n'ont pas la même dimension
   """
   if v1.shape != v2.shape:
      raise ValueError(f"cos_np : dimensions incompatibles {v1.shape} vs {v2.shape}")
   produit = np.dot(v1,v2)
   norme1 = np.linalg.norm(v1)
   norme2 = np.linalg.norm(v2)
   if norme1 * norme2 !=0:
      return produit / (norme1 * norme2)
   return 0

def jaccard_np(v1, v2):
   """
   Indice de Jaccard entre deux vecteurs de fréquences.

   Binarise les vecteurs (présence/absence) puis calcule le rapport
   intersection / union. Utilisé dans l'expérience 'jaccard' (KNN)
   et dans compare_files (comparaison par paires).
   Formule : |A ∩ B| / |A ∪ B|

   Entrées :
       v1, v2 (np.ndarray) : vecteurs de même dimension

   Sortie :
       float : indice dans [0, 1] — 0 si union vide

   Lève :
       ValueError : si v1 et v2 n'ont pas la même dimension
   """
   if v1.shape != v2.shape:
      raise ValueError(f"jaccard_np : dimensions incompatibles {v1.shape} vs {v2.shape}")
   p1 = v1>0
   p2 = v2>0
   inter = np.sum(p1 & p2)
   union = np.sum(p1 | p2)
   if union !=0:
      return inter / union
   return 0

def manhattan_np(v1, v2):
   """
   Distance de Manhattan entre deux vecteurs de fréquences.

   Somme des différences absolues — sensible aux écarts de fréquence brute.
   Implémentée et branchée dans le pipeline (paramètre metric='manhattan'),
   non activée dans les expériences actuelles.
   Formule : Σ |aᵢ − bᵢ|

   Entrées :
       v1, v2 (np.ndarray) : vecteurs de même dimension

   Sortie :
       float : distance (≥ 0)

   Lève :
       ValueError : si v1 et v2 n'ont pas la même dimension
   """
   if v1.shape != v2.shape:
      raise ValueError(f"manhattan_np : dimensions incompatibles {v1.shape} vs {v2.shape}")
   return np.sum(np.abs(v1 - v2))

# COMPARAISON PAR PAIRES
def compare_files(matrix, txt_names, output_path=None):
    """
    Calcule cosinus et Jaccard pour tous les couples uniques de textes
    et exporte les résultats dans un fichier TSV.

    Parcourt la matrice en ne traitant que les paires (i, j) avec j > i
    pour éviter doublons et auto-comparaisons.

    Entrées :
        matrix (np.ndarray) : matrice de fréquences (n-grammes × textes)
        txt_names (list)     : noms des textes (colonnes de la matrice)
        output_path (str)    : chemin de sortie du fichier .tsv

    Sortie :
        fichier .tsv avec colonnes : Texte A | Texte B | Cosinus | Jaccard
    """
    nb_txt = len(txt_names)

    with open(output_path, mode='w', encoding='utf-8') as out:
        out.write("Texte A\tTexte B\tCosinus\tJaccard\n")

        # Gestion des les combinaisions uniques
        for i in range(nb_txt):
            for j in range(i+1, nb_txt):
                t1, t2 = txt_names[i], txt_names[j]

                v1 = matrix[:, i]
                v2 = matrix[:, j]

                sim_cos = cos_np(v1,v2)
                sim_jac = jaccard_np(v1,v2)

                out.write(f"{t1}\t{t2}\t{sim_cos : .4f}\t{sim_jac : .4f}\n")

def create_comparison_matrix(liste_txt):
    """
    Construit la matrice Termes-Documents globale à partir d'une liste d'objets TextProcessor.

    Centralise tous les n-grammes du corpus dans un lexique ordonné commun,
    puis remplit la matrice avec les fréquences de chaque texte.

    Entrées :
        liste_txt (list) : objets TextProcessor après clean_txt() et n_gramm()

    Sorties :
        tuple :
            np_matrix (np.ndarray) : matrice de fréquences (n-grammes × textes)
            ordered_lex (list)     : lexique complet et ordonné (index des lignes)
            txt_name (list)        : noms des textes (index des colonnes)
    """
    full_lex = set()
    txt_name = []

    for text in liste_txt : 
        txt_name.append(text.nom)
        full_lex.update(text.frequences.keys())
    
    ordered_lex = sorted(list(full_lex))
    ngram_to_index = {ngram : i for i, ngram in enumerate(ordered_lex)}

    # Initialisation de la matrice à 0
    nb_ngrams = len(ordered_lex)
    nb_txt = len(liste_txt)
    np_matrix = np.zeros((nb_ngrams, nb_txt), dtype=int)

    # Remplissage de la matrice
    for j, text in enumerate(liste_txt):
        for ngram, freq in text.frequences.items():
            i = ngram_to_index[ngram]
            np_matrix[i, j] = freq

    return np_matrix, ordered_lex, txt_name

# ANALYSES
def knn(matrix, txt_names, biblio, metric='cosinus'):
    """
    Classification KNN (k=1) : évalue dans quelle mesure la similarité stylistique
    reflète les catégories éditoriales (genre, auteur, époque).

    Pour chaque texte, identifie son voisin le plus proche et vérifie si ce voisin
    appartient à la même catégorie. Calcule aussi les 5 paires les plus proches
    et les 5 plus éloignées du corpus.

    Métriques supportées :
        'cosinus'  — similarité angulaire (défaut, expérience morpho)
        'jaccard'  — présence/absence (expérience jaccard)
        'manhattan'— distance absolue (disponible, non activée)

    Entrées :
        matrix (np.ndarray) : matrice de fréquences (n-grammes × textes)
        txt_names (list)     : noms des textes
        biblio (dict)        : métadonnées {nom_texte : catégorie}
        metric (str)         : métrique à utiliser

    Sortie :
        dict :
            'accuracy' (float)  : précision en pourcentage
            'top'      (list)   : 5 paires les plus proches,
                                  chaque élément → {'t1', 'c1', 't2', 'c2', 'score'}
            'bot'      (list)   : 5 paires les plus éloignées, même structure
    """

    all_pairs = []
    nb_txt = len(txt_names)
    sim_matrix = np.full((nb_txt, nb_txt), -1.0 if metric != 'manhattan' else float('inf'))
    # Calcul de toutes les paires uniques
    for i in range(nb_txt):
        v1 = matrix[:, i]
        for j in range(i + 1, nb_txt):
            v2 = matrix[:, j]
            if metric == 'manhattan':
                val = manhattan_np(v1, v2)
            elif metric == 'jaccard':
                val = jaccard_np(v1, v2)
            else:
                val = cos_np(v1, v2)

            sim_matrix[i,j] = val
            sim_matrix[j,i] = val
            all_pairs.append((txt_names[i], txt_names[j], val))

    # Tri adapté par métriques / cosinus : + score grand = proche ; inverse pour manhattan
    is_reverse = metric != 'manhattan'
    all_pairs.sort(key=lambda x: x[2], reverse=is_reverse)

    # Slice de all_pair pour obtenir top_5 et bot_5
    top_5 = all_pairs[:5]
    bot_5 = all_pairs[-5:]

    # Évaluation de la précision
    good_pred = 0
    evaluated_txt = 0

    for i in range(nb_txt):
        t1 = txt_names[i]
        cat1 = biblio.get(t1)
        if not cat1:
            continue
        scores_i = sim_matrix[i, :]
        
        if metric == 'manhattan':
            best_idx = np.argmin(scores_i)
        else :
            best_idx = np.argmax(scores_i)

        best_knn = txt_names[best_idx]
        cat2 = biblio.get(best_knn)
        
        if not best_knn:
            continue
        cat2 = biblio.get(best_knn)
        if cat2 and cat1 == cat2:
            good_pred += 1
        evaluated_txt += 1

    accuracy = (good_pred / evaluated_txt) * 100 if evaluated_txt > 0 else 0

    # Utilitaire inter pour transformer données brutes en format lisible et structuré
    # Transforme tuple en dict
    def _pair_dict(t1, t2, val):
        return {'t1': t1, 
                'c1': biblio.get(t1, 'Inconnu'),
                't2': t2, 
                'c2': biblio.get(t2, 'Inconnu'),
                'score': round(val, 4)}

    return {
        'accuracy': round(accuracy, 1),
        'top': [_pair_dict(t1, t2, v) for t1, t2, v in top_5],
        'bot': [_pair_dict(t1, t2, v) for t1, t2, v in reversed(bot_5)],
    }


def genre_cohesion(matrix, txt_names, biblio, metric='cosinus'):
    """
    Calcule la similarité moyenne entre tous les textes d'une même catégorie.

    Une cohésion élevée indique que les textes du groupe partagent
    un style lexical ou morphologique homogène. Catégories avec un seul
    texte retournent 'Non calculable'.

    Entrées :
        matrix (np.ndarray) : matrice de fréquences (n-grammes × textes)
        txt_names (list)     : noms des textes
        biblio (dict)        : métadonnées {nom_texte : catégorie}
        metric (str)         : 'cosinus' (défaut), 'jaccard' ou 'manhattan'

    Sortie :
        list : une entrée par catégorie →
               {'cat': str, 'score': float|None, 'unite': str, 'na': bool}
               na=True si la catégorie ne contient qu'un seul texte
    """

    genres = {}
    for idx, text in enumerate(txt_names):
        genre = biblio.get(text)
        if genre:
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(idx)

    results = []
    for genre, indices in genres.items():
        if len(indices) < 2:
            results.append({'cat': genre, 'score': None, 'unite': None, 'na': True})
            continue

        scores = []
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                v1 = matrix[:, indices[i]]
                v2 = matrix[:, indices[j]]
                if metric == 'manhattan':
                    scores.append(manhattan_np(v1, v2))
                else:
                    scores.append(cos_np(v1, v2))

        mean = sum(scores) / len(scores)
        unite = 'Distance moyenne' if metric == 'manhattan' else 'Similarité moyenne'
        results.append({'cat': genre, 'score': round(mean, 4), 'unite': unite, 'na': False})

    return results


def ngram_signatures(matrix, txt_names, biblio, lexique, target_genre, top=10):
    """
    Identifie les n-grammes sur-représentés dans une catégorie par rapport
    au reste du corpus via un ratio de fréquences moyennes.

    Formule : score(ng) = freq_moy_cible / (freq_moy_reste + 1)
    Le +1 évite la division par zéro et pénalise les n-grammes absents du reste.

    Entrées :
        matrix (np.ndarray)  : matrice de fréquences (n-grammes × textes)
        txt_names (list)      : noms des textes
        biblio (dict)         : métadonnées {nom_texte : catégorie}
        lexique (list)        : n-grammes ordonnés (index des lignes)
        target_genre (str)    : catégorie cible (ex : 'Roman courtois')
        top (int)             : nombre de n-grammes à retourner (défaut : 10)

    Sortie :
        list : jusqu'à `top` entrées → {'ngram': str, 'ratio': float}
               liste vide si la catégorie est absente du corpus
    """
    indices_cible = [i for i, t in enumerate(txt_names) if biblio.get(t) == target_genre]
    rest_indices  = [i for i, t in enumerate(txt_names) if biblio.get(t) != target_genre]

    if not indices_cible:
        return []

    target_freq = np.mean(matrix[:, indices_cible], axis=1)
    reste_freq  = np.mean(matrix[:, rest_indices],  axis=1)
    scores      = target_freq / (reste_freq + 1)

    indices_tries = np.argsort(scores)[::-1]

    return [
        {'ngram': lexique[idx], 'ratio': round(float(scores[idx]), 2)}
        for idx in indices_tries[:top]
        if scores[idx] > 0
    ]



# LCS — SÉQUENCES COMMUNES
# Identification des formules récurrentes exactes entre textes d'un même auteur,
# avec comptage des occurrences dans chaque texte.

def lcs(t1, t2):
    """
    Plus longue sous-séquence commune de mots (Longest Common Substring) entre deux textes.

    Algorithme optimisé par indexation inversée : les positions de chaque mot dans t2
    sont pré-indexées dans un dictionnaire, ce qui évite de parcourir t2 entièrement
    pour chaque mot de t1.

    Complexité : meilleure que O(n×m) en pratique grâce à l'index,
    bien que le pire cas reste quadratique sur des vocabulaires très partagés.

    Entrées :
        t1 (str) : premier texte (chaîne de mots séparés par des espaces)
        t2 (str) : deuxième texte

    Sortie :
        str : séquence de mots la plus longue commune aux deux textes,
              chaîne vide si aucune correspondance
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

def count_freq(sequence, texte):
    """
    Compte les occurrences exactes d'une séquence de mots dans un texte.

    Utilisée après lcs() pour mesurer combien de fois la formule identifiée
    apparaît dans chacun des deux textes comparés.

    Entrées :
        sequence (str) : séquence de mots à rechercher (sortie de lcs())
        texte (str)    : texte dans lequel compter les occurrences

    Sortie :
        int : nombre d'occurrences exactes — 0 si séquence vide
    """
    if not sequence:
        return 0
    mot_seq = sequence.split()
    mot_text = texte.split()
    n = len(mot_seq)
    count = 0
    for i in range(len(mot_text) - n +1):
        if mot_text[i:i+n] == mot_seq:
            count +=1
    return count 

def analyse_auteur(auteur, texte_dir, dico_author):
    """
    Extrait les formules récurrentes entre toutes les œuvres d'un auteur ciblé.

    Identifie les fichiers associés à l'auteur dans dico_author, les charge,
    puis applique lcs() sur toutes les paires (i, j) avec j > i.
    Pour chaque séquence trouvée (> 10 caractères), compte ses occurrences
    dans chaque texte via count_freq().

    Entrées :
        auteur (str)       : nom exact de l'auteur tel qu'il apparaît dans dico_author
                             (casse sensible — ex : 'Chrétien de Troyes')
        texte_dir (str)    : répertoire contenant les fichiers textes nettoyés (clean-*.txt)
        dico_author (dict) : métadonnées {nom_texte : auteur}

    Sortie :
        str : bloc texte formaté avec pour chaque paire la séquence commune
              et le nombre d'occurrences dans chaque texte.
              Retourne un message d'avertissement si moins de 2 textes trouvés.
    """
    fichiers_auteur = []

    for filename in os.listdir(texte_dir):
        if filename.endswith(".txt"):   
            nom_original = filename.replace("clean-", "").replace(".txt", "")
            auteur_trouve = dico_author.get(nom_original, "").strip()
            if auteur_trouve == auteur.strip():
                fichiers_auteur.append(filename)

    if len(fichiers_auteur) < 2:
        return f"Il faut au moins 2 textes pour faire une comparaison."
    
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
                freq1 = count_freq(lcs_ct, textes[file1])
                freq2 = count_freq(lcs_ct, textes[file2])
                report_lignes.append(f"- **{nom1}** et **{nom2}** ({len(lcs_ct)} caractères) :")
                report_lignes.append(f" > «  *{lcs_ct}* »")
                report_lignes.append(f" - apparitions : {nom1} x {freq1} / {nom2} x {freq2}\n")

    return "\n".join(report_lignes)    

