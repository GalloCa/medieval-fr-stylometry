
"""
Module d'analyse

Ce script centralise les opérations mathématiques et textuelles. Il transforme une collection
d'objets textuels en une matrice Termes-Documents exploitée pour 

Il regroupe l'ensemble des fonctions analytiques de la pipeline : 
    - Utilitaires : chargement des métadonnées, nettoyage des labels,
                    export de la matrice TSV
    — Métriques : similarité cosinus, indice de Jaccard, distance de Manhattan
                           (implémentées manuellement sans scikit-learn)
    — Analyse vectorielle : construction de la matrice Termes-Documents,
                            comparaison par paires (cosinus + Jaccard)
    — Classification : KNN (k=1) avec évaluation de précision,
                        support des métriques cosinus, Jaccard et Manhattan
    — Cohésion interne : similarité moyenne intra-catégorie
    — Signatures : n-grammes sur-représentés par catégorie (ratio TF)
    — LCS : plus longue sous-séquence commune de mots entre textes,
            comptage des occurrences de la séquence dans chaque texte

Dépendances :
    - NumPy : Gestion matricielle et calculs statistiques
"""


# MODULES
import os
import numpy as np
import datetime 

# UTILITAIRES 
# Chargement des métadonnées, nettoyage des labels, export TSV
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

# METRIQUES 
# Trois mesures de similarité / distance implémentées manuellement
# ValueError si les vecteurs n'ont pas la même dimension

def cos_np(v1,v2):
   """
   Calcule la similarité cosinus entre deux vecteurs.

   Formules : (A ⋅ B) / (||A|| * ||B||)

   Entrées :
        v1 (np.ndarray) : le premier vecteur 
        v2 (np.ndarray) : le deuxième vecteur 

   Sortie : 
        float : le score de simlarité cosinus (entre 0 et 1). 
                Retourne 0 si l'un des deux vecteurs est nul
   """
   if v1.shape != v2.shape:
      raise ValueError(f"cos_np : dimensions incompatibles {v1.shape} vs {v2.shape}")
   produit = np.dot(v1,v2)
   norme1 = np.linalg.norm(v1)
   norme2 = np.linalg.norm(v2)
   if norme1 * norme2 !=0:
      return produit / (norme1 * norme2)
   return 0

def jaccard_np(v1,v2):
   """
   Calcule l'indice de Jaccard entre deux vecteurs.

   Formule : |A ∩ B| / |A ∪ B|

   Entrées : 
        v1 (np.ndarray) : le premier vecteur 
        v2 (np.ndarray) : le deuxième vecteur 

   Sortie : 
        float : l'indice de Jaccard (entre 0 et 1)
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
   if v1.shape != v2.shape:
      raise ValueError(f"manhattan_np : dimensions incompatibles {v1.shape} vs {v2.shape}")
   return np.sum(np.abs(v1 - v2))

# COMPARAISON PAR PAIRES
def compare_files(matrix, txt_names, output_path=None):
    """
    Calcule les similitudes (Cosinus et Jaccard) entre tous les 
    couples uniques de textes.
    La fonction parcours une matrice et compare chaque texte i 
    avec chaque texte j (où j > i) pour éviter les doublons et auto-comparaisons.
    Les résultats sont exportés dans un fichier .tsv

    Entrées : 
        matrix (numpy.ndarray) : matrice où chaque colonn représente le vecteur d'un texte
        txt_names (list) : liste des identifiants des textes (colonnes de la matrice)
        output_path(str, optionnel) :chemin de sortie du fichier

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
    Construit la matrice Termes-Documents globale à partir d'une liste d'objets.
    Centralise tous les n-grammes rencontrés.
    Chaque colonne représente un texte, chaque ligne un n-gramme spécifique

    Entrées : 
        liste_txt (list) : liste d'objets instanciés et traités (tokenisation et calcul de fréquences)

    Sorties :
        tuple : 
            np_matrix (numpy.ndarray) : matrice de fréquence (n-grammes x textes)
            ordered_lex (list) : lexique complet et ordonné
            txt_name (list) : liste des noms de fichiers correspondant aux colonnes
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
def knn(matrix, txt_names, biblio, metric ='cosinus'):
    """
    Classification knn (k=1) :  évalue si la similarité stylistique
    reflète les catégories (genre, auteur, époque)

    Pour chaque texte, identifie son voisin le plus proche et vérifie si ce voisin appartient
    à la même catégorie. 
    Calcul aussi les 5 paires les plus proches et les 5 plus éloignées
   
    Métriques supportées : 
        'cosinus' : similarité angulaire (métrique par défaut)
        'jaccard' : présence/absence
        'manhattan' : distance absolue (disponible, non activée)

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : catégorie}
        metric (str) : métrique à utiliser
    
    Sorties :
        str : bloc de texte qui contient les resultats (précision, top_5, bot_5)
     """
    
    all_pairs = []
    nb_txt = len(txt_names)
    # Calcul de toutes les paires uniques
    for i in range(nb_txt):
        for j in range(i + 1,nb_txt) :
            if metric == "manhattan":
                val = manhattan_np(matrix[:,i], matrix[:, j])
            else :
                val = cos_np(matrix[:,i], matrix[:, j])
            all_pairs.append((txt_names[i], txt_names[j], val))

    # Tri adapté par métriques / cosinus : + score grand = proche ; inverse pour manhattan 
    is_reverse = True if metric != 'manhattan' else False
    all_pairs.sort(key=lambda x: x[2], reverse=is_reverse)

    top_5 = all_pairs[:5]
    bot_5 = all_pairs[-5:]
    
    # Mise en place pour évaluation de la précision
    good_pred = 0
    evaluated_txt = 0

    for i in range(nb_txt):
        t1 = txt_names[i]
        cat1 = biblio.get(t1)
        if not cat1:
            continue
        
        # Recherche du voisin le plus proche
        max_score = -1
        max_dist = float('inf')
        best_knn = None
        
        for j in range(nb_txt):
            if i != j :
                v1 = matrix[:,i]
                v2 = matrix[:, j]

                if metric == 'manhattan':
                    dist = manhattan_np(v1,v2)
                    if dist < max_dist:
                        max_dist = dist
                        best_knn = txt_names[j]
                else :
                    score = cos_np(v1,v2)
                    if score > max_score:
                        max_score = score
                        best_knn = txt_names[j]
        if not best_knn:
            continue
        cat2 = biblio.get(best_knn)
        if cat1 == cat2:
            good_pred +=1
        evaluated_txt +=1
    
    accuracy = (good_pred / evaluated_txt) * 100 if evaluated_txt > 0 else 0

    # Construction du bloc de texte final
    report_ligne= []
    report_ligne.append(f"**Précision de l'algorithme KNN ({metric}) : {accuracy :.1f}%**\n")
    
    report_ligne.append(f"#### Les 5 paires les plus proches : ")
    for t1, t2, val in top_5 : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"- **{val:.4f}** : {t1} ({c1}) / {t2} ({c2})")
    
    report_ligne.append(f"\n### Les 5 paires les plus éloignées :")
    for t1, t2, val in reversed(bot_5) : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"- **{val:.4f}** : {t1} ({c1}) / {t2} ({c2})")
    
    return "\n".join(report_ligne)


def genre_cohesion(matrix, txt_names, biblio, metric='cosinus'):
    """
    Calcule de la similarité moyenne de tous les à l'intérieur 
    d'une même catégorie

    Une cohésion élevée indique que les textes du groupes partagent
    un style lexicale ou morphologique.

    Les catégories avec un seul texte retournent 'Non Calculable'

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : catégorie}
        metric (str) : 'cosinus' (défaut), 'jaccard' ou 'manhattan'

    Sortie :
        str : bloc texte avec une ligne par catégorie et son score moyen
     """

    genres = {}
    for idx, text in enumerate(txt_names):
        genre = biblio.get(text)
        if genre:
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(idx)

    report_lignes= []
    for genre, indices in genres.items():
        if len(indices) < 2:
            report_lignes.append(f"- **{genre}** : *Non calculable (1 seul texte)*")
            continue  

        scores = []
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                v1 = matrix[:, indices[i]]
                v2 = matrix[:, indices[j]]
                if metric == 'manhattan':
                    scores.append(manhattan_np(v1,v2))
                else :
                    scores.append(cos_np(v1, v2))

        mean = sum(scores) / len(scores)
        unite = "(Distance moyenne)" if metric == 'manhattan' else "(Similarité moyenne)"
        report_lignes.append(f"- **{genre}** : {mean :.04f} {unite}")

    return "\n".join(report_lignes)


def ngram_signatures(matrix, txt_names, biblio, lexique, target_genre, top=10):
    """
    Identifie les ngrammes csur-représentés dans une catégorie par rapport au 
    reste du corpus via un ration de fréquences moyennes

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : catégorie}
        lexique (list): la liste ordonnée de tous les n-grammes du corpus
        target_genre (str): catégorie cible à analyser (ex: 'genre')
        top (int, optional): nombre de n-grammes à afficher (défaut : 10)
    
    Sortie :
        str : bloc texte listant les top n-grammes avec leur ratio
    """
    indices_cible = [i for i, t in enumerate(txt_names) if biblio.get(t) == target_genre]
    rest_indices = [i for i, t in enumerate(txt_names) if biblio.get(t) != target_genre]

    if not indices_cible:
        return f"\n Signature du genre '{target_genre}' : Aucun textes trouvé."
    
    target_freq = np.mean(matrix[:, indices_cible], axis=1)
    reste_freq = np.mean(matrix[:, rest_indices], axis=1)

    scores = target_freq / (reste_freq + 1)

    indices_tries = np.argsort(scores)[::-1]

    report_lignes = [f"\n#### Signature : '{target_genre}' \n"]
    for idx in indices_tries[:top]:
        ng = lexique[idx]
        s = scores[idx]
        if s > 0:
            report_lignes.append(f"- '{ng}' (ratio : {s :.2f})")
    return "\n".join(report_lignes)

# LCS - SEQUENCES COMMUNES
# Identification des séquences récurrentes exactes entre textes d'un même auteur
# avec comptage des occurences dans chaque texte

def lcs(t1, t2):
    """
    Algorithme LCS optimisé par indexation inversée, les positions de chaque mot dans t2
    sont pré-indexés dans un dictionnaire, évite de parcourir t2 entièrement pour chaque mot de t1
    
    Complexité : O(n log n) => non - c'est quasi linéraire mais 

    Entrées : 
        t1 (str) : le premier texte
        t2 (str) : le deuxième texte

    Sortie :
        str : la plus longue séquence de mots exactes partagées entre les deux textes.
              retourne chaine vide si aucune correspondance n'est trouvée.
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
    Compte le nombre d'apparation d'une séquence dans un texte

    Entrée : 
        sequence (str) : séquence de mots recherchés (ex : issue de la fonction lcs)
        texte (str) : le texte source

    Sortie : 
        count (int) : la fréquence de la séquence dans le texte
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
    Analyse le corpus pour extraire les fomrules récurrentes d'un auteur ciblé.

    La fonction identifie tous les fichiers associés à l'auteur, les charge en mémoire,
    puis utilise la fonction lcs() sur toutes les paires (i, j) avec j > i.
    Pour chaque séquence trouvée (> 10 caractères), compte les occurences 
    dans chaque texte via count_freq()

    Entrées : 
        auteur (str) : le nom de l'auteur à analyser
        texte_dir (str) : le chemin vers le répertoir contenant les fichiers textes nettoyés
        dico_author (dict) : le dictionnaire de métadonnées liant les textes aux auteurs

    Sortie :
        str : bloc de texte contenant les citations récurrentes entre les textes.
              Retourne un avertissement s'il n'y a pas assez de textes à comparer
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

