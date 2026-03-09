
import os
import numpy as np
import datetime 
from metrics import cos_np, jaccard_np

def compare_files(matrix, txt_names, output_path=None):
    """
    """
    nb_txt = len(txt_names)

    with open(output_path, mode='w', encoding='utf-8') as out:
        out.write("Texte A\tTexte B\tCosinus\tJaccard\n")

        for i in range(nb_txt):
            for j in range(i+1, nb_txt):
                t1, t2 = txt_names[i], txt_names[j]

                v1 = matrix[:, i]
                v2 = matrix[:, j]

                sim_cos = cos_np(v1,v2)
                sim_jac = jaccard_np(v1,v2)

                out.write(f"{t1}\t{t2}\t{sim_cos : .4f}\t{sim_jac : .4f}\n")
    print(f"Rapport de similarité généré dans : {output_path}")

def create_comparison_matrix(liste_man):
    """
    Construit la matrice Termes-Documents globale à partir d'une liste d'objets 

    Arguments : 
        liste_man (list) : liste d'objets man instanciés et traités

    Returns :
        tuple : Contient la matrice NumPy (n_gramme, n_textes), le lexique ordonné (list) 
                et la liste des noms de textes (list)
    """
    
    full_lex = set()
    txt_name = []

    for text in liste_man : 
        txt_name.append(text.nom)
        full_lex.update(text.frequences.keys())
    
    ordered_lex = sorted(list(full_lex))
    ngram_to_index = {ngram : i for i, ngram in enumerate(ordered_lex)}

    nb_ngrams = len(ordered_lex)
    nb_txt = len(liste_man)
    np_matrix = np.zeros((nb_ngrams, nb_txt), dtype=int)

    for j, text in enumerate(liste_man):
        for ngram, freq in text.frequences.items():
            i = ngram_to_index[ngram]
            np_matrix[i, j] = freq

    return np_matrix, ordered_lex, txt_name

# Rajouter argument de biblio pour les étiquettes finales ²
def knn(matrix, txt_names, biblio):
    """
    Identifie les 5 paires de textes les plus proches et les 5 plus éloignées

    Arguments :
        matrix (np.ndarray) : la matrice des fréquences
        txt_names (list) : liste des noms de textes 
    Returns :
        str : un rapport contenant les resultats
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
    
    good_pred = 0
    evaluated_txt = 0
    for i in range(nb_txt):
        t1 = txt_names[i]
        cat1 = biblio.get(t1)
        if not cat1:
            continue

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

    # A enregistrer en sortie dans fichiers txt ?
    report_ligne= []
    report_ligne.append(f"\n Précision de l'algorithme KNN : {accuracy :.1f}% \n")
    
    report_ligne.append(f"Les 5 paires les plus proches : \n")
    for t1, t2, score in top_5 : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"{score:.4f} : {t1} ({c1}) / {t2} ({c2})")
    
    report_ligne.append(f"\nLes 5 paires les plus éloignées : \n")
    for t1, t2, score in reversed(bot_5) : 
        c1 = biblio.get(t1, 'Inconnu')
        c2 = biblio.get(t2, 'Inconnu')
        report_ligne.append(f"{score:.4f} : {t1} ({c1}) / {t2} ({c2})")
    
    return "\n".join(report_ligne)


def genre_cohesion(matrix, txt_names, biblio):
    """
    Calcule de la similarité moyenne à l'intérieur de chaque genre

    Arguments : 
        matrix (np.darray) : matrice des fréquences des ngrammes x textes
        txt_name (list) : noms des textes 
        biblio (dict) : le dictionnaire des genres

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
            print(f"{genre : <15} : Non calculable car un 1 seul texte dans les données")
            continue
        scores = []
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                col1 = matrix[:, indices[i]]
                col2 = matrix[:, indices[j]]
                scores.append(cos_np(col1, col2))
        mean = sum(scores) / len(scores)
        print(f"{genre:<15} : {mean :.04f}")

    report_lignes= []
    for genre, indices in genres.items():
        if len(indices) < 2:
            report_lignes.append(f"{genre : <15} : Non calculable car un 1 seul texte dans les données")
            continue

        scores = [cos_np(matrix[:, indices[i]], matrix[:, indices[j]])
                    for i in range(len(indices)) 
                    for j in range(i+1, len(indices))]

        mean = sum(scores) / len(scores)
        report_lignes.append(f"{genre:<15} : {mean :.04f}")
    return "\n".join(report_lignes)


