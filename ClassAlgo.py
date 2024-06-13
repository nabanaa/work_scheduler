import random
import json
from collections import defaultdict
from datetime import datetime, timedelta, date

class Scheduler:
    def __init__(self, pracownicy, dostepnosci, godziny_pracy, days, month, year):
        self.pracownicy = pracownicy
        self.dostepnosci = dostepnosci
        self.godziny_pracy = godziny_pracy
        self.dni = self.generate_days_in_month(month, year)
        self.grafik = {dzień: {godzina: None for godzina in godziny_pracy} for dzień, _ in self.dni}
        self.pracownicy_godziny = defaultdict(int)

    def generate_days_in_month(self, month, year):
        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        days = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
        days_with_weekdays = [(day, (start_date + timedelta(days=i)).strftime('%A')) for i, day in enumerate(days)]
        return days_with_weekdays

    def przypisz_pracownika(self, dzień, godzina, pracownik):
        if self.grafik[dzień][godzina] is None:
            self.grafik[dzień][godzina] = pracownik
            self.pracownicy_godziny[pracownik] += 1
            return True
        return False

    def przypisz_pierwsza_proba(self):
        for dzień, _ in self.dni:
            for godzina in self.godziny_pracy:
                dostepni_pracownicy = [pracownik for pracownik in self.pracownicy 
                                       if dzień in self.dostepnosci[pracownik] 
                                       and any(start <= godzina < end for start, end in self.dostepnosci[pracownik][dzień])]
                if dostepni_pracownicy:
                    wybrany_pracownik = random.choice(dostepni_pracownicy)
                    self.przypisz_pracownika(dzień, godzina, wybrany_pracownik)

    def przypisz_druga_proba(self):
        for dzień, _ in self.dni:
            for godzina in self.godziny_pracy:
                if self.grafik[dzień][godzina] is None:
                    for pracownik in self.pracownicy:
                        if dzień in self.dostepnosci[pracownik]:
                            czy_wolny = any(start <= godzina < end for start, end in self.dostepnosci[pracownik][dzień])
                            if czy_wolny:
                                self.przypisz_pracownika(dzień, godzina, pracownik)
                                break

    def przypisz_trzecia_proba(self):
        for dzień, _ in self.dni:
            for godzina in self.godziny_pracy:
                if self.grafik[dzień][godzina] is None:
                    for pracownik in self.pracownicy:
                        if pracownik not in self.grafik[dzień].values():
                            self.przypisz_pracownika(dzień, godzina, pracownik)
                            break

    def przypisz_czwarta_proba(self):
        for dzień, _ in self.dni:
            for godzina in self.godziny_pracy:
                if self.grafik[dzień][godzina] is None:
                    najmniej_obciazony_pracownik = min(self.pracownicy, key=lambda p: self.pracownicy_godziny[p])
                    self.przypisz_pracownika(dzień, godzina, najmniej_obciazony_pracownik)

    def generuj_grafik(self):
        self.przypisz_pierwsza_proba()
        self.przypisz_druga_proba()
        self.przypisz_trzecia_proba()
        self.przypisz_czwarta_proba()

    def wyswietl_grafik(self):
        for dzień, weekday in self.dni:
            print(f"{dzień} ({weekday}):")
            for godzina in sorted(self.grafik[dzień]):
                pracownik = self.grafik[dzień][godzina] if self.grafik[dzień][godzina] else "Brak"
                print(f"  {godzina}:00 - {pracownik}")

def convert_availability(availability):
    converted = {}
    for day, time_range in availability.items():
        start_str, end_str = time_range.split(" - ")
        start_time = datetime.strptime(start_str, "%H:%M")
        end_time = datetime.strptime(end_str, "%H:%M")
        hours = [(start_time.hour, end_time.hour)]
        converted[day] = hours
    return converted

# Example usage
if __name__ == '__main__':
    with open('dane.json', 'r') as file:
        data = json.load(file)

    pracownicy = []
    dostepnosci = {}
    dni = set()

    for employee in data['employees']:
        name = employee['name']
        availability = convert_availability(employee['availability'])
        pracownicy.append(name)
        dostepnosci[name] = availability
        dni.update(availability.keys())

    dni = sorted(dni)
    godziny_pracy = range(8, 18)
    month = 6  # Example month
    year = 2024  # Example year

    scheduler = Scheduler(pracownicy, dostepnosci, godziny_pracy, month, year)
    scheduler.generuj_grafik()
    scheduler.wyswietl_grafik()