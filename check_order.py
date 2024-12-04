from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce
from binance.client import Client
import sys, time, json
from termcolor import colored
from ordervalues import decrease_value
from telegram import Bot
import asyncio
from bot import send_message


with open('keys.json', 'r') as keys:
    keys = json.load(keys)
    binance_api_key = keys['binance_api_key']
    binance_secret_key = keys['binance_secret_key']
    alpaca_api_key = keys['alpaca_api_key']
    alpaca_secret_key = keys['alpaca_secret_key']
    telegram_token = keys['telegram_bot_token']
    groupchat_id = keys['groupchat_id']

# Verbinde mit dem Binance Testnet
bclient = Client(binance_api_key, binance_secret_key, testnet=True)

#Telegram Setup
tbot = Bot(token=telegram_token)

#AlpacaClient Testnet
if alpaca_api_key != '':
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
# No keys required for crypto data
aclient = CryptoHistoricalDataClient()

file_path = "counter.json"
    
print(colored('Order Monitor', 'light_magenta'))
    
#Check Vars
if len(sys.argv) > 1:
    var1 = sys.argv[1]
    #print(var1)
    botstatus = var1

if len(sys.argv) > 2:
    time.sleep(10)
    var2 = sys.argv[2]
    #print(var2)
    coin = var2
    
if len(sys.argv) > 3:
    var3 = sys.argv[3]
    #print(var3)
    tp = var3
    
if len(sys.argv) > 4:
    var4 = sys.argv[4]
    #print(var4)
    order_type = var4

else:
    print("Argument fehlt.")


print('Variablen erfolgreich uebergeben')
print(f'Botstatus auf {botstatus}')
print(f'Coin ist {coin}')
print(f'TakeProfit ist {tp}')
print(f'Order Type ist {order_type}')
    
def check_price_alpaca(coin, tp, order_type):
    
    while True:
        
        try:
            openorder = trading_client.get_open_position(coin)
            # Creating request object
            request_params = CryptoLatestQuoteRequest(
            symbol_or_symbols=f'{coin[:3]}/USD'
            )
            # Fetch the latest bar (price data)
            latest_quote = aclient.get_crypto_latest_quote(request_params)

            # must use symbol to access even though it is single symbol
            askprice = latest_quote[f'{coin[:3]}/USD'].ask_price
            bidprice = latest_quote[f'{coin[:3]}/USD'].bid_price
            print(f'Askprice is at {askprice}')
        except Exception as e:
            print('Position not longer open', str(e))
            decrease_value( file_path)
            print(colored('StopLoss wurde getriggert', 'light_red'))
            asyncio.run(send_message(chat_id=groupchat_id, text = f'{coin} Price is down to {askprice}! Stoploss triggered'))
            input("Drücke eine Taste, um das Fenster zu schließen...")

        #Get Asset Balance
        asset = trading_client.get_open_position(coin)
        amount = asset.qty
        
        tp = float(tp)
        
        if order_type == 'Long':
            if askprice >= tp:
                close_alpaca(coin = coin, qty = amount)
                decrease_value(file_path)
                print(colored('Trade erfolgreich', 'light_green'))
                asyncio.run(send_message(chat_id=groupchat_id, text =f'{coin} Price is up to {tp}! Takeprofit triggered'))
                break
        elif order_type == 'Short':
            if askprice <= tp:
                close_alpaca(coin = coin, qty = amount)
                decrease_value(file_path)
                print(colored('Trade erfolgreich', 'light_green'))
                break
        # Wait before fetching again
        time.sleep(200)
    

def close_alpaca(coin, qty):
    try:
        takeprofit_order_data = MarketOrderRequest(
            symbol=coin,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        takeprofit_order = trading_client.submit_order(takeprofit_order_data)
        
        print(colored('TakeProfit Order erfolgreich', 'cyan'),takeprofit_order)
        
    except Exception as e:
        print(colored('TakeProfit Order fehlgeschlagen', 'cyan'), str(e))
    
    
def check_price_binance():
    return
    
if  botstatus == 'Alpaca':

    check_price_alpaca(coin = coin, tp = tp, order_type = order_type)
    
if botstatus == 'Binance':
    check_price_binance()
    
    
input("Drücke eine Taste, um das Fenster zu schließen...")