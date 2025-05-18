import os
import time
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import telegram

load_dotenv()

# Setup Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Setup TradingView
tv = TvDatafeed(os.getenv("TV_USERNAME"), os.getenv("TV_PASSWORD"))

def send_telegram_signal(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def analyze_market(symbol='EURUSD', exchange='OANDA'):
    try:
        data_1m = tv.get_hist(symbol, exchange, interval=Interval.in_1_minute, n_bars=50)
        data_5m = tv.get_hist(symbol, exchange, interval=Interval.in_5_minute, n_bars=50)
        data_15m = tv.get_hist(symbol, exchange, interval=Interval.in_15_minute, n_bars=50)

        if data_1m is None or data_5m is None or data_15m is None:
            return None, None

        # Basic strategy: combine price action & support/resistance
        signal = None
        latest_close = data_1m['close'].iloc[-1]
        recent_high = data_15m['high'].max()
        recent_low = data_15m['low'].min()

        if latest_close >= recent_high:
            signal = "PUT"
        elif latest_close <= recent_low:
            signal = "CALL"
        else:
            last_two = data_1m['close'].iloc[-2:]
            if last_two.iloc[1] > last_two.iloc[0]:
                signal = "CALL"
            else:
                signal = "PUT"

        return signal, "1-5 min"
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def start_bot():
    while True:
        pair = "EURUSD"
        signal, duration = analyze_market(pair)
        if signal:
            message = f"Pocket Option Signal:\nPair: {pair}\nAction: {signal}\nDuration: {duration}"
            print(message)
            send_telegram_signal(message)
        time.sleep(60)

if __name__ == "__main__":
    start_bot()
