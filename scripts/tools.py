# MODULES 
import math
import re
import os 
from collections import Counter
import pandas as pd


# FUNCTIONS
def load_stpwords(stopwords_filepath):
    """
    """
    with open(stopwords_filepath) as f:
        content = f.read()
    lines = [re.escape(l.strip()) for l in content.split('\n') if l.strip() and not l.startswith('#')]
    
    if not lines:
        return None
    
    pattern = r"\b(?:" + "|".join(lines)+ r")\b"

    return re.compile(pattern, flags=re.I)

def clean_texts(text, regex_file):
    """
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

def save_text(text, original_filename, output_dir, prefix):
    """
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name_only = os.path.basename(original_filename)
    new_filename = f'{prefix}-{file_name_only}'
    path = os.path.join(output_dir, new_filename)

    with open(path, 'w', encoding="utf-8") as f:
        f.write(text)

###Revoir 
def n_gramm(text,n=3):
    """
    """
    stop_re = load_stpwords(r'/workspaces/medFR-paleao-NLP/data/grammar/300stopwordsMF')
    clean_text = clean_texts(text, regex_file=stop_re)
    ngrams = [clean_text[i:i+n] for i in range(len(clean_text)-n+1)]
    return Counter(ngrams)

def save_freq(frequences, original_filename, output_dir):
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

def create_comparison_matrix(freq_dir, output_path):
    all_data = []
    
    for filename in os.listdir(freq_dir):
        if filename.endswith(".tsv"):
            file_path = os.path.join(freq_dir, filename)
            
            # Chargement du fichier
            df = pd.read_csv(file_path, sep='\t', usecols=['ngramme', 'frequence'])
            
            # --- CORRECTION DES DOUBLONS ---
            # Si 'abc' apparaît 2 fois, on additionne les fréquences et on ne garde qu'une ligne
            df = df.groupby('ngramme').sum()
            
            # Nettoyage du nom pour la colonne
            column_name = filename.replace('freq-filtered-', '').replace('.tsv', '')
            df = df.rename(columns={'frequence': column_name})
            
            all_data.append(df)

    if not all_data:
        print("Aucun fichier TSV trouvé.")
        return

    # La fusion fonctionnera maintenant car chaque index est unique
    matrix = pd.concat(all_data, axis=1)
    
    matrix = matrix.fillna(0).astype(int)
    matrix.to_csv(output_path, sep='\t')
    print(f"Matrice comparative créée avec succès : {output_path}")
    return matrix

def produit_scalaire(v1, v2):
  produit = 0
  for voc in v1:
    if voc in v2:
      produit += v1[voc] * v2[voc]
  return produit

def norme(h):
  somme = 0
  for key in h.keys():
    somme +=  h[key]**2
  return math.sqrt(somme)

def cosinus(v1, v2):
  norme1 = norme(v1)
  norme2 = norme(v2)
  if norme1 * norme2 != 0:
    return produit_scalaire(v1,v2) / (norme1 * norme2)
  else :
    return 0
  
def score_jaccard(v1,v2):
  s1= set(v1.keys())
  s2 = set(v2.keys())
  inter = len(s1 & s2 )
  union = ((len(s1 | s2)))
  if union != 0:
    return inter / union
  else :
    return 0

def clean_label(name):
    """
    Nettoyage des labels de fichiers pour isoler le nom du texte.
    Suppression des préfixes techniques liés au filtrage des fréquences et des extensions
    de fichiers.

    Entrée:
        name (str) : Le nom original de la colone ou du fichier à nettoyer.

    Sortie :
        str : Le nom du texte nettoyé 
    """
    for prefix in ['freq-filtered-', 'freq-', 'filtered-']:
        name = name.replace(prefix, '')
    for ext in ['.tsv', '.txt']:
        name = name.replace(ext, '')
    return name

def compare_files(freq_dir): 
  corpus = {}
  for filename in os.listdir(freq_dir):
    if filename.endswith(".tsv"):
      nom = clean_label(filename)
      corpus[nom] = {}
      with open(os.path.join(freq_dir, filename), mode='r', encoding='utf-8') as f:
        next(f)
        for line in f:
          parts = line.strip().split('\t')
          if len(parts) == 2:
            corpus[nom][parts[0]] = int(parts[1])

    noms = list(corpus.keys())

    with open("compare-matrix-cosinus-jaccard-similarities.tsv", mode='w', encoding='utf-8') as out:
      out.write("Texte_A\tTexte_B\tCosinus\tJaccard\n")
      for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
          t1, t2 = noms[i], noms[j]

          sim_cos = cosinus(corpus[t1], corpus[t2])
          sim_jac = score_jaccard(corpus[t1], corpus[t2])

          out.write(f"{t1}\t{t2}\t{sim_cos:.4f}\t{sim_jac:.4f}\n")

