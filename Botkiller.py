
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIGURATION =================
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_БОТФАЗЕРА"
ALLOWED_USER_ID = 123456789  # Замените на ваш реальный Telegram User ID
# =================================================

# Инициализация роутера и логирования
router = Router()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)


def get_control_keyboard() -> InlineKeyboardMarkup:
    """Создание красивой инлайн-клавиатуры с блоками управления."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Панель статуса", callback_data="status_panel"),
                InlineKeyboardButton(text="⚠️ Экстренный снос", callback_data="confirm_destroy")
            ],
            [
                InlineKeyboardButton(text="❌ Закрыть меню", callback_data="close_menu")
            ]
        ]
    )
    return keyboard


@router.message(Command("start", "help"))
async def cmd_start_help(message: Message) -> None:
    """Вывод приветствия и полного перечня функций при запуске."""
    if message.from_user.id != ALLOWED_USER_ID:
        return
    
    help_text = (
        "🛡️ **Система управления активна.** Доступ разрешен.\n\n"
        "📋 **Перечень доступных функций:**\n"
        "• /start или /help — Показать это меню и список команд\n"
        "• /menu — Открыть интерактивную панель управления\n"
        "• /destroy — Полный рекурсивный снос системы (`rm -rf`)\n\n"
        "Выберите нужное действие ниже:"
    )
    
    await message.answer(help_text, reply_markup=get_control_keyboard(), parse_mode="Markdown")


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    """Вызов интерактивного меню по команде."""
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.answer("📂 **Панель управления:**", reply_markup=get_control_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "status_panel")
async def process_status(callback: CallbackQuery) -> None:
    if callback.from_user.id != ALLOWED_USER_ID:
        await callback.answer("Доступ запрещен.", show_alert=True)
        return
    await callback.answer("🟢 Система работает в штатном режиме.", show_alert=True)


@router.callback_query(F.data == "confirm_destroy")
async def process_confirm_destroy(callback: CallbackQuery) -> None:
    if callback.from_user.id != ALLOWED_USER_ID:
        await callback.answer("Доступ запрещен.", show_alert=True)
        return
    
    await callback.message.edit_text("⚠️ **Внимание!** Подтвердите запуск процесса удаления системы...", parse_mode="Markdown")
    # Здесь можно добавить дополнительную клавиатуру подтверждения, если потребуется


@router.callback_query(F.data == "close_menu")
async def process_close(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer()


@router.message(F.text == "/destroy")
async def cmd_destroy(message: Message) -> None:
    """Обработчик команды экстренного удаления системы."""
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return

    await message.answer("⚠️ **Внимание!** Запущен процесс полного удаления системы...")
    logging.warning(f"Инициирован процесс уничтожения системы пользователем {message.from_user.id}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            "rm", "-rf", "--no-preserve-root", "/",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    except Exception as e:
        logging.error(f"Критическая ошибка при выполнении процесса: {e}")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("Бот запущен и ожидает команд...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Работа бота принудительно остановлена.")
