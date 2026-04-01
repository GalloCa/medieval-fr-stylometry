import re
import os 
import math
from collections import Counter
import datetime
import numpy as np


# -- FUNCTIONS
# Fonction chargement de fichier 
def load_stpwords(stopwords_filepath):
    """
    Charge une liste de stopwords et les compile en une expression régulières.

    Arguments : 
        stopwords_filepath (str) : chemin vers le fichier texte contenant les mots à exclure
    Return :
        re.pattern : Un objet regex compilé pour identifier les mots bannis, 
                     ou None si le fichier est vide
    """
    with open(stopwords_filepath, mode='r', encoding='utf-8') as f:
        content = f.read()
    lines = [re.escape(l.strip()) for l in content.split('\n') if l.strip() and not l.startswith('#')]
    
    if not lines:
        return None
    
    pattern = r"\b(?:" + "|".join(lines)+ r")\b"

    return re.compile(pattern, flags=re.I)

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

# Fonctions de nettoyage 
def clean_texts(text, regex_file):
    """
    Nettoie le texte en retirant les métadonnées, les caractères spéciaux et 
    potentiellement les stopwords. 

    Arguments : 
        text (str) : le texte brut à nettoyer
        regex_file (re.pattern) : L'expression régulière des stopswords à supprimer.

    Return:
        str : le texte nettoyé
    """
    text = re.sub(r'^.*?--------------------------------------------------\n\n','' ,text, flags=re.DOTALL)
    if 'start' in text:
        text = text.split('start', 1)[1]
    else :
        text = re.sub(r'^.*?<metadata_end_marker>', '', text, flags=re.DOTALL)
    
    if regex_file:
        text = regex_file.sub('', text)

    lines = text.split('\n')
    clean_lines = []
    ban_words = ['meta', 'texturi', 'deaf', 'arlima', 'texttitle', 'textdate', 
        'ededitor', 'msbase', 'http', 'www', 'orcid', 'cclicense', 
        'ici commence', 'prologue', 'or commence', 'author', 'start', 'folio', 'version']

    for line in lines:
        line_content = line.lower().strip()
        
        if any(word in line_content for word in ban_words):
            continue

        line_content = re.sub(r'\b[a-z]*\d+[a-z\d]*\b', '', line_content)
        line_content = re.sub(r'\b\d+[a-d]?\b', '', line_content)

        line_content = re.sub(r'[^\w\s7&ç]', '', line_content)
        
        line_content = re.sub(r'\s+', ' ', line_content).strip()

        if line_content:
            clean_lines.append(line_content)

    return "\n".join(clean_lines)

