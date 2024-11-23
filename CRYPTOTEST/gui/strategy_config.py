
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox

class StrategyConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Strategy selection
        strategy_layout = QHBoxLayout()
        strategy_layout.addWidget(QLabel("Select Strategy:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Scalping", "Momentum", "Mean Reversion"])
        strategy_layout.addWidget(self.strategy_combo)
        layout.addLayout(strategy_layout)

        # Strategy parameters
        self.param_layout = QVBoxLayout()
        self.update_strategy_params()
        layout.addLayout(self.param_layout)

        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        self.setLayout(layout)

        # Connect strategy selection to parameter update
        self.strategy_combo.currentIndexChanged.connect(self.update_strategy_params)

    def update_strategy_params(self):
        # Clear existing parameter widgets
        for i in reversed(range(self.param_layout.count())): 
            self.param_layout.itemAt(i).widget().setParent(None)

        strategy = self.strategy_combo.currentText()
        if strategy == "Scalping":
            self.add_param("RSI Period", "14")
            self.add_param("RSI Overbought", "70")
            self.add_param("RSI Oversold", "30")
        elif strategy == "Momentum":
            self.add_param("MACD Fast Period", "12")
            self.add_param("MACD Slow Period", "26")
            self.add_param("MACD Signal Period", "9")
        elif strategy == "Mean Reversion":
            self.add_param("Bollinger Band Period", "20")
            self.add_param("Bollinger Band Std Dev", "2")

    def add_param(self, label, default_value):
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel(label))
        param_input = QLineEdit(default_value)
        param_layout.addWidget(param_input)
        self.param_layout.addLayout(param_layout)

    def save_config(self):
        # Implement saving the configuration
        strategy = self.strategy_combo.currentText()
        params = {}
        for i in range(self.param_layout.count()):
            item = self.param_layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                label = item.itemAt(0).widget().text()
                value = item.itemAt(1).widget().text()
                params[label] = value
        
        print(f"Saving configuration for {strategy}:")
        print(params)
        # Here you would typically save this to a config file or database
