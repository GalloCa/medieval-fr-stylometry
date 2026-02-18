import re
from collections import Counter
from tools import (load_stpwords, clean_texts, save_text, n_gramm, save_freq,
                   create_comparison_matrix, produit_scalaire,
                   norme, cosinus,score_jaccard, clean_label, compare_files, 
                   preparer_corpus, biblio, knn, genre_cohesion,
                   ngram_signatures, confusion_matrix)
from scatter_plot import (similarities_genre, similarities_authors,
                      similarities_dates)