import random
from collections import defaultdict

class Scheduler:
    def __init__(self, pracownicy, dostepnosci, godziny_pracy, dni):
        self.pracownicy = pracownicy
        self.dostepnosci = dostepnosci
        self.godziny_pracy = godziny_pracy
        self.dni = dni
        self.grafik = {dzień: {godzina: None for godzina in godziny_pracy} for dzień in dni}
        self.pracownicy_godziny = defaultdict(int)  # Słownik do śledzenia liczby godzin każdego pracownika
    
    def przypisz_pracownika(self, dzień, godzina, pracownik):
        if self.grafik[dzień][godzina] is None:
            self.grafik[dzień][godzina] = pracownik
            self.pracownicy_godziny[pracownik] += 1
            return True
        return False
    
    def przypisz_pierwsza_proba(self):
        for dzień in self.dni:
            for godzina in self.godziny_pracy:
                dostepni_pracownicy = [pracownik for pracownik in self.pracownicy 
                                       if dzień in self.dostepnosci[pracownik] 
                                       and any(start <= godzina < end for start, end in self.dostepnosci[pracownik][dzień])]
                if dostepni_pracownicy:
                    wybrany_pracownik = random.choice(dostepni_pracownicy)
                    self.przypisz_pracownika(dzień, godzina, wybrany_pracownik)
    
    def przypisz_druga_proba(self):
        for dzień in self.dni:
            for godzina in self.godziny_pracy:
                if self.grafik[dzień][godzina] is None:
                    for pracownik in self.pracownicy:
                        if dzień in self.dostepnosci[pracownik]:
                            czy_wolny = any(start <= godzina < end for start, end in self.dostepnosci[pracownik][dzień])
                            if czy_wolny:
                                self.przypisz_pracownika(dzień, godzina, pracownik)
                                break
    
    def przypisz_trzecia_proba(self):
        for dzień in self.dni:
            for godzina in self.godziny_pracy:
                if self.grafik[dzień][godzina] is None:
                    for pracownik in self.pracownicy:
                        if pracownik not in self.grafik[dzień].values():
                            self.przypisz_pracownika(dzień, godzina, pracownik)
                            break
    
    def przypisz_czwarta_proba(self):
        for dzień in self.dni:
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
        for dzień in self.grafik:
            print(f"{dzień}:")
            for godzina in sorted(self.grafik[dzień]):
                pracownik = self.grafik[dzień][godzina] if self.grafik[dzień][godzina] else "Brak"
                print(f"  {godzina}:00 - {pracownik}")

# Dane wejściowe
pracownicy = ["Anna", "Jan", "Kasia", "Zosia"]
dostepnosci = {
    "Anna": {"poniedziałek": [(8, 12), (14, 18)], "wtorek": [(8, 12)], "środa": [(14, 18)]},
    "Jan": {"poniedziałek": [(12, 16)], "czwartek": [(8, 12)], "piątek": [(10, 14)]},
    "Kasia": {"środa": [(8, 12)], "czwartek": [(12, 16)], "piątek": [(14, 18)]},
    "Zosia": {"wtorek": [(10, 18)]}
}
godziny_pracy = range(8, 18)  # 8:00 - 18:00
dni = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek"]

# Inicjalizacja i generowanie grafiku
scheduler = Scheduler(pracownicy, dostepnosci, godziny_pracy, dni)
scheduler.generuj_grafik()
scheduler.wyswietl_grafik()