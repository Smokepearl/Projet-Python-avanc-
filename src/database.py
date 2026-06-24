"""Couche d'accès à la base de données SQLite.

La table ``pokemon`` ne stocke qu'un *sous-ensemble* des données téléchargées,
comme demandé dans l'énoncé : nom, taille, état, longueur.

Correspondance avec les données brutes de la PokeAPI :
    name   -> nom du Pokémon
    size   -> poids (``weight``, en hectogrammes)
    state  -> type principal (``types[0]``)  ->  joue le rôle de l'« état »
    length -> taille/hauteur (``height``, en décimètres)
"""

from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterable, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(ROOT_DIR, "data", "app.db")


class Database:
    """Petit wrapper orienté objet autour de SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        # On s'assure que le dossier data/ existe (sauf base en mémoire).
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Connexion persistante : indispensable pour une base ":memory:"
        # (sinon chaque nouvelle connexion repartirait d'une base vide).
        # check_same_thread=False : l'interface lance les téléchargements dans
        # un thread séparé ; un verrou sérialise les accès pour rester sûr.
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._init_schema()

    # ------------------------------------------------------------------ #
    # Connexion
    # ------------------------------------------------------------------ #
    @contextmanager
    def _connect(self):
        """Context manager : réutilise la connexion (sous verrou), commit/rollback."""
        with self._lock:
            try:
                yield self._conn
                self._conn.commit()
            except sqlite3.Error:
                self._conn.rollback()
                raise

    def close(self) -> None:
        """Ferme la connexion à la base."""
        self._conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pokemon (
                    id     INTEGER PRIMARY KEY,
                    name   TEXT    NOT NULL,
                    size   REAL    NOT NULL,   -- poids (hectogrammes)
                    state  TEXT    NOT NULL,   -- type principal (« état »)
                    length REAL    NOT NULL    -- hauteur (décimètres)
                )
                """
            )

    # ------------------------------------------------------------------ #
    # Écriture
    # ------------------------------------------------------------------ #
    def insert_many(self, rows: Iterable[dict]) -> int:
        """Insère une liste d'enregistrements. Renvoie le nombre inséré."""
        payload = [
            (r["id"], r["name"], r["size"], r["state"], r["length"])
            for r in rows
        ]
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO pokemon (id, name, size, state, length) "
                "VALUES (?, ?, ?, ?, ?)",
                payload,
            )
        return len(payload)

    def clear(self) -> int:
        """Efface tout le contenu de la table. Renvoie le nb de lignes supprimées."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM pokemon")
            return cur.rowcount

    # ------------------------------------------------------------------ #
    # Lecture
    # ------------------------------------------------------------------ #
    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM pokemon").fetchone()[0]

    def is_empty(self) -> bool:
        return self.count() == 0

    def fetch_all(self) -> list[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT id, name, size, state, length FROM pokemon ORDER BY name"
            ).fetchall()

    # ------------------------------------------------------------------ #
    # Agrégations (calculées en SQL, conformément à l'énoncé)
    # ------------------------------------------------------------------ #
    def aggregate(self, column: str = "length") -> dict:
        """Renvoie min/max/somme/moyenne d'une colonne numérique via SQL.

        :param column: ``"length"`` ou ``"size"`` (liste blanche de sécurité).
        """
        if column not in {"length", "size"}:
            raise ValueError(f"Colonne non autorisée pour l'agrégation : {column!r}")
        with self._connect() as conn:
            row = conn.execute(
                f"""
                SELECT COUNT(*)   AS n,
                       SUM({column})  AS total,
                       AVG({column})  AS moyenne,
                       MIN({column})  AS minimum,
                       MAX({column})  AS maximum
                FROM pokemon
                """
            ).fetchone()
        return {
            "column": column,
            "n": row["n"],
            "total": row["total"] or 0,
            "moyenne": row["moyenne"] or 0,
            "minimum": row["minimum"] or 0,
            "maximum": row["maximum"] or 0,
        }

    def aggregate_by_state(self, column: str = "length") -> list[tuple]:
        """Moyenne d'une colonne groupée par état (type). Renvoie [(state, avg, n)]."""
        if column not in {"length", "size"}:
            raise ValueError(f"Colonne non autorisée : {column!r}")
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT state, AVG({column}) AS moyenne, COUNT(*) AS n
                FROM pokemon
                GROUP BY state
                ORDER BY moyenne DESC
                """
            ).fetchall()
        return [(r["state"], r["moyenne"], r["n"]) for r in rows]
