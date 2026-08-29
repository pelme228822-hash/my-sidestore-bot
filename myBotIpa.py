import asyncio
import os
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import URLInputFile

# Токен из переменных окружения Render или напрямую
TOKEN = os.getenv("TOKEN", "8607944139:AAE1dnqJf0TZrpmuS2sqlF2JZT_poNOB1U8")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Репозиторий SideInstaller
REPO_OWNER = "FrizzleM"
REPO_NAME = "SideInstaller"

# Функция получения прямой ссылки и версии SideInstaller с GitHub
def get_sideinstaller_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
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

    # Резервный фолбэк: если GitHub API недоступен или выдал лимит запросов
    fallback_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/SideInstaller.ipa"
    return fallback_url, "SideInstaller.ipa", "Latest"

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
        "👋 <b>Привет! Это гайд по установке SideStore на iOS без ПК.</b>\n\n"
        "Здесь ты сможешь получить файл SideInstaller и с его помощью установить SideStore прямо с телефона.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# Раздел "Что это такое" (Единая свернутая цитата)
@dp.callback_query(F.data == "info")
async def info_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Перейти к инструкции", callback_data="step_1")
    builder.button(text="🔙 Главное меню", callback_data="home")
    builder.adjust(1)
    
    text = (
        "❓ <b>Что такое SideInstaller?</b>\n\n"
        "<b>SideInstaller</b> — это специальное утилитарное приложение, созданное для установки самого альтернативного магазина <b>SideStore</b> прямо на iPhone без участия компьютера!\n\n"
        "Сам по себе SideInstaller служит «трамплином»: ты подписываешь его через бесплатный веб-сервис, а уже внутри него разворачивается и запускается сам SideStore, который в дальнейшем позволит устанавливать любые .ipa файлы и игры без ПК.\n\n"
        "<blockquote expandable>🇪🇺 <b>Официальный контекст и регуляция ЕС:</b>\n\n"
        "Под давлением Закона о цифровых рынках (DMA) Европейского союза, компания Apple была "
        "официально обязана предоставить пользователям возможность установки приложений из альтернативных "
        "источников вне App Store.\n\n"
        "Несмотря на ограничения Apple по регионам, сообщество разработчиков создало решения "
        "(включая веб-подпись и локальные профили), позволяющие обходить эти рамки и безопасно "
        "устанавливать любые .ipa файлы на любой iOS-девайс.</blockquote>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# Шаг 1 Инструкции
@dp.callback_query(F.data == "step_1")
async def step1_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Шаг 2: Подпись и Установка", callback_data="step_2")
    builder.button(text="🔙 В меню", callback_data="home")
    builder.adjust(1)

    text = (
        "📍 <b>Шаг 1: Скачивание установочного файла</b>\n\n"
        "1. Нажми кнопку в меню: <b>«Получить SideInstaller.ipa в чат»</b>.\n"
        "2. Бот пришлет тебе готовый .ipa файл прямо в Telegram.\n"
        "3. Сохрани этот файл себе в приложение <b>Файлы</b> на iPhone."
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# Шаг 2 Инструкции (Обновлена ссылка на AppleJR)
@dp.callback_query(F.data == "step_2")
async def step2_callback(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Открыть сайт подписи (AppleJR)", url="https://applejr.net/")
    builder.button(text="📥 Запросить IPA файл", callback_data="download_ipa")
    builder.button(text="🔙 Назад к Шагу 1", callback_data="step_1")
    builder.adjust(1)

    text = (
        "📍 <b>Шаг 2: Бесплатная подпись и установка без ПК</b>\n\n"
        "Так как iOS не дает ставить .ipa напрямую, SideInstaller нужно подписать бесплатным сертификатом:\n\n"
        "1. Перейди на сайт подписи по кнопке ниже (<b>AppleJR</b>).\n"
        "2. Загрузи скачанный файл <code>SideInstaller.ipa</code> из приложения «Файлы».\n"
        "3. Нажми кнопку для подписи и дождитесь завершения процесса.\n"
        "4. Нажми <b>«Установить»</b> (Install) и подтверди запрос на рабочем столе.\n"
        "5. Если при запуске пишет «Ненадежный корпоративный разработчик»: зайди в <i>Настройки -> Основные -> VPN и управление устройством</i>, найди сертификат и нажми <b>«Доверять»</b>.\n"
        "6. Запусти <b>SideInstaller</b> и установи через него сам <b>SideStore</b>!"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# Отправка файла прямо в чат
@dp.callback_query(F.data == "download_ipa")
async def download_callback(call: types.CallbackQuery):
    await call.answer("Загружаю файл...")
    
    download_url, file_name, version = get_sideinstaller_release()

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Перейти к инструкции по установке", callback_data="step_2")
    builder.button(text="🔙 Главное меню", callback_data="home")
    builder.adjust(1)

    status_msg = await call.message.answer(
        f"⏳ Отправляю <b>{file_name}</b> ({version}) в чат...",
        parse_mode="HTML"
    )
    
    try:
        ipa_file = URLInputFile(download_url, filename=file_name)
        await bot.send_document(
            chat_id=call.message.chat.id,
            document=ipa_file,
            caption=f"✅ <b>Файл {file_name} готов!</b>\n\nТеперь переходи к Шагу 2 для подписи и установки.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка отправки файла в Telegram: {e}")
        fallback_builder = InlineKeyboardBuilder()
        fallback_builder.button(text=f"📥 Скачать {file_name}", url=download_url)
        fallback_builder.button(text="🚀 Перейти к инструкции", callback_data="step_2")
        fallback_builder.button(text="🔙 Главное меню", callback_data="home")
        fallback_builder.adjust(1)
        
        await status_msg.edit_text(
            f"✅ <b>Файл {file_name} готов к скачиванию:</b>\n\nНажми кнопку ниже, чтобы загрузить файл на iPhone:",
            reply_markup=fallback_builder.as_markup(),
            parse_mode="HTML"
        )

# Возврат в главное меню
@dp.callback_query(F.data == "home")
async def home_callback(call: types.CallbackQuery):
    await call.message.edit_text(
        "👋 <b>Главное меню гида по SideInstaller</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# Фейковый сервер для порта Render
async def handle_ping(request):
    return web.Response(text="Bot is running")

# Точка входа
async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
