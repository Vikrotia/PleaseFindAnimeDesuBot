from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API
from config import START_TEXT
from config import ERROR_TEXT
import os
from config import HELP_TEXT
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher import FSMContext
from main_class import AnimeFinder

PROXY_URL = "http://proxy.server:3128"
storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage, proxy=PROXY_URL)

class ClientStatesGroup(StatesGroup):
    link_state = State()
    upload_state = State()
    more_state = State()

def start_keyboard() -> InlineKeyboardMarkup:
    b1 = InlineKeyboardButton(text='Upload a screenshot from device', callback_data='upload')
    b2 = InlineKeyboardButton(text='Send screenshot link', callback_data='link')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[b1], [b2]])
    return keyboard

def end_processing_keyboard() -> InlineKeyboardMarkup:
    b1 = InlineKeyboardButton(text='Upload a screenshot from device', callback_data='upload')
    b2 = InlineKeyboardButton(text='Send screenshot link', callback_data='link')
    b3 = InlineKeyboardButton(text='More information on this request', callback_data='more')
    b4 = InlineKeyboardButton(text='End search', callback_data='end')
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[b1], [b2], [b3], [b4]])
    return keyboard

def more_keyboard() -> ReplyKeyboardMarkup:
    b1 = KeyboardButton('More information on this request')
    b2 = KeyboardButton('End search')
    b3 = KeyboardButton('Start over')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(b1, b2).add(b3)
    return keyboard


@dp.message_handler(regexp="start")
async def start_command(message: types.Message):
    await message.answer(text=START_TEXT, reply_markup=start_keyboard())
    await message.delete()

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_TEXT, reply_markup=start_keyboard())
    await message.delete()

@dp.message_handler(commands=['end'])
async def start_command(message: types.Message):
    await message.answer(text="Bye!")
    await message.delete()

@dp.message_handler(content_types=['photo'], state=ClientStatesGroup.upload_state)
async def upload_parsing(message, state: FSMContext):
    path = str(message.photo[-1].file_id) + '.jpg'
    await message.photo[-1].download(path)
    sample1 = AnimeFinder()
    if sample1.ProcessingScreen(path) == 0:
        await bot.send_photo(chat_id=message.chat.id, photo=sample1.info[4], caption=sample1.aboutanime)
        await message.answer(text="Do you want to continue?", reply_markup=more_keyboard())
        await message.delete()
    else:
        await bot.send_message(chat_id=message.chat.id, text=ERROR_TEXT)

    @dp.message_handler(lambda message: message.text and 'More information on this request' in message.text)
    async def upload_parsing1(message: types.Message):
        await message.answer(text=sample1.MoreInforation())
        await bot.send_message(chat_id=message.chat.id, text="Search:", reply_markup=start_keyboard())

    @dp.message_handler(lambda message: message.text and 'End search' in message.text)
    async def upload_parsing1(message: types.Message):
        await message.answer(text="Bye!")

    os.remove(path)
    await state.finish()

@dp.message_handler(content_types=['text'], state=ClientStatesGroup.upload_state)
async def upload_error(message: types.Message):
    return await bot.send_message(chat_id=message.chat.id, text="This is not a screen")

@dp.message_handler(lambda message: message.text and 'https://' in message.text, state=ClientStatesGroup.link_state)
async def link_parsing(message: types.Message, state: FSMContext):
    linkscreen = message.text
    sample2 = AnimeFinder()
    if sample2.ProcessingURL(linkscreen) == 0:
        await bot.send_photo(chat_id=message.chat.id, photo=sample2.info[4], caption=sample2.aboutanime)
        await message.answer(text="Do you want to continue?", reply_markup=more_keyboard())
        await message.delete()
    else:
        await bot.send_message(chat_id=message.chat.id, text=ERROR_TEXT)

    @dp.message_handler(lambda message: message.text and 'More information on this request' in message.text)
    async def upload_parsing1(message: types.Message):
        await message.answer(text=sample2.more)
        await bot.send_message(chat_id=message.chat.id, text="Search:", reply_markup=start_keyboard())

    @dp.message_handler(lambda message: message.text and 'End search' in message.text)
    async def upload_parsing1(message: types.Message):
        await message.answer(text="Bye!")

    await state.finish()


@dp.message_handler(lambda message: message.text and 'https://' not in message.text, state=ClientStatesGroup.link_state)
async def link_error(message: types.Message):
    return await bot.send_message(chat_id=message.chat.id, text="This is not a link")

@dp.callback_query_handler()
async def callback_button(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'upload':
        await callback.message.edit_text(text='Please upload a screenshot from your device')
        await ClientStatesGroup.upload_state.set()
    elif callback.data == 'link':
        await callback.message.edit_text(text='Please send screenshot link')
        await ClientStatesGroup.link_state.set()
    elif callback.data == 'more':
        await ClientStatesGroup.more_state.set()
    elif callback.data == 'end':
        await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
