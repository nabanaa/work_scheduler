from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Ścieżka do pliku JSON z grafikiem
dane_FILE = 'dane.json'

# Funkcja do wczytywania grafiku z pliku JSON
def load_dane():
    if os.path.exists(dane_FILE):
        with open(dane_FILE, 'r') as file:
            return json.load(file)
    return {"employees": []}

# Funkcja do zapisywania grafiku do pliku JSON
def save_dane(dane):
    with open(dane_FILE, 'w') as file:
        json.dump(dane, file, indent=4)

# Strona główna z kalendarzem
@app.route('/')
def index():
    dane = load_dane()
    return render_template('main.html', dane=dane)

# Endpoint do zwracania grafiku w formacie JSON
@app.route('/get_dane', methods=['GET'])
def get_dane():
    dane = load_dane()
    return jsonify(dane)

# Endpoint do dodawania dyspozycyjności
@app.route('/add_availability', methods=['POST'])
def add_availability():
    data = request.json
    dane = load_dane()

    # Znajdź pracownika w grafiku
    for employee in dane['employees']:
        if employee['name'] == data['employee']:
            employee['availability'][data['date']] = data['availability']
            break
    else:
        # Jeśli pracownika nie ma w grafiku, dodaj nowego
        dane['employees'].append({
            'name': data['employee'],
            'availability': {
                data['date']: data['availability']
            }
        })

    save_dane(dane)
    return jsonify({"status": "success", "data": data})

# Endpoint do usuwania dyspozycyjności
@app.route('/delete_availability', methods=['POST'])
def delete_availability():
    data = request.json
    dane = load_dane()

    for employee in dane['employees']:
        if employee['name'] == data['employee'] and data['date'] in employee['availability']:
            del employee['availability'][data['date']]
            break

    save_dane(dane)
    return jsonify({"status": "success", "data": data})

if __name__ == '__main__':
    app.run(debug=True)
