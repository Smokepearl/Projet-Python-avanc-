"""Génère le rapport Word complet (Parties 1 et 2) en ligne de commande.

Usage :
    python generate_report.py [book_id] ["Nom de l'auteur du rapport"]

Exemple :
    python generate_report.py 11 "Jean Dupont"

Le rapport couvre la Partie 1 (données PokeAPI + agrégation SQL + graphique)
et la Partie 2 (analyse du livre). Si la base est vide, les données de la
Partie 1 sont téléchargées automatiquement.
"""

import sys

from src import data_fetcher, image_processor, word_report
from src.book_processor import analyze_book
from src.config import AppConfig
from src.database import Database


def main() -> None:
    book_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    author = sys.argv[2] if len(sys.argv) > 2 else "ELIDRISSI Hamza et GUY Michel"
    config = AppConfig.load()

    # --- Partie 1 : on s'assure d'avoir des données en base ---
    db = Database()
    if db.is_empty():
        print("Base vide : téléchargement des données PokeAPI…")
        rows = data_fetcher.fetch_pokemon(limit=config.api_limit)
        db.insert_many(rows)
    print(f"  Données en base : {db.count()} Pokémon")

    # --- Partie 2 : analyse du livre ---
    print(f"Analyse du livre Gutenberg #{book_id}…")
    book = analyze_book(book_id)
    print(f"  Titre   : {book.title}")
    print(f"  Auteur  : {book.author}")
    print(f"  Paragraphes (ch.1) : {book.n_paragraphs}")

    print("Préparation de la photo n° 1 (image #1 + logo)…")
    photo = image_processor.build_photo_one()

    print("Génération du document Word (Parties 1 et 2)…")
    path = word_report.generate_report(book, photo, report_author=author, db=db)
    print(f"Rapport généré : {path}")


if __name__ == "__main__":
    main()