def ngram_signatures(matrix, txt_names, biblio, lexique, target_genre, top=10):
    """
    Identifie les ngrammes caractéristiques d'un genre

    Arguments :
        matrix (np.ndarray): La matrice des fréquences (n_grammes, n_textes).
        txt_names (list): La liste des noms des textes.
        biblio (dict): Le dictionnaire associant les textes à leur genre.
        lexique (list): La liste ordonnée de tous les n-grammes du corpus.
        target_genre (str): Le genre littéraire à analyser (ex: "Roman courtois").
        top (int, optional): Le nombre de n-grammes à afficher. Défaut à 10.
    
    Returns :
        str : Rapport 

    """
    indices_cible = [i for i, t in enumerate(txt_names) if biblio.get(t) == target_genre]
    rest_indices = [i for i, t in enumerate(txt_names) if biblio.get(t) != target_genre]

    if not indices_cible:
        return f"\n Signature du genre '{target_genre}' : Aucun textes trouvé."
    
    target_freq = np.mean(matrix[:, indices_cible], axis=1)
    reste_freq = np.mean(matrix[:, rest_indices], axis=1)

    scores = target_freq / (reste_freq + 1)

    indices_tries = np.argsort(scores)[::-1]

    report_lignes = [f"\n Signature du genre : '{target_genre}' \n"]
    for idx in indices_tries[:top]:
        ng = lexique[idx]
        s = scores[idx]
        if s > 0:
            report_lignes.append(f" -'{ng}' (ratio : {s :.2f})")
    return "\n".join(report_lignes)


# Rapport final 
def generate_report(matrix, txt_names, biblio, lexique, output_path, img_path, titre=None ):
    """
    Réalise l'ensembles des analyses définies précédemment et génère un rapport global 
    sous forme de fichier texte.

    Args:
        matrix (np.ndarray):  matrice des fréquences.
        txt_names (list):liste des noms des textes.
        biblio (dict): dictionnaire des métadonnées (genres/auteurs).
        lexique (list): liste ordonnée des n-grammes.
        output_path (str): chemin absolu ou relatif de sauvegarde du rapport.
        titre (str, optional): titre à afficher en haut du rapport.
    
    Return : 
        fichier (.txt) : Rapport 
    """
    dd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report = [
        f"{titre}",
        f"Généré le : {dd}",
        "\n"
    ]
    report.append("1. Classification KNN \n")
    report.append(knn(matrix, txt_names, biblio))

    report.append("\n" + "="*50 + "\n")
    report.append("\n2. Cohésion interne\n")
    cohesion = genre_cohesion(matrix, txt_names, biblio)
    report.append(cohesion)

    report.append("\n" + "="*50 + "\n")
    report.append("\n3. Ngrammes signatures\n")
    unique_genre = sorted(list(set(biblio.values())))
    for genre in unique_genre: 
        report.append(ngram_signatures(matrix, txt_names, biblio, lexique, target_genre=genre, top=5))
        
    report.append("\n" + "="*50 +"\n")

    if img_path:
        report.append("\n4. Visualisation\n")
        report.append(f"![Nuages de points des {titre}]({img_path})\n")
        
       
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    
    if not output_path.endswith('.md'):
        output_path = output_path.replace('.txt', '.md')    
    with open(output_path, mode="w", encoding='utf-8') as f:
        f.write("\n".join(report))

    print(f"Rapport généré dans : {output_path}")