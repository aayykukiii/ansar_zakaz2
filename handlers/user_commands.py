from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database import crud

router = Router()


@router.message(Command('start'))
async def start_cmd(message: Message):
    # Админская часть меню остаётся прежней
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
        return

    # Клиентское меню: генерируем кнопки динамически из БД
    cats = await crud.list_categories()
    if not cats:
        # Если категорий нет в БД, показываем базовое статическое меню (резерв)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="about:info")],
        ])
        await message.answer("Привет! Категории пока не добавлены. Вот контакты:", reply_markup=kb)
        return

    # Собираем кнопки из категорий, по одной в строке
    buttons = [[InlineKeyboardButton(text=c.name, callback_data=f"cat:{c.name}")] for c in cats]
    # добавляем кнопку информации внизу
    buttons.append([InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="about:info")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Привет! Выберите категорию мебели:", reply_markup=kb)