def preparer_corpus(freq_dir):
    corpus = {}
    for filename in os.listdir(freq_dir):
        if filename.endswith(".tsv"):
            # On nettoie le nom pour avoir "AigarB" au lieu de "freq-AigarB.tsv"
            nom_texte = clean_label(filename)
            
            # On crée un dictionnaire pour ce texte
            corpus[nom_texte] = {}
            
            with open(os.path.join(freq_dir, filename), 'r', encoding='utf-8') as f:
                next(f)  # Sauter l'en-tête (ngramme	frequence)
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        ngramme, freq = parts[0], int(parts[1])
                        corpus[nom_texte][ngramme] = freq
    return corpus

def biblio(path):
   biblio = {}
   with open(path, mode='r', encoding='utf-8') as f:
            for ligne in f:
                if ":" in ligne:
                    cle, valeur = ligne.split(":", 1)
                    biblio[cle.strip()] = valeur.strip()
   return biblio

def knn(corpus):
    noms = list(corpus.keys())
    toutes_les_paires = []
    # Calcul de toutes les paires uniques
    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            t1, t2 = noms[i], noms[j]
            score = cosinus(corpus[t1], corpus[t2])
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

def genre_cohesion(corpus, biblio):
    genres = {}
    for texte, genre in biblio.items():
      if texte in corpus:
         if genre not in genres :
            genres[genre] = []
         genres[genre].append(texte)
    for genre, textes in genres.items():
        if len(textes) < 2:
           continue
        scores = []
        for i in range(len(textes)):
           for j in range(i + 1, len(textes)):
              scores.append(cosinus(corpus[textes[i]], corpus[textes[j]]))
        mean = sum(scores) / len(scores)
        print(f'{genre} : {mean}')

def ngram_signatures(corpus, biblio, genre_cible, top=10):
   # Calculer les fréquences moyennes pour le genre cible vs le reste
    freq_genre = {}
    freq_reste = {}
    
    for texte, ngrams in corpus.items():
        cible = biblio.get(texte) == genre_cible
        dest = freq_genre if cible else freq_reste
        for ng, f in ngrams.items():
            dest[ng] = dest.get(ng, 0) + f

    # Calcul de l'écart (ratio simple ou différence)
    ecarts = []
    for ng in freq_genre:
        # Score = fréquence dans le genre / (fréquence ailleurs + 1 pour éviter div par 0)
        score = freq_genre[ng] / (freq_reste.get(ng, 0) + 1)
        ecarts.append((ng, score))

    ecarts.sort(key=lambda x: x[1], reverse=True)
    print(f"\nSignatures du genre {genre_cible} :")
    for ng, s in ecarts[:top]:
        print(f"  '{ng}' (poids : {s:.2f})")

def confusion_matrix(corpus, biblio):
   classes = sorted(list(set(biblio.values())))
   matrix = {g_reel : {g_pred : 0 for g_pred in classes} for g_reel in classes}

   correct = 0
   total = 0

   for t1 in corpus:
      genre_reel = biblio.get(t1)
      if not genre_reel : 
         continue

      best_score = -1
      near_n = None
      for t2 in corpus : 
         if t1 == t2 :
            continue
         score = cosinus(corpus[t1], corpus[t2])
         if score > best_score : 
            best_score = score
            near_n = t2
      genre_predit = biblio.get(near_n)
      matrix[genre_reel][genre_predit] +=1
      if genre_reel == genre_predit :
         correct += 1
      total +=1
   print("\nMatrice de Confusion (Ligne = Réel, Colonne = Prédit) :")
   header = " " * 15 + "".join([f"{g[:6]:>8}" for g in classes])
   print(header)
   for g_reel in classes:
        ligne = f"{g_reel[:12]:<15}"
        for g_pred in classes:
            ligne += f"{matrix[g_reel][g_pred]:>8}"
        print(ligne)
    
   print(f"\nPrécision globale : {(correct/total)*100:.2f}%")







# MAIN 







path_biblio = "/workspaces/medFR-paleao-NLP/data/metadata/dico_genre.txt"
genre_biblio = biblio(path_biblio)
mon_corpus = preparer_corpus("/workspaces/medFR-paleao-NLP/data/frequencies")
# compare_files("/workspaces/medFR-paleao-NLP/data/frequencies")
knn(mon_corpus)
genre_cohesion(mon_corpus, genre_biblio)
ngram_signatures(mon_corpus, genre_biblio, 'Roman courtois', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Hagiographie', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Didactique', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Prose', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Epique', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Jugement d\'amour', top=10)
ngram_signatures(mon_corpus, genre_biblio, 'Antique', top=10)

confusion_matrix(mon_corpus, genre_biblio)