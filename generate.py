"""
Générateur de site statique Made By Clo depuis export WordPress.
"""
import re
import os
import json
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE, "images")
ARTICLES_DIR = os.path.join(BASE, "articles")
os.makedirs(ARTICLES_DIR, exist_ok=True)

# ─── Helpers ───────────────────────────────────────────────────────────────

def local_image(url):
    """Mappe une URL WordPress vers le chemin local de l'image."""
    if "wp-content/uploads" not in url:
        return url
    filename = url.split("/")[-1]
    # Strip size suffix: IMG_foo-768x1024.jpg → IMG_foo.jpg
    base = re.sub(r"-\d+x\d+(\.[a-zA-Z]+)$", r"\1", filename)
    # Try: exact name, then -scaled variant
    candidates = [base, re.sub(r"(\.[a-zA-Z]+)$", r"-scaled\1", base)]
    for c in candidates:
        if os.path.exists(os.path.join(IMAGES_DIR, c)):
            return f"../images/{c}"
    # Fallback: try without extension manipulation
    if os.path.exists(os.path.join(IMAGES_DIR, filename)):
        return f"../images/{filename}"
    return f"../images/{base}"  # best guess even if missing

def extract_images(body):
    """Extrait toutes les URLs d'images du body WordPress."""
    imgs = []
    # Standard <img src="..."> tags
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', body):
        u = m.group(1)
        if "wp-content/uploads" in u:
            imgs.append(u)
    # Kadence advanced gallery JSON
    for m in re.finditer(r'"imagesDynamic":\s*(\[.*?\])', body, re.DOTALL):
        try:
            data = json.loads(m.group(1))
            for img in data:
                if "url" in img and "wp-content/uploads" in img["url"]:
                    imgs.append(img["url"])
        except Exception:
            pass
    # Deduplicate preserving order
    seen = set()
    result = []
    for u in imgs:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result

def extract_text(body):
    """Extrait les paragraphes de texte significatifs du body."""
    # Remove WP block comments
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    # Remove Kadence/WP structural divs but keep content
    body = re.sub(r"<div[^>]*class=\"[^\"]*(?:kadence|wp-block-kadence|kb-buttons|wp-block-buttons)[^\"]*\"[^>]*>", "", body)
    body = re.sub(r"</div>", "", body)
    # Remove figure/img tags (already shown in gallery)
    body = re.sub(r"<figure[^>]*>.*?</figure>", "", body, flags=re.DOTALL)
    # Remove heading blocks that are just "Cousu main, transformation, création"
    body = re.sub(r"<h[23][^>]*>[^<]*(?:Cousu main|transformation|cr[eé]ation)[^<]*</h[23]>", "", body, flags=re.IGNORECASE)
    # Fix internal links: replace madebyclo.fr article links with local
    body = re.sub(r'href="https://madebyclo\.fr/me-contacter/?"', 'href="../contact.html"', body)
    body = re.sub(r'href="https://madebyclo\.fr/([^"]+)"', r'href="../articles/\1.html"', body)
    # Remove empty anchors
    body = re.sub(r"<a[^>]*>\s*</a>", "", body)
    # Remove WP button wrappers but keep the <a> inside
    body = re.sub(r'<div class="wp-block-button"><a class="wp-block-button__link[^"]*"', '<a class="btn"', body)
    body = re.sub(r'</a></div>', "</a>", body)
    # Extract non-empty <p> tags
    paragraphs = []
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.DOTALL):
        text = m.group(1).strip()
        # Remove style= attrs from inline tags
        text = re.sub(r'\s+style="[^"]*"', "", text)
        # Remove class= attrs
        text = re.sub(r'\s+class="[^"]*"', "", text)
        # Remove id= attrs
        text = re.sub(r'\s+id="[^"]*"', "", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        # Skip truly empty or just whitespace/nbsp
        if text and text not in ("&nbsp;", " ", ""):
            paragraphs.append(f"<p>{text}</p>")
    return paragraphs

NAV = """
<nav>
  <div class="nav-inner">
    <a class="logo" href="../index.html">Made By Clo</a>
    <button class="menu-toggle" aria-label="Menu">&#9776;</button>
    <ul class="nav-links">
      <li><a href="../index.html">Accueil</a></li>
      <li><a href="../creations.html">Mes créations</a></li>
      <li><a href="../actualites.html">Actualités</a></li>
      <li><a href="../contact.html">Me contacter</a></li>
    </ul>
  </div>
</nav>
"""

NAV_ROOT = """
<nav>
  <div class="nav-inner">
    <a class="logo" href="index.html">Made By Clo</a>
    <button class="menu-toggle" aria-label="Menu">&#9776;</button>
    <ul class="nav-links">
      <li><a href="index.html">Accueil</a></li>
      <li><a href="creations.html">Mes créations</a></li>
      <li><a href="actualites.html">Actualités</a></li>
      <li><a href="contact.html">Me contacter</a></li>
    </ul>
  </div>
</nav>
"""

FOOTER = """
<footer>
  <p>© 2026 Made By Clo &mdash; Couture sur mesure aux Montils (Loir-et-Cher)</p>
  <p><a href="contact.html">Me contacter</a></p>
</footer>
"""

FOOTER_SUB = """
<footer>
  <p>© 2026 Made By Clo &mdash; Couture sur mesure aux Montils (Loir-et-Cher)</p>
  <p><a href="../contact.html">Me contacter</a></p>
</footer>
"""

def html_page(title, body, nav, footer, extra_class=""):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} – Made By Clo</title>
  <link rel="stylesheet" href="{'../style.css' if nav == NAV else 'style.css'}">
