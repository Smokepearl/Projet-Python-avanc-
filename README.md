# Projet Python Avancé — Application de bureau

Application de bureau **Tkinter** qui télécharge des données JSON depuis Internet,
les stocke dans une base **SQLite**, en affiche des résumés et des graphiques, et
génère un **rapport Word** illustré à partir d'un livre du *Project Gutenberg*.

Projet réalisé dans le cadre du cours *Python Avancé*.

**Auteurs :** ELIDRISSI Hamza et GUY Michel

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Sources de données](#sources-de-données)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture du projet](#architecture-du-projet)
- [Tests unitaires](#tests-unitaires)
- [Correspondance avec le barème](#correspondance-avec-le-barème)

---

## Fonctionnalités

### Partie 1 — Application de bureau
- **Menu** :
  - *Données* → télécharger depuis Internet, effacer la base, quitter ;
  - *Options* → couleurs (fond, texte, accent) et police (famille, taille),
    **persistées** dans `settings.json` ;
  - *Rapport* → générer le rapport Word (Partie 2).
- **Stockage** d'un *sous-ensemble* des données téléchargées (nom, taille, état,
  longueur) dans une base **SQLite**.
- **Gestion du cas « base non vide »** : à un nouveau téléchargement, l'application
  demande à l'utilisateur s'il veut *effacer puis recharger*, *ajouter*, ou *annuler*.
- **Bouton d'agrégation** : calcul en **SQL** (`SUM`, `AVG`, `MIN`, `MAX`, plus un
  `GROUP BY` par état) de la valeur choisie (longueur ou taille).
- **Bouton graphique** : histogramme **matplotlib** intégré *dans* la fenêtre principale.
- **Barre d'état** en bas de fenêtre indiquant la dernière opération.
- **Téléchargement parallélisé** (threads) pour ne pas geler l'interface — *bonus*.

### Partie 2 — Rapport Word
- Téléchargement de la version texte d'un livre Gutenberg.
- Extraction du **titre**, de l'**auteur** et du **premier chapitre**.
- Comptage des mots par paragraphe, **arrondi à la dizaine inférieure**
  (123, 127, 129 → 120), tri et **distribution** des longueurs.
- **Graphique** de distribution enregistré sur disque.
- **Image #1** (couverture du livre) téléchargée à l'exécution, **recadrée** et
  **redimensionnée**.
- **Image #2** (logo) lue depuis le disque en **noir et blanc**, **pivotée** et
  **collée** dans l'image #1 → *photo n° 1*.
- **Document Word** : page de titre (titre, photo n° 1, auteur du livre, auteur du
  rapport) + page graphique (distribution + statistiques). En-têtes avec polices
  modifiées (gras, italique).

---

## Sources de données

| Usage | Source | Format |
|-------|--------|--------|
| Partie 1 (données) | [PokeAPI](https://pokeapi.co/) | JSON |
| Partie 2 (livre)   | [Project Gutenberg](https://www.gutenberg.org/) | texte |
| Image #1           | Couverture du livre (Gutenberg) | JPEG |

Correspondance du sous-ensemble stocké :

| Colonne SQLite | Donnée PokeAPI | Sens |
|----------------|----------------|------|
| `name`   | `name`             | nom |
| `size`   | `weight`           | taille (poids) |
| `state`  | `types[0]`         | état (type principal) |
| `length` | `height`           | longueur (hauteur) |

---

## Installation

```bash
# 1. (optionnel) créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 2. installer les dépendances
pip install -r requirements.txt
```

> **Note (proxy d'entreprise).** Le paquet optionnel `truststore` permet à Python
> d'utiliser le magasin de certificats du système, ce qui évite les erreurs TLS
> derrière un proxy qui inspecte le trafic. Sur une machine personnelle, il est
> inutile et silencieusement ignoré.

---

## Utilisation

### Lancer l'application de bureau
```bash
python main.py
```
1. Menu *Données → Télécharger depuis Internet*.
2. Cliquer sur *Agrégation (SQL)* ou *Afficher le graphique*.
3. Menu *Options* pour personnaliser couleurs et police.
4. Menu *Rapport* pour générer le document Word.

### Générer le rapport en ligne de commande (Partie 2 indépendante)
```bash
python generate_report.py [book_id] ["Nom de l'auteur du rapport"]
# exemple :
python generate_report.py 11 "H. El Idrissi"
```
Les fichiers sont écrits dans `output/` : `rapport.docx`, `photo_1.png`,
`distribution.png`.

### (Re)générer le logo noir et blanc
```bash
python assets/make_logo.py
```

---

## Architecture du projet

```
projet python/
├── main.py                 # point d'entrée de l'application desktop
├── generate_report.py      # génération du rapport en CLI (Partie 2)
├── requirements.txt
├── settings.json           # préférences (généré au 1er enregistrement)
├── assets/
│   ├── logo.png            # image #2 (logo N&B) lue depuis le disque
│   └── make_logo.py        # script de génération du logo
├── data/
│   └── app.db              # base SQLite (générée)
├── output/                 # rapport et images générés
├── src/
│   ├── config.py           # préférences (couleurs, polices) + persistance JSON
│   ├── database.py         # couche SQLite (CRUD + agrégations SQL)
│   ├── data_fetcher.py     # téléchargement JSON parallélisé (threads)
│   ├── charts.py           # graphiques matplotlib
│   ├── book_processor.py   # analyse d'un livre Gutenberg
│   ├── image_processor.py  # traitement d'images (Pillow)
│   ├── word_report.py      # génération du document Word (python-docx)
│   ├── net.py              # activation du magasin de certificats système
│   └── gui.py              # interface Tkinter
└── tests/                  # tests unitaires (unittest)
```

**Gestion des exceptions** : toutes les opérations réseau, fichier et base de
données sont encapsulées ; l'application affiche un message d'erreur clair au lieu
de se bloquer.

---

## Tests unitaires

```bash
python -m unittest discover -s tests -v
```

Couverture : base de données (insertion, effacement, agrégations, colonne
invalide), traitement du livre (arrondi, extraction titre/auteur/chapitre,
distribution), téléchargement (mappage du sous-ensemble, parallélisme simulé,
échec réseau) et traitement d'images (recadrage, logo N&B, rotation/collage).
Les tests n'accèdent pas au réseau (mocks + images synthétiques + base en mémoire).

---

## Correspondance avec le barème

| Critère | Où c'est traité |
|---------|-----------------|
| Partie 1 – Application desktop | `src/gui.py`, `src/database.py`, `src/data_fetcher.py`, `src/charts.py` |
| Partie 2 – Rapport Word | `src/book_processor.py`, `src/image_processor.py`, `src/word_report.py` |
| Qualité du code | modules découplés, docstrings, type hints, gestion d'erreurs |
| Bonus – threads/processus | téléchargement parallèle (`ThreadPoolExecutor`) |
| GitHub | dépôt + `.gitignore` + ce README |
| Ligne d'état (optionnel) | barre d'état Tkinter en bas de fenêtre |
