from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

dane_FILE = 'dane.json'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def read_db_to_json():
    conn = get_db_connection()
    cursor = conn.cursor()
    db_emp_dispositions = cursor.execute(f'SELECT user_email, date, start_time, end_time FROM dispositions;').fetchall()

    with open(dane_FILE, 'r') as f:
        dane = json.load(f)

    for row in db_emp_dispositions:
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

    with open(dane_FILE, 'w') as f:
        json.dump(dane, f, indent=4)

    cursor.close()
    conn.close()

def insert_disposition(conn, user_email, date, start_time, end_time):
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

def del_disposition(email, date):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute(f'DELETE FROM dispositions WHERE user_email=\'{email}\' AND date=\'{date}\'')
    
    conn.commit()
    
    cursor.close()
    conn.close()

def load_dane():
    if os.path.exists(dane_FILE):
        with open(dane_FILE, 'r') as file:
            return json.load(file)
    return {"employees": []}

def save_dane(dane):
    with open(dane_FILE, 'w') as file:
        json.dump(dane, file, indent=4)

@app.route('/')
def index():
    read_db_to_json()
    dane = load_dane()
    return render_template('main.html', dane=dane)

@app.route('/get_dane', methods=['GET'])
def get_dane():
    dane = load_dane()
    return jsonify(dane)

@app.route('/add_availability', methods=['POST'])
def add_availability():
    data = request.json
    dane = load_dane()
    
    conn = get_db_connection()
    insert_disposition(conn, data['employee'], data['date'], data['availability'].split(' ')[0], data['availability'].split(' ')[2])
    return jsonify({"status": "success", "data": data})

@app.route('/delete_availability', methods=['POST'])
def delete_availability():
    data = request.json
    dane = load_dane()
    
    user_email = data['employee']
    date = data['date']
 
    del_disposition(user_email, date)

    for employee in dane['employees']:
        if employee['name'] == data['employee'] and data['date'] in employee['availability']:
            del employee['availability'][data['date']]
            break

    save_dane(dane)
    return jsonify({"status": "success", "data": data})

@app.route('/schedule')
def schedule():
    from ClassAlgo import Scheduler  # Import the Scheduler class from ClassAlgo

    # Load data from JSON file
    dane = load_dane()

    # Convert availability data
    pracownicy = []
    dostepnosci = {}
    dni = set()

    def convert_availability(availability):
        converted = {}
        for day, time_range in availability.items():
            start_str, end_str = time_range.split(" - ")
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")
            hours = [(start_time.hour, end_time.hour)]
            converted[day] = hours
        return converted

    for employee in dane['employees']:
        name = employee['name']
        availability = convert_availability(employee['availability'])
        pracownicy.append(name)
        dostepnosci[name] = availability
        dni.update(availability.keys())

    dni = sorted(dni)
    godziny_pracy = range(8, 18)

    # Initialize and generate the schedule
    scheduler = Scheduler(pracownicy, dostepnosci, godziny_pracy, dni)
    scheduler.generuj_grafik()
    
    # Collect the schedule data to display
    generated_schedule = scheduler.grafik

    return render_template('schedule.html', schedule=generated_schedule)

if __name__ == '__main__':
    app.run(debug=True)
