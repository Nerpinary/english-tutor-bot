from telegram import Update
from src.bot_init import setup_bot

def main():
    # Инициализация бота
    app = setup_bot()
    print("Бот запущен...")
    # Запускаем бота без asyncio.run()
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен") 