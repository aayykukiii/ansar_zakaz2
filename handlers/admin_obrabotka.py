from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database import crud
from states.admin_states import AddCategoryState, AddProductState, DeleteProductState

router = Router()


@router.callback_query(F.data.startswith("adm:"))
async def admin_menu_actions(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Нет доступа", show_alert=True)
        return

    action = call.data.split(":", 1)[1]

    def admin_kb():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1. Добавить категорию", callback_data="adm:add_category")],
            [InlineKeyboardButton(text="2. Добавить мебель", callback_data="adm:add_product")],
            [InlineKeyboardButton(text="3. Удалить мебель", callback_data="adm:delete_product")],
            [InlineKeyboardButton(text="4. Заявки", callback_data="adm:orders")],
            [InlineKeyboardButton(text="5. Список категорий", callback_data="adm:list_categories")],
        ])

    if action == "add_category":
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отменить", callback_data="adm:cancel")]])
        await call.message.answer(
            "🆕 Создание новой категории мебели\n\nВведите название категории.\n\n🔹 Совет: добавьте эмодзи в начале названия — это делает меню заметнее.\nПримеры:\n🛏️ Спальная мебель\n🍳 Кухонная мебель\n🛋️ Мягкая мебель\n📚 Столы и стулья\n📺 Тумбы и комоды\n🛏️ Кровати\n🛏️️ Матрасы\n🚪 Шкафы\n\nОтправьте название или нажмите «Отменить».",
            reply_markup=kb
        )
        await state.set_state(AddCategoryState.waiting_name)
        await call.answer()
        return

    if action == "add_product":
        await call.message.answer(
            "🪄 Добавление новой мебели\n\n📝 Шаг 1 из 6: Описание мебели\n\nПожалуйста, введите подробное описание мебели:\n• Материалы и отделка\n• Габариты (Д×Ш×В)\n• Особенности конструкции\n• Стиль и назначение\n\nПример:\nЭлегантный кожаный диван \"Комфорт\" с мягким наполнением,\nразмеры 200×90×85 см, каркас из березовой фанеры,\nподушки сиденья на пружинном блоке, цвет черный.",
            reply_markup=None
        )
        await state.set_state(AddProductState.step1_description)
        await call.answer()
        return

    if action == "delete_product":
        products = await crud.list_products()
        if not products:
            await call.message.answer("Товаров пока нет.")
            await call.answer()
            return
        text = "Список мебели (id — название):\n\n"
        for p in products:
            text += f"{p.id} — {p.name}\n"
        text += "\nВыберите id мебели которое нужно удалить (отправьте только число id)."
        await call.message.answer(text)
        await state.set_state(DeleteProductState.waiting_id)
        await call.answer()
        return

    if action == "orders":
        orders = await crud.list_orders()
        if not orders:
            await call.message.answer("Заявок пока нет.")
            await call.answer()
            return
        for o in orders:
            txt = f"#{o.id}\nКлиент: {o.customer_name}\nТел: {o.customer_phone}\nТовар: {o.product_name or '-'}\nКомментарий: {o.comment or '-'}\nСтатус: {o.status}"
            await call.message.answer(txt)
        await call.answer()
        return

    if action == "list_categories":
        cats = await crud.list_categories()
        if not cats:
            await call.message.answer("Категорий пока нет.")
            await call.answer()
            return
        txt = "Список категорий:\n\n"
        for c in cats:
            txt += f"{c.id} — {c.name}\nОписание: {c.description or '-'}\n\n"
        await call.message.answer(txt)
        await call.answer()
        return

    if action == "cancel":
        await call.message.answer(text="Отменено. Выберите действие:", reply_markup=admin_kb())
        await state.clear()
        await call.answer()
        return



@router.message(AddCategoryState.waiting_name)
async def cat_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отменить", callback_data="adm:cancel")]])
    await msg.answer(
        f"✅ Название сохранено: {msg.text.strip()}\n\nТеперь введите краткое описание для категории — одно-две фразы.\nОписание поможет покупателям быстрее понять, что внутри категории.\n\nЕсли хотите отменить — нажмите «Отменить».",
        reply_markup=kb
    )
    await state.set_state(AddCategoryState.waiting_description)


@router.message(AddCategoryState.waiting_description)
async def cat_desc(msg: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    description = msg.text.strip()
    await crud.add_category(name=name, description=description)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Добавить категорию", callback_data="adm:add_category")],
        [InlineKeyboardButton(text="2. Добавить мебель", callback_data="adm:add_product")],
        [InlineKeyboardButton(text="3. Удалить мебель", callback_data="adm:delete_product")],
        [InlineKeyboardButton(text="4. Заявки", callback_data="adm:orders")],
        [InlineKeyboardButton(text="5. Список категорий", callback_data="adm:list_categories")],
    ])
    await msg.answer(f"Категория добавлена ✅\n{name}\nОписание: {description}", reply_markup=kb)
    await state.clear()


