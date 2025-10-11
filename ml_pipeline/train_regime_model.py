"""
MLOps: Market Regime Detection Model Training
"""
import pandas as pd
import numpy as np
import joblib
import os
from hmmlearn import hmm
import yfinance as yf  # Using yfinance to get a large dataset for training

# --- Configuration ---
MODEL_OUTPUT_DIR = "regime_models"
MODEL_FILENAME_TEMPLATE = "{symbol}_regime_model.pkl"
N_REGIMES = 4  # e.g., Low Volatility Bull, High Volatility Bull, Low Volatility Bear, High Volatility Bear


def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the features the HMM will be trained on."""
    df['returns'] = df['Close'].pct_change().fillna(0)
    # Volatility as the rolling standard deviation of returns
    df['volatility'] = df['returns'].rolling(window=21).std().fillna(0) * np.sqrt(252)  # Annualized
    df.dropna(inplace=True)
    return df[['returns', 'volatility']]


def train_regime_model(symbol: str, start_date: str, end_date: str):
    """
    Fetches data, calculates features, and trains a Hidden Markov Model.
    """
    print(f"Training regime model for {symbol}...")

    # 1. Fetch a large dataset for training
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        print(f"Could not download data for {symbol}.")
        return

    # 2. Engineer features
    features = calculate_features(data)

    # 3. Train the HMM
    # The HMM will learn the hidden states (regimes) based on the observable
    # features (returns and volatility).
    model = hmm.GaussianHMM(
        n_components=N_REGIMES,
        covariance_type="full",
        n_iter=1000,
        random_state=42
    )
    model.fit(features)

    # 4. Save the trained model
    if not os.path.exists(MODEL_OUTPUT_DIR):
        os.makedirs(MODEL_OUTPUT_DIR)

    model_path = os.path.join(MODEL_OUTPUT_DIR, MODEL_FILENAME_TEMPLATE.format(symbol=symbol))
    joblib.dump(model, model_path)

    print(f"Regime model for {symbol} trained and saved to {model_path}.")

    # Optional: Analyze the learned regimes
    print("\n--- Learned Regime Characteristics ---")
    for i in range(model.n_components):
        mean_return = model.means_[i, 0] * 252  # Annualized return
        mean_volatility = model.means_[i, 1]
        print(f"Regime {i}: Avg Annual Return = {mean_return:.2%}, Avg Volatility = {mean_volatility:.2%}")


if __name__ == "__main__":
    # This will train and save a model for BTC-USD
    train_regime_model(symbol="BTC-USD", start_date="2018-01-01", end_date="2023-12-31")