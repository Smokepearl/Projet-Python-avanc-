"""Traitement d'images avec Pillow (Partie 2).

Tâches de l'énoncé :
    4. Télécharger une image #1 en rapport avec le livre (lien codé en dur,
       mais téléchargement à l'exécution).
    5. Recadrer et redimensionner l'image #1.
    6. Lire une image #2 (logo) depuis le disque, en noir et blanc,
       la faire pivoter et la coller dans l'image #1 -> « photo n° 1 ».
"""

from __future__ import annotations

import io
import os

import requests
from PIL import Image

from . import net  # noqa: F401 - active le magasin de certificats système

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# Image #1 : couverture d'Alice au pays des merveilles (en rapport avec le livre).
# Lien codé en dur, mais l'image est téléchargée pendant l'exécution.
DEFAULT_IMAGE_URL = "https://www.gutenberg.org/cache/epub/11/pg11.cover.medium.jpg"
FALLBACK_IMAGE_URL = "https://picsum.photos/600/800"

DEFAULT_LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
REQUEST_TIMEOUT = 25


class ImageProcessingError(Exception):
    """Erreur lors du téléchargement ou du traitement d'une image."""


# ---------------------------------------------------------------------- #
# Image #1 : téléchargement, recadrage, redimensionnement
# ---------------------------------------------------------------------- #
def download_image(url: str = DEFAULT_IMAGE_URL) -> Image.Image:
    """Télécharge une image depuis Internet et la renvoie en objet PIL.

    En cas d'échec sur l'URL principale, on bascule sur une image de secours
    pour que l'application ne se bloque jamais.
    """
    for candidate in (url, FALLBACK_IMAGE_URL):
        try:
            resp = requests.get(candidate, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content)).convert("RGB")
        except (requests.RequestException, OSError):
            continue
    raise ImageProcessingError(f"Impossible de télécharger une image depuis {url}.")


def crop_and_resize(
    image: Image.Image,
    crop_factor: float = 0.85,
    resize_to: tuple[int, int] = (400, 550),
) -> Image.Image:
    """Recadre l'image au centre (facteur raisonnable) puis la redimensionne."""
    w, h = image.size
    new_w, new_h = int(w * crop_factor), int(h * crop_factor)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    cropped = image.crop((left, top, left + new_w, top + new_h))
    return cropped.resize(resize_to, Image.LANCZOS)


# ---------------------------------------------------------------------- #
# Image #2 : logo lu depuis le disque, N&B, pivoté, collé
# ---------------------------------------------------------------------- #
def load_logo_bw(path: str = DEFAULT_LOGO_PATH) -> Image.Image:
    """Lit le logo depuis le disque et le convertit en noir et blanc."""
    try:
        logo = Image.open(path)
    except (FileNotFoundError, OSError) as exc:
        raise ImageProcessingError(f"Logo introuvable : {path} ({exc})") from exc
    # « L » = niveaux de gris (noir et blanc), comme demandé.
    return logo.convert("L")


def rotate_and_paste_logo(
    base: Image.Image,
    logo: Image.Image,
    angle: float = 30.0,
    logo_size: tuple[int, int] = (110, 110),
) -> Image.Image:
    """Fait pivoter le logo et le colle dans le coin de l'image de base.

    Renvoie une nouvelle image (« photo n° 1 ») sans modifier l'originale.
    """
    photo = base.copy().convert("RGBA")
    logo_small = logo.convert("RGBA").resize(logo_size, Image.LANCZOS)
    rotated = logo_small.rotate(angle, expand=True)

    # On colle en bas à droite avec une petite marge.
    margin = 12
    pos = (
        photo.width - rotated.width - margin,
        photo.height - rotated.height - margin,
    )
    # Le 3e argument (mask) gère la transparence du logo pivoté.
    photo.paste(rotated, pos, rotated)
    return photo.convert("RGB")


def build_photo_one(
    image_url: str = DEFAULT_IMAGE_URL,
    logo_path: str = DEFAULT_LOGO_PATH,
    output_path: str | None = None,
) -> str:
    """Pipeline complet image #1 + logo -> « photo n° 1 » enregistrée sur disque.

    Renvoie le chemin du fichier généré.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "photo_1.png")

    image1 = download_image(image_url)
    image1 = crop_and_resize(image1)
    logo = load_logo_bw(logo_path)
    photo = rotate_and_paste_logo(image1, logo)
    photo.save(output_path)
    return output_path
