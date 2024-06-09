import random
from collections import defaultdict

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

# Inicjalizacja grafiku
grafik = {dzień: {godzina: None for godzina in godziny_pracy} for dzień in dni}
pracownicy_godziny = defaultdict(int)  # Słownik do śledzenia liczby godzin każdego pracownika

# Funkcja do przypisania pracownika do godziny
def przypisz_pracownika(dzień, godzina, pracownik):
    if grafik[dzień][godzina] is None:
        grafik[dzień][godzina] = pracownik
        pracownicy_godziny[pracownik] += 1
        return True
    return False

# Pierwsza próba przypisania pracowników do godzin zgodnie z ich dostępnościami
for dzień in dni:
    for godzina in godziny_pracy:
        dostepni_pracownicy = [pracownik for pracownik in pracownicy 
                               if dzień in dostepnosci[pracownik] 
                               and any(start <= godzina < end for start, end in dostepnosci[pracownik][dzień])]
        if dostepni_pracownicy:
            wybrany_pracownik = random.choice(dostepni_pracownicy)
            przypisz_pracownika(dzień, godzina, wybrany_pracownik)

# Druga próba: wypełnianie niewypełnionych godzin przez dostępnych pracowników
for dzień in dni:
    for godzina in godziny_pracy:
        if grafik[dzień][godzina] is None:
            # Szukamy pracownika, który już pracuje tego dnia, ale jest wolny w tej godzinie
            for pracownik in pracownicy:
                if dzień in dostepnosci[pracownik]:
                    czy_wolny = any(start <= godzina < end for start, end in dostepnosci[pracownik][dzień])
                    if czy_wolny:
                        przypisz_pracownika(dzień, godzina, pracownik)
                        break

# Trzecia próba: przypisywanie pracowników, którzy są dostępni w inne dni
for dzień in dni:
    for godzina in godziny_pracy:
        if grafik[dzień][godzina] is None:
            for pracownik in pracownicy:
                if pracownik not in grafik[dzień].values():  # Pracownik nie jest zaplanowany w ten dzień
                    przypisz_pracownika(dzień, godzina, pracownik)
                    break

# Czwarta próba: przypisywanie pracowników do dni, w których normalnie nie pracują, ale mają dostępność w inne dni
for dzień in dni:
    for godzina in godziny_pracy:
        if grafik[dzień][godzina] is None:
            # Szukamy pracownika, który nie jest zaplanowany na ten dzień, ale ma dostępność w inne dni
            najmniej_obciazony_pracownik = min(pracownicy, key=lambda p: pracownicy_godziny[p])
            przypisz_pracownika(dzień, godzina, najmniej_obciazony_pracownik)

# Wyświetlenie wyniku
for dzień in grafik:
    print(f"{dzień}:")
    for godzina in sorted(grafik[dzień]):
        pracownik = grafik[dzień][godzina] if grafik[dzień][godzina] else "Brak"
        print(f"  {godzina}:00 - {pracownik}")
