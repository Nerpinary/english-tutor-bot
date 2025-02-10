class AIChat {
    constructor(userId, level) {
        this.userId = userId;
        this.level = level;
        this.startTime = new Date();
        this.messages = [];
    }

    async init() {
        const chatContainer = document.createElement('div');
        chatContainer.className = 'chat-container';
        chatContainer.innerHTML = `
            <div class="chat-messages" id="chat-messages"></div>
            <div class="chat-input-container">
                <textarea 
                    class="chat-input" 
                    placeholder="Type your message..." 
                    rows="1"
                    onInput="this.parentElement.dataset.replicatedValue = this.value"
                ></textarea>
                <button class="chat-send-btn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        `;

        // Добавляем приветственное сообщение
        this.addMessage({
            role: 'assistant',
            content: `Hello! I'm your English practice assistant. Your current level is ${this.level}. How can I help you today?`
        });

        // Обработчики событий
        const input = chatContainer.querySelector('.chat-input');
        const sendBtn = chatContainer.querySelector('.chat-send-btn');

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage(input.value);
                input.value = '';
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage(input.value);
            input.value = '';
        });

        return chatContainer;
    }

    addMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${message.role}`;
        
        messageElement.innerHTML = `
            <div class="message-content">
                ${this.formatMessage(message.content)}
            </div>
            ${message.role === 'assistant' ? '<div class="message-actions">' +
                '<button onclick="chat.correctMessage(this)">Correct mistakes</button>' +
                '<button onclick="chat.explainGrammar(this)">Explain grammar</button>' +
            '</div>' : ''}
        `;

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        this.messages.push(message);
    }

    formatMessage(content) {
        // Простое форматирование текста
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    async sendMessage(content) {
        if (!content.trim()) return;

        // Добавляем сообщение пользователя
        this.addMessage({
            role: 'user',
            content: content.trim()
        });

        try {
            // Отправляем запрос на сервер
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    message: content.trim(),
                    level: this.level
                })
            });

            const data = await response.json();
            
            // Добавляем ответ ассистента
            this.addMessage({
                role: 'assistant',
                content: data.response
            });

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage({
                role: 'assistant',
                content: 'Sorry, there was an error processing your message. Please try again.'
            });
        }
    }

    async correctMessage(button) {
        const messageContent = button.closest('.chat-message').querySelector('.message-content').textContent;
        const response = await fetch('/api/correct', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: messageContent,
                level: this.level
            })
        });

        const data = await response.json();
        this.addMessage({
            role: 'assistant',
            content: data.correction
        });
    }

    async explainGrammar(button) {
        const messageContent = button.closest('.chat-message').querySelector('.message-content').textContent;
        const response = await fetch('/api/explain-grammar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: messageContent,
                level: this.level
            })
        });

        const data = await response.json();
        this.addMessage({
            role: 'assistant',
            content: data.explanation
        });
    }

    getSessionDuration() {
        const endTime = new Date();
        const duration = (endTime - this.startTime) / 1000; // в секундах
        return {
            duration,
            messages: this.messages.length
        };
    }
} 