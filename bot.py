from InquirerPy import inquirer
from termcolor import colored
from flask import Flask, request, jsonify
import threading
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from binance.enums import *
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, OrderClass
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.models import Order
import json, os, time, sys
import subprocess
from ordervalues import increase_value, reset_value, read_value, decrease_value
from telegram import Bot
import asyncio


# Definiere mögliche Optionen
app = Flask(__name__)

systemos = sys.platform
print(f'Os ist {systemos}')

#Load Keys
with open('keys.json', 'r') as keys:
    keys = json.load(keys)
    binance_api_key = keys['binance_api_key']
    binance_secret_key = keys['binance_secret_key']
    alpaca_api_key = keys['alpaca_api_key']
    alpaca_secret_key = keys['alpaca_secret_key']
    telegram_token = keys['telegram_bot_token']
    groupchat_id = keys['groupchat_id']
    #Debug
    #print(api_key)
    #print(secret_key)

#Load Config
with open('config.json', 'r') as config:
    config = json.load(config)
    botstatus = config['mode']
    strategy = config['strategy']

# Verbinde mit dem Binance Testnet
client = Client(binance_api_key, binance_secret_key, testnet=True)

#AlpacaClient Testnet
if alpaca_api_key != '':
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)

file_path = 'counter.json'

received_data = None


#Telegram Setup
tbot = Bot(token=telegram_token)

reset_value(file_path)



def main():
    print(colored("████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ████████╗", 'white'))
    print(colored("╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝", 'white'))
    print(colored("   ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗██████╔╝██║   ██║   ██║", 'white') )
    print(colored("   ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██║", 'green')) 
    print(colored("   ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝   ██║", 'green')) 
    print(colored("   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   ", 'green'))
    while True:
        
        
        # Hauptmenü anzeigen und Auswahl treffen
        choice = inquirer.select(
            message="Select Option:",
            choices=[
                "1. Run Bot",
                "2. Get Balance",
                "3. Config and Keys",
                "4. Switch Api Mode",
                "5. Change Strategy",
                "Exit"
            ],
        ).execute()

        # Auswahl abfragen und entsprechende Aktion ausführen
        if choice == "1. Run Bot":
            print('Starting Bot')
            run_server_in_thread()
        elif choice == "2. Get Balance":
            if botstatus == None:
                print('No Mode selected')
                coice = "4. Switch Api Mode"
            elif botstatus == 'Binance':
                connect_to_binance(guthabenabfrage = True)
            elif botstatus == 'Alpaca':
                get_alpaca_balance()
        elif choice == "3. Config and Keys":
            choice = inquirer.select(
                message = 'Select Option:',
                choices = [
                    '1. Show Config and Keys',
                    '2. Change Config',
                    '3. Change Api Keys'
                    ],
            ).execute()
            if choice == '1. Show Config and Keys':
                print(config, keys)
            elif choice == '2. Change Config':
                change_config()
            elif choice == '3. Change Api Keys':
                change_apikeys()
            choice = "3. Config and Keys"
        elif choice == "4. Switch Api Mode":
            choice = inquirer.select(
                message = 'Select Api:',
                choices = [
                    '1. Binance',
                    '2. Alpaca',
                    '3. ByBit'
                    ],
            ).execute()
            if choice == '1. Binance':
                set_status('Binance')
                #refresh_status()
                print(f'Api Mode changed to {botstatus}')
            elif choice == '2. Alpaca':
                set_status('Alpaca')
                #refresh_status()
                print(f'Api Mode changed to {botstatus}')
            elif choice == 'ByBit':
                set_status('ByBit')
                print(f'Api Mode changed to {botstatus}')
        elif choice == '5. Change Strategy':
            choice = inquirer.select(
                message = 'Select Strategy:',
                choices = [
                    '1. MACD',
                    '2. Placeholder',
                    '3. Placeholder'
                    ],
            ).execute()
            if choice == 'MACD':
                set_strategy('MACD')
            elif choice == '':
                break
        elif choice == "Exit":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Auswahl, bitte erneut versuchen.")
        print('---------------------------')

