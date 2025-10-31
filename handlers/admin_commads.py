from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if message.from_user.id == ADMIN_ID:
        username = message.from_user.username or message.from_user.full_name or "admin"
        text = f"Здравствуйте, {username} (id: {message.from_user.id}). Выберите действие:"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1. Добавить категорию", callback_data="adm:add_category")],
            [InlineKeyboardButton(text="2. Добавить мебель", callback_data="adm:add_product")],
            [InlineKeyboardButton(text="3. Удалить мебель", callback_data="adm:delete_product")],
            [InlineKeyboardButton(text="4. Заявки", callback_data="adm:orders")],
            [InlineKeyboardButton(text="5. Список категорий", callback_data="adm:list_categories")],
        ])
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer("У тебя нет прав.")
