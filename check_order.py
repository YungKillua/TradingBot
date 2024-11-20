from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, OrderSide, TimeInForce
from binance.client import Client
import sys, time, json
from termcolor import colored



with open('keys.json', 'r') as keys:
    keys = json.load(keys)
    binance_api_key = keys['binance_api_key']
    binance_secret_key = keys['binance_secret_key']
    alpaca_api_key = keys['alpaca_api_key']
    alpaca_secret_key = keys['alpaca_secret_key']

# Verbinde mit dem Binance Testnet
client = Client(binance_api_key, binance_secret_key, testnet=True)

#AlpacaClient Testnet
if alpaca_api_key != '':
    trading_client = TradingClient(alpaca_api_key, alpaca_secret_key, paper=True)
    
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
    type = var4

else:
    print("Argument fehlt.")

print('Variablen erfolgreich uebergeben')
print(f'Botstatus auf {botstatus}')
print(f'Coin ist {coin}')
print(f'TakeProfit ist {tp}')
print(f'Order Type ist {type}')
    
def check_price_alpaca(coin, tp, type):
    while True:
        asset = trading_client.get_open_position(coin)
        price = asset.current_price
        qty = asset.qty
        print(f'Checking...  Price is at{price}')
        if type == 'Long':
            if price >= tp:
                close_alpaca(coin = coin, qty = qty)
                print(colored('Trade erfolgreich', 'light_green'))
                break
        elif type == 'Short':
            if price <= tp:
                close_alpaca(coin = coin, qty = qty)
                print(colored('Trade erfolgreich', 'light_green'))
                break
        time.sleep(10)
    

def close_alpaca(coin, qty):
    try:
        takeprofit_order_data = MarketOrderRequest(
            symbol=coin,
            qty=qty,
            side=OrderSide.SELL,
            time_in_Force=TimeInForce.GTC
        )
        takeprofit_order = trading_client.submit_order(takeprofit_order_data)
        
        print(colored('TakeProfit Order erfolgreich', 'cyan'),takeprofit_order)
        
    except Exception as e:
        print(colored('TakeProfit Order fehlgeschlagen', 'cyan'), str(e))
    
    
def check_price_binance():
    return
    
if  botstatus == 'Alpaca':

    check_price_alpaca(coin = coin, tp = tp, type = type)
    
if botstatus == 'Binance':
    check_price_binance()
    
    
input("Drücke eine Taste, um das Fenster zu schließen...")