document.getElementById('toggle-theme').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('dark-mode', isDarkMode);
});

document.addEventListener('DOMContentLoaded', function() {
    const isDarkMode = JSON.parse(localStorage.getItem('dark-mode'));
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
});

document.getElementById('prev-month').addEventListener('click', function() {
    const currentMonthYear = document.getElementById('current-month').dataset;
    const newDate = new Date(currentMonthYear.year, currentMonthYear.month - 1);
    generateCalendar(newDate.getFullYear(), newDate.getMonth());
});

document.getElementById('next-month').addEventListener('click', function() {
    const currentMonthYear = document.getElementById('current-month').dataset;
    const newDate = new Date(currentMonthYear.year, parseInt(currentMonthYear.month) + 1);
    generateCalendar(newDate.getFullYear(), newDate.getMonth());
});

function generateCalendar(year, month) {
    fetch('/get_dane')
        .then(response => response.json())
        .then(dane => {
            const calendarElement = document.getElementById('calendar');
            calendarElement.innerHTML = '';
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const firstDayOfMonth = new Date(year, month, 1).getDay();
            const monthNames = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];
            const currentMonthElement = document.getElementById('current-month');
            currentMonthElement.innerText = `${monthNames[month]} ${year}`;
            currentMonthElement.dataset.year = year;
            currentMonthElement.dataset.month = month;

            for (let i = 0; i < (firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1); i++) {
                const emptyDay = document.createElement('div');
                emptyDay.classList.add('day');
                calendarElement.appendChild(emptyDay);
            }

            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                dayElement.classList.add('day');
                const dateElement = document.createElement('div');
                dateElement.classList.add('date');
                dateElement.innerText = day;
                dayElement.appendChild(dateElement);

                const fullDate = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

                dayElement.addEventListener('click', () => {
                    showModal(fullDate);
                });

                dane.employees.forEach(employee => {
                    if (employee.availability[fullDate]) {
                        const availabilityElement = document.createElement('div');
                        availabilityElement.classList.add('availability');
                        availabilityElement.innerText = `${employee.name}: ${employee.availability[fullDate]}`;
                        dayElement.appendChild(availabilityElement);
                    }
                });

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

    modalDate.value = date;
    deleteDate.value = date;
    modal.style.display = 'block';

    addOption.onclick = () => {
        availabilityForm.style.display = 'block';
        deleteForm.style.display = 'none';
    };

    deleteOption.onclick = () => {
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'block';
    };

    exitOption.onclick = () => {
        modal.style.display = 'none';
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'none';
    };

    span.onclick = () => {
        modal.style.display = 'none';
        availabilityForm.style.display = 'none';
        deleteForm.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
            availabilityForm.style.display = 'none';
            deleteForm.style.display = 'none';
        }
    };
}

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
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
});

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
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
});

generateCalendar(new Date().getFullYear(), new Date().getMonth());
