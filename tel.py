import asyncio
from telegram import Bot

#Telegram Functions
async def send_message(token, chat_id, text):
    #Telegram Setup
    tbot = Bot(token=token)
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