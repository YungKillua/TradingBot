import json
import time
import requests
from ordervalues import decrease_value
import tabulate


def get_current_price(market):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        'symbol': market
    }
    response = requests.get(url, params=params)
    data = response.json()
    #print(f"Preis {market}: {data['price']}")
    return float(data['price'])

def process_trades():
    
    filepath = 'counter.json'
    
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
                    decrease_value(filepath)
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
                    decrease_value(filepath)
                    write_message(text = f"Stop-Loss erreicht: {trade}")

            updated_trades.append(trade)

        # Ergebnisse speichern
        data["balance"] = round(balance, 2)
        data["trades"] = updated_trades
        with open("trade_data.json", "w") as file:
            json.dump(data, file, indent=4)
            
        return data

        print(f"Aktuelle Balance: {balance:.2f}")
    except FileNotFoundError:
        print("JSON-Datei nicht gefunden.")
    except Exception as e:
        print("Fehler:", e)
        
def write_message(text):
    file_path = 'message.txt'
    try:
        with open(file_path, 'a') as file:
            file.write(text)
            print(f"Message written to file: {text}")
    except Exception as e:
        print(f"Fehler beim Schreiben in die Datei: {e}")
        
def display_trades(trades):
    # Filtere nur offene Trades
    open_trades = [trade for trade in trades["trades"] if trade["open"]]

    # Wenn keine offenen Trades vorhanden sind, zeige eine entsprechende Nachricht an
    if not open_trades:
        print("Keine offenen Trades vorhanden.")
        print(f"\nAktuelle Balance: {round(trades['balance'], 2)} USD")
        return

    headers = ["ID", "Pair", "Type", "Entry", "Exit", "TP", "SL", "Qty", "PnL", "Open", "Processed", "Price"]
    table = []

    for trade in open_trades:
        market = trade['market'] + 'T'
        try:
            current_price = get_current_price(market)
        except Exception as e:
            current_price = "Error"  # Fehler beim Abrufen des Preises abfangen
            print(f"Fehler beim Abrufen des Preises für {market}: {e}")

        # Erstelle die Zeile für die Tabelle
        table.append([
            trade["trade_id"],
            trade["market"],
            trade["trade_type"],
            trade["entry_price"],
            trade.get("exit_price", "-"),  # Exit-Preis optional anzeigen
            trade["take_profit"],
            trade["stop_loss"],
            trade["quantity"],
            trade.get("pnl", "-"),  # PnL optional anzeigen
            trade["open"],
            trade["processed"],
            current_price
        ])

    # Tabelle drucken
    print(tabulate.tabulate(table, headers, tablefmt="grid"))
    print(f"\nAktuelle Balance: {round(trades['balance'], 2)} USD")

    
def main():

    while True:

        # Trades verarbeiten
        trades = process_trades()
        # Trades anzeigen
        print("\033c", end="")  # Terminal löschen
        print("Aktuelle Trades:")
        display_trades(trades)

        # Wartezeit vor der nächsten Iteration
        time.sleep(2)

if __name__ == "__main__":
    main()
