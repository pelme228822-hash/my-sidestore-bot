import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import URLInputFile

# Берём токен из переменных окружения Render или вставляем напрямую
TOKEN = os.getenv("TOKEN", "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# РЕПОЗИТОРИЙ SIDEINSTALLER
REPO_OWNER = "FrizzleM"
REPO_NAME = "SideInstaller"

# Функция получения прямой ссылки и версии SideInstaller с GitHub
def get_sideinstaller_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            releases = res.json()
            if releases:
                latest_release = releases[0]
                tag = latest_release.get("tag_name", "v1.0")
                
                for asset in latest_release.get("assets", []):
                    if asset["name"].lower().endswith(".ipa"):
                        return asset["browser_download_url"], asset["name"], tag
    except Exception as e:
        print(f"Ошибка GitHub API: {e}")

    return None, None, None

# Главное меню
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Что это такое и как работает?", callback_data="info")
    builder.button(text="🚀 Инструкция по установке (Без ПК)", callback_data="step_1")
    builder.button(text="📥 Получить SideInstaller.ipa в чат", callback_data="download_ipa")
    builder.adjust(1)
    return builder.as_markup()

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 **Привет! Это гайд по установке сторонних приложений на iOS без ПК.**\n\n"
        "Здесь ты сможешь получить файл SideInstaller и установить его прямо с телефона.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# Раздел "Что это такое"
@dp.callback_query(F.data == "info")
async def info_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Перейти к инструкции", callback_data="step_1")
    builder.button(text="🔙 Главное меню", callback_data="home")
    builder.adjust(1)
    
    text = (
        "❓ **Что такое SideInstaller?**\n\n"
        "Это удобный менеджер и инсталлятор сторонних `.ipa` приложений прямо на твоем iPhone, "
        "работающий без подключения к компьютеру.\n\n"
        "> 🇪🇺 **Официальный контекст и регуляция ЕС:**\n"
        "> Под давлением Закона о цифровых рынках (DMA) Европейского союза, компания Apple была "
        "> официально обязана предоставить пользователям возможность установки приложений из альтернативных "
        "> источников вне App Store. Несмотря на ограничения Apple по регионам, сообщество разработчиков "
        "> создало решения (включая веб-подпись и локальные профили), позволяющие обходить эти рамки "
        "> и безопасно устанавливать любые `.ipa` файлы на любой iOS-девайс."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Шаг 1 Инструкции
@dp.callback_query(F.data == "step_1")
async def step1_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Шаг 2: Подпись и Установка", callback_data="step_2")
    builder.button(text="🔙 В меню", callback_data="home")
    builder.adjust(1)

    text = (
        "📍 **Шаг 1: Скачивание установочного файла**\n\n"
        "1. Нажми кнопку ниже или в меню: **«Получить SideInstaller.ipa в чат»**.\n"
        "2. Бот пришлет тебе готовый `.ipa` файл прямо в Telegram.\n"
        "3. Сохрани этот файл себе в стандартное приложение **Файлы** на iPhone."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Шаг 2 Инструкции
@dp.callback_query(F.data == "step_2")
async def step2_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Открыть сайт подписи (SwagInstall)", url="https://swaginstall.com/")
    builder.button(text="📥 Запросить IPA файл", callback_data="download_ipa")
    builder.button(text="🔙 Назад к Шагу 1", callback_data="step_1")
    builder.adjust(1)

    text = (
        "📍 **Шаг 2: Бесплатная подпись и установка без ПК**\n\n"
        "Так как iOS не дает ставит `.ipa` напрямую, файл нужно подписать бесплатным публичным сертификатом:\n\n"
        "1. Перейди на сервис онлайн-подписи (например, **SwagInstall** по кнопке ниже).\n"
        "2. Нажми **«Выбрать IPA»** и загрузи скачанный из этого бота файл `SideInstaller.ipa`.\n"
        "3. Нажми **«Подписать»** (Sign).\n"
        "4. После завершения появится кнопка **«Установить»** — нажми её и подтверди установку на экран Домой.\n"
        "5. Если при запуске пишет «Ненадежный разработчик»: зайди в *Настройки -> Основные -> VPN и управление устройством* и нажми **«Доверять»**."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# Отправка файла прямо в чат
@dp.callback_query(F.data == "download_ipa")
async def download_callback(call: types.CallbackQuery):
    await call.answer("Загружаю файл с GitHub, подожди пару секунд...")
    
    download_url, file_name, version = get_sideinstaller_release()
    
    if not download_url:
        await call.message.answer("❌ Не удалось получить файл с GitHub. Попробуй позже.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Перейти к инструкции по установке", callback_data="step_2")
    builder.button(text="🔙 Главное меню", callback_data="home")
    builder.adjust(1)

    # Уведомляем пользователя
    await call.message.answer(f"⏳ Отправляю **{file_name}** ({version}) в чат...")
    
    # Отправляем .ipa файл документом прямо в Telegram
    ipa_file = URLInputFile(download_url, filename=file_name)
    
    await bot.send_document(
        chat_id=call.message.chat.id,
        document=ipa_file,
        caption=f"✅ **Файл {file_name} готов!**\n\nТеперь переходи к Шагу 2 для подписи и установки.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# Возврат в главное меню
@dp.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    await call.message.edit_text(
        "👋 **Главное меню гида по SideInstaller**",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
