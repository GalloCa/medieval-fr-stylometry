"""
Module de génération de rapports HTML stylisés
Analyse d'un corpus de l'Ancien Français

Consomme directement les structures de données retournées par analyse.py
(dicts et listes).

Fonction exportée :
    generate_combined_report_html(resultats, biblio, output_path, mode,
                                  lcs_content=None, titre=None)
Dépendances :
    analyse.py (knn, genre_cohesion, ngram_signatures)
"""

import os
import re
import base64
import datetime
from analyse import knn, groupe_cohesion, ngram_signatures

# Visuel de la page --> PAS LA BONNE 
CSS = """<style>
:root {
  --bg:        #f4f6f8;
  --surface:   #ffffff;
  --surface2:  #f0f2f5;
  --border:    #e4e7eb;
  --ink:       #1c1e21;
  --ink2:      #4b4f56;
  --muted:     #65676b;
  --accent:    #0064d1; /* Un bleu plus classique et lisible */
  --accent-bg: #e6f0ff;
  --good:      #0e8a16;
  --bad:       #d73a49;
  --radius:    24px; /* Beaucoup plus arrondi, moins rigide */
  --shadow:    0 4px 12px rgba(0,0,0,0.08);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--ink);
  /* Police système simple, sans chichis, très lisible */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
  font-size: 18px; /* Texte globalement plus grand */
  line-height: 1.7;
}

/* ── HEADER ── */
header {
  background: var(--surface);
  padding: 50px 50px 30px;
  border-bottom: 1px solid var(--border);
  border-radius: 0 0 30px 30px; /* Adoucit le bas du header */
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
  border-radius: 30px; /* Forme de pilule très arrondie */
  padding: 8px 18px;
}
.meta-chip b { color: var(--ink); font-weight: bold; }

/* ── ONGLETS ── */
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
  border-radius: 30px; /* Boutons tout ronds */
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

/* ── PANNEAUX ── */
.tab-panel { display: none; padding: 20px 50px 80px; }
.tab-panel.active { display: block; }

/* ── SECTIONS ── */
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

/* ── KNN ── */
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
  width: 80px; height: 8px; /* Barre plus épaisse */
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
}
.pair-bar-fill { height: 100%; border-radius: 10px; }
.pair-bar-fill.high { background: var(--good); }
.pair-bar-fill.low  { background: var(--bad); }
.pair-names { font-size: 17px; line-height: 1.5; color: var(--ink); }
.pair-cat   { font-size: 15px; color: var(--muted); }

/* ── COHÉSION ── */
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

/* ── SIGNATURES ── */
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

/* ── VISUALISATION ── */
.viz-wrap {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}
.viz-wrap img { display: block; width: 100%; height: auto; border-radius: 12px; }

/* ── LCS ── */
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

/* ── FOOTER ── */
.footer {
  padding: 30px 50px;
  font-size: 15px;
  color: var(--muted);
  text-align: center;
}
.footer a { color: var(--accent); text-decoration: none; font-weight: bold; }
</style>"""

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

# NOMS DES ONGLETS
TAB_LABELS = {
    'morpho':  'N-grammes morphologiques (n=3)',
    'lexical': 'N-grammes lexicaux (n=2)',
}

# MODE D'EXPERIENCE
MODE_LABELS = {
    'genre':   ('Genre littéraire', 'genres'),
    'auteurs': ('Auteur',           'auteurs'),
    'dates':   ('Époque',           'époques'),
}



