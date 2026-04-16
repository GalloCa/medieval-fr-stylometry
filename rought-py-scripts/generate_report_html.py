"""
Module de génération de rapports HTML stylisés
Génère un rapport HTML avec onglets (une expérience par onglet)
pour les trois axes d'analyse :
              mode='genre'   → rapport-genre.html
              mode='auteurs' → rapport-auteurs.html  (+ LCS optionnel)
              mode='dates'   → rapport-epoques.html

Dépendances :
    analyse.py  (knn, genre_cohesion, ngram_signatures)
"""

import os
import re
import datetime
import base64
from analyse import knn, genre_cohesion, ngram_signatures

# DEFINITION DU CSS A APPLIQUER POUR LA SORTIE HTML 
CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:        #f4f6f8;
  --surface:   #ffffff;
  --surface2:  #f0f2f5;
  --border:    #e4e7eb;
  --ink:       #1c1e21;
  --ink2:      #4b4f56;
  --muted:     #65676b;
  --accent:    #0064d1; 
  --accent-bg: #e6f0ff;
  --good:      #0e8a16;
  --bad:       #d73a49;
  --radius:    24px; 
  --shadow:    0 4px 12px rgba(0,0,0,0.08);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--ink);
  /* Police système simple */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
  font-size: 18px; /* Taille texte */
  line-height: 1.7;
}

/* HEADER */
header {
  background: var(--surface);
  padding: 50px 50px 30px;
  border-bottom: 1px solid var(--border);
  border-radius: 0 0 30px 30px; 
  margin-bottom: 20px;
}

.header-eyebrow {
  font-size: 14px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 10px;
  font-weight: bold;
}

h1 {
  font-size: 2.8rem;
  font-weight: 700;
  color: var(--ink);
}

.header-meta {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-chip {
  font-size: 15px;
  color: var(--ink2);
  background: var(--surface2);
  border-radius: 40px; 
  padding: 8px 18px;
}

.meta-chip b { color: var(--ink); font-weight: bold; }

/* ONGLETS */
.tabs-bar {
  padding: 10px 50px;
  display: flex;
  gap: 15px;
}

.tab-btn {
  font-family: inherit;
  font-size: 18px;
  font-weight: bold;
  color: var(--muted);
  background: var(--surface);
  padding: 12px 24px;
  border: 2px solid transparent;
  border-radius: 30px; 
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.tab-btn:hover { background: var(--surface2); }
.tab-btn.active {
  color: var(--surface);
  background: var(--accent);
  border-color: var(--accent);
}

/* PANNEAUX  */
.tab-panel { display: none; padding: 20px 50px 80px; }
.tab-panel.active { display: block; }

/* SECTIONS */
.tab-section {
  padding: 40px 0;
  border-bottom: 2px dashed var(--border);
}

.tab-section:last-child { border-bottom: none; }

.section-label {
  font-size: 14px;
  font-weight: bold;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 10px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 30px;
}

/* SECTION KNN */
.accuracy-block {
  display: inline-flex;
  align-items: center;
  gap: 20px;
  background: var(--accent-bg);
  border-radius: 30px;
  padding: 15px 30px;
  margin-bottom: 40px;
}

.accuracy-num {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--accent);
}

.accuracy-label { font-size: 16px; color: var(--ink2); font-weight: bold; }

.pairs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

@media (max-width: 860px) { .pairs-grid { grid-template-columns: 1fr; } }

.pairs-group-label {
  font-size: 16px;
  font-weight: bold;
  color: var(--muted);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border);
}

.pair-row {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.pair-score {
  font-size: 16px;
  font-weight: bold;
  min-width: 70px;
  text-align: right;
}

.pair-score.high { color: var(--good); }
.pair-score.low  { color: var(--bad); }
.pair-bar {
  width: 80px; height: 8px; 
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.pair-bar-fill { height: 100%; border-radius: 10px; }
.pair-bar-fill.high { background: var(--good); }
.pair-bar-fill.low  { background: var(--bad); }
.pair-names { font-size: 17px; line-height: 1.5; color: var(--ink); }
.pair-cat   { font-size: 15px; color: var(--muted); }

/* SECTION COHESION */
.cohesion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.cohesion-card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 25px;
  box-shadow: var(--shadow);
  text-align: center;
}

.coh-label {
  font-size: 16px;
  font-weight: bold;
  color: var(--muted);
  margin-bottom: 15px;
}

.coh-score {
  font-size: 2rem;
  font-weight: bold;
  color: var(--ink);
}

.coh-score.na { color: var(--muted); font-size: 1.4rem; }
.coh-unit  { font-size: 14px; color: var(--muted); margin-top: 5px; }

/* SECTION SIGNATURES */
.signatures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.sig-card {
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.sig-card-head {
  background: var(--surface2);
  padding: 15px 20px;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  color: var(--ink);
}
.sig-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
}
code {
  font-family: inherit;
  font-size: 18px;
  font-weight: bold;
  background: #eef2f7;
  color: var(--accent);
  padding: 4px 10px;
  border-radius: 8px;
}
.sig-ratio {
  font-size: 15px;
  color: var(--muted);
  font-weight: bold;
}

/* SECTION VISUALISATION */
.viz-wrap {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}
.viz-wrap img { display: block; width: 100%; height: auto; border-radius: 12px; }

/* SECTION LCS */
.lcs-item {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 25px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}
.lcs-title {
  font-size: 15px;
  font-weight: bold;
  color: var(--muted);
  margin-bottom: 15px;
}
.lcs-freq {
  font-size: 15px;
  color: var(--ink2);
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed var(--border);
}
blockquote {
  border-left: 6px solid var(--accent);
  padding: 15px 20px;
  font-size: 19px;
  background: var(--surface2);
  border-radius: 0 16px 16px 0;
}

/* FOOTER */
.footer {
  padding: 30px 50px;
  font-size: 15px;
  color: var(--muted);
  text-align: center;
}
.footer a { color: var(--accent); text-decoration: none; font-weight: bold; }
</style>"""

# DEFINITION DU JS POUR LA GESTION DES ONGLETS
TABS_JS = """<script>
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(target).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});
</script>"""

# LABELS POUR LES ONGLETS ET SECTIONS
TAB_LABELS = {
    'morpho': 'N-grammes caractères (n=3)',
    'lexical': 'N-grammes mots (n=2)',
}

# LABELS POUR LES CATÉGORIES D'ANALYSE
MODE_LABELS = {
    'genre':   ('Genre littéraire', 'genres'),
    'auteurs': ('Auteur','auteurs'),
    'dates':   ('Époque','époques'),
}

# PARSEURS

def _parse_knn(knn_str):
    """
    Analyse le texte brut des résultats KNN pour extraire les métriques, convertit
    la sortie de la fonction analyse.knn() en données structurées pour le tableau html.

    Entrée : 
      knn_str (str) : la chaine de charactères brute renvoyée par le knn().

    Sortie :
      tuple : accuracy, top_pairs, bot_pairs
          - accuracy (float) : le pourcentage de précision de l'algorithme
          - top_pairs (list of dict) : les 5 paires les plus proches
          - bot_pairs (list of dict) : les 5 paires les plus éloignés
          format du dict {'score' : float, 't1' : str, 'c1' : str, 't2': str, 'c2': str}
    """
    accuracy, top_pairs, bot_pairs = None, [], []
    current = None
    for line in knn_str.strip().split('\n'):
        if 'Précision' in line:
            m = re.search(r'(\d+\.?\d*)\%', line)
            if m:
                accuracy = float(m.group(1))
        elif 'plus proches' in line.lower():
            current = 'top'
        elif 'plus éloignées' in line.lower():
            current = 'bot'
        elif line.startswith('-') and current:
            m = re.match(
                r'-\s+\*\*([\d.]+)\*\*\s*:\s*(.+?)\s*\((.+?)\)\s*/\s*(.+?)\s*\((.+?)\)',
                line)
            if m:
                entry = {'score': float(m.group(1)),
                         't1': m.group(2).strip(), 'c1': m.group(3).strip(),
                         't2': m.group(4).strip(), 'c2': m.group(5).strip()}
                (top_pairs if current == 'top' else bot_pairs).append(entry)
    return accuracy, top_pairs, bot_pairs

def _parse_cohesion(cohesion_str):
    """
    Analyse le texte brut des résultats de cohésion pour extraire les métriques 
    afin de construire les cartes en html

    Entrée : 
      cohesion_str (str) : la chaine de caractère brute renvoyée par genre_cohesion()
    
      Sortie :
        list oD dict : liste contenant un dictionnaire par catégorie
        format : {'genre' : str, 'na' : bool, 'score' : str ou None, 'unite" : str ou None}
    """
    results = []
    for line in cohesion_str.strip().split('\n'):
        m = re.match(r'-\s+\*\*(.+?)\*\*\s*:\s*(.+)', line)
        if m:
            genre = m.group(1).strip()
            rest  = m.group(2).strip()
            na    = bool(re.search(r'Non calculable', rest))
            score = re.search(r'([\d.]+)', rest)
            unite = re.search(r'\((.+?)\)', rest)
            results.append({
                'genre': genre,
                'na':    na,
                'score': score.group(1) if score and not na else None,
                'unite': unite.group(1) if unite and not na else None,
            })
    return results

def _parse_signatures(sig_str):
    """
    Analyse le texte brut des résultats des signatures pour extraire les n-grammes clés et
    leurs fréquences afin des les afficher en html
    
    Entrée :
      sig_str (str) :

    Sortie : 
      dict : dictionnaire groupant les n-grammes par catégorie
      format : {'Nom_Catégorie' : [('ngramme', fréquence), ...], ...}

    """
    sections = {}
    current = None
    for line in sig_str.strip().split('\n'):
        m_h = re.search(r"Signature\s*:\s*'(.+?)'", line)
        if m_h:
            current = m_h.group(1)
            sections[current] = []
            continue
        if current and line.startswith('-'):
            m = re.match(r"-\s+'(.+?)'\s+\(ratio\s*:\s*([\d.]+)\)", line)
            if m:
                sections[current].append((m.group(1), float(m.group(2))))
    return sections


# CONSTRUCTION PAGE HTML 
def _pair_rows(pairs, cls):
    """
    Fonctiuon pour générer les balises html (barres de progression et textes) pour 
    afficher les paries de textes (plus proches  / plus éloignés)

    Entrées : 
      pairs (list of dict) : liste des paires extraites par _parse_knn()
      cls (str) : classe de CSS à appliquer
    
      Sortie : 
        str : le sous-bloc html formaté 
    """
    if not pairs:
        return '<p style="color:var(--muted);font-size:13px">Aucune paire calculable.</p>'
    scores = [p['score'] for p in pairs]
    lo, hi = min(scores), max(scores)
    rang   = hi - lo if hi != lo else 1
    rows   = []
    for p in pairs:
        pct = int(((p['score'] - lo) / rang) * 100)
        rows.append(f"""
      <div class="pair-row">
        <span class="pair-score {cls}">{p['score']:.4f}</span>
        <div class="pair-bar">
          <div class="pair-bar-fill {cls}" style="width:{pct}%"></div>
        </div>
        <div class="pair-names">
          {p['t1']} <span class="pair-cat">({p['c1']})</span><br>
          {p['t2']} <span class="pair-cat">({p['c2']})</span>
        </div>
      </div>""")
    return "\n".join(rows)


def _build_tab(suffixe, data, biblio, mode, report_output_path, lcs_content=None):
    """
    Construit le html d'un panneau d'onglet pour une expérience (ngramme de mots ou de caractères)
    Appelle les fonctions d'analyses, les parseurs et leurs résultats et génére l'interface de sortie

    Entrées : 
        suffixe (str) : l'identifiant de l'expérience (ex: 'char3', 'word2')
        data (dict) : les données de l'expérience ('matrix', 'txt_names', 'lexique', etc.)
        biblio (dict) : le dictionnaire des métadonnées
        mode (str) : l'axe d'analyse ('genre', 'auteurs', 'dates')
        report_output_path (str) : le chemin où le HTML final sera sauvegardé
        lcs_content (str, optionnel) : le texte du rapport LCS à intégrer (pour les auteurs)
    
    Sortie : 
      str : le code html complet pour l'onglet
    """

    matrix    = data['matrix']
    txt_names = data['txt_names']
    lexique   = data['lexique']
    img_path  = data.get('img_path')
    metric    = data.get('metric', 'cosinus')

    cat_label, _ = MODE_LABELS.get(mode, ('Catégorie', 'catégories'))

    # Appel des fonctions d'analyse et parseurs pour extraire les données structurées
    knn_str      = knn(matrix, txt_names, biblio, metric=metric)
    cohesion_str = genre_cohesion(matrix, txt_names, biblio, metric=metric)
    unique_cats  = sorted(set(biblio.values()))
    sigs_str     = "\n".join(
        ngram_signatures(matrix, txt_names, biblio, lexique,
                         target_genre=g, top=5)
        for g in unique_cats
    )

    accuracy, top_pairs, bot_pairs = _parse_knn(knn_str)
    cohesion_data = _parse_cohesion(cohesion_str)
    sig_data      = _parse_signatures(sigs_str)

    acc_val = f"{accuracy:.1f}%" if accuracy is not None else "N/A"

    # SECTION 01 : KNN 
    knn_html = f"""
    <div class="tab-section">
      <div class="section-label">01 — Classification</div>
      <div class="section-title">KNN — Voisinage le plus proche (k=1)</div>
      <div class="accuracy-block">
        <span class="accuracy-num">{acc_val}</span>
        <span class="accuracy-label">Précision · {metric}</span>
      </div>
      <div class="pairs-grid">
        <div>
          <div class="pairs-group-label">▲ 5 paires les plus proches</div>
          {_pair_rows(top_pairs, 'high')}
        </div>
        <div>
          <div class="pairs-group-label">▽ 5 paires les plus éloignées</div>
          {_pair_rows(bot_pairs, 'low')}
        </div>
      </div>
    </div>"""

    # SECTION 02 : COHESION
    cards = ""
    for item in cohesion_data:
        if item['na']:
            cards += f"""
        <div class="cohesion-card">
          <div class="coh-label">{item['genre']}</div>
          <div class="coh-score na">N/A</div>
          <div class="coh-unit">1 seul texte</div>
        </div>"""
        else:
            pct = int(min(float(item['score']), 1.0) * 100)
            cards += f"""
        <div class="cohesion-card">
          <div class="coh-label">{item['genre']}</div>
          <div class="coh-score">{item['score']}</div>
          <div class="coh-unit">{item.get('unite', '')}</div>
          <div class="coh-bar"><div class="coh-bar-fill" style="width:{pct}%"></div></div>
        </div>"""

    cohesion_html = f"""
    <div class="tab-section">
      <div class="section-label">02 — Cohésion interne</div>
      <div class="section-title">Similarité moyenne par {cat_label.lower()}</div>
      <div class="cohesion-grid">{cards}</div>
    </div>"""

    # SECTION 03 : N6GRAMS SIGNATURE
    sig_cards = ""
    for genre, ngrams in sig_data.items():
        rows = "".join(f"""
          <div class="sig-row">
            <code>{ng}</code>
            <span class="sig-ratio">×{ratio:.2f}</span>
          </div>""" for ng, ratio in ngrams)
        sig_cards += f"""
        <div class="sig-card">
          <div class="sig-card-head">{genre}</div>
          {rows}
        </div>"""

    sig_html = f"""
    <div class="tab-section">
      <div class="section-label">03 — Signatures lexicales</div>
      <div class="section-title">N-grammes caractéristiques par {cat_label.lower()}</div>
      <div class="signatures-grid">{sig_cards}</div>
    </div>"""

    # SECTION 04 : VISUALISATION - SCATTER PLOT
    viz_html = ""
    if img_path:
        def _embed_img(img_path):
          try:
            with open(img_path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            return f"data:image/png;base64,{data}"
          except (FileNotFoundError, TypeError):
            return None

        embedded = _embed_img(img_path)
        if embedded:
            viz_html = f"""
            <div class="tab-section">
              ...
              <div class="viz-wrap">
                <img src="{embedded}" alt="Scatter plot {suffixe}">
              </div>
            </div>"""

    # SECTION 05 : LCS 
    lcs_html = ""
    if lcs_content:
        auteur_cible = "Auteur Inconnu"
        nom_auteur = re.search(r"Séquences récurrentes de\s+(.+)", lcs_content)
        if nom_auteur:
            auteur_cible = nom_auteur.group(1).strip()
            
        blocks = []
        cur_title, cur_quote, cur_freq = None, None, None
        for line in lcs_content.split('\n'):
            m_t = re.match(
                r'-\s+\*\*(.+?)\*\*\s+et\s+\*\*(.+?)\*\*\s+\((\d+)\s+caractères\)',
                line)
            m_q = re.match(r'\s*>\s*[«»\s]*\*?(.+?)\*?\s*»?\s*$', line)
            m_f = re.match(r'\s*-\s*apparitions\s*:\s*(.+)', line)
            if m_t:
                if cur_title:
                    blocks.append((cur_title, cur_quote, cur_freq))
                cur_title = f"{m_t.group(1)} × {m_t.group(2)} ({m_t.group(3)} car.)"
                cur_quote, cur_freq = None, None
            elif m_q and cur_title:
                cur_quote = m_q.group(1).strip()
            elif m_f and cur_title:
                cur_freq = m_f.group(1).strip()
        
        if cur_title:
            blocks.append((cur_title, cur_quote, cur_freq))

        items = "".join(f"""
          <div class="lcs-item">
            <div class="lcs-title">{t}</div>
            {"<blockquote>« " + q + " »</blockquote>" if q else ""}
            {"<div class='lcs-freq'>" + f + "</div>" if f else ""}
          </div>""" for t, q, f in blocks)

        lcs_html = f"""
    <div class="tab-section">
      <div class="section-label">05 — Séquences récurrentes</div>
      <div class="section-title">LCS — Formules partagées · {auteur_cible}</div>
      <div>{items}</div>
    </div>"""

    return knn_html + cohesion_html + sig_html + viz_html + lcs_html


# FONCTION PRINCIPALE - GENERATION DU RAPPORT
def generate_combined_report_html(resultats, biblio, output_path, mode,
                                   lcs_content=None, titre=None):
    """
    Génère un rapport HTML avec onglets — une expérience par onglet.
    Récupère 

    Entrées :
        resultats (dict)   : {suffixe: {'matrix', 'txt_names', 'lexique',
                                         'img_path', 'metric'}}
                             L'ordre d'insertion = ordre des onglets.
        biblio (dict)      : métadonnées {nom_texte : catégorie}
        output_path (str)  : chemin de sortie ABSOLU ou relatif au CWD.
                             Ex : r'/workspaces/proj/results/rapports/rapport-genre.html'
        mode (str)         : 'genre' | 'auteurs' | 'dates'
        lcs_content (str)  : contenu LCS optionnel (uniquement si mode='auteurs')
        titre (str)        : titre affiché dans le header (auto-généré si None)

    Sortie :
        Écrit le fichier .html et retourne son chemin absolu.
    """
    cat_label, cat_plural = MODE_LABELS.get(mode, ('Catégorie', 'catégories'))
    titre = titre or f"Analyse par {cat_plural.capitalize()}"
    dd    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    first_data = next(iter(resultats.values()))
    nb_textes  = len(first_data['txt_names'])
    nb_cats    = len(set(biblio.values()))

    # Construction du HTML pour les onglets et leurs contenus
    buttons = ""
    panels  = ""
    for idx, (suffixe, data) in enumerate(resultats.items()):
        active  = "active" if idx == 0 else ""
        label   = TAB_LABELS.get(suffixe, suffixe)
        lcs_tab = lcs_content if (mode == 'auteurs' and suffixe == 'lexical') else None
        contenu = _build_tab(suffixe, data, biblio, mode, output_path, lcs_tab)

        buttons += f'<button class="tab-btn {active}" data-tab="tab-{suffixe}">{label}</button>\n'
        panels  += f'<div class="tab-panel {active}" id="tab-{suffixe}">{contenu}</div>\n'

    html = f"""<!DOCTYPE html>
          <html lang="fr">
          <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{titre} · Analyse corpus d'Ancien Français</title>
          {CSS}
        </head>
        <body>

        <header>
          <div class="header-eyebrow">Analyse d'un corpus d'Ancien Français</div>
          <h1>{titre}</h1>
          <div class="header-meta">
            <div class="meta-chip">Généré le <b>{dd}</b></div>
            <div class="meta-chip">Textes <b>{nb_textes}</b></div>
            <div class="meta-chip">{cat_label}s <b>{nb_cats}</b></div>
          </div>
        </header>

        <div class="tabs-bar">
        {buttons}
        </div>

        {panels}

        <div class="footer">
          Source : (2018). <em>Open Medieval French</em>.
          <a href="https://github.com/OpenMedFr/texts" target="_blank">https://github.com/OpenMedFr/texts</a>
        </div>

        {TABS_JS}
        </body>
        </html>"""

    # Sauvegarde du HTML dans le fichier de sortie
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    if not abs_path.endswith('.html'):
        abs_path = re.sub(r'\.(md|txt)$', '.html', abs_path)

    with open(abs_path, mode='w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rapport HTML généré : {abs_path}")
    return abs_path
