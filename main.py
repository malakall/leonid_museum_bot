from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

user_states = {}

# Список художников и пути к фото их известных картин
artists = [
    "Винсент Ван Гог",
    "Пабло Пикассо",
    "Клод Моне",
    "Леонардо да Винчи",
    "Рембрандт",
    "Сальвадор Дали",
    "Фрида Кало"
]

descriptions = {
    "Винсент Ван Гог": "Ван Гог — постимпрессионист, известен своими яркими картинами и драматичной жизнью.",
    "Пабло Пикассо": "Пикассо — основатель кубизма, один из самых влиятельных художников XX века.",
    "Клод Моне": "Моне — основатель импрессионизма, мастер передачи света и цвета.",
    "Леонардо да Винчи": "Да Винчи — гений Возрождения, художник, ученый и изобретатель.",
    "Рембрандт": "Рембрандт — мастер светотени и портретной живописи XVII века.",
    "Сальвадор Дали": "Дали — сюрреалист, известный своими фантастическими образами.",
    "Фрида Кало": "Кало — мексиканская художница, известная автопортретами и яркой палитрой."
}

photos = {
    "Винсент Ван Гог": "src/van_gogh_star_night.png",
    "Пабло Пикассо": "src/picasso_guernica.png",
    "Клод Моне": "src/monet_water_lilies.png",
    "Леонардо да Винчи": "src/da_vinci_mona_lisa.png",
    "Рембрандт": "src/rembrandt_night_watch.png",
    "Сальвадор Дали": "src/dali_persistence_memory.png",
    "Фрида Кало": "src/frida_kahlo_self_portrait.png"
}

def create_main_keyboard():
    keyboard = [[KeyboardButton(artist)] for artist in artists]
    keyboard.append([KeyboardButton("О нас"), KeyboardButton("Помощь")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def add_back_button():
    keyboard = [[KeyboardButton("Назад")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    welcome_text = (
        "Добро пожаловать в онлайн-выставку музея!\n"
        "Выберите экспозицию, чтобы узнать больше о художнике."
    )
    keyboard = create_main_keyboard()
    try:
        # Отправляем фото с подписью (caption)
        await context.bot.send_photo(
            chat_id,
            photo=open("src/musem.png", "rb"),
            caption=welcome_text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка отправки изображения: {e}")
        # Если фото не отправилось, отправляем просто текст
        await context.bot.send_message(chat_id, text=welcome_text, reply_markup=keyboard)
    user_states[chat_id] = "MAIN_MENU"

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (
        "🏛️ Онлайн-выставка музея посвящена великим художникам.\n"
        "Здесь вы можете узнать интересные факты и увидеть работы известных мастеров.\n"
        "Наслаждайтесь путешествием в мир искусства!"
    )
    try:
        await context.bot.send_photo(chat_id, photo=open("src/about_museum.png", "rb"))
    except Exception as e:
        print(f"Ошибка отправки изображения: {e}")
    await context.bot.send_message(chat_id, text=text, reply_markup=add_back_button())
    user_states[chat_id] = "ABOUT_US"

async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (
        "💬 Если у вас есть вопросы, напишите нашему менеджеру: @JI_E_o_H_u_D\n"
        "📚 Вы также можете узнать больше, выбрав экспозицию."
    )
    await context.bot.send_message(chat_id, text=text, reply_markup=add_back_button())
    user_states[chat_id] = "HELP_MENU"

async def show_exposition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    artist = update.message.text
    if artist in artists:
        text = f"🎨 {artist}\n\n{descriptions.get(artist, 'Информация скоро появится.')}"
        photo_path = photos.get(artist)
        if photo_path:
            try:
                await context.bot.send_photo(chat_id, photo=open(photo_path, "rb"))
            except Exception as e:
                print(f"Ошибка отправки изображения: {e}")
        await context.bot.send_message(chat_id, text=text, reply_markup=add_back_button())
        user_states[chat_id] = "EXPOSITION"
    else:
        await context.bot.send_message(chat_id, text="Пожалуйста, выберите экспозицию из списка.")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id, "MAIN_MENU")
    if state in ["ABOUT_US", "HELP_MENU", "EXPOSITION"]:
        await start(update, context)
    else:
        await start(update, context)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id, "Неизвестная команда. Воспользуйтесь меню.", reply_markup=create_main_keyboard())

def main():
    application = ApplicationBuilder().token("8071703401:AAG5QqtxUWmxKJixzhxCF359LTHSMeC57qY").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(" + "|".join(artists) + ")$"), show_exposition))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("О нас"), about_us))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("Помощь"), help_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("Назад"), handle_back))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_command))

    application.run_polling()

if __name__ == "__main__":
    main()
