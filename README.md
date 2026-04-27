# Analyse d'un Corpus d'Ancien Français

Pipeline d'analyse sur un corpus de 25 textes en moyen et ancien français (XI–XVe siècle), tiré du dépôt [Open Medieval French](https://github.com/OpenMedFr/texts). Le projet compare les textes selon leur genre littéraire, leur auteur et leur époque via des méthodes vectorielles et des mesures de similarité.

---

## Structure du dépôt

```
medieval-fr-stylometry/
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
│   ├── frequencies/     # Fréquences de n-grammes par texte (.tsv)
│   ├── gephi/           # Fichiers (.csv) pour import dans Gephi
│   │   ├── morpho/
│   │   └── lexical/
    ├── matrix/           # Matrices Termes-Documents globales (.tsv)
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
├── algorithmiques.pdf       # Explications des structures de données et pseudo-code
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
git clone https://github.com/votre-utilisateur/medieval-fr-stylometry.git
cd medieval-fr-stylometry
pip install -r requirements.txt

```

Configurer le token GitHub (nécessaire pour le téléchargement du corpus) :

```
# Linus / macOS
export GITHUB_TOKEN = ghp_votre_token

# Windows (PowerShell)
$env : GITHUB_TOKEN = "ghp_votre_token"
```
*Attention à ne jamais écrire ce token en clair dans le code Python au risque de le compromettre publiquement sur GitHub*

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

**Les expériences**
Les deux expériences configurées dans `main.py` sont exécutées en séquence, et leurs résultats sont fusionnés dans chaque rapport sous forme d'onglets :

| Expérience | Type de n-gramme | n | Métrique | Ce qu'elle capture |
|------------|-----------------|---|----------|--------------------|
| `morpho`   | Caractères      | 3 | Cosinus  | Niveau morphologique et graphique |
| `lexical`  | Mots            | 2 | Cosinus  | Niveau lexical et syntagmatique |

Chaque rapport HTML *`rapport-genre.html`*,  *`rapport-auteurs.html`*, *`rapport-epoques.html`* présente les deux expériences dans des onglets séparés, avec pour chacune :

- Classification KNN
- Cohésion interne
- Signatures lexicales
- Visualisation MDS.

Le rapport auteurs inclut en plus l'analyse LCS (*Longest Common Substring*) dans l'onglet lexical.

Les visualisations matplotlib sont encodées en base64 et intégrées directement dans le HTML.\
Les rapports sont donc autonomes et s'ouvrent dans n'importe quel navigateur sans dépendances externes.

**Visualisation de réseaux (Gephi)**

A partir du fichier (.tsv) généré par compare_file(), la script produit deux fichiers (*`nodes.csv`* et *`edges.csv`*) dans `results/gephi/` pour permettre une exploration interactive. 

- **Importation** : importez les fichiers, noeuds (*nodes*) puis celui des arêtes (*edges*) dans **Gephi** (version bureau ou navigateur)
- **Spacialisation** : il est recommandé d'utiliser l'algorithme **ForceAtlas2** pour regrouper les textes partageant un "ADN" lexical ou morphologique commun
- **Analyse** : avec la coloration des noeuds par catégorie, on visualise des clusters stylistiques


## Approche algorithmique 

*Une explication plus détaillée des principales structures de données et du pseudo-code est disponible dans le fichier* : `algorithmique.pdf`

**Représentation vectorielle**

Chaque texte est représenté comme un vecteur dans un espace de n-grammes. La matrice globale Termes x Documents (construite dans `analyse.py > create_comparaison_matrix`) a pour dimension :

  -  **lignes** : tous les n-grammes uniques du corpus
  -  **colonnes** : chaque texte

Chaque cellule contient la fréquence brute du n-gramme dans ce texte.

**Mesures de similarité** (`analyse.py`)

Trois métriques sont implémentées manuellement en s'appuyant sur NumPy

