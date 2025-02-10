let tg = window.Telegram.WebApp;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    tg.ready();
    tg.expand();
    
    // Загружаем данные пользователя
    loadUserData();
});

// Загрузка данных пользователя
async function loadUserData() {
    try {
        const response = await fetch('/api/user-data');
        const data = await response.json();
        
        document.getElementById('username').textContent = data.name;
        document.getElementById('level').textContent = `Level: ${data.level}`;
        document.getElementById('messages-count').textContent = data.messages;
        document.getElementById('exercises-count').textContent = data.exercises;
        document.getElementById('streak-days').textContent = data.streak;
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

// Обработчики кнопок
function showExercises() {
    tg.showPopup({
        title: 'Choose Exercise Type',
        message: 'What would you like to practice?',
        buttons: [
            {id: 'grammar', type: 'default', text: '📝 Grammar'},
            {id: 'vocabulary', type: 'default', text: '📚 Vocabulary'},
            {id: 'listening', type: 'default', text: '🎧 Listening'},
            {id: 'writing', type: 'default', text: '✍️ Writing'}
        ]
    });
}

function showLessons() {
    // Implement lessons view
}

function showChat() {
    // Implement chat view
}

function showGoals() {
    // Implement goals view
} 