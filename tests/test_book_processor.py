"""Tests unitaires du traitement de livre (sans accès réseau)."""

import unittest
from collections import OrderedDict

from src import book_processor as bp

SAMPLE_BOOK = """\
The Project Gutenberg eBook of Test Book

Title: Le Livre de Test

Author: Jane Doe

*** START OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***

CHAPTER I. Le commencement

Premier paragraphe avec exactement cinq mots ici.

Deuxième paragraphe un peu plus long que le tout premier paragraphe vraiment.

CHAPTER II. La suite

Ceci appartient au deuxième chapitre et ne doit pas être compté du tout.

*** END OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***
"""


class TestBookProcessor(unittest.TestCase):
    def test_round_down_to_ten(self):
        self.assertEqual(bp.round_down_to_ten(123), 120)
        self.assertEqual(bp.round_down_to_ten(127), 120)
        self.assertEqual(bp.round_down_to_ten(129), 120)
        self.assertEqual(bp.round_down_to_ten(9), 0)
        self.assertEqual(bp.round_down_to_ten(30), 30)

    def test_extract_metadata(self):
        title, author = bp.extract_metadata(SAMPLE_BOOK)
        self.assertEqual(title, "Le Livre de Test")
        self.assertEqual(author, "Jane Doe")

    def test_extract_first_chapter_only(self):
        chapter = bp.extract_first_chapter(SAMPLE_BOOK)
        self.assertIn("Premier paragraphe", chapter)
        self.assertIn("Deuxième paragraphe", chapter)
        # Le contenu du chapitre 2 ne doit pas être présent.
        self.assertNotIn("deuxième chapitre", chapter)

    def test_split_paragraphs(self):
        chapter = bp.extract_first_chapter(SAMPLE_BOOK)
        paras = bp.split_paragraphs(chapter)
        self.assertEqual(len(paras), 2)

    def test_count_words(self):
        self.assertEqual(bp.count_words("un deux trois quatre cinq"), 5)
        self.assertEqual(bp.count_words("  espaces   multiples  "), 2)

    def test_count_words_parallel_matches_sequential(self):
        paras = ["un deux trois", "a b c d e", "seul", ""]
        parallel = bp.count_words_parallel(paras)
        sequential = [bp.count_words(p) for p in paras]
        self.assertEqual(parallel, sequential)

    def test_count_words_parallel_empty(self):
        self.assertEqual(bp.count_words_parallel([]), [])

    def test_build_distribution_sorted_and_counted(self):
        rounded = sorted([20, 20, 10, 30, 20])
        dist = bp.build_distribution(rounded)
        self.assertIsInstance(dist, OrderedDict)
        self.assertEqual(list(dist.keys()), [10, 20, 30])  # trié croissant
        self.assertEqual(dist[20], 3)
        self.assertEqual(dist[10], 1)


if __name__ == "__main__":
    unittest.main()
