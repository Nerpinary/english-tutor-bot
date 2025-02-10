let tg = window.Telegram.WebApp;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    tg.ready();
    tg.expand();
    
    // Получаем initData из URL параметров
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id') || tg.initDataUnsafe?.user?.id;
    
    if (!userId) {
        console.error('No user ID available');
        showError('Ошибка авторизации. Пожалуйста, откройте приложение через Telegram.');
        return;
    }
    
    // Загружаем данные пользователя и проверяем необходимость теста
    checkUserLevel(userId);
});

// Показ ошибки
function showError(message) {
    document.querySelector('.container').innerHTML = `
        <div class="error-container">
            <p class="error-message">${message}</p>
        </div>
    `;
}

// Проверка уровня пользователя
async function checkUserLevel(userId) {
    try {
        const response = await fetch(`/api/user-data?user_id=${userId}`);
        const data = await response.json();
        
        // Если уровень не определен, показываем страницу теста
        if (!data.level || data.level === 'undefined' || data.level === 'Unknown') {
            showLevelTest();
        } else {
            // Иначе показываем основной интерфейс
            loadUserData(data);
            showMainInterface();
        }
    } catch (error) {
        console.error('Error checking user level:', error);
        showError('Ошибка загрузки данных. Пожалуйста, попробуйте позже.');
    }
}

// Показ страницы теста
function showLevelTest() {
    document.querySelector('.container').innerHTML = `
        <div class="test-container">
            <h2>Определение уровня английского</h2>
            <p>Для доступа к упражнениям и урокам необходимо определить ваш уровень владения английским языком.</p>
            <button class="start-test-btn" onclick="startLevelTest()">Начать тест</button>
        </div>
    `;
}

// Начало теста
function startLevelTest() {
    // Отправляем сообщение в бот для начала теста
    tg.sendData(JSON.stringify({
        action: 'start_level_test'
    }));
    // Закрываем веб-приложение, чтобы пользователь мог пройти тест в боте
    tg.close();
}

// Показ основного интерфейса
function showMainInterface() {
    document.querySelector('.container').style.display = 'block';
}

// Загрузка данных пользователя
async function loadUserData(data) {
    // Обновляем аватар
    const avatarElement = document.querySelector('.avatar');
    if (data.photo_url) {
        avatarElement.style.backgroundImage = `url(${data.photo_url})`;
        avatarElement.style.backgroundSize = 'cover';
        avatarElement.style.backgroundPosition = 'center';
    } else {
        avatarElement.textContent = data.name.charAt(0).toUpperCase();
        avatarElement.style.backgroundColor = getRandomColor(data.name);
    }
    
    // Обновляем информацию пользователя
    document.getElementById('username').textContent = data.name;
    document.getElementById('level').textContent = `Level: ${data.level}`;
    document.getElementById('messages-count').textContent = data.messages;
    document.getElementById('exercises-count').textContent = data.exercises;
    document.getElementById('streak-days').textContent = data.streak;
}

// Генерация цвета для аватара
function getRandomColor(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
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