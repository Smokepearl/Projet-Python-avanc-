"""Package source de l'application Python Avancé.

Modules :
    config          -- préférences de l'application (couleurs, polices) persistées en JSON
    database        -- couche d'accès SQLite (CRUD + agrégations SQL)
    data_fetcher    -- téléchargement de données JSON depuis Internet (parallélisé)
    charts          -- génération de graphiques matplotlib
    book_processor  -- traitement d'un livre Project Gutenberg
    image_processor -- traitement d'images (Pillow)
    word_report     -- génération du rapport Word (python-docx)
    gui             -- interface Tkinter (fenêtre principale)
"""

__version__ = "1.0.0"
