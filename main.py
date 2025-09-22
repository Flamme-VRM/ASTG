import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")
ADMIN_ID1=os.getenv("ADMIN_ID1")
ADMIN_ID2=os.getenv("ADMIN_ID2")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class AnonymousState(StatesGroup):
    waiting_message = State()

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    welcome_text = """
🔒 <b>Барлығы анонимно </b>

Өз идеяңмен бөліс оны Данияр мектептін президенті қарастыратын болады

125 HS - Т. Рысқуловтың виртуалды жәшігі
"""
    
    await message.answer(
        welcome_text,
        parse_mode="HTML"
    )
    
    await state.set_state(AnonymousState.waiting_message)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
ℹ️ <b>Как пользоваться:</b>

1. Напиши /start
2. Отправь любое сообщение
3. Оно анонимно придет администратору

<b>Поддерживаются:</b>
* Текст
* Фото
* Видео
* Документы
* Голосовые сообщения
"""
    
    await message.answer(help_text, parse_mode="HTML")

@dp.message(AnonymousState.waiting_message)
async def handle_anonymous_message(message: Message, state: FSMContext):
    try:
        admin_text = f"📩 <b>Новое анонимное сообщение</b>\n\n"
        
        if message.text:
            admin_text += f"💬 Текст: {message.text}"
            await asyncio.gather(
                bot.send_message(ADMIN_ID1, admin_text, parse_mode="HTML"),
                bot.send_message(ADMIN_ID2, admin_text, parse_mode="HTML")
            )
            
        elif message.photo:
            admin_text += "📸 Фото с подписью:" if message.caption else "📸 Фото"
            caption = admin_text + (f"\n\n{message.caption}" if message.caption else "")
            await asyncio.gather(
                bot.send_photo(ADMIN_ID1, message.photo[-1].file_id, caption=caption, parse_mode="HTML"),
                bot.send_photo(ADMIN_ID2, message.photo[-1].file_id, caption=caption, parse_mode="HTML")
            )

        elif message.video:
            admin_text += "🎥 Видео с подписью:" if message.caption else "🎥 Видео"
            caption = admin_text + (f"\n\n{message.caption}" if message.caption else "")
            await asyncio.gather(
                bot.send_video(ADMIN_ID1, message.video.file_id, caption=caption, parse_mode="HTML"),
                bot.send_video(ADMIN_ID2, message.video.file_id, caption=caption, parse_mode="HTML")
            )

        elif message.document:
            admin_text += "📄 Документ с подписью:" if message.caption else "📄 Документ"
            caption = admin_text + (f"\n\n{message.caption}" if message.caption else "")
            await asyncio.gather(
                bot.send_document(ADMIN_ID1, message.document.file_id, caption=caption, parse_mode="HTML"),
                bot.send_document(ADMIN_ID2, message.document.file_id, caption=caption, parse_mode="HTML")
            )
            
        elif message.voice:
            admin_text += "🎤 Голосовое сообщение"
            await asyncio.gather(
                bot.send_voice(ADMIN_ID1, message.voice.file_id, caption=admin_text, parse_mode="HTML"),
                bot.send_voice(ADMIN_ID2, message.voice.file_id, caption=admin_text, parse_mode="HTML")
            )
            
        elif message.sticker:
            admin_text += "😄 Стикер"
            await asyncio.gather(
                bot.send_sticker(ADMIN_ID1, message.sticker.file_id),
                bot.send_sticker(ADMIN_ID2, message.sticker.file_id)
            )
            await asyncio.gather(
                bot.send_message(ADMIN_ID1, admin_text, parse_mode="HTML"),
                bot.send_message(ADMIN_ID2, admin_text, parse_mode="HTML")
            )
            
        else:
            admin_text += "❓ Неизвестный тип сообщения"
            await asyncio.gather(
                bot.send_message(ADMIN_ID1, admin_text, parse_mode="HTML"),
                bot.send_message(ADMIN_ID2, admin_text, parse_mode="HTML")
            )
        
        await message.answer(
            "✅ Твое анонимное сообщение отправлено!\n\n"
            "Можешь отправить еще одно или нажать /start",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения админу: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке. Попробуй позже."
        )

@dp.message()
async def handle_other_messages(message: Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Нажми /start чтобы отправить анонимное сообщение"
    )

@dp.error()
async def error_handler(exception, update, bot):
    logging.error(f"Ошибка: {exception}")
    return True

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    bot_info = await bot.get_me()
    logging.info(f"Бот запущен: @{bot_info.username}")
    
    try:
        startup_message = ("🚀 <b>Анонимный бот запущен!</b>\n\n"
                          "Теперь пользователи могут отправлять анонимные сообщения.")
        await asyncio.gather(
            bot.send_message(ADMIN_ID1, startup_message, parse_mode="HTML"),
            bot.send_message(ADMIN_ID2, startup_message, parse_mode="HTML")
        )
    except Exception as e:
        logging.warning(f"Не удалось отправить уведомление админу: {e}")
    

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())