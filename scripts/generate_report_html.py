"""
Module de génération de rapport HTML stylisé
Remplace la fonction generate_report() de analyse.py

Ce module produit des rapports HTML autonomes avec CSS intégré,
conçus pour l'analyse stylométrique de l'Ancien Français.

Usage :
    Remplacer l'import et l'appel de generate_report() dans main2.py :
    
    Ancienne ligne :
        from analyse import create_comparison_matrix, generate_report, compare_files
    
    Nouvelle ligne :
        from analyse import create_comparison_matrix, compare_files
        from generate_report_html import generate_report_html as generate_report
"""

import os
import datetime
from analyse import knn, genre_cohesion, ngram_signatures


# ─────────────────────────────────────────────
# CSS + TEMPLATE HTML
# ─────────────────────────────────────────────

HTML_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Fira+Code:wght@400;500&display=swap');

  :root {
    --bg:        #0f0e0c;
    --surface:   #1a1916;
    --border:    #2e2c28;
    --accent:    #c9a84c;
    --accent2:   #7a5c2e;
    --text:      #e8e0d0;
    --muted:     #7a7060;
    --good:      #5a8a5a;
    --bad:       #8a3a3a;
    --radius:    6px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 17px;
    line-height: 1.7;
    padding: 0 0 80px;
  }

  /* ── En-tête ── */
  header {
    border-bottom: 1px solid var(--border);
    padding: 48px 64px 40px;
    position: relative;
    overflow: hidden;
  }
  header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 60% 80% at 80% 50%, rgba(201,168,76,.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .header-label {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: .18em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 14px;
  }
  h1 {
    font-size: clamp(1.6rem, 3vw, 2.6rem);
    font-weight: 600;
    letter-spacing: -.01em;
    line-height: 1.2;
    color: #f5ead8;
  }
  .meta {
    margin-top: 18px;
    display: flex;
    gap: 32px;
    flex-wrap: wrap;
  }
  .meta-item {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    color: var(--muted);
  }
  .meta-item span { color: var(--text); }

  /* ── Navigation interne ── */
  nav {
    padding: 20px 64px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  nav a {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    text-decoration: none;
    padding: 5px 12px;
    border: 1px solid transparent;
    border-radius: var(--radius);
    transition: all .2s;
  }
  nav a:hover {
    border-color: var(--accent2);
    color: var(--accent);
  }

  /* ── Contenu principal ── */
  main { padding: 0 64px; }

  /* ── Sections ── */
  section {
    padding: 52px 0 40px;
    border-bottom: 1px solid var(--border);
  }
  section:last-child { border-bottom: none; }

  .section-number {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: .2em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  h2 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #f5ead8;
    margin-bottom: 28px;
  }
  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent);
    margin: 30px 0 12px;
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    letter-spacing: .08em;
    text-transform: uppercase;
  }

  /* ── Précision KNN ── */
  .accuracy-badge {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 14px 22px;
    border: 1px solid var(--accent2);
    border-radius: var(--radius);
    background: rgba(201,168,76,.05);
    margin-bottom: 32px;
  }
  .accuracy-value {
    font-family: 'Fira Code', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: var(--accent);
  }
  .accuracy-label {
    font-size: 0.9rem;
    color: var(--muted);
  }

  /* ── Tableaux de paires ── */
  .pairs-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-top: 16px;
  }
  @media (max-width: 900px) { .pairs-grid { grid-template-columns: 1fr; } }

  .pairs-block h3 { margin-top: 0; }

  .pair-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
  }
  .pair-row:last-child { border-bottom: none; }

  .pair-score {
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    font-weight: 500;
    min-width: 54px;
    text-align: right;
  }
  .pair-score.high { color: var(--good); }
  .pair-score.low  { color: var(--bad); }

  .pair-bar {
    width: 80px;
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
    flex-shrink: 0;
  }
  .pair-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: var(--good);
  }
  .pair-bar-fill.low { background: var(--bad); }

  .pair-names { font-size: 14px; line-height: 1.3; }
  .pair-names .cat { color: var(--muted); font-size: 12px; }

  /* ── Cohésion ── */
  .cohesion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px;
    margin-top: 8px;
  }
  .cohesion-card {
    padding: 16px 18px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
  }
  .cohesion-card .genre-name {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 6px;
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .06em;
  }
  .cohesion-card .score {
    font-family: 'Fira Code', monospace;
    font-size: 1.4rem;
    color: var(--text);
  }
  .cohesion-card .score.na { color: var(--muted); font-size: 1rem; }
  .cohesion-card .unit { font-size: 11px; color: var(--muted); margin-top: 2px; }

  /* ── Signatures n-grammes ── */
  .signatures-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    margin-top: 8px;
  }
  .sig-card {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    background: var(--surface);
  }
  .sig-card-header {
    padding: 12px 16px;
    background: rgba(201,168,76,.07);
    border-bottom: 1px solid var(--border);
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--accent);
  }
  .sig-ngram {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 14px;
    transition: background .15s;
  }
  .sig-ngram:last-child { border-bottom: none; }
  .sig-ngram:hover { background: rgba(255,255,255,.02); }
  .sig-ngram code {
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    color: #c8d8e8;
    background: rgba(100,140,200,.1);
    padding: 2px 6px;
    border-radius: 3px;
  }
  .sig-ratio {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    color: var(--muted);
  }

  /* ── Visualisation ── */
  .viz-container {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    background: var(--surface);
  }
  .viz-container img {
    display: block;
    width: 100%;
    height: auto;
  }

  /* ── LCS ── */
  .lcs-block {
    margin-top: 16px;
  }
  .lcs-pair {
    padding: 16px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    margin-bottom: 12px;
  }
  .lcs-pair-title {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 10px;
    font-family: 'Fira Code', monospace;
  }
  blockquote {
    border-left: 3px solid var(--accent2);
    padding: 10px 16px;
    font-style: italic;
    color: #c8c0b0;
    font-size: 15px;
    background: rgba(201,168,76,.03);
    border-radius: 0 var(--radius) var(--radius) 0;
  }

  /* ── Citation ── */
  .citation {
    padding: 20px 64px 0;
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    color: var(--muted);
    border-top: 1px solid var(--border);
    margin-top: 60px;
  }
  .citation a { color: var(--accent2); }
