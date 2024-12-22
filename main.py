import asyncio
import subprocess
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import time
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Hello! I can help you find user profiles on social networks. Enter the username you need.")

def create_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Search Again", callback_data="search_again")],
        [InlineKeyboardButton(text="Exit", callback_data="exit")]
    ])
    return keyboard

@dp.message()
async def search_user(message: Message):
    username = message.text.strip()
    await message.answer(f"I am looking for: {username}. Wait a bit...")

    try:
        process = await asyncio.create_subprocess_exec(
            "sherlock", username, "--print-found",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            results = stdout.decode().splitlines()
            for line in results:
                if line.strip():
                    time.sleep(1)
                    await message.answer(f"`{line}`", parse_mode="Markdown")
            await message.answer("Would you like to search again or exit?", reply_markup=create_keyboard())
        else:
            await message.answer("No results found.")
            await message.answer("Would you like to search again or exit?", reply_markup=create_keyboard())
    except Exception as e:
        await message.answer(f"Error: {str(e)}")

# Обработчик нажатий на кнопки
@dp.callback_query()
async def handle_callback(call: CallbackQuery):
    if call.data == "search_again":
        await call.answer("Starting new search.")
        await call.message.answer("Enter the username you need.")
    elif call.data == "exit":
        await call.answer("Goodbye!")
        await call.message.answer("Goodbye! Have a great day.")

# Основная асинхронная функция
async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
