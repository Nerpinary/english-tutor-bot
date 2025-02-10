import google.generativeai as genai
from src.config import GOOGLE_API_KEY

class AIHandler:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def get_response(self, message: str, level: str = 'A1') -> str:
        try:
            # Создаем чат
            chat = self.model.start_chat(history=[])
            
            # Задаем более конкретный промпт для естественного общения
            system_prompt = f"""You are a friendly English tutor. Keep your responses:
            1. Short (2-3 sentences max)
            2. Natural and conversational
            3. Appropriate for {level} level
            4. If you see a mistake, correct it briefly
            5. Always stay in context of the conversation
            6. Ask follow-up questions to keep the conversation going
            
            Don't write long explanations unless specifically asked."""
            
            chat.send_message(system_prompt)
            
            # Получаем ответ на сообщение пользователя
            response = chat.send_message(message)
            
            return response.text
            
        except Exception as e:
            return f"Извините, произошла ошибка: {str(e)}" 