</style>
"""


def _parse_knn_output(knn_str, metric):
    """
    Re-parse les résultats KNN pour les injecter dans le HTML structuré.
    On rappelle knn() directement — cette fonction sert juste à extraire les valeurs.
    """
    lines = knn_str.strip().split('\n')
    accuracy = None
    top_pairs = []
    bot_pairs = []

    current = None
    for line in lines:
        if 'Précision' in line:
            import re
            m = re.search(r'(\d+\.?\d*)\%', line)
            if m:
                accuracy = float(m.group(1))
        elif 'plus proches' in line.lower():
            current = 'top'
        elif 'plus éloignées' in line.lower():
            current = 'bot'
        elif line.startswith('-') and current:
            # Exemple : "- **0.9823** : Yvain (Roman courtois) / Lancelot (Roman courtois)"
            import re
            m = re.match(r'-\s+\*\*([\d.]+)\*\*\s*:\s*(.+?)\s*\((.+?)\)\s*/\s*(.+?)\s*\((.+?)\)', line)
            if m:
                score, t1, c1, t2, c2 = m.groups()
                entry = {'score': float(score), 't1': t1.strip(), 'c1': c1.strip(),
                         't2': t2.strip(), 'c2': c2.strip()}
                if current == 'top':
                    top_pairs.append(entry)
                else:
                    bot_pairs.append(entry)

    return accuracy, top_pairs, bot_pairs


def _parse_cohesion_output(cohesion_str):
    """Extrait les données de cohésion depuis la string Markdown."""
    import re
    results = []
    for line in cohesion_str.strip().split('\n'):
        m = re.match(r'-\s+\*\*(.+?)\*\*\s*:\s*(.+)', line)
        if m:
            genre = m.group(1).strip()
            rest  = m.group(2).strip()
            na_match = re.search(r'Non calculable', rest)
            score_m  = re.search(r'([\d.]+)', rest)
            unite_m  = re.search(r'\((.+?)\)', rest)
            results.append({
                'genre': genre,
                'na': bool(na_match),
                'score': score_m.group(1) if score_m and not na_match else None,
                'unite': unite_m.group(1) if unite_m and not na_match else None,
            })
    return results


def _parse_signatures_output(sig_str):
    """Extrait genre → liste de (ngram, ratio) depuis la string Markdown."""
    import re
    sections = {}
    current_genre = None
    for line in sig_str.strip().split('\n'):
        m_header = re.search(r"Signature\s*:\s*'(.+?)'", line)
        if m_header:
            current_genre = m_header.group(1)
            sections[current_genre] = []
            continue
        if current_genre and line.startswith('-'):
            m = re.match(r"-\s+'(.+?)'\s+\(ratio\s*:\s*([\d.]+)\)", line)
            if m:
                sections[current_genre].append((m.group(1), float(m.group(2))))
    return sections


def _pair_rows_html(pairs, score_class):
    """Génère les lignes de paires pour le tableau HTML."""
    rows = []
    scores = [p['score'] for p in pairs]
    max_s  = max(scores) if scores else 1
    min_s  = min(scores) if scores else 0
    rang   = max_s - min_s if max_s != min_s else 1

    for p in pairs:
        pct = int(((p['score'] - min_s) / rang) * 100)
        rows.append(f"""
        <div class="pair-row">
          <span class="pair-score {score_class}">{p['score']:.4f}</span>
          <div class="pair-bar">
            <div class="pair-bar-fill {'low' if score_class == 'low' else ''}" style="width:{pct}%"></div>
          </div>
          <div class="pair-names">
            {p['t1']} <span class="cat">({p['c1']})</span><br>
            {p['t2']} <span class="cat">({p['c2']})</span>
          </div>
        </div>""")
    return "\n".join(rows)


# ─────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────

def generate_report_html(matrix, txt_names, biblio, lexique,
                         output_path, img_paths, titre=None, metric='cosinus',
                         lcs_content=None):
    """
    Génère un rapport d'analyse stylométrique au format HTML autonome.

    Remplace generate_report() de analyse.py.

    Paramètres :
        matrix (np.ndarray)   : matrice des fréquences (n-grammes x textes)
        txt_names (list)      : noms des textes (colonnes)
        biblio (dict)         : métadonnées {nom : catégorie}
        lexique (list)        : n-grammes ordonnés
        output_path (str)     : chemin de sortie (.html)
        img_paths (list|str)  : chemin(s) vers les images de visualisation.
                                Peut être une str (rétrocompatibilité) ou une liste.
        titre (str)           : titre du rapport
        metric (str)          : 'cosinus' ou 'manhattan'
        lcs_content (str)     : bloc LCS pré-calculé à insérer (optionnel)

    Sortie :
        fichier (.html) dans output_path
    """
    # Rétrocompatibilité : img_paths peut être une string ou une liste
    if isinstance(img_paths, str):
        img_paths = [img_paths] if img_paths else []

    dd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Calculs ──────────────────────────────
    knn_str      = knn(matrix, txt_names, biblio, metric=metric)
    cohesion_str = genre_cohesion(matrix, txt_names, biblio, metric=metric)

    unique_genres = sorted(set(biblio.values()))
    all_sigs_str  = "\n".join(
        ngram_signatures(matrix, txt_names, biblio, lexique,
                         target_genre=g, top=5)
        for g in unique_genres
    )

    # ── Parsing ──────────────────────────────
    accuracy, top_pairs, bot_pairs = _parse_knn_output(knn_str, metric)
    cohesion_data = _parse_cohesion_output(cohesion_str)
    sig_data      = _parse_signatures_output(all_sigs_str)

    # ── Sections HTML ────────────────────────

    # 1. KNN
    acc_val = f"{accuracy:.1f}%" if accuracy is not None else "N/A"

    knn_section = f"""
    <section id="knn">
      <div class="section-number">01 — Classification</div>
      <h2>KNN — Voisinage le plus proche (k=1)</h2>
      <div class="accuracy-badge">
        <span class="accuracy-value">{acc_val}</span>
        <span class="accuracy-label">Précision ({metric})</span>
      </div>
      <div class="pairs-grid">
        <div class="pairs-block">
          <h3>▲ 5 paires les plus proches</h3>
          {_pair_rows_html(top_pairs, 'high')}
        </div>
        <div class="pairs-block">
          <h3>▽ 5 paires les plus éloignées</h3>
          {_pair_rows_html(bot_pairs, 'low')}
        </div>
      </div>
    </section>"""

    # 2. Cohésion
    cohesion_cards = ""
    for item in cohesion_data:
        if item['na']:
            cohesion_cards += f"""
        <div class="cohesion-card">
          <div class="genre-name">{item['genre']}</div>
          <div class="score na">N/A</div>
          <div class="unit">1 seul texte</div>
        </div>"""
        else:
            unite = item.get('unite', '')
            cohesion_cards += f"""
        <div class="cohesion-card">
          <div class="genre-name">{item['genre']}</div>
          <div class="score">{item['score']}</div>
          <div class="unit">{unite}</div>
        </div>"""

    cohesion_section = f"""
    <section id="cohesion">
      <div class="section-number">02 — Cohésion interne</div>
      <h2>Similarité moyenne par catégorie</h2>
      <div class="cohesion-grid">
        {cohesion_cards}
      </div>
    </section>"""

    # 3. Signatures
    sig_cards = ""
    for genre, ngrams in sig_data.items():
        ngram_rows = ""
        for ng, ratio in ngrams:
            ngram_rows += f"""
          <div class="sig-ngram">
            <code>{ng}</code>
            <span class="sig-ratio">ratio {ratio:.2f}</span>
          </div>"""
        sig_cards += f"""
        <div class="sig-card">
          <div class="sig-card-header">{genre}</div>
          {ngram_rows}
        </div>"""

    sig_section = f"""
    <section id="signatures">
      <div class="section-number">03 — Signatures lexicales</div>
      <h2>N-grammes caractéristiques par catégorie</h2>
      <div class="signatures-grid">
        {sig_cards}
      </div>
    </section>"""

    # 4. Visualisations
    viz_html = ""
    if img_paths:
        imgs = ""
        for p in img_paths:
            imgs += f'<div class="viz-container" style="margin-bottom:20px"><img src="{p}" alt="Visualisation"></div>\n'
        viz_section = f"""
    <section id="visualisation">
      <div class="section-number">04 — Visualisation</div>
      <h2>Nuages de points (MDS – Similarité Cosinus)</h2>
      {imgs}
    </section>"""
        viz_html = viz_section

    # 5. LCS (optionnel)
    lcs_html = ""
    if lcs_content:
        import re
        lcs_html_inner = ""
        current_pair_title = None
        current_quote = None
        blocks = []

        for line in lcs_content.split('\n'):
            m_title = re.match(r'-\s+\*\*(.+?)\*\*\s+et\s+\*\*(.+?)\*\*\s+\((\d+)\s+caractères\)', line)
            m_quote = re.match(r'\s*>\s*[«»\s]*\*?(.+?)\*?\s*»?\s*$', line)

            if m_title:
                if current_pair_title:
                    blocks.append((current_pair_title, current_quote))
                current_pair_title = f"{m_title.group(1)} × {m_title.group(2)} ({m_title.group(3)} car.)"
                current_quote = None
            elif m_quote and current_pair_title:
                current_quote = m_quote.group(1).strip()

        if current_pair_title:
            blocks.append((current_pair_title, current_quote))

        for title, quote in blocks:
            q = f'<blockquote>« {quote} »</blockquote>' if quote else ''
            lcs_html_inner += f"""
          <div class="lcs-pair">
            <div class="lcs-pair-title">{title}</div>
            {q}
          </div>"""

        lcs_html = f"""
    <section id="lcs">
      <div class="section-number">05 — Séquences récurrentes</div>
      <h2>LCS — Formules partagées</h2>
      <div class="lcs-block">
        {lcs_html_inner}
      </div>
    </section>"""

    # ── Navigation ───────────────────────────
    nav_items = [
        ('<a href="#knn">KNN</a>', True),
        ('<a href="#cohesion">Cohésion</a>', True),
        ('<a href="#signatures">Signatures</a>', True),
        ('<a href="#visualisation">Visualisation</a>', bool(img_paths)),
        ('<a href="#lcs">LCS</a>', bool(lcs_content)),
    ]
    nav_html = "\n".join(item for item, show in nav_items if show)

    # ── Assemblage final ─────────────────────
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titre or 'Rapport d\'analyse'}</title>
  {HTML_CSS}
</head>
<body>

<header>
  <div class="header-label">Analyse Stylométrique · Ancien Français</div>
  <h1>{titre or 'Rapport d\'analyse'}</h1>
  <div class="meta">
    <div class="meta-item">Généré le &nbsp;<span>{dd}</span></div>
    <div class="meta-item">Métrique &nbsp;<span>{metric}</span></div>
    <div class="meta-item">Textes &nbsp;<span>{len(txt_names)}</span></div>
    <div class="meta-item">Catégories &nbsp;<span>{len(set(biblio.values()))}</span></div>
  </div>
</header>

<nav>
  {nav_html}
</nav>

<main>
  {knn_section}
  {cohesion_section}
  {sig_section}
  {viz_html}
  {lcs_html}
</main>

<div class="citation">
  Source : (2018). <em>Open Medieval French</em>.
  <a href="https://github.com/OpenMedFr/texts" target="_blank">https://github.com/OpenMedFr/texts</a>
</div>

</body>
</html>"""

    # ── Écriture ─────────────────────────────
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not output_path.endswith('.html'):
        output_path = output_path.replace('.md', '.html').replace('.txt', '.html')

    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rapport HTML généré : {output_path}")
    return output_path


