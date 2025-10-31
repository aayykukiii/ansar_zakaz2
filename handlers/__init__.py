from aiogram import Router
from .user_commands import router as user_commands_router
from .user_obrabotka import router as user_obrabotka_router
from .admin_commads import router as admin_commands_router
from .admin_obrabotka import router as admin_obrabotka_router


router = Router()

router.include_router(user_commands_router)
router.include_router(user_obrabotka_router)
router.include_router(admin_commands_router)
router.include_router(admin_obrabotka_router)