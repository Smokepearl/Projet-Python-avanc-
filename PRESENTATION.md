# Script de démonstration — Enregistrement d'écran

> Projet Python Avancé — ELIDRISSI Hamza & GUY Michel
> Durée cible : **5 à 7 minutes**. Parlez calmement, montrez en cliquant.

---

## 0. Préparation (avant d'enregistrer)

- [ ] Fermer les fenêtres inutiles, mettre un fond d'écran neutre.
- [ ] Ouvrir un terminal dans le dossier du projet.
- [ ] Vider la base pour partir propre : supprimer `data/app.db` **ou** lancer
      l'appli et faire *Données → Effacer la base de données*.
- [ ] Avoir le code ouvert dans VS Code à côté (pour montrer 2-3 fichiers).
- [ ] Tester une fois le téléchargement (réseau OK) juste avant.

**Outil d'enregistrement (Windows, gratuit, intégré) :** `Xbox Game Bar`
→ touche **`Win + G`**, puis bouton enregistrer (ou **`Win + Alt + R`** pour
démarrer/arrêter directement). Le micro doit être activé pour la voix.
*Alternative : OBS Studio (plus pro, gratuit).*

---

## 1. Introduction (≈ 30 s)

> « Bonjour, nous sommes Hamza ELIDRISSI et Michel GUY. Nous présentons notre
> projet Python Avancé : une application de bureau qui télécharge des données
> depuis Internet, les stocke dans une base SQLite, les analyse et les
> visualise. Elle génère aussi automatiquement un rapport Word à partir d'un
> livre. Le projet est en deux parties indépendantes. »

À l'écran : montrer l'arborescence du projet dans VS Code (le dossier `src/`).

---

## 2. Lancement de l'application (≈ 30 s)

Dans le terminal :
```bash
python main.py
```
> « On lance l'application avec `python main.py`. Voici la fenêtre principale :
> en haut un menu, des boutons d'action, une zone de résultats, une zone
> graphique, et en bas une barre d'état qui indique la dernière opération. »

---

## 3. PARTIE 1 — Données du web (≈ 2 min)

### a) Télécharger
Menu **Données → Télécharger depuis Internet**.
> « On télécharge des données au format JSON depuis l'API publique PokeAPI.
> Le téléchargement se fait dans un thread séparé pour ne pas geler la
> fenêtre, et les détails sont récupérés en parallèle — c'est notre premier
> bonus de parallélisation. On ne stocke qu'un sous-ensemble des données :
> le nom, la taille, l'état (le type) et la longueur. »

Le graphique s'affiche tout seul.
> « Les données sont maintenant en base SQLite, et le graphique s'affiche
> directement dans la fenêtre. »

### b) Agrégation SQL
Bouton **Agrégation (SQL)**.
> « Ce bouton calcule, avec de vraies requêtes SQL, la somme, la moyenne, le
> minimum et le maximum de la valeur choisie, plus une moyenne groupée par
> état. Le calcul est fait par la base, pas en Python. »

Changer la liste **Valeur** (`length` → `size`) puis recliquer.
> « On peut choisir d'agréger la longueur ou la taille. »

### c) Cas « base non vide »
Refaire **Données → Télécharger depuis Internet**.
> « Si on retélécharge alors que la base contient déjà des données,
> l'application demande quoi faire : effacer et recharger, ajouter, ou
> annuler. C'était une question explicite de l'énoncé. »

### d) Options (couleurs / polices)
Menu **Options → Couleur de fond…**, choisir une couleur.
> « Le menu Options permet de personnaliser couleurs et police. Les
> préférences sont sauvegardées dans un fichier et conservées au prochain
> lancement. »

### e) Effacer
Menu **Données → Effacer la base de données**.
> « Et on peut vider la base à tout moment. La barre d'état confirme. »

---

## 4. PARTIE 2 — Rapport Word (≈ 2 min)

Menu **Rapport → Générer le rapport Word**. Valider le nom des auteurs.
> « La deuxième partie génère un rapport automatiquement. L'application
> télécharge le texte d'un livre depuis Project Gutenberg — ici *Alice au
> pays des merveilles* —, en extrait le titre, l'auteur et le premier
> chapitre. »

Pendant le traitement :
> « Elle compte les mots de chaque paragraphe, arrondit à la dizaine, et
> construit une distribution. Ce comptage est parallélisé sur plusieurs
> processus — notre deuxième bonus. En parallèle, elle télécharge une image
> liée au livre, la recadre, la redimensionne, et y colle un logo noir et
> blanc qu'elle fait pivoter. »

Ouvrir le fichier `output/rapport.docx` généré.
> « Voici le résultat : une page de titre avec le titre du livre, l'image,
> l'auteur du livre et nos noms ; puis une page d'analyse avec le graphique
> de distribution et un tableau de statistiques (nombre de paragraphes, mots
> min/max/moyen, source des données). Les en-têtes utilisent des polices
> modifiées, en gras et en italique. »

---

## 5. Qualité du code & tests (≈ 1 min)

Montrer VS Code : ouvrir `src/database.py` puis `src/data_fetcher.py`.
> « Le code est organisé en modules indépendants, chacun avec une seule
> responsabilité. Toutes les opérations réseau, fichier et base sont
> protégées par de la gestion d'exceptions : l'application ne plante jamais,
> elle affiche un message. »

Dans le terminal :
```bash
python -m unittest discover -s tests -v
```
> « Nous avons écrit 22 tests unitaires qui vérifient les fonctions clés sans
> dépendre d'Internet, grâce à des mocks et une base en mémoire. Ils passent
> tous. »

---

## 6. Conclusion (≈ 20 s)

> « En résumé : une application complète qui couvre toute la chaîne — interface
> graphique, API web, base de données, visualisation, traitement d'images,
> génération de document — avec parallélisme par threads et processus, gestion
> d'erreurs et tests. Le code est publié sur GitHub. Merci. »

Montrer la page GitHub du projet pour finir.

---

## Aide-mémoire des points qui rapportent (à ne pas oublier de citer)

- [ ] Données **JSON** depuis Internet (PokeAPI)
- [ ] Sous-ensemble stocké : **nom, taille, état, longueur**
- [ ] Base **SQLite** + agrégation **en SQL**
- [ ] Graphique **dans** la fenêtre principale
- [ ] **Barre d'état** en bas
- [ ] Menu **Options** (couleurs, polices) persistées
- [ ] Gestion du cas **base non vide**
- [ ] Rapport **Word** : page titre + page graphique, polices gras/italique
- [ ] Image #1 **téléchargée à l'exécution**, recadrée/redimensionnée
- [ ] Logo #2 **N&B**, pivoté, collé
- [ ] **Arrondi à la dizaine** + distribution des paragraphes
- [ ] **Threads** (réseau) + **processus** (calcul) — les 2 bonus
- [ ] **Gestion des exceptions** partout
- [ ] **Tests unitaires** (22, tous OK)
- [ ] Code publié sur **GitHub**
