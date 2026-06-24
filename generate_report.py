"""Génère le rapport Word en ligne de commande (Partie 2, indépendante).

Usage :
    python generate_report.py [book_id] ["Nom de l'auteur du rapport"]

Exemple :
    python generate_report.py 11 "Jean Dupont"
"""

import sys

from src import image_processor, word_report
from src.book_processor import analyze_book


def main() -> None:
    book_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    author = sys.argv[2] if len(sys.argv) > 2 else "ELIDRISSI Hamza et GUY Michel"

    print(f"Analyse du livre Gutenberg #{book_id}…")
    book = analyze_book(book_id)
    print(f"  Titre   : {book.title}")
    print(f"  Auteur  : {book.author}")
    print(f"  Paragraphes (ch.1) : {book.n_paragraphs}")

    print("Préparation de la photo n° 1 (image #1 + logo)…")
    photo = image_processor.build_photo_one()

    print("Génération du document Word…")
    path = word_report.generate_report(book, photo, report_author=author)
    print(f"Rapport généré : {path}")


if __name__ == "__main__":
    main()
