from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import os

app = Flask(__name__)

# Ścieżka do pliku JSON z grafikiem
dane_FILE = 'dane.json'

# Łączenie z bazą
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Odczytanie bazy
def read_db_to_json():
    """Odczytanie z bazy dyspozycji"""
    
    # Póki co dane z bazy ładuje to tego JSONA bo trzebaby przerobić całą logikę pobierania 
    
    conn = get_db_connection()
    cursor = conn.cursor()
    db_emp_dispositions = cursor.execute(f'SELECT user_email, date, start_time, end_time FROM dispositions;').fetchall()

    with open('dane.json', 'r') as f:
        dane = json.load(f)

    for row in db_emp_dispositions:
        print(f"{row[0]},{row[1]},{row[2]}")
    
        found = False
        for employee in dane["employees"]:
            if employee["name"] == row[0]:
                found = True
                date_str = row[1]
                time_str = f"{row[2]} - {row[3]}"
                employee["availability"][date_str] = time_str

        if not found:
            new_employee = {
                "name": row[0],
                "availability": {}
            }
            date_str = row[1]
            time_str = f"{row[2]} - {row[3]}"
            new_employee["availability"][date_str] = time_str
            dane["employees"].append(new_employee)

    with open('dane.json', 'w') as f:
        json.dump(dane, f, indent=4)

    cursor.close()
    conn.close()
    
# Insert danych dyspozycji do bazy
def insert_disposition(conn, user_email, date, start_time, end_time):
    """Wstawia dane do tabeli dispositions, generując unikalne ID."""

    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM dispositions")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        next_id = 1
    else:
        next_id = max_id + 1

    cursor.execute(
        "INSERT INTO dispositions (id, user_email, date, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
        (next_id, user_email, date, start_time, end_time),
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
def del_disposition(email,date):
    """Usuwa dyspozycyjnosc danego pracownika po jego emailu & dacie z tabeli dispositions"""
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute(f'DELETE FROM dispositions WHERE user_email=\'{email}\' AND date=\'{date}\'')
    
    conn.commit()
    
    cursor.close()
    conn.close()

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

    read_db_to_json()

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
    
    # Dodaj do bazy danych (dziwnie zrobione bo też baza ma po prostu DATE YYYY-MM-DD HH:MM)
    
    conn = get_db_connection()
    insert_disposition(conn,data['employee'],data['date'],data['availability'].split(' ')[0],data['availability'].split(' ')[2]) # 15:00 - 18:00 np.

    # Znajdź pracownika w grafiku (zakomentowane bo jak dodajemy do bazy to żeby nie dublować się z JSON kiedy już i tak do niego wpisujemy na poczatku)
    # for employee in dane['employees']:
    #     if employee['name'] == data['employee']:
    #         employee['availability'][data['date']] = data['availability']
    #         break
    # else:
    #     # Jeśli pracownika nie ma w grafiku, dodaj nowego
    #     dane['employees'].append({
    #         'name': data['employee'],
    #         'availability': {
    #             data['date']: data['availability']
    #         }
    #     })

    # save_dane(dane)
    return jsonify({"status": "success", "data": data})

# Endpoint do usuwania dyspozycyjności
@app.route('/delete_availability', methods=['POST'])
def delete_availability():
    data = request.json
    dane = load_dane()
    
    user_email = data['employee']
    date = data['date']
 
    del_disposition(user_email,date)

    for employee in dane['employees']:
        if employee['name'] == data['employee'] and data['date'] in employee['availability']:
            del employee['availability'][data['date']]
            break

    save_dane(dane)
    return jsonify({"status": "success", "data": data})

if __name__ == '__main__':
    app.run(debug=True)
