"""Traitement d'un livre Project Gutenberg (Partie 2).

Étapes (énoncé) :
    1. Télécharger la version texte d'un livre.
    2. Extraire le titre, l'auteur et le premier chapitre.
    3. Compter les mots de chaque paragraphe du premier chapitre,
       arrondir le compte à la dizaine (par le bas, cf. exemple de l'énoncé :
       123, 127, 129 -> 120), trier puis compter les paragraphes ayant le
       même nombre de mots -> distribution.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass, field

import requests

from . import net  # noqa: F401 - active le magasin de certificats système

REQUEST_TIMEOUT = 30


class BookProcessingError(Exception):
    """Erreur lors du téléchargement ou de l'analyse du livre."""


@dataclass
class BookData:
    """Résultat structuré de l'analyse d'un livre."""

    title: str
    author: str
    source_url: str
    paragraphs: list[str] = field(default_factory=list)
    word_counts: list[int] = field(default_factory=list)        # bruts, triés
    rounded_counts: list[int] = field(default_factory=list)     # arrondis, triés
    distribution: "OrderedDict[int, int]" = field(default_factory=OrderedDict)

    # Statistiques pratiques pour le rapport
    @property
    def n_paragraphs(self) -> int:
        return len(self.paragraphs)

    @property
    def total_words(self) -> int:
        return sum(self.word_counts)

    @property
    def min_words(self) -> int:
        return min(self.word_counts) if self.word_counts else 0

    @property
    def max_words(self) -> int:
        return max(self.word_counts) if self.word_counts else 0

    @property
    def avg_words(self) -> float:
        return self.total_words / self.n_paragraphs if self.n_paragraphs else 0.0


# ---------------------------------------------------------------------- #
# Téléchargement
# ---------------------------------------------------------------------- #
def download_book(book_id: int = 11) -> tuple[str, str]:
    """Télécharge le texte brut d'un livre Gutenberg. Renvoie (texte, url).

    Plusieurs URL sont essayées car Gutenberg change parfois le chemin.
    """
    urls = [
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
    ]
    last_err: Exception | None = None
    for url in urls:
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text, url
        except requests.RequestException as exc:
            last_err = exc
            continue
    raise BookProcessingError(
        f"Impossible de télécharger le livre {book_id} : {last_err}"
    )


# ---------------------------------------------------------------------- #
# Extraction
# ---------------------------------------------------------------------- #
def extract_metadata(text: str) -> tuple[str, str]:
    """Extrait le titre et l'auteur depuis l'en-tête Gutenberg."""
    title = _search(r"^\s*Title:\s*(.+)$", text) or "Titre inconnu"
    author = _search(r"^\s*Author:\s*(.+)$", text) or "Auteur inconnu"
    return title.strip(), author.strip()


def _search(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1).strip() if m else None


def strip_gutenberg_boilerplate(text: str) -> str:
    """Retire les en-têtes/pieds de page légaux de Project Gutenberg."""
    start = re.search(r"\*\*\* ?START OF TH(?:E|IS) PROJECT GUTENBERG.*?\*\*\*",
                      text, re.IGNORECASE)
    end = re.search(r"\*\*\* ?END OF TH(?:E|IS) PROJECT GUTENBERG.*?\*\*\*",
                    text, re.IGNORECASE)
    s = start.end() if start else 0
    e = end.start() if end else len(text)
    return text[s:e]


def extract_first_chapter(text: str) -> str:
    """Renvoie le texte du premier chapitre.

    Difficulté : beaucoup de livres Gutenberg commencent par une table des
    matières qui contient aussi des lignes « CHAPTER I … ». Pour ne pas
    confondre la TdM avec les vrais chapitres :

    1. On tente d'abord un motif *strict* : un en-tête de chapitre seul sur sa
       ligne (« CHAPTER I. »), ce qui exclut les entrées de TdM où le titre
       suit sur la même ligne.
    2. À défaut, on retombe sur un motif souple et on choisit la première
       paire d'en-têtes séparée par un contenu suffisamment long (≥ 80
       caractères), ce qui écarte les entrées de TdM rapprochées.
    """
    body = strip_gutenberg_boilerplate(text)
    # Normalisation des fins de ligne pour fiabiliser les ancres ^ et $.
    body = body.replace("\r\n", "\n").replace("\r", "\n")

    strict_re = re.compile(
        r"^[ \t]*(?:CHAPTER|Chapter)\s+(?:[IVXLCDM]+|\d+)\.?[ \t]*$",
        re.MULTILINE,
    )
    matches = list(strict_re.finditer(body))
    if len(matches) < 2:
        loose_re = re.compile(
            r"^[ \t]*(?:CHAPTER|Chapter)\s+(?:[IVXLCDM]+|\d+)\b.*$",
            re.MULTILINE,
        )
        matches = list(loose_re.finditer(body))

    # Première paire d'en-têtes encadrant un vrai contenu.
    for i in range(len(matches) - 1):
        segment = body[matches[i].end():matches[i + 1].start()].strip()
        if len(segment) >= 80:
            return segment

    if matches:
        return body[matches[-1].end():].strip()
    # Aucun en-tête reconnu : on prend le début du corps.
    return body[:4000].strip()


# ---------------------------------------------------------------------- #
# Comptage / distribution
# ---------------------------------------------------------------------- #
def split_paragraphs(chapter_text: str) -> list[str]:
    """Découpe un chapitre en paragraphes (séparés par des lignes vides)."""
    raw = re.split(r"\n\s*\n", chapter_text)
    paragraphs = []
    for block in raw:
        # On recolle les retours à la ligne internes et on nettoie.
        clean = " ".join(block.split())
        if len(clean) > 1:
            paragraphs.append(clean)
    return paragraphs


def count_words(paragraph: str) -> int:
    """Compte les mots d'un paragraphe."""
    return len(re.findall(r"\b\w+\b", paragraph))


def round_down_to_ten(n: int) -> int:
    """Arrondit à la dizaine par le bas (123, 127, 129 -> 120)."""
    return (n // 10) * 10


def build_distribution(rounded_sorted: list[int]) -> "OrderedDict[int, int]":
    """Compte le nombre de paragraphes par longueur arrondie (trié croissant)."""
    dist: "OrderedDict[int, int]" = OrderedDict()
    for value in rounded_sorted:
        dist[value] = dist.get(value, 0) + 1
    return dist


# ---------------------------------------------------------------------- #
# Orchestration
# ---------------------------------------------------------------------- #
def analyze_book(book_id: int = 11) -> BookData:
    """Pipeline complet : télécharge et analyse un livre. Renvoie un BookData."""
    text, url = download_book(book_id)
    title, author = extract_metadata(text)
    chapter = extract_first_chapter(text)

    paragraphs = split_paragraphs(chapter)
    if not paragraphs:
        raise BookProcessingError("Premier chapitre introuvable ou vide.")

    word_counts = [count_words(p) for p in paragraphs]
    rounded = sorted(round_down_to_ten(c) for c in word_counts)
    distribution = build_distribution(rounded)

    return BookData(
        title=title,
        author=author,
        source_url=url,
        paragraphs=paragraphs,
        word_counts=sorted(word_counts),
        rounded_counts=rounded,
        distribution=distribution,
    )
