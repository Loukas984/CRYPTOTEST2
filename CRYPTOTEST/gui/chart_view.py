
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ChartView:
    def __init__(self, parent, bot):
        self.bot = bot
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        # Sélection du symbole
        symbol_frame = ttk.Frame(self.frame)
        symbol_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(symbol_frame, text="Symbole:").pack(side='left')
        self.symbol_var = tk.StringVar()
        self.symbol_combobox = ttk.Combobox(symbol_frame, textvariable=self.symbol_var)
        self.symbol_combobox['values'] = self.bot.get_available_symbols()
        self.symbol_combobox.pack(side='left', padx=5)
        self.symbol_combobox.bind('<<ComboboxSelected>>', self.on_symbol_selected)

        # Graphique
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def on_symbol_selected(self, event):
        self.update_chart()

    def update_chart(self):
        symbol = self.symbol_var.get()
        if not symbol:
            return

        self.ax.clear()
        
        # Récupérer les données historiques
        historical_data = self.bot.get_historical_data(symbol)
        
        if historical_data is not None and not historical_data.empty:
            # Tracer le graphique des prix
            self.ax.plot(historical_data.index, historical_data['close'], label='Prix de clôture')
            
            # Ajouter les moyennes mobiles
            self.ax.plot(historical_data.index, historical_data['close'].rolling(window=20).mean(), label='MA20')
            self.ax.plot(historical_data.index, historical_data['close'].rolling(window=50).mean(), label='MA50')
            
            # Ajouter les indicateurs techniques (exemple avec RSI)
            rsi = self.calculate_rsi(historical_data['close'])
            ax2 = self.ax.twinx()
            ax2.plot(historical_data.index, rsi, color='orange', label='RSI')
            ax2.set_ylim(0, 100)
            ax2.set_ylabel('RSI')
            
            # Ajouter les positions ouvertes
            for position in self.bot.get_open_positions(symbol):
                self.ax.axhline(y=position['entry_price'], color='g', linestyle='--')
            
            self.ax.set_title(f"Graphique {symbol}")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Prix")
            self.ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            
            self.canvas.draw()

    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def update(self):
        self.update_chart()
