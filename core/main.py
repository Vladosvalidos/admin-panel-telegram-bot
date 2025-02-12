import asyncio
import requests
import sqlite3
from random import randint
from datetime import date
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = ''

admins = [242494911, 689892377, 983265598]

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключение к базе данных SQLite
connect = sqlite3.connect('admin.db')
cursor = connect.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id TEXT, joining_date TEXT)")
connect.commit()

# Текст сообщений
hello = """Hello! You are using the "Arbitration Goose" command bot.

✅ In this bot, you can get a photo to pass the checkpoint.

Brief instructions:
1. Click the "👨 Get a photo to pass the checkpoint" button.
2. Refresh the photo until you get the desired face.
3. Download the file to your device.
4. Upload the file from your device to Tsuker's account (Facebook).

❗️Attention
You need to upload the photo from your device, don't upload it directly from Telegram to Facebook, as the photo won't pass the checkpoint."""

chat = """❤️ And don't forget to join our chat, where we share up-to-date information about FB uploads, tricks, and much more."""

# Клавиатура
def get_main_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(types.KeyboardButton(text="👨Получить фото для прохода чекпоинта"))
    return keyboard.as_markup(resize_keyboard=True)

# Состояния FSM
class States(StatesGroup):
    text = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = str(message.chat.id)
    if cursor.execute(f"SELECT * FROM users WHERE id='{user_id}'").fetchone() is None:
        joining_date_text = date.today().strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO users (id, joining_date) VALUES (?, ?)", (user_id, joining_date_text))
        connect.commit()

    await message.answer(hello, reply_markup=get_main_keyboard())
    await message.answer(chat, reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="📣Наш ЧАТ", url="https://t.me/arbi_goose_chat")]]
    ))

# Обработчик команды /message для админов
@dp.message(Command("message"))
async def sending(message: Message, state: FSMContext):
    if message.chat.id in admins:
        await message.answer("Введите сообщение, которое хотите отправить пользователям")
        await state.set_state(States.text)
    else:
        await start_handler(message)

# Обработчик отправки сообщений пользователям
@dp.message(States.text)
async def end_sending(message: Message, state: FSMContext):
    await state.clear()
    for user in cursor.execute("SELECT id FROM users WHERE id != ?", (message.chat.id,)).fetchall():
        try:
            await bot.send_message(user[0], f"Сообщение от администратора:\n\n{message.text}", reply_markup=get_main_keyboard())
        except:
            pass
    await message.answer("Сообщение отправлено", reply_markup=get_main_keyboard())

# Обработчик получения фото
@dp.message()
async def handle_messages(message: Message):
    if message.text in ["👨Получить фото для прохода чекпоинта", "🔄Обновить"]:
        async with requests.Session() as session:
            site = session.get('https://this-person-does-not-exist.com')
            parser = BeautifulSoup(site.text, 'html.parser')
            image_url = 'https://this-person-does-not-exist.com' + parser.find('img', id='avatar')['src']
            data = session.get(image_url)

        photo = (f'image{randint(1000, 9999)}.jpeg', data.content)
        keyboard = ReplyKeyboardBuilder()
        keyboard.add(types.KeyboardButton(text="🔄Обновить"))

        await message.answer_document(document=photo, reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        await start_handler(message)

# Функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
