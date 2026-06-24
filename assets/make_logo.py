"""Génère un logo noir et blanc (image #2) lu ensuite depuis le disque.

Exécuter : ``python assets/make_logo.py``

Le logo est en noir et blanc (mode « L »), conformément à l'énoncé. Motif :
un livre ouvert (en lien avec la Partie 2 « rapport à partir d'un livre »)
dans un médaillon circulaire, surmonté des initiales du projet.
"""

import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

BLACK = 0
WHITE = 255


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Charge une police grasse si disponible, sinon la police par défaut."""
    for name in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _centered_text(draw, cx, y, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2 - bbox[0], y), text, fill=BLACK, font=font)


def make_logo(size: int = 320) -> str:
    img = Image.new("L", (size, size), color=WHITE)
    draw = ImageDraw.Draw(img)
    cx = size / 2

    # --- Médaillon : deux cercles concentriques ---
    draw.ellipse([10, 10, size - 10, size - 10], outline=BLACK, width=8)
    draw.ellipse([26, 26, size - 26, size - 26], outline=BLACK, width=3)

    # --- Livre ouvert au centre ---
    top = size * 0.40       # haut des pages
    bottom = size * 0.66    # bas des pages
    spine_top = size * 0.36
    half = size * 0.26      # demi-largeur du livre
    # Page gauche et page droite (trapèzes se rejoignant à la reliure centrale)
    draw.polygon(
        [(cx - half, top), (cx, spine_top), (cx, bottom), (cx - half, bottom + 6)],
        outline=BLACK, width=5,
    )
    draw.polygon(
        [(cx + half, top), (cx, spine_top), (cx, bottom), (cx + half, bottom + 6)],
        outline=BLACK, width=5,
    )
    # Lignes de texte stylisées sur chaque page
    for i in range(3):
        y = top + 14 + i * 13
        draw.line([(cx - half + 16, y + 4), (cx - 10, y - 2)], fill=BLACK, width=2)
        draw.line([(cx + 10, y - 2), (cx + half - 16, y + 4)], fill=BLACK, width=2)

    # --- Initiales du projet au-dessus du livre ---
    _centered_text(draw, cx, size * 0.16, "PA", _load_font(int(size * 0.16)))

    # --- Nom du cours en bas, dans le médaillon ---
    _centered_text(draw, cx, size * 0.72, "PYTHON", _load_font(int(size * 0.075)))
    _centered_text(draw, cx, size * 0.80, "AVANCE", _load_font(int(size * 0.075)))

    img.save(OUT)
    return OUT


if __name__ == "__main__":
    path = make_logo()
    print(f"Logo généré : {path}")
