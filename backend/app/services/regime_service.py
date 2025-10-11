"""
AuraQuant - Real-Time Market Regime Detection Service (Corrected)
"""
import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, Optional
from pathlib import Path

# Use Pathlib for robust, OS-agnostic path construction
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "regime_models"

class RegimeDetectionService:
    def __init__(self):
        self._models: Dict[str, any] = {}
        # The service no longer loads models automatically upon initialization.

    def load_all_models(self):
        """
        Loads all trained .pkl models from the model directory.
        This method should be called once at application startup.
        """
        # Ensure the directory exists to prevent the warning.
        if not os.path.exists(MODEL_DIR):
            print(f"INFO: Regime model directory '{MODEL_DIR}' not found. Creating it.")
            os.makedirs(MODEL_DIR)

        print(f"Searching for regime models in: {MODEL_DIR}")
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith(".pkl"):
                symbol = filename.split('_')[0].upper().replace('-', '')
                model_path = os.path.join(MODEL_DIR, filename)
                try:
                    self._models[symbol] = joblib.load(model_path)
                    print(f"Loaded regime model for {symbol} from {model_path}")
                except Exception as e:
                    print(f"ERROR: Failed to load regime model {filename}: {e}")

    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates features from a historical dataframe for training or bulk prediction."""
        df_copy = df.copy()
        df_copy['returns'] = df_copy['Close'].pct_change()
        df_copy['volatility'] = df_copy['returns'].rolling(window=21).std() * np.sqrt(365) # Annualized for daily
        return df_copy[['returns', 'volatility']].fillna(0)

    def predict_current_regime(self, symbol: str, historical_data: pd.DataFrame) -> Optional[int]:
        # ... (this method remains the same)
        model = self._models.get(symbol.upper())
        if not model or len(historical_data) < 22:
            return None
        features = self._calculate_features(historical_data.rename(columns={"close": "Close"})).tail(1)
        if features.empty: return None
        return int(model.predict(features)[0])

regime_service = RegimeDetectionService()