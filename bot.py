from InquirerPy import inquirer
from termcolor import colored
from flask import Flask, request, jsonify
import threading
import ccxt
from binance.client import Client as binance_client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from binance.enums import *
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, OrderClass
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.models import Order
from pybitget import Client as bitget_client
import json, os, time, sys
import subprocess
from ordervalues import increase_value, reset_value, read_value, decrease_value
from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
from paper import add_trade, get_paper_balance


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
    bitget_api_key = keys['bitget_api_key']
    bitget_secret_key = keys['bitget_secret_key']
    bitget_passphrase = keys['bitget_passphrase']
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
client = binance_client(binance_api_key, binance_secret_key, testnet=True)

#AlpacaClient Testnet
if alpaca_api_key != '':
    alpaca_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
#Bitget 

if bitget_api_key != '':
    bitget = ccxt.bitget({
        'apiKey': bitget_api_key,
        'secret': bitget_secret_key,
        'password': bitget_passphrase,  # Passphrase ist bei Bitget erforderlich
    })

file_path = 'counter.json'
message_file = 'message.txt'

received_data = None


#Telegram Setup

# HTTPXRequest konfigurieren (Timeouts und Poolgröße anpassen)
hx_request = HTTPXRequest(
    connect_timeout=10,  # Timeout für Verbindungsaufbau
    read_timeout=20,    # Timeout für Antwort vom Telegram-Server
    pool_timeout=40    # Zeit, auf einen freien Pool zu warten
)

tbot = Bot(token=telegram_token, request=hx_request)

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
            else:
                get_futures_balance()
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
                    '3. Bitget',
                    '4. Papertrading'
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
            elif choice == '3. Bitget':
                set_status('Bitget')
                print(f'Api Mode changed to {botstatus}')
            elif choice == '4. Papertrading':
                set_status('Papertrading')
                print(f'Api Mode changed to {botstatus}')
        elif choice == '5. Change Strategy':
            choice = inquirer.select(
                message = 'Select Strategy:',
                choices = [
                    '1. MACD',
                    '2. PDHL',
                    '3. GCDA',
                    '4. BBA',
                    '5. BBW'
                    ],
            ).execute()
            if choice == '1. MACD':
                set_strategy('MACD')
                print(f'Strategy changed to {strategy}')
            elif choice == '2. PDHL':
                set_strategy('PDHL')
                print(f'Strategy changed to {strategy}')
            elif choice == '3. GCDA':
                set_strategy('GCDA')
                print(f'Strategy changed to {strategy}')
            elif choice == '4. BBA':
                set_strategy('BBA')
                print(f'Strategy changed to {strategy}')
            elif choice == '5. BBW':
                set_strategy('BBW')
                print(f'Strategy changed to {strategy}')
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
    
def set_strategy(strat):
    global config
    global strategy
    
    config['strategy'] = strat
    strategy = strat
    with open('config.json', 'w') as newconfig:
        json.dump(config, newconfig, indent=4)


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
    MAX_RETRIES = 3
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            await tbot.send_message(chat_id=chat_id, text=text)
            print("Nachricht erfolgreich gesendet!")
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Nachricht: {e}")
            retry_count += 1
            await asyncio.sleep(5)

    print("Maximale Wiederholungen erreicht. Nachricht konnte nicht gesendet werden.")
    return False

def write_message(text):
    file_path = message_file
    try:
        with open(file_path, 'a') as file:
            file.write(text)
            print(f"Message written to file: {text}")
    except Exception as e:
        print(f"Fehler beim Schreiben in die Datei: {e}")
        
def clear_message():
    file_path = message_file
    
    try:
        # Datei bereinigen
        with open(file_path, 'w') as file:
                    file.truncate(0)  # Datei leeren
    except Exception as e:
        print(f"Fehler beim Bereinigen der Datei: {e}")

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
    if botstatus == 'Bitget':
        try:
            balance = bitget.fetch_balance({'type': 'future'})
            print(colored(f'Futures Balance on Bitget is {balance} ', 'green'))
        except Exception as e:
            print("Fehler bei der Anfrage:", e)
        
    elif botstatus == 'Binance':
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
    account = alpaca_client.get_account()
    print(account.cash)
    print(account.crypto_status)
    asset = alpaca_client.get_open_position('ETHUSD')
    print(asset)
    print(asset.qty)