</head>
<body class="{extra_class}">
{nav}
<main>
{body}
</main>
{footer}
<script src="{'../script.js' if nav == NAV else 'script.js'}"></script>
</body>
</html>"""

# ─── Parse WordPress XML ────────────────────────────────────────────────────

tree = ET.parse(os.path.join(BASE, "madebyclo.WordPress.2026-05-21.xml"))
root = tree.getroot()

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}

articles = []  # list of dicts

for item in root.iter("item"):
    post_type = item.find("wp:post_type", NS)
    status = item.find("wp:status", NS)
    if post_type is None or status is None:
        continue
    if post_type.text != "post" or status.text != "publish":
        continue

    title_el = item.find("title")
    slug_el = item.find("wp:post_name", NS)
    body_el = item.find("content:encoded", NS)

    title = title_el.text if title_el is not None and title_el.text else ""
    slug = slug_el.text if slug_el is not None and slug_el.text else ""
    body = body_el.text if body_el is not None and body_el.text else ""

    # Skip empty / placeholder articles
    if not body.strip() or title in ("Hello world!",):
        continue

    # Categories
    cats = []
    for cat in item.findall("category"):
        domain = cat.get("domain", "")
        if domain == "category" and cat.text:
            cats.append(cat.text)

    images = extract_images(body)
    paragraphs = extract_text(body)

    articles.append({
        "title": title,
        "slug": slug,
        "cats": cats,
        "images": images,
        "paragraphs": paragraphs,
    })

print(f"Articles trouvés: {len(articles)}")

# ─── Generate article pages ─────────────────────────────────────────────────

for art in articles:
    imgs_html = ""
    local_imgs = [local_image(u) for u in art["images"]]

    if len(local_imgs) == 1:
        imgs_html = f'<div class="article-gallery single"><img src="{local_imgs[0]}" alt="{art["title"]}"></div>'
    elif len(local_imgs) > 1:
        imgs_inner = "\n".join(f'<img src="{u}" alt="{art["title"]}">' for u in local_imgs)
        imgs_html = f'<div class="article-gallery">\n{imgs_inner}\n</div>'

    cats_html = " ".join(f'<span class="tag">{c}</span>' for c in art["cats"])
    text_html = "\n".join(art["paragraphs"])

    body = f"""
<article class="article-detail">
  <div class="article-header">
    <h1>{art["title"]}</h1>
    <div class="article-cats">{cats_html}</div>
  </div>
  {imgs_html}
  <div class="article-text">
    {text_html}
  </div>
  <div class="article-cta">
    <a href="../contact.html" class="btn">Me contacter pour ce projet</a>
  </div>
  <p class="back-link"><a href="../creations.html">&larr; Retour aux créations</a></p>
</article>
"""
    html = html_page(art["title"], body, NAV, FOOTER_SUB)
    out_path = os.path.join(ARTICLES_DIR, f"{art['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Article: {art['slug']}.html")

# ─── Generate creations.html (galerie) ──────────────────────────────────────

# Build list of unique categories
all_cats = []
seen_cats = set()
for art in articles:
    for c in art["cats"]:
        if c not in seen_cats:
            seen_cats.add(c)
            all_cats.append(c)

filter_buttons = '<button class="filter-btn active" data-filter="all">Tout</button>\n'
for c in sorted(all_cats):
    slug_c = c.lower().replace(" ", "-").replace("é", "e").replace("è", "e").replace("ê", "e").replace("â", "a").replace("à", "a").replace("î", "i").replace("û", "u").replace("ô", "o")
    filter_buttons += f'<button class="filter-btn" data-filter="{slug_c}">{c}</button>\n'

cards_html = ""
for art in articles:
    thumb = local_image(art["images"][0]).replace("../", "") if art["images"] else "images/patchwork-page-accueil.png"
    cat_slugs = " ".join(
        c.lower().replace(" ", "-").replace("é", "e").replace("è", "e").replace("ê", "e").replace("â", "a").replace("à", "a").replace("î", "i").replace("û", "u").replace("ô", "o")
        for c in art["cats"]
    )
    tags_html = " ".join(f'<span class="tag">{c}</span>' for c in art["cats"])
    cards_html += f"""
