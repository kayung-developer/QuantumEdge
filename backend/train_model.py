import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import pandas_ta as pta
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# --- DEFINITIVE FIX: Import the necessary converter and type ---
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

# ==============================================================================
# IMPORTANT: CONFIGURE YOUR MT5 CREDENTIALS HERE
# ==============================================================================
MT5_SERVER = "XMTrading-MT5 3"  # e.g., "XMGlobal-MT5-Demo"
MT5_LOGIN = 75394874  # Your MT5 account number
MT5_PASSWORD = "!0TzJpJd"  # Your MT5 main password

# ==============================================================================
# 1. DATA ACQUISITION
# ==============================================================================
def fetch_data(symbol="EURUSD", timeframe=mt5.TIMEFRAME_H1, num_bars=50000):
    """Fetches a large dataset from a pre-running MetaTrader 5 terminal."""
    print("--- Data Acquisition ---")
    print("Attempting to connect to a running MetaTrader 5 terminal...")

    if not mt5.initialize(login=MT5_LOGIN, server=MT5_SERVER, password=MT5_PASSWORD):
        print(f"MT5 initialize() failed, error code = {mt5.last_error()}")
        mt5.shutdown()
        return None

    account_info = mt5.account_info()
    if not account_info:
        print("Could not retrieve account info. Connection failed.")
        mt5.shutdown()
        return None

    print(f"MT5 connection successful to account {account_info.login} on {account_info.server}.")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("No data received.")
        return None

    print(f"Successfully fetched {len(rates)} bars for {symbol}.")

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df


# ==============================================================================
# 2. FEATURE ENGINEERING & 3. LABELING
# ==============================================================================
def create_features_and_labels(df: pd.DataFrame, look_forward: int = 5) -> pd.DataFrame:
    """Engineers features and creates the target label for prediction."""
    print("\n--- Feature Engineering & Labeling ---")

    df.ta.rsi(length=14, append=True, col_names=('feature_rsi',))
    df.ta.atr(length=14, append=True, col_names=('feature_atr',))
    df.ta.bbands(length=20, append=True)
    df.ta.macd(append=True)

    df['feature_bb_width'] = (df['BBU_20_2.0'] - df['BBL_20_2.0']) / df['BBM_20_2.0']
    df['feature_atr_norm'] = df['feature_atr'] / df['close']

    future_price = df['close'].shift(-look_forward)
    df['target'] = np.where(future_price > df['close'], 1, 0)

    feature_cols = [col for col in df.columns if 'feature_' in col or 'MACD_' in col]
    valid_feature_cols = [col for col in feature_cols if col in df.columns]
    final_cols = valid_feature_cols + ['target']

    processed_df = df[final_cols].dropna().reset_index(drop=True)
    print(f"Feature engineering complete. Dataset shape: {processed_df.shape}")
    return processed_df


# ==============================================================================
# MAIN TRAINING SCRIPT
# ==============================================================================
if __name__ == "__main__":

    raw_data = fetch_data()
    if raw_data is None:
        print("\nModel training aborted due to data fetching failure.")
        exit()

    processed_data = create_features_and_labels(raw_data)

    if processed_data.empty:
        print("\nProcessed data is empty after feature engineering. Cannot train model.")
        exit()

    X = processed_data.drop('target', axis=1)
    y = processed_data['target']

    print(f"\n--- Data Splitting ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples.")

    print("\n--- Data Preprocessing (Scaling) ---")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\n--- Model Training ---")
    model = lgb.LGBMClassifier(
        objective='binary', random_state=42, n_estimators=250,
        learning_rate=0.05, num_leaves=31, max_depth=-1, n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)

    print("\n--- Model Evaluation ---")
    preds = model.predict(X_test_scaled)
    print("\n--- Classification Report ---")
    print(classification_report(y_test, preds, target_names=['DOWN', 'UP']))
    print(f"Model Accuracy: {accuracy_score(y_test, preds):.4f}")

    print("\n--- Model Saving ---")
    os.makedirs("models", exist_ok=True)

    scaler_path = "models/scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to: {scaler_path}")

    # --- DEFINITIVE FIX: Model Conversion to ONNX ---
    # 1. Define the input type for the ONNX model. The name 'input' is conventional.
    num_features = X_train.shape[1]
    initial_type = [('input', FloatTensorType([None, num_features]))]

    # 2. Use the dedicated `convert_lightgbm` function from onnxmltools.
    # This is the correct way to convert LightGBM models.
    print("Converting LightGBM model to ONNX format...")
    onnx_model = onnxmltools.convert_lightgbm(
        model,
        initial_types=initial_type,
        target_opset=12  # A widely compatible opset version
    )

    # 3. Save the converted ONNX model to a file.
    onnx_path = "models/lgbm_signal_model.onnx"
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"ONNX model saved to: {onnx_path}")

    print("\n--- MODEL GENERATION COMPLETE ---")