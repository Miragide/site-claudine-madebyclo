# Made By Clo - Static Site Project

This project is a static website for **Made By Clo**, a sewing and creation business based in Les Montils (near Blois, France). The site is generated from a WordPress XML export to ensure a fast, lightweight, and easily hostable static presence.

## Publication & Workflow Protocol

You act as a **Publication Assistant** for this site. To ensure consistent updates and site integrity, follow this mandatory protocol for every modification:

1.  **Research & Plan:** Analyze the request and identify the necessary changes (HTML, CSS, or JS).
2.  **Image Optimization (Mandatory):** If new images are added or existing ones are modified, you MUST optimize them using the local script before any other action:
    ```powershell
    python optimage.py
    ```
    *This script resizes images to a maximum width of 2000px and applies compression.*
3.  **Execute Changes:** Apply the requested modifications to the codebase.
4.  **Verification:** Test the changes locally (if possible) and ensure no regressions.
5.  **Deployment (Git Push):** Since the site is hosted on **Cloudflare Pages** and linked to **GitHub**, every modification must be committed and pushed to the repository to trigger the live update.
    *   `git add .`
    *   `git commit -m "Description of changes"`
    *   `git push`

## Project Overview

*   **Type:** Static Site Generator / Portfolio
*   **Main Technologies:** 
    *   **Generation:** Python (using `xml.etree.ElementTree` for parsing)
    *   **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript
    *   **Integrations:** Instagram embed, Formspree (for contact form)
    *   **Hosting:** Cloudflare Pages (via GitHub)
*   **Architecture:** The site consists of a few root pages (`index.html`, `creations.html`, `actualites.html`, `contact.html`, `mentions-legales.html`) and a collection of individual article pages in the `articles/` directory.

## Project Structure

*   `generate.py`: The core script that parses the WordPress XML export and generates all HTML files.
*   `articles/`: Directory containing individual creation pages generated from the XML.
*   `images/`: Directory containing all image assets used by the site.
*   `style.css`: Global styles for the entire site.
*   `script.js`: Small utility scripts (e.g., mobile menu toggle).
*   `index.html`: The homepage, highlighting services and featured creations.
*   `creations.html`: A filterable gallery of all sewing projects.
*   `actualites.html`: A list of the latest posts/creations.
*   `contact.html`: Contact page with a Formspree-powered form.
*   `madebyclo.WordPress.YYYY-MM-DD.xml`: (Not listed but implied) The source WordPress export file used by `generate.py`.

## Building and Running

### Prerequisites
*   Python 3.x installed.
*   A WordPress XML export file named according to the pattern in `generate.py` (e.g., `madebyclo.WordPress.2026-05-21.xml`).

### Site Generation
To (re)generate the static site, run the following command from the project root:

```powershell
python generate.py
```

This script will:
1.  Parse the WordPress XML export.
2.  Extract content, images, and metadata for each post.
3.  Clean up WordPress-specific HTML/CSS.
4.  Generate HTML files for individual articles in `articles/`.
5.  Generate the main pages (`index.html`, `creations.html`, `actualites.html`, `contact.html`).

## Development Conventions

*   **Static Assets:** All images should be placed in the `images/` directory. `generate.py` attempts to map WordPress URLs to these local files.
*   **CSS:** Styles are kept in `style.css`. Avoid adding inline styles during generation where possible.
*   **HTML Structure:** The site uses a common layout with a navigation bar and a footer, which are defined as strings within `generate.py` for reuse across generated pages.
*   **Clean-up:** `generate.py` includes logic to strip WordPress block comments and Kadence-specific structural divs to ensure clean static output.
