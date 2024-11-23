
import tkinter as tk
from tkinter import ttk
from gui.dashboard import Dashboard
from gui.strategy_config import StrategyConfig
from gui.chart_view import ChartView

class MainWindow:
    def __init__(self, bot):
        self.bot = bot
        self.root = tk.Tk()
        self.root.title("Bot de Trading Crypto")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        self.dashboard = Dashboard(self.notebook, self.bot)
        self.strategy_config = StrategyConfig(self.notebook, self.bot)
        self.chart_view = ChartView(self.notebook, self.bot)

        self.notebook.add(self.dashboard.frame, text="Dashboard")
        self.notebook.add(self.strategy_config.frame, text="Configuration des Stratégies")
        self.notebook.add(self.chart_view.frame, text="Graphiques")

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self.root.quit)

        trading_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trading", menu=trading_menu)
        trading_menu.add_command(label="Démarrer", command=self.bot.start_trading)
        trading_menu.add_command(label="Arrêter", command=self.bot.stop_trading)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("À propos")
        about_window.geometry("300x200")
        
        label = tk.Label(about_window, text="Bot de Trading Crypto\nVersion 1.0\n\nDéveloppé par OpenAI Assistant")
        label.pack(expand=True)

    def run(self):
        self.root.mainloop()

    def update(self):
        self.dashboard.update()
        self.chart_view.update()
