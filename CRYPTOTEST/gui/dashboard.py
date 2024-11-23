
import tkinter as tk
from tkinter import ttk

class Dashboard:
    def __init__(self, parent, bot):
        self.bot = bot
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        # Informations générales
        general_frame = ttk.LabelFrame(self.frame, text="Informations générales")
        general_frame.pack(padx=10, pady=10, fill='x')

        self.status_label = ttk.Label(general_frame, text="Statut: Arrêté")
        self.status_label.pack(anchor='w')

        self.balance_label = ttk.Label(general_frame, text="Solde total: 0 USDT")
        self.balance_label.pack(anchor='w')

        # Performances
        performance_frame = ttk.LabelFrame(self.frame, text="Performances")
        performance_frame.pack(padx=10, pady=10, fill='x')

        self.profit_loss_label = ttk.Label(performance_frame, text="Profit/Perte: 0 USDT")
        self.profit_loss_label.pack(anchor='w')

        self.roi_label = ttk.Label(performance_frame, text="ROI: 0%")
        self.roi_label.pack(anchor='w')

        # Positions ouvertes
        positions_frame = ttk.LabelFrame(self.frame, text="Positions ouvertes")
        positions_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.positions_tree = ttk.Treeview(positions_frame, columns=('Symbol', 'Amount', 'Entry Price', 'Current Price', 'PNL'), show='headings')
        self.positions_tree.heading('Symbol', text='Symbole')
        self.positions_tree.heading('Amount', text='Montant')
        self.positions_tree.heading('Entry Price', text="Prix d'entrée")
        self.positions_tree.heading('Current Price', text='Prix actuel')
        self.positions_tree.heading('PNL', text='PNL')
        self.positions_tree.pack(fill='both', expand=True)

    def update(self):
        # Mettre à jour les informations générales
        self.status_label.config(text=f"Statut: {'En cours' if self.bot.is_running else 'Arrêté'}")
        self.balance_label.config(text=f"Solde total: {self.bot.portfolio.get_total_value():.2f} USDT")

        # Mettre à jour les performances
        profit_loss = self.bot.portfolio.get_total_value() - self.bot.initial_balance
        self.profit_loss_label.config(text=f"Profit/Perte: {profit_loss:.2f} USDT")
        roi = (profit_loss / self.bot.initial_balance) * 100 if self.bot.initial_balance > 0 else 0
        self.roi_label.config(text=f"ROI: {roi:.2f}%")

        # Mettre à jour les positions ouvertes
        self.positions_tree.delete(*self.positions_tree.get_children())
        for symbol, position in self.bot.portfolio.positions.items():
            current_price = self.bot.exchange_handler.get_latest_price(symbol)
            pnl = (current_price - position['price']) * position['amount']
            self.positions_tree.insert('', 'end', values=(symbol, position['amount'], position['price'], current_price, f"{pnl:.2f}"))
