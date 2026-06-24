"""Tests unitaires de la couche base de données (base SQLite en mémoire)."""

import unittest

from src.database import Database

SAMPLE = [
    {"id": 1, "name": "bulbasaur", "size": 69.0, "state": "grass", "length": 7.0},
    {"id": 2, "name": "charmander", "size": 85.0, "state": "fire", "length": 6.0},
    {"id": 3, "name": "squirtle", "size": 90.0, "state": "water", "length": 5.0},
    {"id": 4, "name": "vulpix", "size": 99.0, "state": "fire", "length": 6.0},
]


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # ":memory:" -> base isolée et jetable pour chaque test.
        self.db = Database(db_path=":memory:")

    def test_starts_empty(self):
        self.assertTrue(self.db.is_empty())
        self.assertEqual(self.db.count(), 0)

    def test_insert_and_count(self):
        inserted = self.db.insert_many(SAMPLE)
        self.assertEqual(inserted, 4)
        self.assertEqual(self.db.count(), 4)
        self.assertFalse(self.db.is_empty())

    def test_clear(self):
        self.db.insert_many(SAMPLE)
        removed = self.db.clear()
        self.assertEqual(removed, 4)
        self.assertTrue(self.db.is_empty())

    def test_insert_replace_on_same_id(self):
        self.db.insert_many(SAMPLE)
        self.db.insert_many([{**SAMPLE[0], "name": "modifié"}])
        rows = {r["id"]: r["name"] for r in self.db.fetch_all()}
        self.assertEqual(rows[1], "modifié")
        self.assertEqual(self.db.count(), 4)  # pas de doublon

    def test_aggregate_length(self):
        self.db.insert_many(SAMPLE)
        agg = self.db.aggregate("length")
        self.assertEqual(agg["n"], 4)
        self.assertAlmostEqual(agg["total"], 24.0)
        self.assertAlmostEqual(agg["moyenne"], 6.0)
        self.assertAlmostEqual(agg["minimum"], 5.0)
        self.assertAlmostEqual(agg["maximum"], 7.0)

    def test_aggregate_invalid_column(self):
        with self.assertRaises(ValueError):
            self.db.aggregate("name")  # colonne non autorisée

    def test_aggregate_by_state(self):
        self.db.insert_many(SAMPLE)
        result = dict((s, (avg, n)) for s, avg, n in self.db.aggregate_by_state("length"))
        self.assertEqual(result["fire"][1], 2)        # 2 pokémon de type feu
        self.assertAlmostEqual(result["fire"][0], 6.0)  # moyenne longueur feu


if __name__ == "__main__":
    unittest.main()
