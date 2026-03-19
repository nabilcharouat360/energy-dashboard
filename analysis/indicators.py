"""
Technical-analysis indicator wrappers built on top of the `ta` library.

Every public function accepts a DataFrame with OHLCV columns and returns
the same DataFrame augmented with indicator columns.
"""
import pandas as pd
import ta


# ───────────────────────────── Trend ─────────────────────────────

def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    col = f"SMA_{window}"
    df[col] = ta.trend.sma_indicator(df["Close"], window=window)
    return df


def add_ema(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    col = f"EMA_{window}"
    df[col] = ta.trend.ema_indicator(df["Close"], window=window)
    return df


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"] = macd.macd_diff()
    return df


def add_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    ichi = ta.trend.IchimokuIndicator(df["High"], df["Low"])
    df["Ichimoku_A"] = ichi.ichimoku_a()
    df["Ichimoku_B"] = ichi.ichimoku_b()
    df["Ichimoku_Base"] = ichi.ichimoku_base_line()
    df["Ichimoku_Conv"] = ichi.ichimoku_conversion_line()
    return df


# ──────────────────────────── Momentum ───────────────────────────

def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    df["RSI"] = ta.momentum.rsi(df["Close"], window=window)
    return df


def add_stochastic(df: pd.DataFrame) -> pd.DataFrame:
    stoch = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"])
    df["Stoch_K"] = stoch.stoch()
    df["Stoch_D"] = stoch.stoch_signal()
    return df


def add_williams_r(df: pd.DataFrame) -> pd.DataFrame:
    df["Williams_R"] = ta.momentum.williams_r(df["High"], df["Low"], df["Close"])
    return df


# ──────────────────────────── Volatility ─────────────────────────

def add_bollinger_bands(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    bb = ta.volatility.BollingerBands(df["Close"], window=window)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Middle"] = bb.bollinger_mavg()
    df["BB_Lower"] = bb.bollinger_lband()
    return df


def add_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    df["ATR"] = ta.volatility.average_true_range(
        df["High"], df["Low"], df["Close"], window=window
    )
    return df


# ──────────────────────────── Volume ─────────────────────────────

def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    df["OBV"] = ta.volume.on_balance_volume(df["Close"], df["Volume"])
    return df


# ──────────────────────────── Dispatcher ─────────────────────────

# Maps indicator keys (from config.py) to functions.
INDICATOR_DISPATCH = {
    "sma_20": lambda df: add_sma(df, 20),
    "sma_50": lambda df: add_sma(df, 50),
    "ema_20": lambda df: add_ema(df, 20),
    "ema_50": lambda df: add_ema(df, 50),
    "bbands": add_bollinger_bands,
    "ichimoku": add_ichimoku,
    "rsi": add_rsi,
    "macd": add_macd,
    "stoch": add_stochastic,
    "willr": add_williams_r,
    "atr": add_atr,
    "obv": add_obv,
}


def apply_indicators(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Apply a list of indicator keys to *df* (in-place) and return it."""
    df = df.copy()
    for key in keys:
        fn = INDICATOR_DISPATCH.get(key)
        if fn:
            df = fn(df)
    return df
