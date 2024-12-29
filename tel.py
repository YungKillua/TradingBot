import json
import telegram
from datetime import datetime
import asyncio

#Variablen
message_file = 'message.txt'

#Get Keys
with open('keys.json', 'r') as keys:
    keys = json.load(keys)
    token = keys['telegram_bot_token']
    chat_id = keys['groupchat_id']

# Telegram Bot Setup
API_TOKEN = token
CHAT_ID = chat_id
bot = telegram.Bot(token=API_TOKEN)

# Funktion zum Senden einer Nachricht an Telegram (asynchron)
async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Funktion zum Überprüfen der Datei, Senden einer Nachricht und Bereinigen der Datei
async def check_file_and_send_message():
    file_path = message_file
    
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            if content:
                await send_telegram_message(content)
                # Datei bereinigen, nachdem die Nachricht gesendet wurde
                with open(file_path, 'w') as file:
                    file.truncate(0)  # Datei leeren
    except Exception as e:
        print(f"Fehler beim Lesen oder Bereinigen der Datei: {e}")


# Hauptprogramm
async def main():
    while True:
        await check_file_and_send_message()  # Überprüfen und Nachricht senden, wenn Text vorhanden ist
        await asyncio.sleep(100)  # FetchIntervall

# Starten des asynchronen Programms
if __name__ == "__main__":
    asyncio.run(main())

