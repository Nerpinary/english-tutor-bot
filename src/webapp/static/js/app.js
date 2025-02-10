let tg = window.Telegram.WebApp;
let chat;

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initializing...');
    
    // Выводим все доступные данные из Telegram
    console.log('Telegram WebApp:', {
        initDataUnsafe: tg.initDataUnsafe,
        initData: tg.initData,
        version: tg.version,
        platform: tg.platform,
        colorScheme: tg.colorScheme,
        themeParams: tg.themeParams,
    });

    // Если есть данные пользователя, выводим их
    if (tg.initDataUnsafe?.user) {
        console.log('Telegram User:', {
            id: tg.initDataUnsafe.user.id,
            first_name: tg.initDataUnsafe.user.first_name,
            last_name: tg.initDataUnsafe.user.last_name,
            username: tg.initDataUnsafe.user.username,
            language_code: tg.initDataUnsafe.user.language_code
        });
    }

    initializeApp();
});

async function initializeApp() {
    try {
        tg.ready();
        tg.expand();

        const userId = tg.initDataUnsafe?.user?.id;
        if (!userId) {
            throw new Error('No user ID available');
        }

        // Загружаем данные пользователя
        const userData = await loadUserData(userId);
        
        // Инициализируем чат
        chat = new AIChat(userId, userData.level);
        const chatContainer = await chat.init();
        document.getElementById('chat-view').appendChild(chatContainer);

        // Настраиваем навигацию
        setupNavigation();

        // Загружаем начальный вид
        showView('dashboard');

        // Устанавливаем обработчик закрытия
        tg.onEvent('viewportChanged', handleViewportChange);

    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize app');
    }
}

// Загрузка данных с сервера
async function loadUserData(userId) {
    const response = await fetch(`/api/user-data?user_id=${userId}`);
    if (!response.ok) {
        throw new Error('Failed to load user data');
    }
    const data = await response.json();
    updateUserInfo(data);
    return data;
}

function updateUserInfo(data) {
    document.getElementById('username').textContent = data.name;
    document.getElementById('level').textContent = `Level: ${data.level}`;
    document.getElementById('messages-count').textContent = data.messages;
    document.getElementById('exercises-count').textContent = data.exercises;
    document.getElementById('streak-days').textContent = data.streak;

    const avatar = document.querySelector('.avatar');
    if (data.photo_url) {
        avatar.style.backgroundImage = `url(${data.photo_url})`;
    } else {
        avatar.textContent = data.name.charAt(0).toUpperCase();
    }
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            showView(view);
            
            // Обновляем активную кнопку
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function showView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => {
        view.style.display = view.id === `${viewName}-view` ? 'block' : 'none';
    });
}

async function handleViewportChange() {
    if (!tg.isExpanded) {
        // Приложение закрывается
        const sessionStats = chat.getSessionDuration();
        await fetch('/api/end-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: tg.initDataUnsafe.user.id,
                duration: sessionStats.duration,
                messages_count: sessionStats.messages
            })
        });
    }
}

function showError(message) {
    // Показываем ошибку пользователю
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
}

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
        console.log('Checking level for user:', userId);
        
        // Добавляем явный протокол и хост, если их нет
        const apiUrl = new URL('/api/user-data', window.location.origin);
        apiUrl.searchParams.set('user_id', userId);
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('User data:', data);
        
        if (!data.level || data.level === 'undefined' || data.level === 'Unknown') {
            showLevelTest();
        } else {
            loadUserData(data);
            showMainInterface();
        }
    } catch (error) {
        console.error('Error checking user level:', error);
        document.getElementById('username').textContent = 'Error loading data';
        document.getElementById('level').textContent = 'Please try again';
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

// Генерация цвета для аватара
function getRandomColor(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
}

// Показ упражнений
function showExercises() {
    const exercisesModal = document.createElement('div');
    exercisesModal.className = 'modal';
    exercisesModal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Exercises</h3>
                <button class="close-btn" onclick="closeModal(this)">&times;</button>
            </div>
            <div class="modal-body">
                <div class="exercise-item" onclick="startExercise('grammar')">
                    <span class="exercise-icon">📝</span>
                    <h4>Grammar</h4>
                    <p>Practice your grammar skills</p>
                </div>
                <div class="exercise-item" onclick="startExercise('vocabulary')">
                    <span class="exercise-icon">📚</span>
                    <h4>Vocabulary</h4>
                    <p>Learn new words</p>
                </div>
                <div class="exercise-item" onclick="startExercise('listening')">
                    <span class="exercise-icon">🎧</span>
                    <h4>Listening</h4>
                    <p>Improve your listening skills</p>
                </div>
                <div class="exercise-item" onclick="startExercise('speaking')">
                    <span class="exercise-icon">🗣</span>
                    <h4>Speaking</h4>
                    <p>Practice pronunciation</p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(exercisesModal);
}

// Закрытие модального окна
function closeModal(element) {
    element.closest('.modal').remove();
}

// Начало упражнения
function startExercise(type) {
    // Отправляем сообщение в бот
    tg.sendData(JSON.stringify({
        action: 'start_exercise',
        type: type
    }));
    // Закрываем веб-приложение
    tg.close();
}

// Аналогично для других разделов
function showLessons() {
    const lessonsModal = document.createElement('div');
    lessonsModal.className = 'modal';
    lessonsModal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Lessons</h3>
                <button class="close-btn" onclick="closeModal(this)">&times;</button>
            </div>
            <div class="modal-body">
                <div class="lesson-item" onclick="startLesson('basic')">
                    <span class="lesson-icon">📖</span>
                    <h4>Basic English</h4>
                    <p>Start with the basics</p>
                </div>
                <div class="lesson-item" onclick="startLesson('intermediate')">
                    <span class="lesson-icon">📚</span>
                    <h4>Intermediate</h4>
                    <p>More complex topics</p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(lessonsModal);
}

function showChat() {
    tg.sendData(JSON.stringify({
        action: 'open_chat'
    }));
    tg.close();
}

function showGoals() {
    const goalsModal = document.createElement('div');
    goalsModal.className = 'modal';
    goalsModal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Your Goals</h3>
                <button class="close-btn" onclick="closeModal(this)">&times;</button>
            </div>
            <div class="modal-body">
                <div class="goals-list">
                    <div class="goal-item">
                        <h4>Daily Practice</h4>
                        <div class="progress-bar">
                            <div class="progress" style="width: 60%"></div>
                        </div>
                        <p>3/5 exercises completed</p>
                    </div>
                    <div class="goal-item">
                        <h4>Weekly Lessons</h4>
                        <div class="progress-bar">
                            <div class="progress" style="width: 40%"></div>
                        </div>
                        <p>2/5 lessons completed</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(goalsModal);
} 