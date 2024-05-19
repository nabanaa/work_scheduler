// Dodanie nasłuchiwacza zdarzeń do przycisku zmiany motywu
document.getElementById('toggle-theme').addEventListener('click', function() {
    // Przełączanie klasy 'dark-mode' dla elementu body
    document.body.classList.toggle('dark-mode');
    // Sprawdzanie, czy body ma klasę 'dark-mode'
    const isDarkMode = document.body.classList.contains('dark-mode');
    // Zapisanie stanu motywu (ciemny/jasny) w localStorage
    localStorage.setItem('dark-mode', isDarkMode);
});

// Inicjalizacja ustawień motywu po załadowaniu dokumentu
document.addEventListener('DOMContentLoaded', function() {
    // Pobieranie stanu motywu z localStorage
    const isDarkMode = JSON.parse(localStorage.getItem('dark-mode'));
    // Jeśli motyw ciemny jest zapisany, dodanie klasy 'dark-mode' do body
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
});

// Dodanie nasłuchiwacza zdarzeń do przycisku 'Poprzedni miesiąc'
document.getElementById('prev-month').addEventListener('click', function() {
    // Pobieranie aktualnego roku i miesiąca z atrybutów dataset
    const currentMonthYear = document.getElementById('current-month').dataset;
    // Obliczanie nowej daty, przechodząc do poprzedniego miesiąca
    const newDate = new Date(currentMonthYear.year, currentMonthYear.month - 1);
    // Generowanie kalendarza dla nowego miesiąca
    generateCalendar(newDate.getFullYear(), newDate.getMonth());
});

// Dodanie nasłuchiwacza zdarzeń do przycisku 'Następny miesiąc'
document.getElementById('next-month').addEventListener('click', function() {
    // Pobieranie aktualnego roku i miesiąca z atrybutów dataset
    const currentMonthYear = document.getElementById('current-month').dataset;
    // Obliczanie nowej daty, przechodząc do następnego miesiąca
    const newDate = new Date(currentMonthYear.year, parseInt(currentMonthYear.month) + 1);
    // Generowanie kalendarza dla nowego miesiąca
    generateCalendar(newDate.getFullYear(), newDate.getMonth());
});

// Funkcja generowania kalendarza na podstawie roku i miesiąca
function generateCalendar(year, month) {
    // Pobieranie danych z serwera
    fetch('/get_dane')
        .then(response => response.json())
        .then(dane => {
            // Element kalendarza
            const calendarElement = document.getElementById('calendar');
            calendarElement.innerHTML = ''; // Czyszczenie poprzedniego kalendarza

            // Obliczanie liczby dni w miesiącu
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            // Obliczanie pierwszego dnia miesiąca
            const firstDayOfMonth = new Date(year, month, 1).getDay();

            // Nazwy miesięcy
            const monthNames = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];

            // Aktualizacja wyświetlania bieżącego miesiąca i roku
            const currentMonthElement = document.getElementById('current-month');
            currentMonthElement.innerText = `${monthNames[month]} ${year}`;
            currentMonthElement.dataset.year = year;
            currentMonthElement.dataset.month = month;

            // Wypełnianie dniami z poprzedniego miesiąca, jeśli miesiąc nie zaczyna się w niedzielę
            for (let i = 0; i < (firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1); i++) {
                const emptyDay = document.createElement('div');
                emptyDay.classList.add('day');
                calendarElement.appendChild(emptyDay);
            }

            // Tworzenie komórek dni w kalendarzu
            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                dayElement.classList.add('day');
                const dateElement = document.createElement('div');
                dateElement.classList.add('date');
                dateElement.innerText = day;
                dayElement.appendChild(dateElement);

                // Pełna data dla bieżącego dnia
                const fullDate = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

                // Dodanie nasłuchiwacza zdarzeń do komórek dni, aby wyświetlać modal
                dayElement.addEventListener('click', () => {
                    showModal(fullDate);
                });

                // Dodawanie dostępności pracowników dla bieżącego dnia
                dane.employees.forEach(employee => {
                    if (employee.availability[fullDate]) {
                        const availabilityElement = document.createElement('div');
                        availabilityElement.classList.add('availability');
                        availabilityElement.innerText = `${employee.name}: ${employee.availability[fullDate]}`;
                        dayElement.appendChild(availabilityElement);
                    }
                });

                // Oznaczanie weekendów
                const dayOfWeek = new Date(year, month, day).getDay();
                if (dayOfWeek === 0) {
                    dayElement.classList.add('sunday');
                } else if (dayOfWeek === 6) {
                    dayElement.classList.add('saturday');
                }

                calendarElement.appendChild(dayElement);
            }
        });
}

// Funkcja wyświetlająca modal z opcjami dostępności
function showModal(date) {
    const modal = document.getElementById('availability-modal');
    const span = document.getElementsByClassName('close')[0];
    const addOption = document.getElementById('add-option');
    const deleteOption = document.getElementById('delete-option');
    const exitOption = document.getElementById('exit-option');
    const availabilityForm = document.getElementById('availability-form');
    const deleteForm = document.getElementById('delete-form');
    const modalDate = document.getElementById('modal-date');
    const deleteDate = document.getElementById('delete-date');

    // Ustawienie daty w formularzach
    modalDate.value = date;
    deleteDate.value = date;

    // Wyświetlanie modala
    modal.style.display = 'block';

    // Obsługa kliknięcia na opcję dodania dostępności
    addOption.onclick = () => {
        availabilityForm.style.display = 'block';
        deleteForm.style.display = 'none';
    };

    // Obsługa kliknięcia na opcję usunięcia dostępności
    deleteOption.onclick = () => {
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'block';
    };

    // Obsługa kliknięcia na opcję zamknięcia modala
    exitOption.onclick = () => {
        modal.style.display = 'none';
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'none';
    };

    // Obsługa kliknięcia na przycisk zamknięcia modala
    span.onclick = () => {
        modal.style.display = 'none';
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'none';
    };

    // Obsługa kliknięcia poza modalem, aby go zamknąć
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
            availabilityForm.style.display = 'none';
            deleteForm.style.display = 'none';
        }
    };
}

// Obsługa wysłania formularza dodania dostępności
document.getElementById('availability-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const employee = document.getElementById('employee').value;
    const date = document.getElementById('modal-date').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    const availability = `${startTime} - ${endTime}`;

    const data = { employee, date, availability };

    fetch('/add_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Dyspozycyjność dodana pomyślnie!');
            location.reload(); // Przeładuj stronę, aby zaktualizować kalendarz
        }
    })
    .catch(error => console.error('Error:', error));
});

// Obsługa wysłania formularza usunięcia dostępności
document.getElementById('delete-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const employee = document.getElementById('delete-employee').value;
    const date = document.getElementById('delete-date').value;

    const data = { employee, date };

    fetch('/delete_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Dyspozycyjność usunięta pomyślnie!');
            location.reload(); // Przeładuj stronę, aby zaktualizować kalendarz
        }
    })
    .catch(error => console.error('Error:', error));
});

// Inicjalizacja kalendarza przy załadowaniu strony
generateCalendar(new Date().getFullYear(), new Date().getMonth());
