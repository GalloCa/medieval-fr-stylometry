# Analyse d'un Corpus d'Ancien Français

Pipeline d'analyse sur un corpus de 25 textes en moyen et ancien français (XI–XVe siècle), tiré du dépôt [Open Medieval French](https://github.com/OpenMedFr/texts). Le projet compare les textes selon leur genre littéraire, leur auteur et leur époque via des méthodes vectorielles et des mesures de similarité.

---

## Structure du dépôt (WIP)

```
medFR-paleo-NLP/
├── data/
│   ├── raw-txt/          # Textes bruts téléchargés 
│   ├── clean-txt/        # Textes nettoyés générés par le pipeline
│   └── metadata/
│       ├── dico_genre.txt    # Nom du texte : Genre littéraire
│       ├── dico_auteur.txt   # Nom du texte : Auteur
│       └── dico_date.txt     # Nom du texte : Siècle

```

### Format des fichiers de métadonnées (WIP)

Les trois fichiers dans `data/metadata/` suivent le même format, une entrée par ligne :

```
NomDuFichierSansExtension : Catégorie
```
Mettre un exemple -

Les clés doivent correspondre exactement aux noms de fichiers dans `raw-txt/` (sans `.txt`).

---

## Installation (WIP)

```bash
git clone https://github.com/votre-utilisateur/medFR-paleo-NLP.git
cd medFR-paleo-NLP
pip install -r requirements.txt
```

Mettre la configuration du token GitHub => nécessaire pour le téléchargement du corpus


Ne pas écrire le token dans le code. Ne pas le committer.

---

## Utilisation

```bash
python main.py
```

Le pipeline s'exécute en 6 étapes automatiques :

1. **Téléchargement** — récupère les textes depuis OpenMedFr via l'API GitHub (sauté si déjà présents)
2. **Nettoyage** — suppression des métadonnées, ponctuation, normalisation
3. **Matrice Termes-Documents** — construction de la matrice de fréquences de n-grammes
4. **Visualisation** — scatter plots MDS
5. **Accumulation** — les résultats de chaque expérience sont stockés en mémoire
6. **LCS + Rapports** — extraction des formules récurrentes (Chrétien de Troyes) puis génération des trois rapports HTML combinés

Les deux expériences configurées dans `main.py` sont exécutées en séquence, et leurs résultats sont fusionnés dans chaque rapport sous forme d'onglets :

| Expérience | Type de n-gramme | n | Métrique | Ce qu'elle capture |
|------------|-----------------|---|----------|--------------------|
| `morpho`   | Caractères      | 3 | Cosinus  | Niveau morphologique et graphique |
| `lexical`  | Mots            | 2 | Cosinus  | Niveau lexical et syntagmatique |

Chaque rapport HTML (`rapport-genre.html`, `rapport-auteurs.html`, `rapport-epoques.html`) présente les deux expériences dans des onglets séparés, avec pour chacune : classification KNN, cohésion interne, signatures lexicales et visualisation MDS. Le rapport auteurs inclut en plus l'analyse LCS dans l'onglet `ngramme de mot`

Préciser que visu matplotlib sont encodées en base64 et intégrées directement dans le HTML => les rapports sont donc autonomes et s'ouvrent sans dépendances externes.

---

## Algorithmique

### Représentation vectorielle

Chaque texte est représenté comme un vecteur dans un espace de n-grammes. La matrice globale **Termes × Documents** (construite dans `analyse.py > create_comparison_matrix`) a pour dimensions :

- **lignes** : tous les n-grammes uniques du corpus (lexique)
- **colonnes** : chaque texte

Chaque cellule contient la fréquence brute du n-gramme dans ce texte.

### Mesures de similarité (`metrics.py`)

Trois métriques sont implémentées manuellement sans scikit-learn :

**Similarité cosinus** — mesure l'angle entre deux vecteurs, indépendamment de leur longueur. Adaptée ici car les textes ont des longueurs très différentes. Utilisée dans les deux expériences.

```
cos(A, B) = (A · B) / (‖A‖ × ‖B‖)
```