def _build_tab_content(suffixe, data, biblio, lcs_content=None):
    """
    Construit le contenu HTML d'un onglet pour une expérience donnée.

    Entrées :
        suffixe (str)      : identifiant de l'expérience ('caracteres3', 'mots2')
        data (dict)        : {'matrix', 'txt_names', 'lexique', 'img_path', 'metric'}
        biblio (dict)      : métadonnées {nom : auteur}
        lcs_content (str)  : contenu LCS optionnel (uniquement pour caracteres3)
    Sortie :
        str : HTML du contenu de l'onglet
    """
    import re

    matrix    = data['matrix']
    txt_names = data['txt_names']
    lexique   = data['lexique']
    img_path  = data['img_path']
    metric    = data['metric']

    # ── Calculs ──
    knn_str      = knn(matrix, txt_names, biblio, metric=metric)
    cohesion_str = genre_cohesion(matrix, txt_names, biblio, metric=metric)
    unique_cats  = sorted(set(biblio.values()))
    all_sigs_str = "\n".join(
        ngram_signatures(matrix, txt_names, biblio, lexique, target_genre=g, top=5)
        for g in unique_cats
    )

    accuracy, top_pairs, bot_pairs = _parse_knn_output(knn_str, metric)
    cohesion_data = _parse_cohesion_output(cohesion_str)
    sig_data      = _parse_signatures_output(all_sigs_str)

    acc_val = f"{accuracy:.1f}%" if accuracy is not None else "N/A"

    # ── KNN ──
    cohesion_cards = ""
    for item in cohesion_data:
        if item['na']:
            cohesion_cards += f"""
            <div class="cohesion-card">
              <div class="genre-name">{item['genre']}</div>
              <div class="score na">N/A</div>
              <div class="unit">1 seul texte</div>
            </div>"""
        else:
            cohesion_cards += f"""
            <div class="cohesion-card">
              <div class="genre-name">{item['genre']}</div>
              <div class="score">{item['score']}</div>
              <div class="unit">{item.get('unite', '')}</div>
            </div>"""

    # ── Signatures ──
    sig_cards = ""
    for genre, ngrams in sig_data.items():
        rows = "".join(f"""
              <div class="sig-ngram">
                <code>{ng}</code>
                <span class="sig-ratio">ratio {ratio:.2f}</span>
              </div>""" for ng, ratio in ngrams)
        sig_cards += f"""
            <div class="sig-card">
              <div class="sig-card-header">{genre}</div>
              {rows}
            </div>"""

    # ── Visualisation ──
    viz_html = ""
    if img_path:
        viz_html = f"""
            <div class="tab-section">
              <div class="section-number">04 — Visualisation</div>
              <h3 class="sec-h3">Nuage de points (MDS – Cosinus)</h3>
              <div class="viz-container">
                <img src="{img_path}" alt="Scatter plot {suffixe}">
              </div>
            </div>"""

    # ── LCS ──
    lcs_html = ""
    if lcs_content:
        blocks = []
        current_title = None
        current_quote = None
        for line in lcs_content.split('\n'):
            m_t = re.match(r'-\s+\*\*(.+?)\*\*\s+et\s+\*\*(.+?)\*\*\s+\((\d+)\s+caractères\)', line)
            m_q = re.match(r'\s*>\s*[«»\s]*\*?(.+?)\*?\s*»?\s*$', line)
            if m_t:
                if current_title:
                    blocks.append((current_title, current_quote))
                current_title = f"{m_t.group(1)} × {m_t.group(2)} ({m_t.group(3)} car.)"
                current_quote = None
            elif m_q and current_title:
                current_quote = m_q.group(1).strip()
        if current_title:
            blocks.append((current_title, current_quote))

        lcs_inner = "".join(f"""
              <div class="lcs-pair">
                <div class="lcs-pair-title">{t}</div>
                {"<blockquote>« " + q + " »</blockquote>" if q else ""}
              </div>""" for t, q in blocks)

        lcs_html = f"""
            <div class="tab-section">
              <div class="section-number">05 — Séquences récurrentes</div>
              <h3 class="sec-h3">LCS — Formules partagées · Chrétien de Troyes</h3>
              <div class="lcs-block">{lcs_inner}</div>
            </div>"""

    return f"""
        <!-- KNN -->
        <div class="tab-section">
          <div class="section-number">01 — Classification</div>
          <h3 class="sec-h3">KNN — Voisinage le plus proche (k=1)</h3>
          <div class="accuracy-badge">
            <span class="accuracy-value">{acc_val}</span>
            <span class="accuracy-label">Précision · {metric}</span>
          </div>
          <div class="pairs-grid">
            <div class="pairs-block">
              <div class="pairs-label">▲ 5 paires les plus proches</div>
              {_pair_rows_html(top_pairs, 'high')}
            </div>
            <div class="pairs-block">
              <div class="pairs-label">▽ 5 paires les plus éloignées</div>
              {_pair_rows_html(bot_pairs, 'low')}
            </div>
          </div>
        </div>

        <!-- Cohésion -->
        <div class="tab-section">
          <div class="section-number">02 — Cohésion interne</div>
          <h3 class="sec-h3">Similarité moyenne par auteur</h3>
          <div class="cohesion-grid">
            {cohesion_cards}
          </div>
        </div>

        <!-- Signatures -->
        <div class="tab-section">
          <div class="section-number">03 — Signatures lexicales</div>
          <h3 class="sec-h3">N-grammes caractéristiques par auteur</h3>
          <div class="signatures-grid">
            {sig_cards}
          </div>
        </div>

        {viz_html}
        {lcs_html}
    """


