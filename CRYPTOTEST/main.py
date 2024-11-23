
import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox
from gui.main_window import MainWindow
from core.engine import TradingEngine
from utils.logging_config import setup_logging
from utils.security import APIKeyManager
from utils.password_manager import PasswordManager
from analysis.sentiment_analysis import SentimentAnalyzer
from analysis.parameter_optimizer import ParameterOptimizer
from strategies.sentiment_momentum_strategy import SentimentMomentumStrategy
from data.real_time_data_manager import RealTimeDataManager
import pandas as pd

async def main():
    # Setup logging
    logger = setup_logging()

    # Initialize API Key Manager and Password Manager
    api_key_manager = APIKeyManager()
    password_manager = PasswordManager()

    # Get API keys (in a real scenario, you would prompt the user for these)
    exchange = 'binance'
    api_key = 'your_api_key'
    secret_key = 'your_secret_key'
    
    # Prompt for password
    app = QApplication(sys.argv)
    password = password_manager.prompt_for_password()
    if password is None:
        logger.error("Password not provided. Exiting.")
        sys.exit(1)

    api_key_manager.store_api_keys(exchange, api_key, secret_key, password)
    keys = api_key_manager.get_api_keys(exchange, password)

    # Initialize the trading engine
    config = {
        'exchange': {'name': exchange, 'api_key': keys['api_key'], 'secret_key': keys['secret_key']},
        'initial_balance': 10000,
        'risk_params': {
            'max_position_size': 0.02,
            'stop_loss_pct': 0.03,
            'take_profit_pct': 0.06,
            'max_drawdown_pct': 0.2
        },
        'strategies': [
            {'name': 'SentimentMomentumStrategy', 'params': {
                'symbol': 'BTC/USDT',
                'timeframe': '1h',
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'rsi_period': 14,
                'sentiment_threshold': 0.2
            }}
        ],
        'update_interval': 1,  # seconds
        'strategy_interval': 5  # seconds
    }
    engine = TradingEngine(config)

    # Initialize Sentiment Analyzer
    sentiment_analyzer = SentimentAnalyzer()

    # Initialize RealTimeDataManager
    symbols = ['BTC/USDT', 'ETH/USDT']  # Add more symbols as needed
    data_manager = RealTimeDataManager(engine.exchange_handler, symbols)

    # Start the GUI
    main_window = MainWindow(engine, data_manager, sentiment_analyzer)
    main_window.show()

    # Add option to change password
    def change_password_action():
        new_password, message = password_manager.change_password()
        if new_password:
            # Update stored API keys with new password
            api_key_manager.store_api_keys(exchange, api_key, secret_key, new_password)
            QMessageBox.information(main_window, "Password Changed", message)
        else:
            QMessageBox.warning(main_window, "Password Change Failed", message)

    main_window.add_menu_action("Security", "Change Password", change_password_action)

    # Start the trading engine and data manager
    await asyncio.gather(
        engine.start(),
        data_manager.start()
    )

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    asyncio.run(main())
