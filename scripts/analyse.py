
import os
import numpy as np
import datetime 
from metrics import cos_np, jaccard_np

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

def knn_np(matrix, txt_names):
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
    # A enregistrer en sortie dans fichiers txt ?
    #  Traces pour test
    print("Les 5 plus proches sont :")
    for t1, t2, s in all_pairs[:5]:
        print(f"{s:.4f} : {t1} / {t2}")
    print("\nLes 5 plus éloignés sont :")
    for t1, t2, s in all_pairs[-5:][::-1]:
        print(f"{s:.4f} : {t1} / {t2}")
   
    report_ligne= ["Les 5 plus proches sont : "]
    for t1, t2, s in all_pairs[:5]:
        report_ligne.append(f"{s:.4f} : {t1} / {t2}")
    
    report_ligne.append("\nLes 5 plus éloignés sont :")
    for t1, t2, s in all_pairs[-5:][::-1]:
        report_ligne.append(f"{s:.4f} : {t1} / {t2}")
    
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
            genres.setdefault(genre, [].append(idx))

    # Trace de test
    print("\n Cohésion par genre")
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

    report_lignes= ["\nCohésion par genre"]
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

    report_lignes = [f"\n Signature du genre : '{target_genre}'"]
    for idx in indices_tries[:top]:
        ng = lexique[idx]
        s = scores[idx]
        if s > 0:
            report_lignes.append(f" -'{ng}' (ratio : {s :.2f})")
    return "\n".join(report_lignes)


# 
def confusion_matrix(matrix, txt_names, biblio, output_file=None):
   """
   Génère et affiche une matrice de confusion basée sur le plus proche voisin, avec Numpy

    Arguments:
        matrix (np.ndarray): La matrice des fréquences.
        txt_names (list): La liste des noms des textes.
        biblio (dict): Le dictionnaire de vérité terrain (vrai genre de chaque texte).
        output_file (str, optional): Chemin vers le fichier texte de sauvegarde.

    Returns:
        float: Le score de précision globale de l'algorithme (Accuracy) en pourcentage
    
   """
   classes = sorted(list(set(biblio.values())))
   nb_classes = len(classes)
   genre_to_idx = {g : i for i, g in enumerate(classes)}

   conf_matrix = np.zeros((nb_classes, nb_classes), dtype=int)

   correct = 0
   total = 0
   nb_txt = len(txt_names)

   for i in range(nb_txt):
       t1 = txt_names[i]
       real_genre = biblio.get(t1)
       if not real_genre : continue

       best_score = -1
       nghr_idx = -1 

       for j in range(nb_txt):
           if i == j : continue

           score = cos_np(matrix[:,i], matrix[:,j])
           if score > best_score:
               best_score = score 
               nghr_idx = j

       nghr_t = txt_names[nghr_idx]
       predict_genre = biblio.get(nghr_t)

       real_idx = genre_to_idx[real_genre]
       idx_predict = genre_to_idx[predict_genre]
       conf_matrix[real_idx, idx_predict] +=1

       if real_genre == predict_genre:
           correct +=1 
       total += 1

   accuracy = (correct / total) * 100 if total > 0 else 0

   report_lignes = []
   report_lignes.append("Matrice de confusion")
   header = " " * 15 + "".join([f"{g[:6]:>8}" for g in classes])
   report_lignes.append(header)
   
   for i, g_real in enumerate(classes):
       ligne = f"{g_real[:12]:<15}"
       for j in range(nb_classes):
           ligne += f"{conf_matrix[i,j]:>8}"
       report_lignes.append(ligne)
       
   report_lignes.append(f"\nPrécision global : {accuracy:.02f}%")
   
   final = "\n".join(report_lignes)
   print("\n" + final)

   if output_file:
       folder = os.path.dirname(output_file)
       if folder and not os.path.exists(folder):
           os.makedirs(folder)
        
       with open(output_file, mode='w', encoding='utf-8') as f:
           f.write(final + "\n")
           print(f"Matrice de confusion sauvegarder dans : {output_file}")

   return accuracy

# Rapport final 
def generate_report(matrix, txt_names, biblio, lexique, output_path, titre=None):
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
    report.append("1. Classification KNN")
    report.append(knn_np(matrix, txt_names))
    
    report.append("\n" + "="*50 + "\n")
    report.append("\n2. Cohésion des genres")
    report.append(matrix, txt_names, biblio)

    report.append("\n" + "="*50 + "\n")
    report.append("\n3. Ngrammes signatures par genre")
    unique_genre = sorted(list(set(biblio.values())))
    for genre in unique_genre: 
        report.append(ngram_signatures(matrix, txt_names, biblio, lexique, target_genre=genre, top=5))
        
    report.append("\n" + "="*50 +"\nFin")

    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with open(output_path, mode="w", encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"Rapport généré dans : {output_path}")