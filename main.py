import os
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
MIN_RATE = float(os.getenv("MIN_RATE", "65.80"))
MAX_RATE = float(os.getenv("MAX_RATE", "70.50"))
UPDATE_INTERVAL_MIN = int(os.getenv("UPDATE_INTERVAL_MIN", "5"))
ADMIN_PASS = os.getenv("ADMIN_PASS", "adminpass")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

state = {
    "rate": round(random.uniform(MIN_RATE, MAX_RATE), 2),
    "last_update": datetime.utcnow().isoformat()
}

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def smooth_step(current: float) -> float:
    step = random.uniform(0.01, 0.08)
    direction = random.choice([-1, 1])
    next_rate = current + direction * step
    if next_rate < MIN_RATE or next_rate > MAX_RATE:
        next_rate = current - direction * step
    return round(clamp(next_rate, MIN_RATE, MAX_RATE), 2)

async def rate_updater():
    while True:
        await asyncio.sleep(UPDATE_INTERVAL_MIN * 60)
        state["rate"] = smooth_step(state["rate"])
        state["last_update"] = datetime.utcnow().isoformat()

def header() -> str:
    return "<b>K‑VALVI</b>\nКурс в основной планетной 220 валюты\n"

def menu() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Текущий курс в долларах", callback_data="rate_now")
    return kb.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(header() + "Нажмите кнопку, чтобы узнать курс.", reply_markup=menu())

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if call.data == "rate_now":
        await call.message.edit_text(header() + "⏳ Загрузка курса…")
        await asyncio.sleep(2)
        await call.message.edit_text(
            header() + f"Текущий курс: <b>{state['rate']}$</b>\nОбновляется каждые {UPDATE_INTERVAL_MIN} минут.",
            reply_markup=menu()
        )
        await call.answer()

@dp.message(Command("set_range"))
async def set_range(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) != 4:
        await message.answer("Используй: /set_range <min> <max> <adminpass>")
        return
    _, smin, smax, apass = parts
    if apass != ADMIN_PASS:
        await message.answer("Неверный пароль.")
        return
    try:
        new_min, new_max = float(smin), float(smax)
        if new_min >= new_max:
            await message.answer("Минимум должен быть меньше максимума.")
            return
    except ValueError:
        await message.answer("min/max должны быть числами.")
        return
    global MIN_RATE, MAX_RATE
    MIN_RATE, MAX_RATE = new_min, new_max
    state["rate"] = clamp(state["rate"], MIN_RATE, MAX_RATE)
    await message.answer(f"Диапазон обновлён: {MIN_RATE:.2f} — {MAX_RATE:.2f}. Текущий курс: {state['rate']:.2f}$")

async def main():
    asyncio.create_task(rate_updater())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