# CSS supplémentaire pour les onglets — à fusionner dans HTML_CSS
TABS_CSS = """
  /* ── Onglets ── */
  .tabs-bar {
    display: flex;
    gap: 0;
    padding: 0 64px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 10;
  }
  .tab-btn {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 16px 24px;
    cursor: pointer;
    transition: all .2s;
    margin-bottom: -1px;
  }
  .tab-btn:hover { color: var(--text); }
  .tab-btn.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }
  .tab-panel { display: none; padding: 0 64px 80px; }
  .tab-panel.active { display: block; }

  /* ── Sections dans onglet ── */
  .tab-section {
    padding: 48px 0 36px;
    border-bottom: 1px solid var(--border);
  }
  .tab-section:last-child { border-bottom: none; }
  .sec-h3 {
    font-size: 1.4rem;
    font-weight: 600;
    color: #f0e8d8;
    margin-bottom: 24px;
    font-family: 'EB Garamond', Georgia, serif;
    letter-spacing: -.01em;
    text-transform: none;
  }
  .pairs-label {
    font-family: 'Fira Code', monospace;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
  }
"""

# JS minimal pour la gestion des onglets
TABS_JS = """
<script>
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(target).classList.add('active');
    });
  });
</script>
"""


def generate_combined_report_html(resultats, biblio, output_path,
                                   lcs_content=None, titre="Analyse par Auteurs"):
    """
    Génère un rapport HTML unique avec onglets pour plusieurs expériences.

    Entrées :
        resultats (dict)   : {suffixe: {'matrix', 'txt_names', 'lexique', 'img_path', 'metric'}}
                             Les clés sont les noms d'expériences (ex: 'caracteres3', 'mots2')
                             L'ordre d'insertion détermine l'ordre des onglets.
        biblio (dict)      : métadonnées {nom : auteur}
        output_path (str)  : chemin de sortie (.html)
        lcs_content (str)  : contenu LCS à insérer dans l'onglet 'caracteres3' (optionnel)
        titre (str)        : titre affiché dans le header

    Sortie :
        fichier .html dans output_path

    Exemple d'appel dans main2.py :
        generate_combined_report_html(
            resultats=resultats_auteurs,
            biblio=dico_author,
            output_path=".../rapport-auteurs.html",
            lcs_content=lcs_content
        )
    """
    import datetime

    dd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Libellés lisibles pour les onglets
    tab_labels = {
        'caracteres3': 'N-grammes caractères (n=3)',
        'mots2':       'N-grammes mots (n=2)',
    }

    # ── Construction des onglets ──
    tab_buttons = ""
    tab_panels  = ""

    for idx, (suffixe, data) in enumerate(resultats.items()):
        is_first   = idx == 0
        active_cls = "active" if is_first else ""
        label      = tab_labels.get(suffixe, suffixe)

        # LCS uniquement sur caracteres3
        lcs_pour_tab = lcs_content if suffixe == 'caracteres3' else None

        contenu = _build_tab_content(suffixe, data, biblio, lcs_content=lcs_pour_tab)

        tab_buttons += f'<button class="tab-btn {active_cls}" data-tab="tab-{suffixe}">{label}</button>\n'
        tab_panels  += f'<div class="tab-panel {active_cls}" id="tab-{suffixe}">{contenu}</div>\n'

    # ── CSS fusionné ──
    css_complet = HTML_CSS.replace("</style>", TABS_CSS + "\n</style>")

    # ── HTML final ──
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titre}</title>
  {css_complet}