- **Similarité cosinus** : cos(A, B) = (A · B) / (‖A‖ × ‖B‖) ─ Évalue l'angle entre deux vecteurs. C'est la métrique la plus robuste pour comparer des textes de longueurs inégales en se basant sur la fréquence des termes.
- **Indice Jaccard** : J(A, B)   = |A ∩ B| / |A ∪ B| ─​ Mesure le taux de chevauchement du vocabulaire brut, indépendamment des fréquences de répétition.
- **Distance de Manhattan** : d(A, B)   = Σ |Aᵢ − Bᵢ| ─ Calcule la somme des différences absolues de fréquences

**Classification KNN(k=1)** (`analyse.py > knn()`)

Pour chaque texte, on identifie son voisin le plus proche dans le corpus (k=1) et on vérifie si ce voisin appartient à la même catégorie.
La précision globale indique dans quelle mesure la similarité stylistique reflète les catégories (genre, auteur, époque).

La fonction supporte trois métriques via le paramètre `metric` : cosinus, Jaccard et Manhattan.\
Les expériences par défaut utilisent toutes cosinus.

**Cohésion interne** (`analyse.py > groupe_cohesion()`)

Calcule la similarité moyenne entre tous les textes d'une même catégorie. 

**Signatures** (`analyse.py > ngram_signatures()`)

Identifie les n-grammes sur-représentés dans une catégorie par rapport au reste du corpus via un ratio ()

**Réduction de dimension** ── MDS (`plot_generator.py`)

Le MDS (Multidimensional Scaling) projette la matrice de dissimilarité (1 - cosinus) en 2D pour visualiser les regroupements stylistiques.
La dissimilarité est calculée manuellement avant d'être passée à scikit-learn en mode `precomputed`.

**Séquences communes** ── LCS (`analyse.py > lcs, count_freq, analyse_auteur`)

Algorithme LCS (*Longest Common Substring*) optimisé par indexation inversée des positions : les positions de chaque mot dans le texte 2 sont pré-indexées dans un dictionnaire, ce qui évite de parcourir le texte 2 entièrement pour chaque mot du texte 1.

`count_freq` : compte les occurrences exactes de la séquences trouvée dans chaque texte.

`analyse_auteur` : orchestre l'utilisation de fonction lcs et count_freq sur un auteur choisi dans le corpus

**Rapport HTML** (script repport)

`generate_combined_report_html` produit un fichier HTML autonome pour chaucun des trois axes d'analyses (auteurs, genres, époques).

# Aperçu des résultats 

L'exécution du pipeline sur ce corpus médiéval met en lumière plusieurs phénomènes littéraires :

**L'empreinte forte des auteurs** : Les modèles basés sur les n-grammes de caractères (n=3) réussissent avec une meilleure précision à regrouper les œuvres d'un même auteur (ex: le cluster très dense formé par les œuvres de Chrétien de Troyes dans l'espace MDS, visible dans `rapport-auteurs.html`).

**La volatilité orthographique** : Le passage aux n-grammes de mots diminue la précision de l'algorithme KNN. Cela démontre non seulement l'instabilité orthographique des scribes, mais souligne également la grande hétérogénéité du corpus : les textes s'étalent sur plusieurs siècles et croisent différentes aires linguistiques (textes en ancien occitan et en langue d'oïl), ce qui multiplie les variations pour un même mot.

**La prévisibilité des genres** : Les textes épiques ou hagiographiques partagent un lexique thématique très typé, ce qui se traduit par des scores de cohésion interne particulièrement élevés lors des calculs de similarité vectorielle.

**Le poids des mots-outils (stopwords) dans les signatures :** L'extraction des signatures lexicales ayant été réalisée sans filtrage des *stopwords*, les mots les plus distinctifs qui ressortent sont très souvent des mots grammaticaux courts ("a", "ce", etc.). Loin d'être un biais, cela confirme un principe classique de la stylométrie : l'identité stylistique d'un texte (ou d'un auteur) repose souvent davantage sur ses tics syntaxiques inconscients que sur son vocabulaire thématique conscient.


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


