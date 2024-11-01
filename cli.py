from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from flask import Flask, request
import threading
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Definiere mögliche Optionen
app = Flask(__name__)



# Deine API-Schlüssel vom Testnet
api_key = 'apikey'    #ApiKey
api_secret = 'secretkey' #Secret

# Verbinde mit dem Binance Testnet
client = Client(api_key, api_secret, testnet=True)


commands = ['Option 1', 'Option 2', 'Option 3', 'Exit']
completer = WordCompleter(commands, ignore_case=True)
received_data = None



def main():
    print("████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ████████╗")
    print("╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝")
    print("   ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗██████╔╝██║   ██║   ██║")   
    print("   ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██║")   
    print("   ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝   ██║")   
    print("   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   ")
    while True:
        # Eingabeaufforderung mit Autovervollständigung
        print('1. Run Bot')
        print('2. Change Api-Keys etc.')
        print('exit. Close Bot')
        print('')
        user_input = prompt('Wähle eine Option: ', completer=completer)
        
        if user_input == '1':
            start_bot()
    
            break
        elif user_input == '2':
            print("Du hast Option 2 gewählt.")
            break
        elif user_input == 'Option 3':
            print("Du hast Option 3 gewählt.")
            break
        elif user_input.lower() == 'exit':
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl, bitte erneut versuchen.")


def start_bot():
    print('Starting Bot')
    run_server_in_thread()

def connect_to_binance(guthabenabfrage):
    connection = False
    try:
        # Teste die Verbindung durch Abrufen der Kontoinformationen
        account = client.get_account()
    
        if account:
            print('Verbunden mit Testnet-Account')
            connection = True
            
        else:
            print('Konnte nicht verbinden')
            connection = False
        
    except BinanceAPIException as e:
        print(f"Binance API Fehler: {e}")
        connection = False
    except BinanceRequestException as e:
        print(f"Netzwerkfehler: {e}")
        connection = False
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        connection = False
    if guthabenabfrage == True:
        # Rufe das Guthaben für BTC ab
        btc_balance = client.get_asset_balance(asset='BTC')
        print(f"BTC Balance: {btc_balance['free']} BTC")

        # Rufe das Guthaben für USDT ab
        usdt_balance = client.get_asset_balance(asset='USDT')
        print(f"USDT Balance: {usdt_balance['free']} USDT")
    return connection

def create_buy_order():
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        return


def create_sell_order():
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        return 

def start_server():
    app.run(host='0.0.0.0', port=80)

def run_server_in_thread():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    return server_thread

def process_data():
    global received_data
    if received_data:
        print(f"Verarbeite Daten: {received_data}")
        
        # Hier kannst du mit den empfangenen Daten weiterarbeiten
    else:
        print("Keine Daten empfangen")

@app.route('/webhook', methods=['POST'])
def webhook():
    global received_data
    received_data = request.get_json()  # Hole JSON-Daten
    print(f"Empfangene Daten: {received_data}")
    process_data()  # Verarbeite die empfangenen Daten direkt nach dem Empfang
    return "Webhook received and data processed!", 200


if __name__ == "__main__":
    main()
