import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = 'YOUR_API_TOKEN'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bot = Bot("6000288006:AAEMQUjpJOytrLQXtf9KxMdN2Kaax93ijr4")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

class UserInfo(StatesGroup):
    last_name = State()
    first_name = State()
    middle_name = State()
    age = State()
    phone_number = State()

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Введите вашу Фамилию:")
    await UserInfo.last_name.set()

@dp.message_handler(lambda message: message.text, state=UserInfo.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await UserInfo.next()
    await message.answer("Введите ваше Имя:")

@dp.message_handler(lambda message: message.text, state=UserInfo.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await UserInfo.next()
    await message.answer("Введите ваше Отчество:")

@dp.message_handler(lambda message: message.text, state=UserInfo.middle_name)
async def process_middle_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['middle_name'] = message.text

    await UserInfo.next()
    await message.answer("Введите ваш возраст:")

@dp.message_handler(lambda message: message.text.isdigit(), state=UserInfo.age)
async def process_age(message: types.Message, state: FSMContext):
    age = int(message.text)
    async with state.proxy() as data:
        data['age'] = age

    await UserInfo.next()
    await message.answer("Введите ваш номер:")

@dp.message_handler(lambda message: re.fullmatch(r'\+7\d{10}', message.text), state=UserInfo.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

        user_info = f"Фамилия: {data['last_name']}\n" \
                    f"Имя: {data['first_name']}\n" \
                    f"Отчество: {data['middle_name']}\n" \
                    f"Возраст: {data['age']}\n" \
                    f"Номер: {data['phone_number']}"

    await message.answer("Ваши данные:\n" + user_info)
    await state.finish()

@dp.message_handler(lambda message: not re.fullmatch(r'\+7\d{10}', message.text), state=UserInfo.phone_number)
async def process_invalid_phone_number(message: types.Message):
    await message.answer("Введите корректный номер телефона, начинающийся с '+7' и содержащий 11 цифр.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling
