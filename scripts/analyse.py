
"""
Pipeline d'Analyse de Corpus
Ce script opère le traitement de données textuelles segmentées pour mener une étude
contrastive entre différents genres, auteurs ou époques. Il transforme une collection
d'objets textuels en une matrice Termes-Documents exploitée pour :
    1. Calculer des mesures de similarité (Cosinus, Jaccard)
    2. Évaluer la prédictibilité des catégories via un algorithme KNN (K=1)
    3. Mesurer la cohésion interne (genre, époque, auteurs)
    4. Extraire les signatures lexicales

Utilisation :
    Conçu pour produire un rapport final au format Markdown (.md) intégrant
    des métadonnées bibliographiques et des visualisations externes

Dépendances :
    - NumPy : Gestion matricielle et calculs statistiques
    - metrics : script Python possédant les 
                fonctions personnalisées de calcul
                de distance (cos_np, jaccard_np)
"""
# MODULES
import os
import numpy as np
import datetime 
from metrics import cos_np, jaccard_np

# FONCTIONS
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
        
    """
    nb_txt = len(txt_names)

    with open(output_path, mode='w', encoding='utf-8') as out:
        out.write("Texte A\tTexte B\tCosinus\tJaccard\n")

        # Boucles imbriquées pour générer les combinaisions unique
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
            - np_matrix (numpy.ndarray) : matrice de fréquence (n-grammes x textes)
            - ordered_lex (list) : lexique complet et ordonné
            - txt_name (list) : liste des noms de fichiers correspondant aux colonnes
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

# Rajouter argument de biblio pour les étiquettes finales 
def knn(matrix, txt_names, biblio):
    """
    Identifie les 5 paires de textes les plus proches et les 5 plus éloignées à
    partir de la similarité cosinus pour comparer les vecteurs.
    Evalue la précision du voisinage (k=1)

    
    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}
    Sorties :
        str : un rapport au format Markdown contenant les resultats
     """
    
    all_pairs = []
    nb_txt = len(txt_names)
    # Calcul de toutes les paires uniques
    for i in range(nb_txt):
        for j in range(i + 1,nb_txt) :
            score = cos_np(matrix[:,i], matrix[:, j])
            all_pairs.append((txt_names[i], txt_names[j], score))
    # Tri par score décroissant
    all_pairs.sort(key=lambda x: x[2], reverse=True)
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
        best_knn = None
        
        for j in range(nb_txt):
            if i ==j :
                continue
            score = cos_np(matrix[:,i], matrix[:, j])
            if score > max_score:
                max_score = score
                best_knn = txt_names[j]

        cat2 = biblio.get(best_knn)

        if cat1 == cat2:
            good_pred +=1
        evaluated_txt +=1
    
    accuracy = (good_pred / evaluated_txt) * 100 if evaluated_txt > 0 else 0

    # Construction du rapport
    report_ligne= []
    report_ligne.append(f"**Précision de l'algorithme KNN : {accuracy :.1f}%**\n")
    
    report_ligne.append(f"#### Les 5 paires les plus proches : ")
    for t1, t2, score in top_5 : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"- **{score:.4f}** : {t1} ({c1}) / {t2} ({c2})")
    
    report_ligne.append(f"\n### Les 5 paires les plus éloignées :")
    for t1, t2, score in reversed(bot_5) : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"- **{score:.4f}** : {t1} ({c1}) / {t2} ({c2})")
    
    return "\n".join(report_ligne)


def genre_cohesion(matrix, txt_names, biblio):
    """
    Calcule de la similarité moyenne à l'intérieur de chaque genre, date ou auteur

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}

    Sorties :
        str : un rapport au format Markdown contenant les resultats
     """

    genres = {}
    for idx, text in enumerate(txt_names):
        genre = biblio.get(text)
        if genre:
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(idx)
            
    for genre, indices in genres.items():
        if len(indices) < 2:
            continue
        scores = []
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                col1 = matrix[:, indices[i]]
                col2 = matrix[:, indices[j]]
                scores.append(cos_np(col1, col2))
        mean = sum(scores) / len(scores)
        

    report_lignes= []
    for genre, indices in genres.items():
        if len(indices) < 2:
            report_lignes.append(f"- **{genre}** : *Non calculable (1 seul texte)*")
            continue

        scores = [cos_np(matrix[:, indices[i]], matrix[:, indices[j]])
                    for i in range(len(indices)) 
                    for j in range(i+1, len(indices))]

        mean = sum(scores) / len(scores)
        report_lignes.append(f"- **{genre}** : {mean :.04f}")
    return "\n".join(report_lignes)


def ngram_signatures(matrix, txt_names, biblio, lexique, target_genre, top=10):
    """
    Identifie les ngrammes caractéristiques d'un genre, auteur ou époque

    Entrées :
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}
        lexique (list): la liste ordonnée de tous les n-grammes du corpus
        target_genre (str): le genre littéraire à analyser (ex: "Roman courtois")
        top (int, optional): le nombre de n-grammes à afficher, par défaut 10
    
    Sortie :
        str : un rapport au format Markdown contenant les resultats
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


# Génération d'un rapport final 
# Rajouter citation du Git de base dans le rapport
def generate_report(matrix, txt_names, biblio, lexique, output_path, img_path, titre=None ):
    """
    Réalise l'ensemble des analyses définies précédemment et génère un rapport global au format 
    MarkDown. Orchestre l'appel des fonctions de classification, de cohésion et des n-grammes signature.
    Elle récupère aussi les graphes de visualisation réalisés dans le script plot_generator.py

    Entrées:
        matrix (np.ndarray) : la matrice des fréquences (n-grammes x textes)
        txt_names (list) : liste des noms de textes 
        biblio (dict) : dictionnaire de métadonnées {nom : auteur | date | genre}
        lexique (list): liste ordonnée des n-grammes
        output_path (str): chemin absolu ou relatif de sauvegarde du rapport
        img_path (str) : chemin vers l'image de visualisation
        titre (str, optional): titre à afficher en haut du rapport
    
    Sortie : 
        fichier (.md) : rapport final "rapport_genre | auteur | époque.md
    """
    dd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report = [
        f"## {titre}",
        f"*Généré le : {dd}*",
        "\n"
    ]
    citation_header = f'Citation: (2018). Open Medieval French. https://github.com/OpenMedFr/texts\n'       
    report.append(citation_header)
    report.append("\n" + "="*50 + "\n")
    report.append("### 1. Classification KNN \n")
    report.append(knn(matrix, txt_names, biblio))

    report.append("\n" + "="*50 + "\n")
    report.append("\n### 2. Cohésion interne\n")
    cohesion = genre_cohesion(matrix, txt_names, biblio)
    report.append(cohesion)

    report.append("\n" + "="*50 + "\n")
    report.append("\n### 3. Ngrammes signatures\n")
    unique_genre = sorted(list(set(biblio.values())))
    for genre in unique_genre: 
        report.append(ngram_signatures(matrix, txt_names, biblio, lexique, target_genre=genre, top=5))
        
    report.append("\n" + "="*50 +"\n")

    if img_path:
        report.append("\n### 4. Visualisation\n")
        report.append(f"![Nuages de points des {titre}]({img_path})\n")
        
       
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    
    if not output_path.endswith('.md'):
        output_path = output_path.replace('.txt', '.md')    
    with open(output_path, mode="w", encoding='utf-8') as f:
        f.write("\n".join(report))

    print(f"Rapport généré dans : {output_path}")