# Analyse d'un Corpus d'Ancien Français

Pipeline d'analyse sur un corpus de 25 textes en moyen et ancien français (XI–XVe siècle), tiré du dépôt [Open Medieval French](https://github.com/OpenMedFr/texts). Le projet compare les textes selon leur genre littéraire, leur auteur et leur époque via des méthodes vectorielles et des mesures de similarité.

---

## Structure du dépôt

```
medFR-paleo-NLP/
│
├── data/
│   ├── raw-txt/          # Textes bruts téléchargés 
│   ├── clean-txt/        # Textes nettoyés générés par le pipeline
│   └── metadata/
│       ├── dico_genre.txt    # Nom du texte : Genre littéraire
│       ├── dico_auteur.txt   # Nom du texte : Auteur
│       └── dico_date.txt     # Nom du texte : Siècle
│
├── results/
│   ├── frequencies/      # Fréquences de n-grammes par texte (.tsv)
│   ├── matrix/           # Matrices Termes-Documents globales (.tsv)
│   │   ├── morpho/
│   │   └── lexical/
│   ├── scatter-plots/    # Visualisations MDS (.png)
│   │   ├── morpho/
│   │   └── lexical/
│   └── rapports/         # Rapports HTML finaux (un fichier par axe d'analyse)
│       ├── rapport-genre.html
│       ├── rapport-auteurs.html
│       └── rapport-epoques.html
│
├── download_data.py         # Acquisition via l'API GitHub
├── text_processor.py        # Nettoyage et extraction de n-grammes
├── analyse.py               # Métriques, KNN, cohésion, signatures, LCS, utilitaires
├── plots_generator.py       # Scatter plots MDS et dendogramme
├── generate_report_html.py  # Génération des rapports HTML avec onglets
├── main.py                  # Point d'entrée — orchestre tout le pipeline
│
├── requirements.txt
├── .gitignore
├── Algorithmes.pdf          # Explications des structures de données et pseudo-code
└── README.md
```

# Format des fichiers de métadonnées

Les trois fichiers dans `data/metadata/` suivent le même format, une entrée par ligne :

```
NomDuFichierSansExtension : Catégorie
```

Exemple pour `dico_genre.txt` :

```
Yvain        : Roman courtois
Roland       : Epique
StAlexis     : Hagiographie
```

Les clés doivent correspondre exactement aux noms de fichiers dans `raw-txt/` (sans `.txt`).

# Installation

```
git clone https://github.com/votre-utilisateur/medFR-paleo-NLP.git
cd medFR-paleo-NLP
pip install -r requirements.txt

```

Configurer le token GitHub (nécessaire pour le téléchargement du corpus) :

```
# Linus / macOS
export GITHUB_TOKEN = ghp_votre_token

# Windows (PowerShell)
$env : GITHUB_TOKEN = "ghp_votre_token"
```
Attention de pas écrire le token dans le code au risque de le corrompre.

# Utilisation

```
python main.py
```

Le pipeline s'exécute en 6 étapes automatiques :

1. **Téléchargement** — récupère les textes depuis OpenMedFr via l'API GitHub (sauté si déjà présents)
2. **Nettoyage** — suppression des métadonnées, ponctuation, normalisation
3. **Matrice Termes-Documents** — construction de la matrice de fréquences de n-grammes
4. **Visualisation** — scatter plots MDS et dendogramme des auteurs anonymes
5. **Accumulation** — les résultats de chaque expérience sont stockés en mémoire
6. **LCS + Rapports** — extraction des formules récurrentes (Chrétien de Troyes) puis génération des trois rapports HTML combinés

Les deux expériences configurées dans main.py sont exécutées en séquence, et leurs résultats sont fusionnés dans chaque rapport sous forme d'onglets :

| Expérience | Type de n-gramme | n | Métrique | Ce qu'elle capture |
|------------|-----------------|---|----------|--------------------|
| `morpho`   | Caractères      | 3 | Cosinus  | Niveau morphologique et graphique |
| `lexical`  | Mots            | 2 | Cosinus  | Niveau lexical et syntagmatique |

Chaque rapport HTML `rapport-genre.html`,  `rapport-auteurs.html`, `rapport-epoques.html` présente les deux expériences dans des onglets séparés, avec pour chacune :

- Classification KNN
- Cohésion interne
- Signatures lexicales
- Visualisation MDS.

Le rapport auteurs inclus en plus l'analyse LCS (*Longest Common Substring*) dans l'onglet lexical.

les visualisation matplotlib sont encodées en base64 et intégrée directement dans le HTML. Les rapports sont donc autonomes et s'ouvrent sans dépendances externes.

## Approche algorithmique 
## EXPLICATION SCRIPT 
Détaillée dans le fichier `algorithmique.pdf`

Représentation vectorielle

Chaque texte est représenté comme un vecteur dans un espace de n-grammes. La matrice globale Termes x Documents (construite dans `analyse.py > create_comparaison_matrix`) a pour dimension :

  -  lignes : tous les n-grammes uniques du corpus
  -  colonnes : chaque texte

Chaque cellule contient la fréquence brute du n-gramme dans ce texte.

# Mesures de similarité (analyse.py)

Trois métriques sont implémentées manuellement, sans scikit-learn, directement dans analyse.py : 

- Similarité cosinus =>
- Indice Jaccard =>
- Distance de Manhattan =>

Classification KNN (k=1) ()

Pour chaque texte, on identifiee son voisin le plus proche dans le corpus (k=1) et on vérifie si ce voisin appartient à la même catégorie.
La précison globale indique dans quelle mesure la similarité stylistique reflète les catégories (genre, auteur, époque).

La fonction supporte trois métriques via le paramètre metric : cosinus, Jaccard et Manhattan.
Les expériences par défaut utilisent toutes cosinus. 

*Mettre un peu analyse de résultats ? Les résultats*

Cohésion interne ()

Calcule la similarité cosinus moyenne entre tous les textes d'une même catégorie. 

Signatures 

Identifie les n-grammes sur-représentés dans une catégorie par rapport au reste du corpus via un ratio ()

Réduction de dimension ── MDS (plot_generator.py)

Le MDS (Multidimensional Scaling) projette la matrice de dissimilarité (1 - cosinus) en 2D pour visualiser le regroupements stylistiques.
La dissimilarité est calculée manuellement avant d'être passée à scikit-learn en mode `precomputed`.

Séquences communes ── LCS (script)

Algorithme LCS (Longest Common Substring) optimisé par indexation inversée des positions : les positions de chaque mot dans t2 sont pré-indexées dans un dictionnaire, ce qui évite de parcourir t2 entièrement pour chaque mot de t1.
`count_freq` : compte les occurrences exactes de la séquences trouvée dans chaque texte.

`analyse_auteur` : orchestre l'utilisation de fonction lcs et count_freq sur un auteur choisi dans le corpus

Rapport HTML (script repport)





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


