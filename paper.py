import json
import time

def add_trade(market, trade_type, entry_price, quantity, take_profit, stop_loss):
    try:
        with open("trade_data.json", "r") as file:
            data = json.load(file)

        # Eindeutige Trade-ID erstellen
        new_trade_id = max([trade["trade_id"] for trade in data["trades"]], default=0) + 1

        new_trade = {
            "trade_id": new_trade_id,
            "market": market,
            "trade_type": trade_type,
            "entry_price": entry_price,
            "quantity": quantity,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "processed": False,
            "open": True
        }
        data["trades"].append(new_trade)

        with open("trade_data.json", "w") as file:
            json.dump(data, file, indent=4)

        print(f"Neuer Trade hinzugefügt: {new_trade}")
    except FileNotFoundError:
        print("JSON-Datei nicht gefunden.")
    except Exception as e:
        print("Fehler:", e)

# Beispielaufruf
#add_trade("SOLUSD", "long", 186, 5, 190, 182)
#add_trade("LTCUSD", "short", 101, 8, 90, 105)