**Indice de Jaccard** — compare les ensembles de n-grammes présents (binarisation des vecteurs). Sensible à la présence/absence plutôt qu'aux fréquences. Utilisé dans `compare_files` pour la comparaison par paires. Un fichier TSV est crée pour faire d'autres analyse (?) - si le temps regarder pour prévoir une visualisation gephi -

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

**Distance de Manhattan** — somme des différences absolues de fréquences. Implémentée et branchée dans le pipeline via le paramètre `metric`, mais non activée dans les expériences actuelles (qui utilisent toutes deux la similarité cosinus).

```
d(A, B) = Σ |aᵢ - bᵢ|
```

### Classification KNN (k=1) (`analyse.py > knn`)

Pour chaque texte, on identifie son voisin le plus proche dans le corpus (k=1) et on vérifie si ce voisin appartient à la même catégorie. La précision globale indique dans quelle mesure la similarité stylistique reflète les catégories editoriales (genre, auteur, époque).

La fonction identifie aussi les 5 paires les plus proches et les 5 plus éloignées du corpus.

### Cohésion interne (`analyse.py > genre_cohesion`)

Calcule la similarité cosinus moyenne entre tous les textes d'une même catégorie. Une cohésion élevée indique que les textes du groupe partagent un style lexical homogène.

### Signatures lexicales (`analyse.py > ngram_signatures`)

Identifie les n-grammes sur-représentés dans un genre par rapport au reste du corpus via un ratio :

```
score(ng) = freq_moyenne_dans_genre / (freq_moyenne_hors_genre + 1)
```

Le `+1` évite la division par zéro et pénalise légèrement les n-grammes absents du reste.

### Réduction de dimension — MDS (`plots_generator.py`)

Le MDS (*Multidimensional Scaling*) projette la matrice de dissimilarité (1 − cosinus) en 2D pour visualiser les regroupements stylistiques. La dissimilarité est calculée manuellement avant d'être passée à scikit-learn en mode `precomputed`.

### Séquences communes — LCS (`lcs_analyse.py`)

Algorithme LCS (longest common substring => formule partagée exacxte sans gap) optimisé par indexation inversée des positions : au lieu de comparer chaque mot de t1 avec chaque mot de t2 en O(n²), on pré-indexe les positions de chaque mot dans t2, ce qui réduit le nombre de comparaisons inutiles.

### Rapports HTML (`generate_report_html.py`)

La fonction `generate_combined_report_html` produit un fichier HTML autonome (CSS intégré, pas de dépendance externe hors polices Google Fonts) pour chacun des trois axes d'analyse. Chaque rapport présente les résultats des deux expériences dans des onglets séparés. Les visualisations matplotlib sont encodées en base64 et intégrées directement dans le HTML, ce qui rend les fichiers entièrement portables — ils s'ouvrent sans avoir besoin des images sur le disque.

---

## Corpus

25 textes en ancien et moyen français issus de [OpenMedFr/texts](https://github.com/OpenMedFr/texts), couvrant 7 genres littéraires sur 5 siècles (XIe–XVe).

| Genre            | Exemples                                      |
|------------------|-----------------------------------------------|
| Roman courtois   | Yvain, Lancelot, Erec et Enide (Chrétien de Troyes) |
| Épique           | Chanson de Roland, Raoul de Cambrai           |
| Hagiographie     | Vie de Saint Alexis, Vie de Saint Brendan     |
| Antique          | Roman d'Eneas, Roman de Troie                 |
| Didactique       | Bestiaire divin, Exempla (Jacques de Vitry)   |
| Prose            | Meliador                                      |
| Jugement d'amour | —                                             |

---

## Dépendances principales

| Bibliothèque | Usage |
|---|---|
| `numpy` | Matrices et calculs vectoriels |
| `scikit-learn` | MDS (réduction de dimension) |
| `scipy` | Clustering hiérarchique (dendogramme) |
| `matplotlib` | Visualisations |
| `adjustText` | Anti-chevauchement des étiquettes |
| `requests` | Téléchargement via API GitHub |

---

## Source des données

> (2018). *Open Medieval French*. https://github.com/OpenMedFr/texts