<div class="card" data-cats="{cat_slugs}">
  <a href="articles/{art['slug']}.html">
    <div class="card-img"><img src="{thumb}" alt="{art['title']}" loading="lazy"></div>
    <div class="card-body">
      <h3>{art['title']}</h3>
      <div class="card-tags">{tags_html}</div>
    </div>
  </a>
</div>"""

creations_body = f"""
<section class="page-hero">
  <h1>Mes créations</h1>
  <p>Retouches, créations sur mesure, upcycling — chaque pièce est unique.</p>
</section>
<section class="gallery-section">
  <div class="filter-bar">
    {filter_buttons}
  </div>
  <div class="cards-grid" id="gallery">
    {cards_html}
  </div>
</section>
<script>
  const btns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.card');
  btns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;
      cards.forEach(c => {{
        c.style.display = (f === 'all' || c.dataset.cats.includes(f)) ? '' : 'none';
      }});
    }});
  }});
</script>
"""
with open(os.path.join(BASE, "creations.html"), "w", encoding="utf-8") as f:
    f.write(html_page("Mes créations", creations_body, NAV_ROOT, FOOTER, "page-creations"))
print("creations.html généré")

# ─── Generate actualites.html ────────────────────────────────────────────────

news_cards = ""
for art in articles:
    thumb = local_image(art["images"][0]).replace("../", "") if art["images"] else "images/patchwork-page-accueil.png"
    tags_html = " ".join(f'<span class="tag">{c}</span>' for c in art["cats"])
    excerpt = art["paragraphs"][0] if art["paragraphs"] else ""
    news_cards += f"""
<div class="news-card">
  <a href="articles/{art['slug']}.html">
    <div class="news-img"><img src="{thumb}" alt="{art['title']}" loading="lazy"></div>
    <div class="news-body">
      <h3>{art['title']}</h3>
      <div class="card-tags">{tags_html}</div>
      {excerpt}
    </div>
  </a>
</div>"""

actualites_body = f"""
<section class="page-hero">
  <h1>Actualités</h1>
  <p>Toutes les nouvelles créations de Made By Clo.</p>
</section>
<section class="news-section">
  <div class="news-grid">
    {news_cards}
  </div>
</section>
"""
with open(os.path.join(BASE, "actualites.html"), "w", encoding="utf-8") as f:
    f.write(html_page("Actualités", actualites_body, NAV_ROOT, FOOTER, "page-actualites"))
print("actualites.html généré")

# ─── Generate contact.html ───────────────────────────────────────────────────

contact_body = """
<section class="page-hero">
  <h1>Me contacter</h1>
  <p>Je réponds sous 48 à 72 heures. Parlons de votre projet !</p>
</section>
<section class="contact-section">
  <div class="contact-grid">
    <div class="contact-info">
      <h2>Comment ça marche ?</h2>
      <ol>
        <li>Envoyez-moi votre message via le formulaire</li>
        <li>Je vous réponds dans un délai de 48 à 72 heures</li>
        <li>J'étudie votre projet couture</li>
        <li>Je crée, retouche ou répare dans un délai déterminé ensemble</li>
        <li>Je vous contacte pour récupérer votre commande</li>
      </ol>
      <p><strong>Retrait possible aux Montils</strong> (à 15 minutes de Blois) et dans un rayon de 20 km.</p>
    </div>
    <div class="contact-form-wrap">
      <form action="https://formspree.io/f/xpwrjkgz" method="POST" class="contact-form">
        <label>
          Votre nom
          <input type="text" name="name" required placeholder="Prénom Nom">
        </label>
        <label>
          Votre email
          <input type="email" name="email" required placeholder="votre@email.fr">
        </label>
        <label>
          Votre message
          <textarea name="message" rows="6" required placeholder="Décrivez votre projet, retouche ou demande…"></textarea>
        </label>
        <button type="submit" class="btn">Envoyer mon message</button>
      </form>
    </div>
  </div>
