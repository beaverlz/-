from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import random
from datetime import datetime, timedelta
import asyncio

# Загрузка данных из файла
def load_data():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохранение данных в файл
def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Настройка Telegram бота
TELEGRAM_TOKEN = "7783523478:AAFQ6l28kJb77aSW_Nd_NdTiHVrXcuFTv8k"  # Замените на ваш токен

# Загрузка данных при старте
data = load_data()

# Список из 20 советов (общий для всех пользователей)
advice_list = [
    "Разделяйте задачи на мелкие шаги.",
    "Используйте технику Pomodoro: 25 минут работы, 5 минут отдыха.",
    "Составляйте список задач на каждый день.",
    "Не откладывайте сложные задачи на потом.",
    "Регулярно делайте перерывы, чтобы избежать переутомления.",
    "Используйте планировщик задач для организации времени.",
    "Ставьте перед собой реалистичные цели.",
    "Учитесь говорить 'нет', чтобы не перегружать себя.",
    "Планируйте время для отдыха и развлечений.",
    "Используйте утренние часы для самых важных задач.",
    "Не бойтесь просить помощи, если это необходимо.",
    "Ведите дневник успехов, чтобы отслеживать прогресс.",
    "Избегайте многозадачности — сосредоточьтесь на одном деле.",
    "Регулярно пересматривайте свои цели и планы.",
    "Используйте напоминания, чтобы не забывать о важных делах.",
    "Учитесь делегировать задачи, если это возможно.",
    "Создайте комфортное рабочее пространство.",
    "Планируйте время для физической активности.",
    "Избегайте отвлекающих факторов, таких как социальные сети.",
    "Регулярно обновляйте свои знания и навыки."
]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in data:
        data[user_id] = {"deadlines": []}
        save_data(data)

    await update.message.reply_text(
        "Привет! Я твой бот-помощник для учёбы. Вот что я могу:\n"
        "1. /add_deadline <описание> <дата> - добавить дедлайн.\n"
        "2. /deadlines - показать все дедлайны.\n"
        "3. /remove_deadline <номер> - удалить дедлайн.\n"
        "4. /advice - получить случайный совет.\n"
        "5. /help - показать список команд."
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "1. /add_deadline <описание> <дата> - добавить дедлайн.\n"
        "2. /deadlines - показать все дедлайны.\n"
        "3. /remove_deadline <номер> - удалить дедлайн.\n"
        "4. /advice - получить случайный совет.\n"
        "5. /help - показать список команд."
    )

# Команда /add_deadline
async def add_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in data:
        data[user_id] = {"deadlines": []}

    try:
        # Получаем аргументы команды
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Используйте: /add_deadline <описание> <дата>")
            return

        description = " ".join(args[:-1])  # Описание дедлайна
        date = args[-1]  # Дата дедлайна

        # Проверяем формат даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await update.message.reply_text("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
            return

        # Добавляем дедлайн в список
        data[user_id]["deadlines"].append({"description": description, "date": date})
        save_data(data)
        await update.message.reply_text(f"Дедлайн добавлен: {description} до {date}")
    except Exception as e:
        await update.message.reply_text("Ошибка при добавлении дедлайна.")

# Команда /deadlines
async def show_deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in data or not data[user_id]["deadlines"]:
        await update.message.reply_text("Дедлайнов пока нет.")
        return

    # Формируем список дедлайнов
    response = "Ваши дедлайны:\n"
    for i, deadline in enumerate(data[user_id]["deadlines"], 1):
        response += f"{i}. {deadline['description']} до {deadline['date']}\n"

    await update.message.reply_text(response)

# Команда /remove_deadline
async def remove_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in data or not data[user_id]["deadlines"]:
        await update.message.reply_text("Дедлайнов пока нет.")
        return

    try:
        # Получаем номер дедлайна
        if not context.args:
            await update.message.reply_text("Используйте: /remove_deadline <номер>")
            return

        index = int(context.args[0]) - 1

        # Проверяем, существует ли дедлайн
        if 0 <= index < len(data[user_id]["deadlines"]):
            removed_deadline = data[user_id]["deadlines"].pop(index)
            save_data(data)
            await update.message.reply_text(f"Дедлайн удалён: {removed_deadline['description']} до {removed_deadline['date']}")
        else:
            await update.message.reply_text("Неверный номер дедлайна.")
    except Exception as e:
        await update.message.reply_text("Ошибка при удалении дедлайна.")

# Команда /advice
async def get_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Выбираем случайный совет
    random_advice = random.choice(advice_list)
    await update.message.reply_text(f"Совет: {random_advice}")

# Функция для проверки дедлайнов
async def check_deadlines(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    for user_id, user_data in data.items():
        for deadline in user_data["deadlines"]:
            deadline_date = datetime.strptime(deadline["date"], "%Y-%m-%d").date()
            days_left = (deadline_date - today).days

            if 0 < days_left <= 3:  # Уведомление за 3 дня до дедлайна
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Напоминание: до дедлайна '{deadline['description']}' осталось {days_left} дней."
                )
            elif days_left == 0:  # Уведомление в день дедлайна
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Сегодня последний день для дедлайна: '{deadline['description']}'!"
                )

# Запуск бота
def main():
    # Создаём приложение и передаём токен
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_deadline", add_deadline))
    application.add_handler(CommandHandler("deadlines", show_deadlines))
    application.add_handler(CommandHandler("remove_deadline", remove_deadline))
    application.add_handler(CommandHandler("advice", get_advice))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()