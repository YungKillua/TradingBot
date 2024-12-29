# TradingBot

>Python Bot that uses Tradingview webhook signals to place orders on various exchanges.
                                                                                                          Works on Windows, Linux and Mac.                                                                         Made for usage on Rasberry Pi.

## Installation

Clone the repo with:

```bash
>>git clone https://github.com/YungKillua/TradingBot
>>cd TradingBot
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
>>pip install -r requirements.txt 
```
## Setup
>Put your api keys in keys.json you can change the config via menu
## Usage
### 1. Tradingview Setup
>Go to strategy folder and copy the strategy you want yo use. Then go to [Tradingview](https://tradingview.com) and paste into new pinescript and create alert for Crypto Coins you want to trade. Webhook adress should be the one you get when running bot. Make sure to forward ports or use with ngrok. 
### 2. Start Bot
```python
python3 bot.py
```
#### For Telegram Messages open another shell and run:
```python
python3 tel.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.