</section>
"""
with open(os.path.join(BASE, "contact.html"), "w", encoding="utf-8") as f:
    f.write(html_page("Me contacter", contact_body, NAV_ROOT, FOOTER, "page-contact"))
print("contact.html généré")

# ─── Generate index.html ─────────────────────────────────────────────────────

# Pick a few featured articles for the home page preview
featured = articles[:6]
featured_html = ""
for art in featured:
    thumb = local_image(art["images"][0]).replace("../", "") if art["images"] else "images/patchwork-page-accueil.png"
    featured_html += f"""
<div class="card">
  <a href="articles/{art['slug']}.html">
    <div class="card-img"><img src="{thumb}" alt="{art['title']}" loading="lazy"></div>
    <div class="card-body"><h3>{art['title']}</h3></div>
  </a>
</div>"""

index_body = """
<section class="hero">
  <div class="hero-inner">
    <img src="images/patchwork-page-accueil.png" alt="Made By Clo – bannière" class="hero-banner">
  </div>
</section>

<section class="intro">
  <div class="intro-grid">
    <div class="intro-text">
      <h1>Qui suis-je ?</h1>
      <p>Bonjour et bienvenue sur mon blog ! Je m'appelle Clo, couturière passionnée. Je pique, je couds, je retouche… Je crée des accessoires, des vêtements pour vous, Mesdames, pour les enfants, pour les poupées. Je réalise aussi des gâteaux de couches pour célébrer les naissances de vos enfants ou petits-enfants.</p>
      <p>Entre les fleurs du jardin, le potager et les fils de couture, je trouve mon bonheur.</p>
      <p>Ici vous trouverez mes créations, mes conseils et tout mon univers couture. Que ce soit pour une retouche, une réparation ou une création sur mesure, je suis là pour donner vie à vos projets.</p>
      <a href="creations.html" class="btn">Découvrir mes créations</a>
    </div>
    <div class="intro-photo">
      <img src="images/clo-fleur-1.jpg" alt="Clo dans son jardin">
    </div>
  </div>
</section>

<section class="how-it-works">
  <h2>Me rencontrer</h2>
  <div class="how-grid">
    <div class="how-map">
      <img src="images/point-map.png" alt="Carte – Les Montils, près de Blois">
    </div>
    <div class="how-steps">
      <ol>
        <li><a href="contact.html">Contactez-moi à l'aide du formulaire</a></li>
        <li>Je vous réponds dans un délai de 48 à 72 heures</li>
        <li>J'étudie vos projets couture</li>
        <li>Je crée, je retouche, je répare dans un délai déterminé ensemble</li>
        <li>Je vous contacte pour récupérer votre commande</li>
        <li>Retrait possible aux Montils (à 15 minutes de Blois) et dans un rayon de 20 km.</li>
      </ol>
    </div>
  </div>
</section>

<section class="services">
  <h2>Mes services</h2>
  <div class="services-grid">
    <div class="service-card">
      <span class="service-icon">✂️</span>
      <h3>Retouches</h3>
      <p>Votre vêtement préféré ne vous va plus tout à fait ? Je réalise toutes vos retouches sur mesure pour que chaque pièce épouse parfaitement votre silhouette.</p>
    </div>
    <div class="service-card">
      <span class="service-icon">🧵</span>
      <h3>Réparation</h3>
      <p>Un accroc, une fermeture cassée ou une couture défaite ? Je redonne vie à vos vêtements abîmés pour leur offrir une seconde jeunesse.</p>
    </div>
    <div class="service-card">
      <span class="service-icon">🎨</span>
      <h3>Création</h3>
      <p>Vous avez une idée en tête ? Ensemble nous imaginons et confectionnons une pièce unique qui vous ressemble, du choix du tissu jusqu'à la dernière finition.</p>
    </div>
    <div class="service-card">
      <span class="service-icon">♻️</span>
      <h3>Upcycling</h3>
      <p>Transformez vos vêtements oubliés au fond du placard en pièces tendances et originales. Rien ne se jette, tout se réinvente avec un peu de créativité et de fil !</p>
    </div>
  </div>
  <div class="services-cta">
    <a href="contact.html" class="btn">Me contacter</a>
  </div>
</section>

<section class="featured-creations">
  <h2>Dernières créations</h2>
  <div class="cards-grid">
""" + featured_html + """
  </div>
  <div class="services-cta">
    <a href="creations.html" class="btn btn-outline">Voir toutes mes créations</a>
  </div>
</section>
"""

with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_page("Accueil", index_body, NAV_ROOT, FOOTER, "page-home"))
print("index.html généré")
print("\nTerminé !")