</head>
<body>

<header>
  <div class="header-label">Analyse Stylométrique · Ancien Français</div>
  <h1>{titre}</h1>
  <div class="meta">
    <div class="meta-item">Généré le &nbsp;<span>{dd}</span></div>
    <div class="meta-item">Textes &nbsp;<span>{len(next(iter(resultats.values()))['txt_names'])}</span></div>
    <div class="meta-item">Auteurs &nbsp;<span>{len(set(biblio.values()))}</span></div>
    <div class="meta-item">Expériences &nbsp;<span>{len(resultats)}</span></div>
  </div>
</header>

<div class="tabs-bar">
  {tab_buttons}
</div>

{tab_panels}

<div class="citation" style="padding: 20px 64px 0; font-family:'Fira Code',monospace; font-size:11px; color:var(--muted); border-top:1px solid var(--border);">
  Source : (2018). <em>Open Medieval French</em>.
  <a href="https://github.com/OpenMedFr/texts" target="_blank" style="color:var(--accent2)">https://github.com/OpenMedFr/texts</a>
</div>

{TABS_JS}
</body>
</html>"""

    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not output_path.endswith('.html'):
        output_path = output_path.replace('.md', '.html').replace('.txt', '.html')

    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rapport combiné généré : {output_path}")
    return output_path
