from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Deine API-Schlüssel vom Testnet
api_key = 'BibAXBReE7i0i6D9Mbahtztl58HTEZtBCgWhZwoVntopKuDOVF6F9Z3diy3jsfjW'    #ApiKey
api_secret = 'uhNe1bOe640SNtkhfAt4RTvwfkK4z46cfPReq785Vlr0nX9SpF51vnJh7gDEKACE' #Secret

# Verbinde mit dem Binance Testnet
client = Client(api_key, api_secret, testnet=True)

try:
    # Teste die Verbindung durch Abrufen der Kontoinformationen
    account = client.get_account()
    
    if account:
        print('Verbunden mit Testnet-Account')
    else:
        print('Konnte nicht verbinden')
        
except BinanceAPIException as e:
    print(f"Binance API Fehler: {e}")
except BinanceRequestException as e:
    print(f"Netzwerkfehler: {e}")
except Exception as e:
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Rufe das Guthaben für BTC ab
btc_balance = client.get_asset_balance(asset='BTC')
print(f"BTC Balance: {btc_balance['free']} BTC")

# Rufe das Guthaben für USDT ab
usdt_balance = client.get_asset_balance(asset='USDT')
print(f"USDT Balance: {usdt_balance['free']} USDT")