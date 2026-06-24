"""Tests unitaires du module de téléchargement (réseau simulé via mocks)."""

import unittest
from unittest.mock import patch

from src import data_fetcher
from src.data_fetcher import DataFetchError

POKEMON_DETAIL = {
    "id": 25,
    "name": "pikachu",
    "weight": 60,
    "height": 4,
    "types": [{"type": {"name": "electric"}}],
}


class TestParseDetail(unittest.TestCase):
    def test_parse_detail_maps_subset(self):
        row = data_fetcher._parse_detail(POKEMON_DETAIL)
        self.assertEqual(row["name"], "pikachu")
        self.assertEqual(row["size"], 60.0)        # weight -> size
        self.assertEqual(row["length"], 4.0)       # height -> length
        self.assertEqual(row["state"], "electric")  # type -> state
        self.assertEqual(row["id"], 25)


class TestFetchPokemon(unittest.TestCase):
    @patch("src.data_fetcher._get_json")
    def test_fetch_pokemon_parallel(self, mock_get):
        listing = {"results": [
            {"url": "u1"}, {"url": "u2"}, {"url": "u3"},
        ]}

        def side_effect(url, params=None):
            if url == data_fetcher.API_BASE:
                return listing
            return {**POKEMON_DETAIL, "id": int(url[1:]), "name": f"p{url[1:]}"}

        mock_get.side_effect = side_effect
        rows = data_fetcher.fetch_pokemon(limit=3)
        self.assertEqual(len(rows), 3)
        self.assertEqual([r["id"] for r in rows], [1, 2, 3])  # trié par id

    @patch("src.data_fetcher._get_json")
    def test_fetch_pokemon_all_details_fail(self, mock_get):
        def side_effect(url, params=None):
            if url == data_fetcher.API_BASE:
                return {"results": [{"url": "u1"}]}
            raise DataFetchError("boom")

        mock_get.side_effect = side_effect
        with self.assertRaises(DataFetchError):
            data_fetcher.fetch_pokemon(limit=1)


if __name__ == "__main__":
    unittest.main()
