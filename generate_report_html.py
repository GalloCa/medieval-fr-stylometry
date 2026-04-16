"""
Module de génération de rapports HTML stylisés
Analyse Stylométrique de l'Ancien Français

Consomme directement les structures de données retournées par analyse.py
(dicts et listes) — aucun parsing de Markdown intermédiaire.

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
from analyse import knn, genre_cohesion, ngram_signatures


# ═══════════════════════════════════════════════════════════════
# DESIGN — sobre / académique
# Palette : parchemin chaud, encre foncée, rehauts bordeaux
# Typo    : Lora (serif) + JetBrains Mono (code)
# ═══════════════════════════════════════════════════════════════

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:        #f7f4ef;
  --surface:   #ffffff;
  --surface2:  #f0ece4;
  --border:    #ddd8ce;
  --border2:   #cbc4b8;
  --ink:       #1e1a16;
  --ink2:      #4a4540;
  --muted:     #8a8278;
  --accent:    #7a2c2c;
  --accent2:   #a84040;
  --accent-bg: #f5eeee;
  --good:      #2d6a2d;
  --bad:       #8a2020;
  --radius:    5px;
  --shadow:    0 1px 4px rgba(0,0,0,.07);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--ink);
  font-family: 'Lora', Georgia, serif;
  font-size: 16px;
  line-height: 1.75;
}

/* ── HEADER ── */
header {
  background: var(--surface);
  border-bottom: 2px solid var(--accent);
  padding: 44px 72px 36px;
}
.header-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
}
h1 {
  font-size: clamp(1.5rem, 2.8vw, 2.2rem);
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -.02em;
  line-height: 1.2;
}
.header-meta {
  margin-top: 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.meta-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 3px 10px;
}
.meta-chip b { color: var(--ink2); font-weight: 500; }

/* ── ONGLETS ── */
.tabs-bar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 72px;
  display: flex;
  position: sticky;
  top: 0;
  z-index: 20;
  box-shadow: 0 2px 8px rgba(0,0,0,.05);
}
.tab-btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 14px 20px;
  cursor: pointer;
  transition: color .15s, border-color .15s;
  margin-bottom: -1px;
  white-space: nowrap;
}
.tab-btn:hover { color: var(--ink2); }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

/* ── PANNEAUX ── */
.tab-panel { display: none; padding: 0 72px 80px; }
.tab-panel.active { display: block; }

/* ── SECTIONS ── */
.tab-section {
  padding: 48px 0 40px;
  border-bottom: 1px solid var(--border);
}
.tab-section:last-child { border-bottom: none; }
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
}
.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 24px;
  letter-spacing: -.01em;
}

/* ── KNN ── */
.accuracy-block {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  background: var(--accent-bg);
  border: 1px solid #d8b8b8;
  border-radius: var(--radius);
  padding: 14px 22px;
  margin-bottom: 28px;
}
.accuracy-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.2rem;
  font-weight: 500;
  color: var(--accent);
  line-height: 1;
  letter-spacing: -.04em;
}
.accuracy-label { font-size: 13px; color: var(--ink2); }
.pairs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}
@media (max-width: 860px) { .pairs-grid { grid-template-columns: 1fr; } }
.pairs-group-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.pair-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 0;
  border-bottom: 1px solid var(--border);
}
.pair-row:last-child { border-bottom: none; }
.pair-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  min-width: 52px;
  text-align: right;
  flex-shrink: 0;
}
.pair-score.high { color: var(--good); }
.pair-score.low  { color: var(--bad); }
.pair-bar {
  width: 60px; height: 3px;
  background: var(--border);
  border-radius: 2px;
  flex-shrink: 0;
  overflow: hidden;
}
.pair-bar-fill { height: 100%; border-radius: 2px; }
.pair-bar-fill.high { background: var(--good); }
.pair-bar-fill.low  { background: var(--bad); }
.pair-names { font-size: 14px; line-height: 1.4; color: var(--ink2); }
.pair-cat   { font-size: 12px; color: var(--muted); font-style: italic; }

/* ── COHÉSION ── */
.cohesion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 12px;
}
.cohesion-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  box-shadow: var(--shadow);
  transition: border-color .15s;
}
.cohesion-card:hover { border-color: var(--border2); }
.coh-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 6px;
}
.coh-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.4rem;
  color: var(--ink);
  line-height: 1;
}
.coh-score.na { color: var(--muted); font-size: 1rem; }
.coh-unit  { font-size: 11px; color: var(--muted); margin-top: 4px; }
.coh-bar   { margin-top: 10px; height: 2px; background: var(--border); border-radius: 1px; overflow: hidden; }
.coh-bar-fill { height: 100%; background: var(--accent2); border-radius: 1px; }

/* ── SIGNATURES ── */
.signatures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}
.sig-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.sig-card-head {
  background: var(--surface2);
  border-bottom: 1px solid var(--border);
  padding: 9px 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--accent);
}
.sig-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 14px;
  border-bottom: 1px solid var(--border);
  transition: background .1s;
}
.sig-row:last-child { border-bottom: none; }
.sig-row:hover { background: var(--surface2); }
code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  background: #eef2f7;
  color: #2a4a7a;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #d0dcea;
}
.sig-ratio {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
}

/* ── VISUALISATION ── */
.viz-wrap {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--surface);
  box-shadow: var(--shadow);
}
.viz-wrap img { display: block; width: 100%; height: auto; }
.viz-error {
  padding: 32px;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--muted);
  background: var(--surface2);
  border: 1px dashed var(--border2);
  border-radius: var(--radius);
}

/* ── LCS ── */
.lcs-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 10px;
  box-shadow: var(--shadow);
}
.lcs-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 10px;
  letter-spacing: .04em;
}
.lcs-freq {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}
blockquote {
  border-left: 3px solid var(--accent);
  padding: 8px 16px;
  font-style: italic;
  color: var(--ink2);
  font-size: 15px;
  background: var(--accent-bg);
  border-radius: 0 var(--radius) var(--radius) 0;
}

/* ── FOOTER ── */
.footer {
  padding: 20px 72px;
  border-top: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  background: var(--surface);
  margin-top: 40px;
}
.footer a { color: var(--accent2); text-decoration: none; }
.footer a:hover { text-decoration: underline; }
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

TAB_LABELS = {
    'morpho':  'N-grammes morphologiques (n=3)',
    'lexical': 'N-grammes lexicaux (n=2)',
    'jaccard': 'Jaccard — morphologique (n=3)',
}

MODE_LABELS = {
    'genre':   ('Genre littéraire', 'genres'),
    'auteurs': ('Auteur',           'auteurs'),
    'dates':   ('Époque',           'époques'),
}


# ═══════════════════════════════════════════════════════════════
# BLOCS HTML — consomment directement les structures de données
# ═══════════════════════════════════════════════════════════════

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


def _html_lcs(lcs_content):
    """
    Section LCS depuis la chaîne brute retournée par analyse_auteur().
    Parse le format :
        - **nom1** et **nom2** (N caractères) :
         > « séquence »
         - apparitions : nom1 x N / nom2 x N
    """
    if not lcs_content:
        return ""

    blocks = []
    cur = {'title': None, 'quote': None, 'freq': None}

    for line in lcs_content.split('\n'):
        m_t = re.match(
            r'-\s+\*\*(.+?)\*\*\s+et\s+\*\*(.+?)\*\*\s+\((\d+)\s+caractères\)', line)
        m_q = re.match(r'\s*>\s*[«»\s]*\*?(.+?)\*?\s*»?\s*$', line)
        m_f = re.match(r'\s*-\s*apparitions\s*:\s*(.+)', line)

        if m_t:
            if cur['title']:
                blocks.append(dict(cur))
            cur = {
                'title': f"{m_t.group(1)} × {m_t.group(2)} ({m_t.group(3)} car.)",
                'quote': None,
                'freq':  None,
            }
        elif m_q and cur['title']:
            cur['quote'] = m_q.group(1).strip()
        elif m_f and cur['title']:
            cur['freq'] = m_f.group(1).strip()

    if cur['title']:
        blocks.append(dict(cur))

    if not blocks:
        return ""

    items = "".join(f"""
      <div class="lcs-item">
        <div class="lcs-title">{b['title']}</div>
        {"<blockquote>« " + b['quote'] + " »</blockquote>" if b['quote'] else ""}
        {"<div class='lcs-freq'>" + b['freq'] + "</div>" if b['freq'] else ""}
      </div>""" for b in blocks)

    return f"""
    <div class="tab-section">
      <div class="section-label">05 — Séquences récurrentes</div>
      <div class="section-title">LCS — Formules partagées · Chrétien de Troyes</div>
      <div>{items}</div>
    </div>"""


# ═══════════════════════════════════════════════════════════════
# CONSTRUCTION D'UN ONGLET
# ═══════════════════════════════════════════════════════════════

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

    # ── Calculs → structures de données ──
    knn_data      = knn(matrix, txt_names, biblio, metric=metric)
    cohesion_data = genre_cohesion(matrix, txt_names, biblio, metric=metric)

    unique_cats = sorted(set(biblio.values()))
    sig_data    = {
        cat: ngram_signatures(matrix, txt_names, biblio, lexique,
                              target_genre=cat, top=5)
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


# ═══════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

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
  <title>{titre} · Stylométrie Ancien Français</title>
  {CSS}
</head>
<body>

<header>
  <div class="header-eyebrow">Analyse Stylométrique · Ancien Français</div>
  <h1>{titre}</h1>
  <div class="header-meta">
    <div class="meta-chip">Généré le <b>{dd}</b></div>
    <div class="meta-chip">Textes <b>{nb_textes}</b></div>
    <div class="meta-chip">{cat_label}s <b>{nb_cats}</b></div>
    <div class="meta-chip">Expériences <b>{len(resultats)}</b></div>
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

    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    if not abs_path.endswith('.html'):
        abs_path = re.sub(r'\.(md|txt)$', '.html', abs_path)

    with open(abs_path, mode='w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rapport HTML généré : {abs_path}")
    return abs_path