@router.message(AddProductState.step1_description)
async def p_step1(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text.strip())
    await msg.answer("Шаг 2 из 6: Введите название мебели (пример: Диван Комфорт):")
    await state.set_state(AddProductState.step2_name)


@router.message(AddProductState.step2_name)
async def p_step2(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    cats = await crud.list_categories()
    if not cats:
        await msg.answer("Сначала добавьте категорию. Операция отменена.")
        await state.clear()
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=c.name, callback_data=f"choose_cat:{c.id}")] for c in cats])
    await msg.answer("Шаг 3 из 6: Выберите категорию из списка:", reply_markup=kb)


@router.callback_query(F.data.startswith("choose_cat:"))
async def choose_cat(call: CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split(":")[1])
    await state.update_data(category_id=cat_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Российская", callback_data="choose_subcat:Российская")],
        [InlineKeyboardButton(text="🇹🇷 Турецкая", callback_data="choose_subcat:Турецкая")]
    ])
    await call.message.answer("Шаг 4 из 6: Выберите подкатегорию (только Российская или Турецкая):", reply_markup=kb)
    await state.set_state(AddProductState.step3_subcategory)
    await call.answer()


@router.callback_query(F.data.startswith("choose_subcat:"))
async def choose_subcat(call: CallbackQuery, state: FSMContext):
    sub = call.data.split(":", 1)[1]
    await state.update_data(subcategory=sub)
    await call.message.answer("Шаг 5 из 6: Введите страну производства и размеры (пример: Россия; 200x160):")
    await state.set_state(AddProductState.step4_country_size)
    await call.answer()


@router.message(AddProductState.step4_country_size)
async def p_step4(msg: Message, state: FSMContext):
    await state.update_data(country_size=msg.text.strip())
    await msg.answer("Шаг 6 из 6: Введите цену (или 'договорная'):")
    await state.set_state(AddProductState.step5_price)


@router.message(AddProductState.step5_price)
async def p_step5(msg: Message, state: FSMContext):
    await state.update_data(price=msg.text.strip())
    await msg.answer("Отправьте фото товара (одно). После отправки фото товар будет добавлен.")
    await state.set_state(AddProductState.step6_photo)


@router.message(AddProductState.step6_photo, F.photo)
async def p_step6(msg: Message, state: FSMContext):
    data = await state.get_data()
    file_id = msg.photo[-1].file_id
    cs = data.get("country_size", "")
    country, size = (cs.split(";")[0].strip(), cs.split(";")[1].strip()) if ";" in cs else (cs.strip(), None)
    await crud.add_product(
        name=data.get("name"),
        category_id=data.get("category_id"),
        subcategory=data.get("subcategory"),
        country=country,
        size=size,
        price=data.get("price"),
        description=data.get("description"),
        photo=file_id
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Добавить категорию", callback_data="adm:add_category")],
        [InlineKeyboardButton(text="2. Добавить мебель", callback_data="adm:add_product")],
        [InlineKeyboardButton(text="3. Удалить мебель", callback_data="adm:delete_product")],
        [InlineKeyboardButton(text="4. Заявки", callback_data="adm:orders")],
        [InlineKeyboardButton(text="5. Список категорий", callback_data="adm:list_categories")],
    ])
    await msg.answer("✅ Мебель добавлена. Выберите действие:", reply_markup=kb)
    await state.clear()


@router.message(DeleteProductState.waiting_id)
async def delete_by_id(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not text.isdigit():
        await msg.answer("Пожалуйста, отправьте только число — id товара.")
        return
    pid = int(text)
    p = await crud.get_product_by_id(pid)
    if not p:
        await msg.answer("Товар с таким id не найден. Отправьте другой id или /cancel")
        return
    await crud.delete_product_by_id(pid)
    products = await crud.list_products()
    txt = "Мебель успешно удалена.\n\n" if not products else "Мебель успешно удалена. Обновлённый список:\n\n"
    for it in products:
        txt += f"{it.id} — {it.name}\n"
    await msg.answer(txt)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Добавить категорию", callback_data="adm:add_category")],
        [InlineKeyboardButton(text="2. Добавить мебель", callback_data="adm:add_product")],
        [InlineKeyboardButton(text="3. Удалить мебель", callback_data="adm:delete_product")],
        [InlineKeyboardButton(text="4. Заявки", callback_data="adm:orders")],
        [InlineKeyboardButton(text="5. Список категорий", callback_data="adm:list_categories")],
    ])
    await msg.answer("Выберите действие:", reply_markup=kb)
    await state.clear()