def set_status(mode):
    global config
    global botstatus
    
    config['mode'] = mode
    botstatus = mode
    with open('config.json', 'w') as newconfig:
        json.dump(config, newconfig, indent=4)
    
def set_strategy():
    return

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
def change_config():
    return

#Telegram Functions
async def send_message(chat_id, text):
    
    try:
        await tbot.send_message(chat_id=chat_id, text=text)
        print("Nachricht erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der Nachricht: {e}")

#Exchange/Broker Functions
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
        risk_amount_usdt = usdt_balance * 0.05
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
        '''print(coin)
        print(roundcoin_amount)
        print(takeprofit)
        print(stoploss)
        print(stoploss+10)'''

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

def get_alpaca_balance():
    account = trading_client.get_account()
    print(account.cash)
    print(account.crypto_status)
    asset = trading_client.get_open_position('ETHUSD')
    print(asset)
    print(asset.qty)

def alpaca_open_long_position(coin, stoploss, price):

    def refresh():
        account = trading_client.get_account()
        return account
    
    account = refresh()
    usd_balance = float(account.cash)
    usd_balance_4th = usd_balance/4
    risk_amount_usd = usd_balance_4th * 0.05
    coin_amount = risk_amount_usd / (price - stoploss)
    if coin_amount * price > usd_balance_4th:
        coin_amount = (usd_balance_4th - risk_amount_usd) / price
    
    stoploss_distance = price - stoploss
    takeprofit = price + (stoploss_distance * 1.5)

    limit = stoploss * (1 - 0.01)

    round_coin_amount = round(coin_amount, 0)
    takeprofit = round(takeprofit, 2)

    try:

        # Create a market buy order
        market_order_data = MarketOrderRequest(
            symbol=coin,
            qty=round_coin_amount,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        market_order = trading_client.submit_order(market_order_data)
        print(colored("Buy order successfully created", 'cyan'), market_order)

        # Wait for the buy order to fill
        time.sleep(2)  # Optional: add checks for actual order fill status here

        #Get Asset Balance
        asset = trading_client.get_open_position(coin)
        amount = asset.qty
        
        # Create a stop loss order
        stoploss_order_data = StopLimitOrderRequest(
            symbol=coin,
            qty=amount,
            side=OrderSide.SELL,
            stop_price=stoploss,
            limit_price=limit,
            time_in_force=TimeInForce.GTC
        )
        stoploss_order = trading_client.submit_order(stoploss_order_data)
        print(colored("Stop loss order successfully created", 'cyan'), stoploss_order)
        return takeprofit, True
    
    except Exception as e:
        print(colored("Error creating order on Alpaca:",'green'), str(e))
        return takeprofit, False
    

    

def alpaca_open_short_position(coin, stoploss, price):
    account = trading_client.get_account()
    usd_balance = float(account.cash)
    usd_balance_4th = usd_balance/4
    risk_amount_usd = usd_balance_4th * 0.05
    coin_amount = risk_amount_usd / (stoploss - price)
    if coin_amount * price > usd_balance_4th:
        coin_amount = (usd_balance_4th - risk_amount_usd) / price

    stoplossdistance = stoploss - price
    takeprofit = price - (stoplossdistance * 1.5)

    limit = stoploss * (1 - 0.01)

    round_coin_amount = round(coin_amount, 0)
    takeprofit = round(takeprofit, 2)

    try:
        # Create a market sell order
        market_order_data = MarketOrderRequest(
            symbol=coin,
            qty=round_coin_amount,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        market_order = trading_client.submit_order(market_order_data)
        print("Sell order successfully created", market_order)

        # Wait for the buy order to fill
        time.sleep(2)  # Optional: add checks for actual order fill status here


        # Create a stop loss order
        stoploss_order_data = StopLimitOrderRequest(
            symbol=coin,
            qty=round_coin_amount,
            side=OrderSide.BUY,
            stop_price=stoploss,
            limit_price=limit,
            time_in_force=TimeInForce.GTC
        )
        stoploss_order = trading_client.submit_order(stoploss_order_data)
        print("Stop loss order successfully created", stoploss_order)

    except Exception as e:
        print("Error creating order on Alpaca:", str(e))
    
def alpaca_check(coin):
    try:
        openorder = trading_client.get_open_position(coin)  
        amount = openorder.qty
        price = openorder.current_price
    
        try:
            takeprofit_order_data = MarketOrderRequest(
                symbol=coin,
                qty=amount,
                side=OrderSide.SELL,
                time_in_Force=TimeInForce.GTC
            )
            takeprofit_order = trading_client.submit_order(takeprofit_order_data)
        
            print(colored('TakeProfit Order erfolgreich', 'cyan'),takeprofit_order)
            decrease_value(file_path)
            asyncio.run(send_message(chat_id=groupchat_id, text =f'{coin} Price is up to {price}! Takeprofit triggered'))
            
        except Exception as e:
            print(colored('TakeProfit Order fehlgeschlagen', 'cyan'), str(e))
            
    except Exception as e:
        print('No open Position found')
        print('Waiting for next Signal...')
        
def bybit_open_long_position(coin, stoploss, price):
    return

#Flask Functions
def start_server():
    app.run(host='::', port=80)

def run_server_in_thread():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    return server_thread

def create_subprocess(order, tp, order_type):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #python_executable = sys.executable
    script = "check_order.py"
    var1 = botstatus
    var2 = order 
    var3 = tp
    var4 = order_type

    
    if systemos == 'win32':
        subprocess.Popen(f'start powershell -NoExit -Command "python {os.path.join(script_dir, script)} {var1} {var2} {var3} {var4}"', shell=True)
    elif systemos == 'linux':
        venv_path = os.path.join(script_dir, "BotEnv")
        command = f"source {os.path.join(venv_path, 'bin', 'activate')} && python3 {os.path.join(script_dir, script)} {var1} {var2} {var3} {var4}"

        subprocess.Popen(
            f'lxterminal -t "Order Monitor" -e bash -c "{command}; exec bash"', 
            shell=True
            )
    elif systemos == 'darwin':
        script = os.path.abspath('check_order.py')
        command = f'python3 {script} {var1} {var2} {var3} {var4}'
        apple_script = f'tell application "Terminal" to do script "{command}"'
        subprocess.Popen(["osascript", "-e", apple_script], shell=False)

def process_data():
    global received_data
    if received_data:
        print(f"Verarbeite Daten: {received_data}")
        chart = received_data.get('chart')
        alert = received_data.get('alert')
        price = float(received_data.get('price'))
        ema200 = float(received_data.get('ema200'))
        
        orders = read_value(file_path)
        if orders < 4 :
        
            #Binance
            if botstatus == 'binance' and alert == 'Buy Signal':
                binance_open_long_position(coin = chart, stoploss = ema200, price = price)
            
            if botstatus == 'binance' and alert == 'Sell Signal':
                binance_open_short_position(coin = chart, stoploss = ema200, price = price)
            #Alpaca
            if botstatus == 'Alpaca' and alert == 'Buy Signal':
                long = alpaca_open_long_position(coin = chart, stoploss = ema200, price = price)
                takeprofit = long[0]
                sucess = long[1]
                if sucess == True:
                    #create_subprocess(order = chart, tp = takeprofit, order_type = 'Long')
                    increase_value(file_path)
                    asyncio.run(send_message(chat_id=groupchat_id, text = f'Opening Trade on {chart} at {price}$. Stoploss set at {ema200}. Takeprofit set at {takeprofit}.'))
                else:
                    print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
            if botstatus == 'Alpaca' and alert == 'Sell Signal':
                #alpaca_open_short_position(coin = chart, stoploss = ema200, price = price)
                alpaca_check(coin = chart)
                
        else:
            print(colored('Order wird nicht erstellt, da schon 4 Positionen offen sind', 'light_red'))
            
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
