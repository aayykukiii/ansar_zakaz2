# states/admin_states.py
from aiogram.fsm.state import State, StatesGroup

class AddCategoryState(StatesGroup):
    waiting_name = State()
    waiting_description = State()

class AddProductState(StatesGroup):
    step1_description = State()
    step2_name = State()
    step3_subcategory = State()
    step4_country_size = State()
    step5_price = State()
    step6_photo = State()

class DeleteProductState(StatesGroup):
    waiting_id = State()
