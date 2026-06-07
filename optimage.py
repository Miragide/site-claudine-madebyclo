#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import os

def a_transparence(img):
    if img.mode == 'RGBA':
        return img.getextrema()[3][0] < 255  # au moins un pixel non opaque
    if img.mode == 'P':
        return 'transparency' in img.info
    return False

def traiter_image(chemin, quality=80):
    try:
        taille_avant = os.path.getsize(chemin) / 1024  # Ko

        img = Image.open(chemin)
        est_png = chemin.suffix.lower() == '.png'

        transparence = est_png and a_transparence(img)

        # Redimensionner si largeur > 2000px
        if img.width > 2000:
            ratio = 2000 / img.width
            nouvelle_hauteur = int(img.height * ratio)
            img = img.resize((2000, nouvelle_hauteur), Image.LANCZOS)

        if est_png and not transparence:
            # Pas de transparence réelle : convertir en JPEG
            img = img.convert('RGB')
            sortie = chemin.with_suffix('.jpg')
            img.save(sortie, 'JPEG', quality=quality, optimize=True)
            chemin.unlink()
        elif est_png:
            # Transparence détectée : garder en PNG optimisé
            sortie = chemin
            img.save(sortie, 'PNG', optimize=True)
        else:
            # Fichier JPEG : recompresser en place
            if img.mode != 'RGB':
                img = img.convert('RGB')
            sortie = chemin
            img.save(sortie, 'JPEG', quality=quality, optimize=True)

        taille_apres = os.path.getsize(sortie) / 1024  # Ko
        reduction = ((taille_avant - taille_apres) / taille_avant) * 100

        print(f"✓ {sortie.name}: {taille_avant:.0f}Ko → {taille_apres:.0f}Ko (-{reduction:.0f}%)")
    except Exception as e:
        print(f"✗ {chemin}: {e}")

# Parcourir tous les dossiers
for fichier in Path('.').rglob('*'):
    if fichier.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        traiter_image(fichier, quality=80)
