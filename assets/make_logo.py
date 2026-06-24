"""Génère un logo noir et blanc (image #2) lu ensuite depuis le disque.

Exécuter une seule fois : ``python assets/make_logo.py``
Le logo est volontairement simple et en noir et blanc, conformément à l'énoncé.
"""

import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")


def make_logo() -> str:
    size = 220
    img = Image.new("L", (size, size), color=255)  # fond blanc, niveaux de gris
    draw = ImageDraw.Draw(img)

    # Cadre + cercle noirs
    draw.rectangle([6, 6, size - 6, size - 6], outline=0, width=6)
    draw.ellipse([34, 34, size - 34, size - 34], outline=0, width=6)

    # Initiales « PA » (Python Avancé) au centre
    try:
        font = ImageFont.truetype("arialbd.ttf", 80)
    except OSError:
        font = ImageFont.load_default()
    text = "PA"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
              text, fill=0, font=font)

    img.save(OUT)
    return OUT


if __name__ == "__main__":
    path = make_logo()
    print(f"Logo généré : {path}")
