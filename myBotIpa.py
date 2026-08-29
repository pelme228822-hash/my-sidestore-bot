import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция авто-поиска свежего IPA SideStore (с поддержкой pre-releases и фолбэком)
def get_sidestore_ipa():
    url = "https://api.github.com/repos/SideStore/SideStore/releases"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            releases = res.json()
            if releases:
                latest_release = releases[0]
                tag = latest_release.get("tag_name", "v0.5.8")
                
                for asset in latest_release.get("assets", []):
                    if asset["name"].lower().endswith(".ipa"):
                        return asset["browser_download_url"], tag
    except Exception as e:
        print(f"Ошибка GitHub API: {e}")

    # Запасная рабочая ссылка, если API GitHub недоступен или лимитирован
    return "https://github.com/SideStore/SideStore/releases/download/0.5.8/SideStore-0.5.8.ipa", "v0.5.8"

# Главное меню
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Что такое SideStore?", callback_data="info")
    builder.button(text="🚀 Инструкция (Без ПК)", callback_data="step_1")
    builder.button(text="📥 Скачать актуальный SideStore.ipa", callback_data="download_ipa")
    builder.adjust(1)
    return builder.as_markup()

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 **Привет! Это гид по установке SideStore без ПК.**\n\n"
        "Здесь ты найдешь пошаговую инструкцию и актуальные файлы.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# Информация
@dp.callback_query(F.data == "info")
async def info_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="home")
    
    text = (
        "ℹ️ **Что такое SideStore?**\n\n"
        "Это альтернативный магазин приложений для iOS, который позволяет ставить любой `.ipa` "
        "прямо с телефона без проводов и компьютера! Приложения нужно переподписывать раз в 7 дней "
        "прямо внутри шторки Wi-Fi."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Шаг 1 Инструкции
@dp.callback_query(F.data == "step_1")
async def step1_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Шаг 2: Установка WireGuard", callback_data="step_2")
    builder.button(text="🔙 В меню", callback_data="home")
    builder.adjust(1)

    text = (
        "📍 **Шаг 1: Подготовка**\n\n"
        "1. Убедись, что на iPhone включен **Режим разработчика** (Настройки -> Конфиденциальность -> Режим разработчика).\n"
        "2. Установи приложение **Команды (Shortcuts)** из App Store, если снес его."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Шаг 2 Инструкции
@dp.callback_query(F.data == "step_2")
async def step2_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📥 Скачать IPA файл", callback_data="download_ipa")
    builder.button(text="🔙 Назад к Шагу 1", callback_data="step_1")
    builder.adjust(1)

    text = (
        "📍 **Шаг 2: VPN профиль (Loopback)**\n\n"
        "SideStore обманывает систему, подменяя локальный сервер.\n"
        "1. Скачай **WireGuard** из App Store.\n"
        "2. Загрузи конфиг-файл `SideStore.conf` (или создай WireGuard-петлю).\n"
        "3. Включи VPN в WireGuard перед каждым входом в SideStore!"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Выдача файла
@dp.callback_query(F.data == "download_ipa")
async def download_callback(call: types.CallbackQuery):
    await call.answer("Запрашиваю свежий релиз с GitHub...")
    url, ver = get_sidestore_ipa()
    
    builder = InlineKeyboardBuilder()
    if url:
        builder.button(text=f"🔥 Скачать SideStore ({ver})", url=url)
    builder.button(text="🔙 Главное меню", callback_data="home")
    builder.adjust(1)

    msg = f"✅ **Свежий SideStore ({ver}) найден!**\n\nНажми на кнопку ниже для загрузки:"
    await call.message.edit_text(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Возврат в главное меню
@dp.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    await call.message.edit_text(
        "👋 **Главное меню гида по SideStore**",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# Точка входа
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
