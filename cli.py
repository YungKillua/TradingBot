from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from flask import Flask, request, jsonify
import threading
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from binance.enums import *
import json
import os

# Definiere mögliche Optionen
app = Flask(__name__)

with open('keys.json', 'r') as keys:
    keys = json.load(keys)
    binance_api_key = keys['binance_api_key']
    binance_secret_key = keys['binance_secret_key']
    alpaca_api_key = keys['alpaca_api_key']
    alpaca_secret_key = keys['alpaca_secret_key']
    #Debug
    #print(api_key)
    #print(secret_key)

# Verbinde mit dem Binance Testnet
client = Client(binance_api_key, binance_secret_key, testnet=True)


commands = ['Option 1', 'Option 2', 'Option 3', 'Exit']
completer = WordCompleter(commands, ignore_case=True)
received_data = None

status = {'Binance': False, 'Alpaca': False}
botstatus = None



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
        print('4. Modus setzen')
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
            print('E for ETH')
            print('S for SOL')
            print('M for MainMenu')
            user_input = prompt('Wähle eine Option: ', completer=completer)
            if user_input == 'A':
                connect_to_binance(guthabenabfrage = True)
                print('-----------------------------------')
            if user_input == 'F':
                get_futures_balance()
                print('-----------------------------------')
            elif user_input == "u" or 'U':
                connect_to_binance(guthabenabfrage = 'u')
                print('-----------------------------------')
            elif user_input == 'b' or 'B':
                connect_to_binance(guthabenabfrage = 'b')
                print('-----------------------------------')
            elif user_input == 'e' or 'E':
                connect_to_binance(guthabenabfrage = 'e')
                print('-----------------------------------')
            elif user_input == 's' or 'S':
                connect_to_binance(guthabenabfrage = 's')
                print('-----------------------------------')
            elif user_input == 'm' or 'M':
                print('-----------------------------------')
            
        elif user_input == '3':
            print('Change your Api-Keys')
            break
        elif user_input == '4':
            print('A for Alpaca')
            print('B for Binance')
            uin = input()
            if uin == 'a' or uin == 'A':
                set_status('Alpaca')
                refresh_status()
            elif uin == 'b' or uin == 'B':
                set_status('Binance')
                refresh_status()
            print(f'Modus auf {botstatus} gesetzt')
            print('-----------------------------------')
        elif user_input.lower() == 'exit':
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl, bitte erneut versuchen.")

def set_status(aktiv):
    global status
    for key in status:
        if key == aktiv:
            status[key] = True
        else:
            status[key] = False
    

def refresh_status():
    global botstatus

    for key, value in status.items():
        if value:
            botstatus = key
            

def change_apikeys():
        

        print('Input API-Key')
        api = input()
        print('Input Secret-Key')
        secret = input()

        if os.path.isfile('keys.json'):
            keys = json.load(keys)
        json = {
                "api_key": api,
                "secret_key": secret
               }
        

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



        # Rufe das Guthaben für BTC ab
    def btc_balance():
        btc_balance = client.get_asset_balance(asset='BTC')
        print(f"BTC Balance: {btc_balance['free']} BTC")
        return btc_balance
        
        # Rufe das Guthaben für USDT ab
    def usdt_balance():
        usdt_balance = client.get_asset_balance(asset='USDT')
        print(f"USDT Balance: {usdt_balance['free']} USDT")
        return usdt_balance

        # Rufe Solana Guthaben ab
    def sol_balance():
        sol_balance = client.get_asset_balance(asset='SOL')
        print(f"SOL Balance: {sol_balance['free']} SOL")
        return sol_balance

        #Rufe Ethereum Guthaben ab
    def eth_balance():
        eth_balance = client.get_asset_balance(asset='ETH')
        print(f"ETH Balance: {eth_balance['free']} ETH")
        return eth_balance

    if guthabenabfrage == True: 
        usdt_balance()
        btc_balance()

    if guthabenabfrage == ('u'):
        usdt_balance()
        
    if guthabenabfrage == 'e':
        eth_balance()

    if guthabenabfrage == 'b':
        btc_balance()
    
    if guthabenabfrage == 's':
        sol_balance()


    return connection

def get_futures_balance():
    # Rufe die Balance für das Futures-Konto ab
    try:
        futures_balance = client.futures_account_balance()
        for balance in futures_balance:
            print(f"Asset: {balance['asset']}, Balance: {balance['balance']}")
    except Exception as e:
        print(f"Fehler beim Abrufen des Futures-Guthabens: {e}")