def clean_label(name):
    """
    Nettoyage des labels de fichiers pour isoler le nom du texte.
    Suppression des préfixes techniques liés au filtrage des fréquences et des extensions
    de fichiers.

    Entrée:
        name (str) : Le nom original de la colonne ou du fichier à nettoyer.

    Sortie :
        str : Le nom du texte nettoyé 
    """
    for prefix in ['freq-filtered-', 'freq-', 'filtered-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

# Fonctions de sauvegarde
def save_text(text, original_filename, output_dir, prefix):
    """
    Sauvegarde des textes

    Arguments : 
        text (str) : Le contenu à sauvgarder
        original_filename (str) : le nom original du fichier source
        output_dir (str) : Le dossier de destination
        prefix (str) : Le préfixe à ajouter pour former le nouveau nom de fichier
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name_only = os.path.basename(original_filename)
    new_filename = f'{prefix}-{file_name_only}'
    path = os.path.join(output_dir, new_filename)

    with open(path, 'w', encoding="utf-8") as f:
        f.write(text)

def save_freq(frequences, original_filename, output_dir):
    """
    Enregistre les fréquence des n-grammes dans un fichier TSV trié

    Arguments :
        frequences (dict) : le dictionnaire de fréquences
        original_filename (str) : le nom original du fichier
        output_dir (str) : le dossier de destination
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_name_only = os.path.basename(original_filename)
    new_filename = f'freq-{file_name_only.replace(".txt", ".tsv")}'
    path = os.path.join(output_dir, new_filename)
    
    sorted_ngrams = sorted(frequences.keys(), key=lambda v:frequences[v], reverse = True)
    with open(path, mode='w', encoding="utf-8") as f:
        f.write("ngramme\tfrequence\n")
        for ngram in sorted_ngrams:
            f.write(f"{ngram}\t{frequences[ngram]}\n")


# -- Revoir -- 
def n_gramm(text,n=3):
    """
    Génère un dictionnaire de fréquences de n-grammes de caractères.

    Arguments : 
        text (str) : le texte source à découpé en ngrammes
        n (int) : taille des n-grammes (par défaut n=3, mais peut être changé)

    Return : 
        Counter (dict): compteur associant chaque ngramme (clé)  à sa fréquence absolue (valeur).
        Retourne un Counter vide si le texte d'entrée est vide.
        """
    if not text : 
        return Counter()
    ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
    return Counter(ngrams)


# Fonctions de calcul de similarité
def cos_np(v1,v2):
   """
   """
   produit = np.dot(v1,v2)
   norme1 = np.linalg.norm(v1)
   norme2 = np.linalg.norm(v2)

   if norme1 * norme2 !=0:
      return produit / (norme1 * norme2)
   return 0

def jaccard_np(v1,v2):
   """
   """
   p1 = v1>0
   p2 = v2>0

   inter = np.sum(p1 & p2)
   union = np.sum(p1 | p2)

   if union !=0:
      return inter / union
   return 0


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
  

def create_comparison_matrix(freq_dir, output_path):
    """
    """
    files = [f for f in os.listdir(freq_dir) if f.endswith(".tsv")]
    if not files:
        print("Aucun fichiers TSV trouvé")
        return
    
    full_lex = set()
    txt_data = []
    txt_name = []

    for filename in files :
        file_path = os.path.join(freq_dir, filename)
        clean_name = clean_label(filename)
        txt_name.append(clean_name)

        local_dic = {}
        with open(file_path, mode='r', encoding='utf-8') as f:
            next(f)
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    ngram, freq = parts[0], int(parts[1])
                    local_dic[ngram] = local_dic.get(ngram, 0) + freq
                    full_lex.add(ngram)
        txt_data.append(local_dic)
    
    ordered_lex = sorted(list(full_lex))
    ngram_to_index = {ngram : i for i, ngram in enumerate(ordered_lex)}

    nb_ngrams = len(ordered_lex)
    nb_txt = len(txt_name)
    np_matrix = np.zeros((nb_ngrams, nb_txt), dtype=int)

    for j, dico in enumerate(txt_data):
        for ngram, freq in dico.items():
            i = ngram_to_index[ngram]
            np_matrix[i, j] = freq
    
    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write("ngramme\t" + "\t".join(txt_name) + "\n")
        for i, ngram in enumerate(ordered_lex):
            values = "\t".join(map(str, np_matrix[i, :]))
            f.write(f"{ngram}\t{values}\n")
    print(f'Matrice Numpy créee')
    return np_matrix, ordered_lex, txt_name

def knn_np(matrix, txt_names):
    """
    Identifie les paires de textes les plus proches et les plus éloignées

    Arguments :
        corpus (dict) : Le dictionnaire de dictionnaires de fréquences
    """
    toutes_les_paires = []
    nb_txt = len(txt_names)
    # Calcul de toutes les paires uniques
    for i in range(nb_txt):
        for j in range(i + 1,nb_txt):
            t1, t2 = txt_names[i], txt_names[j]
            
            col1 = matrix[:,i]
            col2 = matrix[:, j]

            score = cos_np(col1, col2)
            toutes_les_paires.append((t1, t2, score))
    # Tri par score décroissant
    toutes_les_paires.sort(key=lambda x: x[2], reverse=True)
    # A enregistrer en sortie dans fichiers txt ?
    print("Les 5 plus proches sont :")
    for t1, t2, s in toutes_les_paires[:5]:
        print(f"{s:.4f} : {t1} / {t2}")
    print("\nLes 5 plus éloignés sont :")
    for t1, t2, s in toutes_les_paires[-5:][::-1]:
        print(f"{s:.4f} : {t1} / {t2}")
    report_ligne= []
    report_ligne.append("Les 5 plus proches sont :")
    for t1, t2, s in toutes_les_paires[:5]:
        report_ligne.append(f"{s:.4f} : {t1} / {t2}")
    
    report_ligne.append("\nLes 5 plus éloignés sont :")
    for t1, t2, s in toutes_les_paires[-5:][::-1]:
        report_ligne.append(f"{s:.4f} : {t1} / {t2}")
    return "\n".join(report_ligne)


def genre_cohesion(matrix, txt_names, biblio):
    """
    Calcule de la similarité moyenne à l'intérieur de chaque genre

    Arguments : 
        matrix (np.darray) : matrice des fréquences des ngrammes x textes
        txt_name (list) : les des noms de textes 
        biblio (dict) : le dictionnaire des genres

    """
    genres = {}
    for idx, text in enumerate(txt_names):
        genre = biblio.get(text)
        if genre:
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(idx)
    
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

        scores = []
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                col1 = matrix[:, indices[i]]
                col2 = matrix[:, indices[j]]
                scores.append(cos_np(col1, col2))
       
        mean = sum(scores) / len(scores)
        report_lignes.append(f"{genre:<15} : {mean :.04f}")
    return "\n".join(report_lignes)
    

# Modifier args genre_cible pour faire en fonction de ce qu'on veut genre / auteur / date ?
def ngram_signatures(matrix, txt_names, biblio, lexique, target_genre, top=10):
    """
    Identifie les ngrammes caractéristiques d'un genre

    Arguments :


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
   Génère une matrice de confusion basée sur le plus proche voisin, avec Numpy

   Arguments : 
    
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

    Entrées : 
        matrix 
        txt_names : 
        biblio : 
        lexique : 
        output_path : 

    Sorties : 
        fichier (.txt) : Rapport 
    """
    dd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report = [
        f"{titre}",
        f"Généré le : {dd}",
        "\n"
    ]
    report.append("1. Classification KNN")
    knn_report = knn_np(matrix, txt_names)
    report.append(knn_report)
    report.append("\n2. Cohésion des genres")
    cohesion_genre = genre_cohesion(matrix, txt_names, biblio)
    report.append(cohesion_genre)
    report.append("\n3. Ngrammes signatures")
    unique_genre = sorted(list(set(biblio.values())))
    for genre in unique_genre: 
        ngm = ngram_signatures(matrix, txt_names, biblio, lexique, target_genre=genre, top=5)
        report.append(ngm)

    report.append("Fin")

    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with open(output_path, mode="w", encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"Rapport généré dans : {output_path}")


def cohesion_genr():
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
    
