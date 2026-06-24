"""Génération de graphiques matplotlib.

Deux usages :
    * ``build_db_figure``        -> figure pour la fenêtre Tkinter (Partie 1).
    * ``build_paragraph_figure`` -> figure de distribution des paragraphes,
                                    enregistrée sur disque pour le rapport
                                    Word (Partie 2).

On utilise l'API orientée objet de matplotlib (``Figure``) plutôt que
``pyplot`` pour pouvoir intégrer proprement les figures dans Tkinter.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # backend non interactif par défaut (sûr hors GUI)
from matplotlib.figure import Figure


# Libellés français et unités pour les colonnes numériques affichables.
COLUMN_LABELS = {
    "length": ("taille", "Taille / hauteur (dm)"),
    "size": ("poids", "Poids (hg)"),
}


def build_db_figure(rows: Sequence, column: str = "length",
                    accent_color: str = "#2d6cdf") -> Figure:
    """Construit un graphique en barres des données de la base.

    :param column: colonne numérique à représenter (``"length"`` ou ``"size"``).
    ``rows`` est une liste d'objets indexables par clé (sqlite3.Row).
    """
    label, ylabel = COLUMN_LABELS.get(column, (column, column))
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    if not rows:
        ax.text(0.5, 0.5, "Base de données vide", ha="center", va="center")
        ax.set_axis_off()
        return fig

    names = [r["name"].capitalize() for r in rows]
    values = [r[column] for r in rows]

    ax.bar(range(len(names)), values, color=accent_color)
    ax.set_title(f"{label.capitalize()} des Pokémon en base")
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=75, ha="right", fontsize=7)
    fig.tight_layout()
    return fig


def build_paragraph_figure(distribution: dict[int, int]) -> Figure:
    """Graphique de la distribution des longueurs de paragraphes (Partie 2).

    :param distribution: dict {longueur_arrondie: nombre_de_paragraphes},
                         déjà trié du plus court au plus long.
    """
    fig = Figure(figsize=(7, 4.2), dpi=120)
    ax = fig.add_subplot(111)

    if not distribution:
        ax.text(0.5, 0.5, "Aucun paragraphe", ha="center", va="center")
        ax.set_axis_off()
        return fig

    lengths = list(distribution.keys())
    counts = list(distribution.values())

    ax.bar([str(x) for x in lengths], counts, color="#2d6cdf", edgecolor="#1b2a41")
    ax.set_title("Distribution des longueurs des paragraphes (chapitre 1)")
    ax.set_xlabel("Nombre de mots (arrondi à la dizaine)")
    ax.set_ylabel("Nombre de paragraphes")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig


def save_figure(fig: Figure, path: str) -> str:
    """Enregistre une figure sur disque et renvoie le chemin."""
    fig.savefig(path, bbox_inches="tight")
    return path