def binance_open_long_position(coin, stoploss, price):
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        print(f'create buy order for {coin}')
        print('Berechne Order Details...')
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        risk_amount_usdt = usdt_balance * 0.05
        coin_amount = risk_amount_usdt / (price - stoploss)
        stoplossdistance = price - stoploss
        takeprofit = price + (stoplossdistance * 1.5)
        #Runde Zahlen
        roundcoin_amount = round(coin_amount, 1)
        takeprofit = round(takeprofit, 2)

        try:
            response = client.futures_create_order(symbol = coin, 
                                                   side = SIDE_BUY, 
                                                   type = FUTURE_ORDER_TYPE_STOP_MARKET,
                                                   stopPrice = price,
                                                   price = price,
                                                   quantity = roundcoin_amount,
                                                   timeInForce = TIME_IN_FORCE_GTC
            )
            print('Buy Order erfolgreich')
            print(response)
        except Exception as e:
            print('Fehler beim erstellen der Buy Order', str(e))

        try:
            response = client.futures_create_order(symbol = coin,
                                                   side = SIDE_SELL,
                                                   type = ORDER_TYPE_LIMIT,
                                                   quantity = roundcoin_amount,
                                                   price = takeprofit,
                                                   timeInForce = TIME_IN_FORCE_GTC
            )
            print('TakeProfit Order erfolgreich')
            print(response)
        except Exception as e:
            print('Fehler beim erstellen der TakeProfit Order', str(e))

        try:
            response = client.futures_create_order(symbol = coin,
                                                   side = SIDE_SELL,
                                                   type = FUTURE_ORDER_TYPE_STOP_MARKET,
                                                   quantity = roundcoin_amount,
                                                   stopPrice = stoploss
            )
            print('StopLoss Order erfolgreich')
            print(response)
        except Exception as e:
            print('Fehler beim erstellen der StopLoss Order', str(e))


def binance_open_short_position(coin, stoploss, price):
    connection = connect_to_binance(guthabenabfrage=False)
    if connection == True:
        print(f'create sell order for {coin}')
        print('Berechne Order Details...')
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        print(usdt_balance)
        risk_amount_usdt = usdt_balance * 0.05
        print(risk_amount_usdt)
        coin_amount = risk_amount_usdt / (stoploss - price)
        if coin_amount * price > usdt_balance:
            coin_amount = usdt_balance / price
        stoplossdistance = price - stoploss
        takeprofit = price - (stoplossdistance * 1.5)
        print(coin_amount)

        #Runde Zahlen
        roundcoin_amount = round(coin_amount, 1)
        takeprofit = round(takeprofit, 2)

        #Debugging
        print(coin)
        print(roundcoin_amount)
        print(takeprofit)
        print(stoploss)
        print(stoploss+10)

        try:
            response = client.futures_create_order(symbol = coin, 
                                                   side = SIDE_SELL, 
                                                   type = FUTURE_ORDER_TYPE_STOP_MARKET,
                                                   stopPrice = price,
                                                   price = price, 
                                                   quantity = roundcoin_amount,
                                                   timeInForce = TIME_IN_FORCE_GTC
            )
            print('Sell Order erfolgreich')
            print(response)

        except Exception as e:
            print('Fehler beim erstellen der Sell Order', str(e))

        try :
            response = client.futures_create_order(symbol = coin,
                                                   side = SIDE_BUY,
                                                   type = ORDER_TYPE_LIMIT,
                                                   quantity = roundcoin_amount,
                                                   price = takeprofit,
                                                   timeInForce = TIME_IN_FORCE_GTC
            )
            print('TakeProfit Order erfolgreich')
            print(response)
        except Exception as e:
            print('Fehler beim erstellen der TakeProfit Order', str(e))

        try:
            response = client.futures_create_order(symbol = coin, 
                                                   side = SIDE_BUY,
                                                   type = FUTURE_ORDER_TYPE_STOP_MARKET,
                                                   quantity = roundcoin_amount,
                                                   stopPrice = stoploss,
            )
            print('Sell Order erstellt', response)
        except Exception as e:
            print('Fehler beim Erstellen der OCO Buy Order', str(e))

def alpaca_open_long_position():
    return

def alpaca_open_short_position():
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
        #Binance
        if botstatus == 'binance' and alert == 'Buy Signal':
            binance_open_long_position(coin = chart, stoploss = ema200, price = price)
            
        if botstatus == 'binance' and alert == 'Sell Signal':
            binance_open_short_position(coin = chart, stoploss = ema200, price = price)
        #Alpaca
        if botstatus == 'alpaca' and alert == 'Buy Signal':
            alpaca_open_long_position()

        if botstatus == 'alpaca' and alert == 'Sell Signal':
            alpaca_open_short_position()
        
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
