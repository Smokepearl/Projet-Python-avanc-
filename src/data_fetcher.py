"""Téléchargement des données JSON depuis Internet (PokeAPI).

Site fournissant des données au format JSON : https://pokeapi.co/

Stratégie :
    1. On récupère la liste des Pokémon (1 requête).
    2. On télécharge le détail de chacun *en parallèle* avec un
       ThreadPoolExecutor. C'est le bonus « paralléliser les calculs par
       l'utilisation des threads » : les appels réseau sont I/O-bound, donc
       les threads accélèrent réellement le téléchargement.

Toutes les fonctions gèrent les exceptions réseau et renvoient des données
exploitables ou lèvent une ``DataFetchError`` explicite.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from . import net  # noqa: F401 - active le magasin de certificats système

API_BASE = "https://pokeapi.co/api/v2/pokemon"
REQUEST_TIMEOUT = 20  # secondes


class DataFetchError(Exception):
    """Erreur levée lorsqu'on ne parvient pas à récupérer les données."""


def _get_json(url: str, params: dict | None = None) -> dict:
    """Effectue une requête GET et renvoie le JSON, ou lève DataFetchError."""
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise DataFetchError(f"Échec de la requête vers {url} : {exc}") from exc
    except ValueError as exc:  # JSON invalide
        raise DataFetchError(f"Réponse JSON invalide depuis {url} : {exc}") from exc


def _parse_detail(detail: dict) -> dict:
    """Extrait le sous-ensemble (id, name, size, state, length) d'un détail brut.

    Conversion des unités PokeAPI vers des unités courantes :
        * height est en décimètres -> on stocke la taille en centimètres (×10) ;
        * weight est en hectogrammes -> on stocke le poids en kilogrammes (÷10).
    """
    return {
        "id": detail["id"],
        "name": detail["name"],
        "size": float(detail["weight"]) / 10.0,   # poids (hg -> kg)
        "state": detail["types"][0]["type"]["name"],  # type principal -> état
        "length": float(detail["height"]) * 10.0,  # taille (dm -> cm)
    }


def fetch_pokemon(limit: int = 30, max_workers: int = 8) -> list[dict]:
    """Télécharge ``limit`` Pokémon et renvoie le sous-ensemble de leurs données.

    Les détails sont téléchargés en parallèle via des threads (bonus).

    :raises DataFetchError: si la liste initiale ne peut être récupérée.
    """
    listing = _get_json(API_BASE, params={"limit": limit, "offset": 0})
    urls = [entry["url"] for entry in listing.get("results", [])]

    results: list[dict] = []
    # --- téléchargement parallèle des détails ---
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_get_json, url): url for url in urls}
        for future in as_completed(futures):
            try:
                detail = future.result()
                results.append(_parse_detail(detail))
            except (DataFetchError, KeyError, IndexError, TypeError):
                # On ignore un Pokémon défaillant plutôt que de tout faire échouer.
                continue

    if not results:
        raise DataFetchError("Aucune donnée n'a pu être téléchargée.")

    # Tri stable par id pour un affichage reproductible.
    results.sort(key=lambda r: r["id"])
    return results
