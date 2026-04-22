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


