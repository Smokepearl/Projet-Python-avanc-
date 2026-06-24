"""Gestion des préférences de l'application (couleurs, polices...).

Les préférences sont sérialisées dans un petit fichier JSON à côté de
l'application, ce qui permet de les conserver entre deux exécutions. Le
module est volontairement tolérant aux erreurs : si le fichier est absent
ou corrompu, on retombe sur les valeurs par défaut au lieu de planter.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

# Répertoire racine du projet (le dossier parent de src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "settings.json")


@dataclass
class AppConfig:
    """Préférences modifiables depuis le menu « Options » de l'application."""

    bg_color: str = "#f0f4f8"
    fg_color: str = "#1b2a41"
    accent_color: str = "#2d6cdf"
    font_family: str = "Segoe UI"
    font_size: int = 11
    # Source de données et livre par défaut (modifiables au besoin)
    api_limit: int = 30
    book_id: int = 11  # Alice's Adventures in Wonderland (Project Gutenberg)

    # Champs utilitaires non sérialisés
    extra: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------ #
    # Persistance
    # ------------------------------------------------------------------ #
    @classmethod
    def load(cls, path: str = CONFIG_PATH) -> "AppConfig":
        """Charge les préférences depuis le disque, ou renvoie les défauts."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # On ne garde que les clés connues pour éviter les surprises.
            known = {k: data[k] for k in cls.__annotations__ if k in data}
            return cls(**known)
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return cls()

    def save(self, path: str = CONFIG_PATH) -> bool:
        """Écrit les préférences sur le disque. Renvoie True si succès."""
        try:
            data = asdict(self)
            data.pop("extra", None)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    # ------------------------------------------------------------------ #
    # Aides pour Tkinter
    # ------------------------------------------------------------------ #
    @property
    def font(self) -> tuple:
        """Tuple de police prêt à l'emploi pour les widgets Tkinter."""
        return (self.font_family, self.font_size)

    @property
    def title_font(self) -> tuple:
        return (self.font_family, self.font_size + 6, "bold")
