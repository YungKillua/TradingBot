from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from flask import Flask, request, jsonify
import threading
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Definiere mögliche Optionen
app = Flask(__name__)



# Deine API-Schlüssel vom Testnet
api_key = 'BibAXBReE7i0i6D9Mbahtztl58HTEZtBCgWhZwoVntopKuDOVF6F9Z3diy3jsfjW'    #ApiKey
api_secret = 'uhNe1bOe640SNtkhfAt4RTvwfkK4z46cfPReq785Vlr0nX9SpF51vnJh7gDEKACE' #Secret

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
        print('2. Get Binance Balance')
        print('3. Change Api-Keys etc.')
        print('exit. Close Bot')
        print('')
        user_input = prompt('Wähle eine Option: ', completer=completer)
        
        if user_input == '1':
            start_bot()
    
            break
        elif user_input == '2':
            print("A for all Balance")
            print('U for USD')
            print('B for BTC')
            print('M for MainMenu')
            user_input = prompt('Wähle eine Option: ', completer=completer)
            if user_input == 'A':
                connect_to_binance(guthabenabfrage = True)
                print('-----------------------------------')
            elif user_input == "U":
                break
            elif user_input == 'M':
                print('-----------------------------------')
            
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

        # Rufe Solana Guthaben ab
        sol_balance = client.get_asset_balance(asset='SOL')
        print(f"SOL Balance: {sol_balance['free']} SOL")

        #Rufe Ethereum Guthaben ab
        eth_balance = client.get_asset_balance(asset='ETH')
        print(f"ETH Balance: {eth_balance['free']} ETH")


    return connection

def create_buy_order(coin, stoploss, price):
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        print(f'create buy order for {coin}')
        print('Berechne Order Details...')
        usdt_balance = client.get_asset_balance(asset='USDT')
        risk_amount_usdt = usdt_balance * 0.05
        coin_amount = risk_amount_usdt / (price - stoploss)
        stoplossdistance = price - stoploss
        takeprofit = price + (stoplossdistance * 1.5)
        try:
            response = client.order_oco_buy(symbol = coin, 
                                            quantity = coin_amount, 
                                            price = takeprofit, 
                                            stopPrice = stoploss, 
                                            stopLimitPrice = stoploss+10, 
                                            stopLimitTimeInForce='GTC'
                                            )
            print('Buy Order erstellt', response)
        except Exception as e:
            print('Fehler beim Erstellen der Buy Order', str(e))
        return


def create_sell_order(coin, stoploss, price):
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        print(f'create sell order for {coin}')
        print('Berechne Order Details...')
        usdt_balance = client.get_asset_balance(asset='USDT')
        risk_amount_usdt = usdt_balance * 0.05
        coin_amount = risk_amount_usdt / (stoploss - price)
        stoplossdistance = price - stoploss
        takeprofit = price - (stoplossdistance * 1.5)
        try:
            response = client.order_oco_sell(symbol = coin, 
                                             quantity = coin_amount, 
                                             price = takeprofit,
                                             stopPrice = stoploss, 
                                             stopLimitPrice = stoploss-10, 
                                             stopLimitTimeInForce='GTC'
                                             )
            print('Sell Order erstellt', response)
        except Exception as e:
            print('Fehler beim Erstellen der Sell Order', str(e))
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
        chart = received_data.get('chart')
        alert = received_data.get('alert')
        price = received_data.get('price')
        ema200 = received_data.get('ema200')

        if alert == 'Buy Signal':
            create_buy_order(coin = chart, stoploss = ema200, price = price)
            
        if alert == 'Sell Signal':
            create_sell_order(coin = chart, stoploss = ema200, price = price)
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
