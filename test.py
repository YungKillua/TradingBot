from flask import Flask, request

app = Flask(__name__)

# Route für Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()  # Hole JSON-Daten aus der Anfrage
    if data:
        print(f"Empfangene Daten: {data}")
        return "Webhook received!", 200
    else:
        return "No JSON data received", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
