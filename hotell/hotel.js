const form = document.getElementById('bookingForm');
const roomSelect = document.getElementById('roomSelect');
const dateInput = document.getElementById('dateInput');
const commentInput = document.getElementById('commentInput');
const saveBtn = document.getElementById('saveBtn');
const bookingsContainer = document.getElementById('bookingsContainer');
const errorMsg = document.getElementById('errorMsg');
const successMsg = document.getElementById('successMsg');

const API_URL = 'http://localhost:8080';

// Скрыть сообщения об ошибке через 5 секунд
function showMessage(element, text, duration = 5000) {
    element.textContent = text;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// Загрузить комнаты при загрузке страницы
async function loadRooms() {
    try {
        const response = await fetch(`${API_URL}/rooms`);
        if (!response.ok) throw new Error('Ошибка при загрузке комнат');

        const rooms = await response.json();
        
        // Очистить select и заполнить его
        roomSelect.innerHTML = '<option value="">-- Выберите комнату --</option>';
        rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = room.name;
            roomSelect.appendChild(option);
        });
    } catch (error) {
        showMessage(errorMsg, '❌ Не удалось загрузить комнаты: ' + error.message);
    }
}

// Загрузить все бронирования
async function loadBookings() {
    try {
        const response = await fetch(`${API_URL}/bookings`);
        if (!response.ok) throw new Error('Ошибка при загрузке бронирований');

        const bookings = await response.json();

        if (bookings.length === 0) {
            bookingsContainer.innerHTML = '<div class="empty-message">Нет забронированных комнат</div>';
            return;
        }

        const bookingsList = document.createElement('ul');
        bookingsList.id = 'bookingsList';

        bookings.forEach(booking => {
            const li = document.createElement('li');
            
            const roomDiv = document.createElement('div');
            roomDiv.className = 'booking-room';
            roomDiv.textContent = `🛏️ ${booking.room_name || 'Комната ' + booking.roomId}`;

            const dateDiv = document.createElement('div');
            dateDiv.className = 'booking-date';
            const bookingDate = new Date(booking.date);
            dateDiv.textContent = `📅 ${bookingDate.toLocaleDateString('sv-SE')}`;

            li.appendChild(roomDiv);
            li.appendChild(dateDiv);

            if (booking.comment) {
                const commentDiv = document.createElement('div');
                commentDiv.className = 'booking-comment';
                commentDiv.textContent = `💬 "${booking.comment}"`;
                li.appendChild(commentDiv);
            }

            bookingsList.appendChild(li);
        });

        bookingsContainer.innerHTML = '';
        bookingsContainer.appendChild(bookingsList);
    } catch (error) {
        bookingsContainer.innerHTML = `<div class="error" style="display: block;">Ошибка при загрузке: ${error.message}</div>`;
    }
}

// Обработка отправки формы
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const roomId = roomSelect.value;
    const date = dateInput.value;
    const comment = commentInput.value;

    if (!roomId || !date) {
        showMessage(errorMsg, '❌ Пожалуйста, выберите комнату и дату');
        return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = 'Сохраняю...';

    try {
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomId: parseInt(roomId),
                date: date,
                comment: comment
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при сохранении');
        }

        showMessage(successMsg, '✅ Бронирование успешно сохранено!');

        // Очистить форму
        form.reset();

        // Перезагрузить список бронирований
        await loadBookings();
    } catch (error) {
        showMessage(errorMsg, '❌ ' + error.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Spara bokning';
    }
});

// Установить минимальную дату - сегодня
const today = new Date().toISOString().split('T')[0];
dateInput.min = today;

// Загрузить данные при загрузке страницы
loadRooms();
loadBookings();
