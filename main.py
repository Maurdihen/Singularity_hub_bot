import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

storage = MemoryStorage()

bot = Bot("6000288006:AAEMQUjpJOytrLQXtf9KxMdN2Kaax93ijr4")
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class UserInfo(StatesGroup):
    last_name = State()
    first_name = State()
    middle_name = State()
    age = State()
    phone_number = State()
    percent = State


@dp.message_handler(commands=["start"])
async def handle_start_command(message: types.Message):
    await bot.send_sticker(message.chat.id, "CAACAgEAAxkBAAIpamQoRqS1makh9CPrB5HGlK1tVYUcAAKlAgACRv7wRzjrsF8nFDx2LwQ")
    inline_markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton("Мероприятия", callback_data="events")
    )
    await bot.send_message(chat_id=message.chat.id, text=f"Здравствуйте {message.from_user.username}, я бот Singularity Hub - meet, хотите приобрести бесплатные билеты на наши мероприятия?", reply_markup=inline_markup)

@dp.callback_query_handler(lambda call: call.data == 'events')
async def events_handler(call: types.CallbackQuery):
    inline_markup = InlineKeyboardMarkup().row(
        InlineKeyboardButton("19.05.2023 - Герман Гаврилов - Предприниматель", callback_data="event_1")
    )
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вот доступные мероприятия:', reply_markup=inline_markup)

@dp.callback_query_handler(lambda call: call.data == 'event_1')
async def event1_handler(call: types.CallbackQuery):
    text = "19.05.2023 - Герман Гаврилов - Предприниматель.\n\n*Всякая инфа*\n\nМесто: …\nВремя: …\nСвободные места: Имеются"
    inline_markup = types.InlineKeyboardMarkup(row_width=2).add(
        types.InlineKeyboardButton("Взять билет", callback_data="get_ticket"),
        types.InlineKeyboardButton("Назад к мероприятиям", callback_data="events")
    )
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=inline_markup, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query_handler(lambda call: call.data == 'get_ticket')
async def event_get_ticket_handler(call: types.CallbackQuery):
    await bot.send_message(chat_id=call.message.chat.id, text="Введите вашу Фамилию:")
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

@dp.message_handler(lambda message: not message.text.isdigit(), state=UserInfo.age)
async def process_age(message: types.Message):
    await message.answer("Введите корректный возраст:")

...
@dp.message_handler(lambda message: re.fullmatch(r'\+7\d{10}', message.text), state=UserInfo.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

        user_info = f"Фамилия: {data['last_name']}\n" \
                    f"Имя: {data['first_name']}\n" \
                    f"Отчество: {data['middle_name']}\n" \
                    f"Возраст: {data['age']}\n" \
                    f"Номер: {data['phone_number']}"

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("Точно", callback_data="sure"),
        InlineKeyboardButton("50/50", callback_data="maybe"),
        InlineKeyboardButton("Врядли", callback_data="unlikely")
    )
    await message.answer("Ваши данные:\n" + user_info)
    await message.answer("Ваши данные записанны. Вы точно будете на мероприятии?", reply_markup=markup)
    await state.finish()

@dp.message_handler(lambda message: not re.fullmatch(r'\+7\d{10}', message.text), state=UserInfo.phone_number)
async def process_invalid_phone_number(message: types.Message):
    await message.answer("Введите корректный номер телефона, начинающийся с '+7' и содержащий 11 цифр.")

@dp.callback_query_handler(lambda call: call.data in ['sure', 'maybe', 'unlikely'])
async def process_event_decision(call: types.CallbackQuery):
    if call.data == 'sure':
        await call.answer("Отлично! Мы ждем вас на мероприятии.")
    elif call.data == 'maybe':
        await call.answer("Поняли, надеемся увидеть вас на мероприятии.")
    else:
        await call.answer("Жаль, что вы не сможете прийти. Возможно, увидимся на других мероприятиях.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