def alpaca_open_long_position(coin, stoploss, price):

    ordervalue = read_value(file_path)
    risk_factor = 4
    if ordervalue == '1':
        risk_factor = 3
    elif ordervalue == '2':
        risk_factor = 2
    elif ordervalue == '3':
        risk_factor = 1
    
    if stoploss == None:
        stoploss = 0
    
    def refresh():
        account = alpaca_client.get_account()
        return account
    
    account = refresh()
    usd_balance = float(account.cash)
    usd_balance_4th = usd_balance/risk_factor
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
        market_order = alpaca_client.submit_order(market_order_data)
        print(colored("Buy order successfully created", 'cyan'), market_order)

        # Wait for the buy order to fill
        time.sleep(2)  # Optional: add checks for actual order fill status here

        #Get Asset Balance
        asset = alpaca_client.get_open_position(coin)
        amount = asset.qty
        
        if stoploss != 0:
            # Create a stop loss order
            stoploss_order_data = StopLimitOrderRequest(
                symbol=coin,
                qty=amount,
                side=OrderSide.SELL,
                stop_price=stoploss,
                limit_price=limit,
                time_in_force=TimeInForce.GTC
            )
            stoploss_order = alpaca_client.submit_order(stoploss_order_data)
            print(colored("Stop loss order successfully created", 'cyan'), stoploss_order)
            
        return takeprofit, True
    
    except Exception as e:
        print(colored("Error creating order on Alpaca:",'green'), str(e))
        return takeprofit, False
    

    

def alpaca_open_short_position(coin, stoploss, price):
    account = alpaca_client.get_account()
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
        market_order = alpaca_client.submit_order(market_order_data)
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
        stoploss_order = alpaca_client.submit_order(stoploss_order_data)
        print("Stop loss order successfully created", stoploss_order)

    except Exception as e:
        print("Error creating order on Alpaca:", str(e))
    
def alpaca_check(coin):
    try:
        openorder = alpaca_client.get_open_position(coin)  
        amount = openorder.qty
        price = openorder.current_price
        prozent = float(openorder.unrealized_plpc) * 100
    
        try:
            takeprofit_order_data = MarketOrderRequest(
                symbol=coin,
                qty=amount,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC
            )
            takeprofit_order = alpaca_client.submit_order(takeprofit_order_data)
        
            print(colored('TakeProfit Order erfolgreich', 'cyan'),takeprofit_order)
            decrease_value(file_path)
            if prozent > 0:
                write_message(text =f'{coin} Price is up to {price}! Percentage is {prozent:.2f}%')
            if prozent < 0:
                write_message(text =f'{coin} Price is down to {price}! Percentage is {prozent:.2f}%')
            
        except Exception as e:
            print(colored('TakeProfit Order fehlgeschlagen', 'cyan'), str(e))
            
    except Exception as e:
        print('No open Position found')
        print('Waiting for next Signal...')
        
def get_orders():
    pos = alpaca_client.get_all_positions()
    poslen = len(pos)
    return poslen
        
def bitget_open_long_position(coin, stoploss, price):
    return
def bitget_open_short_position(coin, stoploss, price):
    return

def calc_coin_amount(type, price, stoploss):

    balance = get_paper_balance()
    risk_amount_usd = balance * 0.05

    if type == "long":
        coin_amount = risk_amount_usd / (price - stoploss)
    elif type == "short":
        coin_amount = risk_amount_usd / (stoploss - price)

    # Sicherstellen, dass coin_amount das Risikokapital nicht überschreitet
    if coin_amount * price > balance:
        coin_amount = (balance - risk_amount_usd) / price

    return coin_amount

    

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
        
        orders = read_value(file_path)
        if orders < 4 :
        
            #BUY
            if all([alert == "Buy Signal",
                    botstatus == "Alpaca",
                    strategy == "MACD"
                    ]): 
                        ema200 = float(received_data.get('ema200'))
                        long = alpaca_open_long_position(coin = chart, stoploss = ema200, price = price)
                        takeprofit = long[0]
                        sucess = long[1]
                        if sucess == True:
                            #create_subprocess(order = chart, tp = takeprofit, order_type = 'Long')
                            increase_value(file_path)
                            asyncio.run(send_message(chat_id=groupchat_id, text = f'Opening Trade on {chart} at {price}$. Stoploss set at {ema200}. Takeprofit set at {takeprofit}.'))
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
            
            if all([alert == "Buy Signal",
                    botstatus == "Alpaca",
                    strategy == "PDHL"
                    ]):
                        sl = float(received_data.get('sl'))
                        tp = float(received_data.get('tp'))
                        long = alpaca_open_long_position(coin = chart, price = price, stoploss = sl)
                        sucess = long[1]
                        if sucess == True:
                            create_subprocess(order = chart, tp = tp, order_type = 'Long')
                            increase_value(file_path)
                            asyncio.run(send_message(chat_id=groupchat_id, text = f'Opening Trade on {chart} at {price}$. Stoploss set at {sl}. Takeprofit set at {tp}.'))
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
            
            if all([alert == "Buy Signal",
                    botstatus == "Alpaca",
                    strategy == "GCDA"
                    ]):
                        long = alpaca_open_long_position(coin = chart, price = price, stoploss = None)
                        sucess = long[1]
                        if sucess == True:
                            increase_value(file_path)
                            asyncio.run(send_message(chat_id=groupchat_id, text = f'Opening Trade on {chart} at {price}$.'))
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
                            
                        
            if all([alert == "Buy Signal",
                    botstatus == "Alpaca",
                    strategy == "BBA"
                    ]):
                        long = alpaca_open_long_position(coin = chart, price = price, stoploss = None)
                        sucess = long[1]
                        if sucess == True:
                            increase_value(file_path)
                            write_message(text=f'Opening Trade on {chart} at {price}$.')
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
 
            if all([alert == "Buy Signal",
                    botstatus == "Alpaca",
                    strategy == "BBW"
                    ]):
                        long = alpaca_open_long_position(coin = chart, price = price, stoploss = None)
                        sucess = long[1]
                        if sucess == True:
                            increase_value(file_path)
                            write_message(text=f'Opening Trade on {chart} at {price}$.')
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
                            
            if all([alert == "Buy Signal",
                    botstatus == "Papertrading",
                    strategy == "BBW"
                    ]):
                        sl = float(received_data.get('sl'))
                        tp = float(received_data.get('tp'))
                        qty = calc_coin_amount(type = 'long', price = price, stoploss = sl)
                        long = add_trade(market = chart, trade_type = 'long', entry_price = price, quantity = qty, take_profit = tp, stop_loss = sl)
                        if long == True:
                            increase_value(file_path)
                            write_message(text=f'Opening Trade on {chart} at {price}$.')
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
                        
            if all([alert == "Sell Signal",
                    botstatus == "Papertrading",
                    strategy == "BBW"
                    ]):
                        sl = float(received_data.get('sl'))
                        tp = float(received_data.get('tp'))
                        qty = calc_coin_amount(type = 'short',price = price, stoploss = sl)
                        short = add_trade(market = chart, trade_type = 'short', entry_price = price, quantity = qty, take_profit = tp, stop_loss = sl)
                        if short == True:
                            increase_value(file_path)
                            write_message(text=f'Opening Trade on {chart} at {price}$.')
                        else:
                            print(colored('Order konnte nicht erstellt werden, warte auf weitere Signale', 'light_red'))
            
            if all([alert == "Sell Signal",
                    botstatus == "Alpaca",
                    strategy == "MACD"
                    ]):
                        #short = alpaca_open_short_position()
                        print('Short Funktion nicht aktiv')
                        
        else:       
            print(colored('Order wird nicht erstellt, da schon 4 Positionen offen sind', 'light_red'))
            
        if all([alert == "Close Signal",
                    botstatus == "Alpaca",
                    strategy == "BBA"
                    ]):
                        alpaca_check(coin = chart)
                        
        if all([alert == "Close Signal",
                    botstatus == "Alpaca",
                    strategy == "BBW"
                    ]):
                        alpaca_check(coin = chart)                
                        
        if all([alert == "Close Signal",
                    botstatus == "Alpaca",
                    strategy == "GCDA"
                    ]):
                        alpaca_check(coin = chart)
        
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
