
import pandas as pd
import ta

def compute_indicators(df):
    df['sma20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['sma50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    signal = None
    reasons = []

    if latest['rsi'] < 30 and latest['sma20'] > latest['sma50']:
        signal = "BUY"
        reasons.append("RSI bas + SMA20 > SMA50")
    elif latest['rsi'] > 70 and latest['macd'] < latest['macd_signal']:
        signal = "SELL"
        reasons.append("RSI haut + MACD décroise")

    if latest['volume'] > 1.5 * latest['volume_ma']:
        reasons.append("Volume élevé")

    return signal, ", ".join(reasons)
