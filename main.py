import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Чтение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MIN_RATE = float(os.getenv("MIN_RATE"))
MAX_RATE = float(os.getenv("MAX_RATE"))
UPDATE_INTERVAL_MIN = int(os.getenv("UPDATE_INTERVAL_MIN"))
ADMIN_PASS = os.getenv("ADMIN_PASS")

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Глобальное состояние
current_rate = round(random.uniform(MIN_RATE, MAX_RATE), 2)

# Функция обновления курса
async def update_rate():
    global current_rate
    while True:
        current_rate = round(random.uniform(MIN_RATE, MAX_RATE), 2)
        await asyncio.sleep(UPDATE_INTERVAL_MIN * 60)

# Команда /start
@dp.message(commands=["start"])
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="📈 Узнать курс", callback_data="get_rate")
    await message.answer("Добро пожаловать в K‑VALVI.\nВыберите действие:", reply_markup=kb.as_markup())

# Обработка кнопки
@dp.callback_query(lambda c: c.data == "get_rate")
async def get_rate_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(f"<b>Текущий курс:</b> {current_rate} K‑VALVI")

# Команда /set_range
@dp.message(commands=["set_range"])
async def set_range(message: Message):
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer("Формат: /set_range min max пароль")
        return
    min_val, max_val, password = parts[1], parts[2], parts[3]
    if password != ADMIN_PASS:
        await message.answer("Неверный пароль.")
        return
    try:
        global MIN_RATE, MAX_RATE
        MIN_RATE = float(min_val)
        MAX_RATE = float(max_val)
        await message.answer(f"Диапазон обновлён: {MIN_RATE}–{MAX_RATE}")
    except ValueError:
        await message.answer("Ошибка: значения должны быть числами.")

# Команда /get_range
@dp.message(commands=["get_range"])
async def get_range(message: Message):
    await message.answer(f"Текущий диапазон: {MIN_RATE}–{MAX_RATE}")

# Команда /about
@dp.message(commands=["about"])
async def about(message: Message):
    await message.answer(
        "<b>K‑VALVI</b> — официальная система единого валютного курса.\n"
        "Курс обновляется каждые 5 минут и отображается всем пользователям одинаково.\n"
        "Прозрачность. Контроль. Надёжность."
    )

# Запуск
async def main():
    asyncio.create_task(update_rate())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
