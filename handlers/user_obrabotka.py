from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from database import crud
from states.client_states import OrderState

router = Router()

@router.callback_query(F.data.startswith("cat:"))
async def on_category(call: CallbackQuery):
    category_name = call.data.split(":", 1)[1]

    rus_tr_categories = {"🛏️ Спальная мебель", "🛋️ Мягкая мебель", "🛏️ Кровати"}
    kitchen_categories = {"🍳 Кухонная мебель"}

    if category_name in rus_tr_categories:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Российская", callback_data=f"sub:{category_name}:Российская")],
            [InlineKeyboardButton(text="Турецкая", callback_data=f"sub:{category_name}:Турецкая")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:menu")]
        ])
        await call.message.answer(f"Вы выбрали: {category_name}\nВыберите подкатегорию:", reply_markup=kb)
        await call.answer()
        return

    if category_name in kitchen_categories:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📐 Прямая", callback_data=f"sub:{category_name}:Прямая")],
            [InlineKeyboardButton(text="🔽 Угловая", callback_data=f"sub:{category_name}:Угловая")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:menu")]
        ])
        await call.message.answer(f"Вы выбрали: {category_name}\nВыберите тип кухни:", reply_markup=kb)
        await call.answer()
        return


    products = await crud.list_products_by_category_name(category_name)
    if not products:
        await call.message.answer("У этого товара пока нет подкатегории или товаров.")
        await call.answer()
        return
    

    for p in products:
        text = f"<b>{p.name}</b>\n{p.description or ''}\nСтрана: {p.country or '-'}\nРазмеры: {p.size or '-'}\nЦена: {p.price or '-'}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"ask:{p.id}"),
             InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"order:{p.id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:menu")]
        ])
        if p.photo:
            await call.message.answer_photo(photo=p.photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()
    

@router.callback_query(F.data == "about:info")
async def about_info_handler(call: CallbackQuery):
    await call.message.answer(
        "📞 Контакты:\n"
        "🏢 Компания по продаже мебели\n"
        "📍 Грозный, ул. Мебельная, 10\n"
        "📱 +7 (995) 800-89-95"
    )
    await call.answer()


@router.callback_query(F.data.startswith("sub:"))
async def on_subcategory(call: CallbackQuery):
    _, category_name, subcategory = call.data.split(":", 2)
    products = await crud.list_products_by_category_and_subcat(category_name, subcategory)

    if not products:
        await call.message.answer("У этого подварианта пока нет товаров.")
        await call.answer()
        return

    for p in products:
        text = f"<b>{p.name}</b>\n{p.description or ''}\nПодкатегория: {p.subcategory or '-'}\nСтрана: {p.country or '-'}\nРазмеры: {p.size or '-'}\nЦена: {p.price or '-'}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"ask:{p.id}"),
             InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"order:{p.id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:menu")]
        ])
        if p.photo:
            await call.message.answer_photo(photo=p.photo, caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "back:menu")
async def back_to_menu(call: CallbackQuery):
    from .user_commands import start_cmd
    await start_cmd(call.message)
    await call.answer()


@router.callback_query(F.data.startswith("order:"))
async def order_start(call: CallbackQuery, state: FSMContext):
    _, pid = call.data.split(":")
    await state.update_data(product_id=int(pid))
    await call.message.answer("Введите ваше имя:")
    await state.set_state(OrderState.waiting_name)
    await call.answer()


@router.message(OrderState.waiting_name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите телефон (пример +79161234567):")
    await state.set_state(OrderState.waiting_phone)


@router.message(OrderState.waiting_phone)
async def order_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    data = await state.get_data()
    prod = await crud.get_product_by_id(data["product_id"])
    await crud.add_order(
        customer_name=data["name"],
        customer_phone=phone,
        product_id=prod.id if prod else None,
        product_name=prod.name if prod else None
    )
    await message.answer("Спасибо! Ваша заявка принята. Менеджер свяжется с вами.")
    await state.clear()
