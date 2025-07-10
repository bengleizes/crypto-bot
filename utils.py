import csv
import datetime
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur lors de l'envoi Telegram : {e}")

def log_signal(symbol, signal, reason):
    with open("alerts.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.datetime.now(), symbol, signal, reason])
