from flask import Flask, request
import threading

# Initialisiere Flask-App
app = Flask(__name__)

# Variable zum Speichern der empfangenen Daten
received_data = None

# Route für Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    global received_data
    received_data = request.get_json()  # Hole JSON-Daten
    print(f"Empfangene Daten: {received_data}")
    process_data()  # Verarbeite die empfangenen Daten direkt nach dem Empfang
    return "Webhook received and data processed!", 200

# Funktion zum Starten des Servers
def start_server():
    app.run(host='0.0.0.0', port=5000)

# Thread für den Flask-Server, damit er parallel läuft
def run_server_in_thread():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    return server_thread

# Funktion zur Verarbeitung der empfangenen Daten
def process_data():
    global received_data
    if received_data:
        print(f"Verarbeite Daten: {received_data}")
        # Hier kannst du mit den empfangenen Daten weiterarbeiten
    else:
        print("Keine Daten empfangen")

if __name__ == "__main__":
    # Server in einem separaten Thread starten
    run_server_in_thread()
    
    # Hauptprogramm läuft weiter
    while True:
        # Hier könntest du andere Logik ausführen oder prüfen, ob neue Daten verarbeitet werden sollen
        pass
