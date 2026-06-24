"""Interface graphique Tkinter (Partie 1).

Fenêtre principale avec :
    * Une barre de menus : Données (télécharger / effacer), Options
      (couleurs, polices), Rapport (génération Word de la Partie 2).
    * Des boutons d'action : agrégation SQL et affichage du graphique.
    * Le résultat texte ET le graphique affichés DANS la fenêtre principale.
    * Une barre d'état en bas de la fenêtre.

Les opérations longues (réseau) tournent dans un thread séparé pour ne pas
geler l'interface ; le résultat est renvoyé au thread Tk via ``root.after``.
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import colorchooser, font as tkfont, messagebox, simpledialog, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from . import charts, data_fetcher, image_processor, word_report
from .book_processor import analyze_book, BookProcessingError
from .config import AppConfig
from .data_fetcher import DataFetchError
from .database import Database


class App(tk.Tk):
    """Fenêtre principale de l'application."""

    def __init__(self) -> None:
        super().__init__()
        self.config_obj = AppConfig.load()
        self.db = Database()
        self._canvas = None  # canvas matplotlib courant

        self.title("Python Avancé — Application de bureau")
        self.geometry("900x680")
        self.minsize(760, 560)

        self._build_menu()
        self._build_layout()
        self._apply_theme()
        self.set_status("Prêt. Téléchargez des données via le menu « Données ».")

    # ------------------------------------------------------------------ #
    # Construction de l'interface
    # ------------------------------------------------------------------ #
    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="Télécharger depuis Internet",
                              command=self.on_download)
        data_menu.add_command(label="Effacer la base de données",
                              command=self.on_clear_db)
        data_menu.add_separator()
        data_menu.add_command(label="Quitter", command=self.destroy)
        menubar.add_cascade(label="Données", menu=data_menu)

        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="Couleur de fond…",
                                command=lambda: self.on_pick_color("bg_color"))
        options_menu.add_command(label="Couleur du texte…",
                                command=lambda: self.on_pick_color("fg_color"))
        options_menu.add_command(label="Couleur d'accent…",
                                command=lambda: self.on_pick_color("accent_color"))
        options_menu.add_command(label="Police…", command=self.on_pick_font)
        menubar.add_cascade(label="Options", menu=options_menu)

        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="Générer le rapport Word (Partie 2)",
                               command=self.on_generate_report)
        menubar.add_cascade(label="Rapport", menu=report_menu)

        self.config(menu=menubar)

    def _build_layout(self) -> None:
        # Bandeau de titre
        self.header = tk.Label(self, text="Données Pokémon (PokeAPI)",
                               anchor="w", padx=12, pady=8)
        self.header.pack(fill="x")

        # Barre de boutons d'action
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_agg = ttk.Button(self.toolbar, text="Agrégation (SQL)",
                                  command=self.on_aggregate)
        self.btn_agg.pack(side="left", padx=(0, 6))

        self.btn_chart = ttk.Button(self.toolbar, text="Afficher le graphique",
                                    command=self.on_show_chart)
        self.btn_chart.pack(side="left", padx=6)

        # Libellés français affichés -> noms de colonnes SQL internes.
        # taille = hauteur (length), poids = weight (size). Deux mesures distinctes.
        self.METRIC_COLUMNS = {"taille": "length", "poids": "size"}
        self.metric_var = tk.StringVar(value="taille")
        ttk.Label(self.toolbar, text="Valeur :").pack(side="left", padx=(16, 4))
        self.metric_combo = ttk.Combobox(
            self.toolbar, textvariable=self.metric_var, width=10,
            values=list(self.METRIC_COLUMNS.keys()), state="readonly",
        )
        self.metric_combo.pack(side="left")
        # Changer la valeur met à jour graphique + agrégation automatiquement.
        self.metric_combo.bind("<<ComboboxSelected>>", self.on_metric_change)

        # Zone de résultat texte (dans la fenêtre principale)
        self.result_text = tk.Text(self, height=7, wrap="word")
        self.result_text.pack(fill="x", padx=12, pady=6)
        self.result_text.configure(state="disabled")

        # Zone graphique (dans la fenêtre principale)
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Barre d'état
        self.status_var = tk.StringVar(value="")
        self.status_bar = tk.Label(self, textvariable=self.status_var, anchor="w",
                                   relief="sunken", padx=8)
        self.status_bar.pack(side="bottom", fill="x")

    # ------------------------------------------------------------------ #
    # Thème (couleurs / polices)
    # ------------------------------------------------------------------ #
    def _apply_theme(self) -> None:
        c = self.config_obj
        self.configure(bg=c.bg_color)
        for widget in (self.header, self.toolbar, self.chart_frame, self.status_bar):
            widget.configure(bg=c.bg_color)
        self.header.configure(fg=c.fg_color, font=c.title_font)
        self.status_bar.configure(fg=c.fg_color, font=c.font)
        self.result_text.configure(bg="white", fg=c.fg_color, font=c.font)

    # ------------------------------------------------------------------ #
    # Barre d'état & résultat
    # ------------------------------------------------------------------ #
    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def show_result(self, message: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)
        self.result_text.configure(state="disabled")

    # ------------------------------------------------------------------ #
    # Actions : téléchargement / effacement
    # ------------------------------------------------------------------ #
    def on_download(self) -> None:
        # Que faire si la base n'est pas vide ? -> on demande à l'utilisateur.
        if not self.db.is_empty():
            answer = messagebox.askyesnocancel(
                "Base non vide",
                "La base de données contient déjà des données.\n\n"
                "Oui  = effacer puis re-télécharger\n"
                "Non  = ajouter aux données existantes\n"
                "Annuler = ne rien faire",
            )
            if answer is None:
                self.set_status("Téléchargement annulé.")
                return
            if answer is True:
                self.db.clear()

        self.set_status("Téléchargement en cours…")
        self._set_buttons_state("disabled")
        # Opération réseau dans un thread pour ne pas geler l'interface.
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self) -> None:
        try:
            rows = data_fetcher.fetch_pokemon(limit=self.config_obj.api_limit)
            inserted = self.db.insert_many(rows)
            self.after(0, lambda: self._on_download_done(inserted))
        except DataFetchError as exc:
            self.after(0, lambda: self._on_download_error(str(exc)))
        except Exception as exc:  # noqa: BLE001 - ne jamais planter en silence
            self.after(0, lambda e=exc: self._on_download_error(repr(e)))

    def _on_download_done(self, inserted: int) -> None:
        self._set_buttons_state("normal")
        self.set_status(f"{inserted} enregistrements téléchargés et stockés.")
        self.show_result(
            f"Téléchargement réussi : {inserted} Pokémon enregistrés.\n"
            f"Total en base : {self.db.count()}.\n"
            "Utilisez « Agrégation (SQL) » ou « Afficher le graphique »."
        )
        self.on_show_chart()

    def _on_download_error(self, message: str) -> None:
        self._set_buttons_state("normal")
        self.set_status("Échec du téléchargement.")
        messagebox.showerror("Erreur réseau", message)

    def on_clear_db(self) -> None:
        if self.db.is_empty():
            self.set_status("La base est déjà vide.")
            return
        if messagebox.askyesno("Confirmation", "Effacer tout le contenu de la base ?"):
            n = self.db.clear()
            self.show_result(f"{n} enregistrements supprimés. La base est vide.")
            self._clear_chart()
            self.set_status(f"{n} enregistrements supprimés.")

    # ------------------------------------------------------------------ #
    # Actions : agrégation & graphique
    # ------------------------------------------------------------------ #
    def _current_column(self) -> str:
        """Renvoie le nom de colonne SQL correspondant au choix de l'utilisateur."""
        return self.METRIC_COLUMNS.get(self.metric_var.get(), "length")

    def on_metric_change(self, event=None) -> None:
        """Quand on change la valeur : rafraîchit graphique et agrégation."""
        if self.db.is_empty():
            return
        self.on_show_chart()
        self.on_aggregate()

    def on_aggregate(self) -> None:
        if self.db.is_empty():
            messagebox.showinfo("Base vide", "Téléchargez d'abord des données.")
            return
        try:
            column = self._current_column()
            agg = self.db.aggregate(column)
            by_state = self.db.aggregate_by_state(column)
        except Exception as exc:  # noqa: BLE001 - robustesse demandée
            messagebox.showerror("Erreur", f"Agrégation impossible : {exc}")
            return

        label = self.metric_var.get()
        lines = [
            f"Agrégation SQL sur la {label} de {agg['n']} Pokémon :",
            f"  • Somme    : {agg['total']:.1f}",
            f"  • Moyenne  : {agg['moyenne']:.2f}",
            f"  • Minimum  : {agg['minimum']:.1f}",
            f"  • Maximum  : {agg['maximum']:.1f}",
            "",
            f"Moyenne de la {label} par état (type) :",
        ]
        for state, avg, n in by_state:
            lines.append(f"  • {state:<12} {avg:6.2f}  ({n} pokémon)")
        self.show_result("\n".join(lines))
        self.set_status(f"Agrégation SQL calculée sur la colonne « {column} ».")

    def on_show_chart(self) -> None:
        rows = self.db.fetch_all()
        if not rows:
            messagebox.showinfo("Base vide", "Téléchargez d'abord des données.")
            return
        column = self._current_column()
        fig = charts.build_db_figure(rows, column=column,
                                     accent_color=self.config_obj.accent_color)
        self._embed_figure(fig)
        self.set_status(
            f"Graphique de la {self.metric_var.get()} affiché dans la fenêtre."
        )

    def _embed_figure(self, fig) -> None:
        self._clear_chart()
        self._canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def _clear_chart(self) -> None:
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None

    # ------------------------------------------------------------------ #
    # Options : couleurs & polices
    # ------------------------------------------------------------------ #
    def on_pick_color(self, attribute: str) -> None:
        current = getattr(self.config_obj, attribute)
        _, hexcolor = colorchooser.askcolor(color=current, title="Choisir une couleur")
        if hexcolor:
            setattr(self.config_obj, attribute, hexcolor)
            self.config_obj.save()
            self._apply_theme()
            self.set_status(f"Couleur « {attribute} » mise à jour.")

    def on_pick_font(self) -> None:
        families = sorted(set(tkfont.families()))
        family = simpledialog.askstring(
            "Police", "Nom de la police :",
            initialvalue=self.config_obj.font_family,
        )
        if family and family in families:
            self.config_obj.font_family = family
        size = simpledialog.askinteger(
            "Taille", "Taille de la police :",
            initialvalue=self.config_obj.font_size, minvalue=8, maxvalue=28,
        )
        if size:
            self.config_obj.font_size = size
        self.config_obj.save()
        self._apply_theme()
        self.set_status("Police mise à jour.")

    # ------------------------------------------------------------------ #
    # Rapport Word (Partie 2)
    # ------------------------------------------------------------------ #
    def on_generate_report(self) -> None:
        author = simpledialog.askstring(
            "Auteur du rapport", "Votre nom :",
            initialvalue="ELIDRISSI Hamza et GUY Michel",
        )
        if author is None:
            return
        self.set_status("Génération du rapport en cours…")
        self._set_buttons_state("disabled")
        threading.Thread(target=self._report_worker, args=(author,),
                         daemon=True).start()

    def _report_worker(self, author: str) -> None:
        try:
            book = analyze_book(self.config_obj.book_id)
            photo = image_processor.build_photo_one()
            path = word_report.generate_report(book, photo, report_author=author)
            self.after(0, lambda: self._on_report_done(path))
        except (BookProcessingError, image_processor.ImageProcessingError) as exc:
            self.after(0, lambda: self._on_report_error(str(exc)))
        except Exception as exc:  # noqa: BLE001 - on ne doit jamais planter
            self.after(0, lambda: self._on_report_error(repr(exc)))

    def _on_report_done(self, path: str) -> None:
        self._set_buttons_state("normal")
        self.set_status(f"Rapport généré : {path}")
        messagebox.showinfo("Rapport généré", f"Le rapport Word a été créé :\n{path}")

    def _on_report_error(self, message: str) -> None:
        self._set_buttons_state("normal")
        self.set_status("Échec de la génération du rapport.")
        messagebox.showerror("Erreur", message)

    # ------------------------------------------------------------------ #
    # Utilitaires
    # ------------------------------------------------------------------ #
    def _set_buttons_state(self, state: str) -> None:
        for btn in (self.btn_agg, self.btn_chart):
            btn.configure(state=state)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
