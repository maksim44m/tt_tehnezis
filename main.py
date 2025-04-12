import asyncio
import os
import time

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from config import EXCEL_DIR
from utils import read_xlsx
from db import save_to_db, get_all_title_avg_price
from parser import run_parser

dp = Dispatcher()
router = Router()
dp.include_router(router)


@router.message(Command('start'))
async def start(message: Message):
    """Старт и вывод кнопки 'Загрузить файл'"""
    button = KeyboardButton(text='Загрузить файл')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button]],
                                   is_persistent=True,
                                   resize_keyboard=True)
    await message.answer(
        'Отправьте файл *.xlsx и нажмите "Загрузить файл" для его обработки',
        reply_markup=keyboard
    )


@router.message(F.text == "Загрузить файл")
async def upload(message: Message, state: FSMContext, bot: Bot):
    """Загрузка и сохранение файла. Чтение и вывод содержимого"""
    data = await state.get_data()
    file = await bot.get_file(data['file_id'])
    file_path = file.file_path
    file_name = f'data_{time.time()}.xlsx'
    destination = EXCEL_DIR / file_name
    await bot.download_file(file_path, destination)
    await state.clear()
    df = await read_xlsx(destination)
    # если вернулась ошибка - отправить ошибку
    answer = df if isinstance(df, str) else df.to_string()
    await message.answer(text=answer)
    save_to_db(df)
    await run_parser()

    result = get_all_title_avg_price()
    text = '\n'.join(f'{i[0]} = {i[1]} руб.' for i in result)
    await message.answer(text=f'Проверка цен завершена. Средние цены:\n{text}')


@router.message(F.content_type.in_({'document', }))
async def save_target_msg_id(message: Message, state: FSMContext):
    """Сохранение данных о загруженном файле"""
    await state.update_data(file_id=message.document.file_id)


async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