# BLOCS HTML 
def _embed_img(img_path):
    """Encode une image PNG en base64 pour l'intégrer dans le HTML."""
    try:
        with open(img_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        return f"data:image/png;base64,{data}"
    except (FileNotFoundError, TypeError):
        return None


def _html_pairs(pairs, cls):
    """Génère les lignes de paires KNN depuis une liste de dicts."""
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

def _html_knn(knn_data, metric):
    """Section KNN depuis le dict retourné par knn()."""
    acc = f"{knn_data['accuracy']:.1f}%"
    return f"""
    <div class="tab-section">
      <div class="section-label">01 — Classification</div>
      <div class="section-title">KNN — Voisinage le plus proche (k=1)</div>
      <div class="accuracy-block">
        <span class="accuracy-num">{acc}</span>
        <span class="accuracy-label">Précision · {metric}</span>
      </div>
      <div class="pairs-grid">
        <div>
          <div class="pairs-group-label">▲ 5 paires les plus proches</div>
          {_html_pairs(knn_data['top'], 'high')}
        </div>
        <div>
          <div class="pairs-group-label">▽ 5 paires les plus éloignées</div>
          {_html_pairs(knn_data['bot'], 'low')}
        </div>
      </div>
    </div>"""

def _html_cohesion(cohesion_data, cat_label):
    """Section cohésion depuis la liste retournée par genre_cohesion()."""
    cards = ""
    for item in cohesion_data:
        if item['na']:
            cards += f"""
        <div class="cohesion-card">
          <div class="coh-label">{item['cat']}</div>
          <div class="coh-score na">N/A</div>
          <div class="coh-unit">1 seul texte</div>
        </div>"""
        else:
            pct = int(min(item['score'], 1.0) * 100)
            cards += f"""
        <div class="cohesion-card">
          <div class="coh-label">{item['cat']}</div>
          <div class="coh-score">{item['score']}</div>
          <div class="coh-unit">{item['unite']}</div>
          <div class="coh-bar"><div class="coh-bar-fill" style="width:{pct}%"></div></div>
        </div>"""
    return f"""
    <div class="tab-section">
      <div class="section-label">02 — Cohésion interne</div>
      <div class="section-title">Similarité moyenne par {cat_label.lower()}</div>
      <div class="cohesion-grid">{cards}</div>
    </div>"""

def _html_signatures(sig_data, cat_label):
    """Section signatures depuis le dict {cat: [{'ngram', 'ratio'}]} ."""
    cards = ""
    for cat, ngrams in sig_data.items():
        rows = "".join(f"""
          <div class="sig-row">
            <code>{item['ngram']}</code>
            <span class="sig-ratio">×{item['ratio']:.2f}</span>
          </div>""" for item in ngrams)
        cards += f"""
        <div class="sig-card">
          <div class="sig-card-head">{cat}</div>
          {rows if rows else '<div class="sig-row"><span style="color:var(--muted);font-size:12px">Aucun n-gramme</span></div>'}
        </div>"""
    return f"""
    <div class="tab-section">
      <div class="section-label">03 — Signatures lexicales</div>
      <div class="section-title">N-grammes caractéristiques par {cat_label.lower()}</div>
      <div class="signatures-grid">{cards}</div>
    </div>"""

def _html_viz(img_path, suffixe):
    """Section visualisation avec image encodée en base64."""
    if not img_path:
        return ""
    embedded = _embed_img(img_path)
    if embedded:
        return f"""
    <div class="tab-section">
      <div class="section-label">04 — Visualisation</div>
      <div class="section-title">Nuage de points (MDS – Similarité Cosinus)</div>
      <div class="viz-wrap">
        <img src="{embedded}" alt="Scatter plot {suffixe}">
      </div>
    </div>"""
    return f"""
    <div class="tab-section">
      <div class="section-label">04 — Visualisation</div>
      <div class="section-title">Nuage de points</div>
      <div class="viz-error">⚠ Image introuvable : {img_path}</div>
    </div>"""

def _html_lcs(lcs_data):
    """Section LCS depuis la liste retournée par analyse_auteur()."""
    if not lcs_data:
        return ""

    items = "".join(f"""
      <div class="lcs-item">
        <div class="lcs-title">{b['nom1']} × {b['nom2']} ({b['len']} car.)</div>
        <blockquote>« {b['seq']} »</blockquote>
        <div class="lcs-freq">{b['nom1']} ×{b['freq1']} / {b['nom2']} ×{b['freq2']}</div>
      </div>""" for b in lcs_data)

    return f"""
    <div class="tab-section">
      <div class="section-label">05 — Séquences récurrentes</div>
      <div class="section-title">LCS — Formules partagées · Chrétien de Troyes</div>
      <div>{items}</div>
    </div>"""

# CONSTRUCTION D'UN ONGLET
def _build_tab(suffixe, data, biblio, mode, lcs_content=None):
    """
    Construit le HTML complet d'un panneau d'onglet.

    Appelle directement knn(), genre_cohesion() et ngram_signatures()
    et passe leurs résultats (dicts/listes) aux fonctions HTML — sans
    aucune conversion Markdown intermédiaire.
    """
    matrix    = data['matrix']
    txt_names = data['txt_names']
    lexique   = data['lexique']
    img_path  = data.get('img_path')
    metric    = data.get('metric', 'cosinus')

    cat_label, _ = MODE_LABELS.get(mode, ('Catégorie', 'catégories'))

    # Calculs
    knn_data      = knn(matrix, txt_names, biblio, metric=metric)
    cohesion_data = groupe_cohesion(matrix, txt_names, biblio, metric=metric)

    unique_cats = sorted(set(biblio.values()))
    sig_data    = {
        cat: ngram_signatures(matrix, txt_names, biblio, lexique,
                              target_cat=cat, top=5)
        for cat in unique_cats
    }

    # ── HTML ──
    return (
        _html_knn(knn_data, metric)
        + _html_cohesion(cohesion_data, cat_label)
        + _html_signatures(sig_data, cat_label)
        + _html_viz(img_path, suffixe)
        + _html_lcs(lcs_content)
    )


# FONCTION PRINCIPALE
def generate_combined_report_html(resultats, biblio, output_path, mode,
                                   lcs_content=None, titre=None):
    """
    Génère un rapport HTML avec onglets — une expérience par onglet.

    Paramètres :
        resultats (dict)   : {suffixe: {'matrix', 'txt_names', 'lexique',
                                         'img_path', 'metric'}}
        biblio (dict)      : métadonnées {nom_texte : catégorie}
        output_path (str)  : chemin de sortie absolu ou relatif au CWD
        mode (str)         : 'genre' | 'auteurs' | 'dates'
        lcs_content (str)  : sortie de analyse_auteur() (mode='auteurs' uniquement)
        titre (str)        : titre affiché dans le header

    Sortie :
        fichier .html écrit dans output_path
    """
    cat_label, cat_plural = MODE_LABELS.get(mode, ('Catégorie', 'catégories'))
    titre = titre or f"Analyse par {cat_plural.capitalize()}"
    dd    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    first_data = next(iter(resultats.values()))
    nb_textes  = len(first_data['txt_names'])
    nb_cats    = len(set(biblio.values()))

    buttons = ""
    panels  = ""
    for idx, (suffixe, data) in enumerate(resultats.items()):
        active  = "active" if idx == 0 else ""
        label   = TAB_LABELS.get(suffixe, suffixe)
        lcs_tab = lcs_content if (mode == 'auteurs' and suffixe == 'lexical') else None
        contenu = _build_tab(suffixe, data, biblio, mode, lcs_tab)

        buttons += f'<button class="tab-btn {active}" data-tab="tab-{suffixe}">{label}</button>\n'
        panels  += f'<div class="tab-panel {active}" id="tab-{suffixe}">{contenu}</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titre} · Corpus d'Ancien Français</title>
  {CSS}
</head>
<body>

<header>
  <div class="header-eyebrow">Analyse · Ancien Français</div>
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

    # Ecriture
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    if not abs_path.endswith('.html'):
        abs_path = re.sub(r'\.(md|txt)$', '.html', abs_path)

    with open(abs_path, mode='w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rapport HTML généré : {abs_path}")
    return abs_path
