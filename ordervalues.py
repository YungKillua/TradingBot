import json

# Funktion, um den Wert zu erhöhen
def increase_value(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Lade den Inhalt der Datei als Dictionary

        # Erhöhe den Wert um 1
        data['value'] += 1

        with open(file_path, 'w') as file:
            json.dump(data, file)  # Speichere die aktualisierten Daten zurück in die Datei
        print(f"OrderAnzahl: {data['value']}")

    except (FileNotFoundError, json.JSONDecodeError):
        print("Fehler beim Laden oder Erstellen der Datei.")

# Funktion, um den Wert zu verringern
def decrease_value(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Verringere den Wert um 1
        data['value'] -= 1

        with open(file_path, 'w') as file:
            json.dump(data, file)
        print(f"OrderAnzahl: {data['value']}")

    except (FileNotFoundError, json.JSONDecodeError):
        print("Fehler beim Laden oder Erstellen der Datei.")

# Funktion, um den Wert auf 0 zu setzen
def reset_value(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Setze den Wert auf 0
        data['value'] = 0

        with open(file_path, 'w') as file:
            json.dump(data, file)
        print(f"OrderAnzahl: {data['value']}")

    except (FileNotFoundError, json.JSONDecodeError):
        print("Fehler beim Laden oder Erstellen der Datei.")
        
# Beispiel wie die Datei zu Beginn aussehen könnte:
def create_initial_file(file_path):
    data = {"value": 0}
    with open(file_path, 'w') as file:
        json.dump(data, file)

def read_value(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data['value']

    except (FileNotFoundError, json.JSONDecodeError):
        print("Fehler beim Laden der Datei.")
        
        
# Beispiel

#file_path = "counter.json"

# Erstelle die Datei mit dem initialen Wert, falls sie noch nicht existiert
#create_initial_file(file_path)

# Beispielaufrufe der Funktionen
#increase_value(file_path)  # Erhöht den Wert
#decrease_value(file_path)  # Verringert den Wert
#reset_value(file_path)     # Setzt den Wert auf 0
#read_value(file_path)      # Liest den Wert aus

