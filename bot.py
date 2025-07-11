import ccxt
import time
import pandas as pd
from datetime import datetime, timedelta, timezone
from analyse import compute_indicators, generate_signal
from utils import send_telegram_message, log_signal
from config import BINANCE_API_KEY, BINANCE_API_SECRET

# Initialisation de l'API Binance
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'options': {
        'adjustForTimeDifference': False,  # On gère manuellement
    }
})

# Fonction de synchronisation de l’horloge avec Binance
def get_time_offset():
    server_time = exchange.fetch_time()          # Heure serveur en ms
    local_time = int(time.time() * 1000)         # Heure locale en ms
    offset = server_time - local_time            # Décalage
    print(f"[SYNC] Décalage détecté : {offset} ms")
    return offset

time_offset = get_time_offset()

# Paires de cryptos à surveiller
symbols = ['BTC/USDC', 'SOL/USDC']

# Fonction de récupération des bougies
def fetch_ohlcv(symbol):
    # Resynchroniser l'heure à chaque appel
    server_time = exchange.fetch_time()
    local_time = int(time.time() * 1000)
    offset = server_time - local_time
    print(f"[{symbol}] Décalage ajusté : {offset} ms")

    since = (datetime.now(tz=timezone.utc) - timedelta(days=30)).timestamp() * 1000
    since += offset

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe='1h',
        since=int(since),
    )
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Boucle principale (exécution toutes les heures)
while True:
    for symbol in symbols:
        try:
            df = fetch_ohlcv(symbol)
            df = compute_indicators(df)
            signal, reason = generate_signal(df)
            if signal:
                message = f"[{datetime.now(tz=timezone.utc)}] Signal {signal} détecté sur {symbol} : {reason}"
                send_telegram_message(message)
                log_signal(symbol, signal, reason)
        except Exception as e:
            import traceback
            stacktrace = traceback.format_exc()
            print(f"Erreur sur {symbol} : {e}")
            send_telegram_message(f"⛔ Erreur sur {symbol} :\n{e}\n{stacktrace}")
    time.sleep(3600)
