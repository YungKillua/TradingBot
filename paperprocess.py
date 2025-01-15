import json
import time
import requests

message_file = 'message.txt'

def get_current_price(market):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        'symbol': market
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(f"Preis {market}: {data['price']}")
    return float(data['price'])

def process_trades():
    print('Checking open trades...')
    try:
        with open("trade_data.json", "r") as file:
            data = json.load(file)

        balance = data["balance"]
        updated_trades = []

        for trade in data["trades"]:
            if trade["open"]:  # Nur offene Trades prüfen
                symbol = trade['market'] + 'T'
                current_price = get_current_price(symbol)
                trade_type = trade["trade_type"]
                entry_price = trade["entry_price"]
                quantity = trade["quantity"]
                take_profit = trade["take_profit"]
                stop_loss = trade["stop_loss"]

                # Prüfen, ob der Trade geschlossen werden soll
                if (trade_type == "long" and current_price >= take_profit) or \
                   (trade_type == "short" and current_price <= take_profit):
                    # Take-Profit erreicht
                    pnl = (take_profit - entry_price) * quantity if trade_type == "long" else (entry_price - take_profit) * quantity
                    fee = entry_price * quantity * 0.001
                    balance += pnl - fee
                    trade["open"] = False
                    trade["processed"] = True
                    trade["exit_price"] = take_profit
                    trade["pnl"] = round(pnl - fee, 2)
                    print(f"Take-Profit erreicht: {trade}")
                    write_message(text = f"Take-Profit erreicht: {trade}")

                elif (trade_type == "long" and current_price <= stop_loss) or \
                     (trade_type == "short" and current_price >= stop_loss):
                    # Stop-Loss erreicht
                    pnl = (stop_loss - entry_price) * quantity if trade_type == "long" else (entry_price - stop_loss) * quantity
                    fee = entry_price * quantity * 0.001
                    balance += pnl - fee
                    trade["open"] = False
                    trade["processed"] = True
                    trade["exit_price"] = stop_loss
                    trade["pnl"] = round(pnl - fee, 2)
                    print(f"Stop-Loss erreicht: {trade}")
                    write_message(text = f"Stop-Loss erreicht: {trade}")

            updated_trades.append(trade)

        # Ergebnisse speichern
        data["balance"] = round(balance, 2)
        data["trades"] = updated_trades
        with open("trade_data.json", "w") as file:
            json.dump(data, file, indent=4)

        print(f"Aktuelle Balance: {balance:.2f}")
    except FileNotFoundError:
        print("JSON-Datei nicht gefunden.")
    except Exception as e:
        print("Fehler:", e)
        
def write_message(text):
    file_path = message_file
    try:
        with open(file_path, 'a') as file:
            file.write(text)
            print(f"Message written to file: {text}")
    except Exception as e:
        print(f"Fehler beim Schreiben in die Datei: {e}")

# Trades regelmäßig prüfen
while True:
    process_trades()
    time.sleep(2)

