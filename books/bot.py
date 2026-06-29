import os
import django
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from books.models import Book, Loan, Fine, CustomUser
from datetime import date

# ТОКЕН БОТА - ВСТАВЬТЕ СВОЙ
TOKEN = "7852013883:AAFTj7VPdG4JB0THD7iw_3iIryUAXvMq_-8"

# Хранилище данных пользователей
user_data_store = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📚 Поиск книги", callback_data="search_book")],
        [InlineKeyboardButton("📖 Мои книги", callback_data="my_books")],
        [InlineKeyboardButton("💰 Мои штрафы", callback_data="my_fines")],
        [InlineKeyboardButton("🔗 Связать с аккаунтом", callback_data="link_account")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я библиотечный помощник. Выбери действие:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия кнопок"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "search_book":
        # Запрашиваем поисковый запрос
        user_data_store[user_id] = {'state': 'waiting_search'}
        await query.edit_message_text(
            "📚 Введите название книги или фамилию автора:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )

    elif callback_data == "my_books":
        await show_my_books(query, user_id, context)

    elif callback_data == "my_fines":
        await show_my_fines(query, user_id, context)

    elif callback_data == "link_account":
        user_data_store[user_id] = {'state': 'waiting_username'}
        await query.edit_message_text(
            "🔗 *Привязка аккаунта*\n\nВведите ваш ЛОГИН:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )

    elif callback_data == "help":
        await query.edit_message_text(
            "🤖 *Помощь*\n\n"
            "📚 Поиск книги - найти книгу по названию или автору\n"
            "📖 Мои книги - список ваших книг\n"
            "💰 Мои штрафы - информация о штрафах\n"
            "🔗 Связать с аккаунтом - привязать аккаунт библиотеки\n\n"
            "Для входа используйте логин и пароль от сайта",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )

    elif callback_data == "menu":
        await show_menu(query)


async def show_menu(query):
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("📚 Поиск книги", callback_data="search_book")],
        [InlineKeyboardButton("📖 Мои книги", callback_data="my_books")],
        [InlineKeyboardButton("💰 Мои штрафы", callback_data="my_fines")],
        [InlineKeyboardButton("🔗 Связать с аккаунтом", callback_data="link_account")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    await query.edit_message_text(
        "👋 Главное меню\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_my_books(query, user_id, context):
    """Показать книги пользователя"""
    # Проверяем, привязан ли аккаунт
    if user_id not in user_data_store or 'library_user_id' not in user_data_store[user_id]:
        await query.edit_message_text(
            "🔗 Сначала привяжите аккаунт библиотеки!\n\n"
            "Нажмите кнопку 'Связать с аккаунтом' в главном меню.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )
        return

    library_user_id = user_data_store[user_id]['library_user_id']

    @sync_to_async
    def get_user_books():
        try:
            user = CustomUser.objects.get(id=library_user_id)
            loans = Loan.objects.filter(user=user, is_returned=False).select_related('book_copy__book')
            return loans, user
        except CustomUser.DoesNotExist:
            return None, None

    loans, user = await get_user_books()

    if loans is None:
        await query.edit_message_text(
            "❌ Пользователь не найден. Привяжите аккаунт заново.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )
        return

    if loans:
        text = f"📖 *Книги у {user.first_name} {user.last_name}:*\n\n"
        for loan in loans:
            book = loan.book_copy.book
            due_date = loan.due_date
            days_left = (due_date - date.today()).days
            if days_left < 0:
                status = f"⚠️ ПРОСРОЧЕНА на {abs(days_left)} дн.!"
            else:
                status = f"⏳ Осталось {days_left} дн."
            text += f"📕 *{book.title}*\n"
            text += f"📅 Вернуть до: {due_date.strftime('%d.%m.%Y')}\n"
            text += f"{status}\n\n"
    else:
        text = f"📚 У вас нет активных выдач."

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад", callback_data="menu")
        ]])
    )


async def show_my_fines(query, user_id, context):
    """Показать штрафы пользователя"""
    if user_id not in user_data_store or 'library_user_id' not in user_data_store[user_id]:
        await query.edit_message_text(
            "🔗 Сначала привяжите аккаунт библиотеки!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )
        return

    library_user_id = user_data_store[user_id]['library_user_id']

    @sync_to_async
    def get_fines():
        try:
            user = CustomUser.objects.get(id=library_user_id)
            fines = Fine.objects.filter(user=user, status='unpaid').select_related('loan__book_copy__book')
            return fines, user
        except CustomUser.DoesNotExist:
            return None, None

    fines, user = await get_fines()

    if fines is None:
        await query.edit_message_text(
            "❌ Пользователь не найден.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="menu")
            ]])
        )
        return

    if fines:
        text = f"💰 *Штрафы {user.first_name} {user.last_name}:*\n\n"
        total = 0
        for fine in fines:
            book_title = fine.loan.book_copy.book.title
            text += f"📕 *{book_title}*\n"
            text += f"📅 Просрочка: {fine.days_overdue} дн.\n"
            text += f"💸 Сумма: {fine.amount} руб.\n\n"
            total += fine.amount
        text += f"---\n*Итого: {total} руб.*"
    else:
        text = f"✅ У вас нет штрафов."

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад", callback_data="menu")
        ]])
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data_store:
        await update.message.reply_text("Отправьте /start для начала работы")
        return

    state = user_data_store[user_id].get('state')

    if state == 'waiting_search':
        # Поиск книг
        @sync_to_async
        def search_books():
            books = Book.objects.filter(title__icontains=text)[:5]
            if not books:
                books = Book.objects.filter(authors__last_name__icontains=text).distinct()[:5]
            return books

        books = await search_books()

        if books:
            result = "📚 *Результаты поиска:*\n\n"
            for book in books:
                authors = ", ".join([f"{a.last_name} {a.first_name}" for a in book.authors.all()])
                result += f"📖 *{book.title}*\n✍️ {authors}\n📅 {book.publication_year or 'Год не указан'}\n"
                result += f"📌 {'✅ Доступна' if book.status == 'available' else '❌ Выдана'}\n\n"
        else:
            result = "😔 Книги не найдены."

        user_data_store[user_id] = {}
        await update.message.reply_text(
            result,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Главное меню", callback_data="menu")
            ]])
        )

    elif state == 'waiting_username':
        user_data_store[user_id]['temp_username'] = text
        user_data_store[user_id]['state'] = 'waiting_password'
        await update.message.reply_text(
            "🔑 Введите ваш ПАРОЛЬ:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Отмена", callback_data="menu")
            ]])
        )

    elif state == 'waiting_password':
        username = user_data_store[user_id].get('temp_username')
        password = text

        @sync_to_async
        def check_user():
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password):
                    return user.id
                return None
            except CustomUser.DoesNotExist:
                return None

        library_user_id = await check_user()

        if library_user_id:
            user_data_store[user_id]['library_user_id'] = library_user_id
            user_data_store[user_id].pop('temp_username', None)
            user_data_store[user_id]['state'] = None
            await update.message.reply_text(
                "✅ Аккаунт успешно привязан!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Главное меню", callback_data="menu")
                ]])
            )
        else:
            user_data_store[user_id]['state'] = 'waiting_username'
            await update.message.reply_text(
                "❌ Неверный логин или пароль. Попробуйте снова.\n\nВведите ЛОГИН:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Отмена", callback_data="menu")
                ]])
            )


def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()