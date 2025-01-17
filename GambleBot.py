from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import random
import logging
logging.basicConfig(level=logging.INFO)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🎰Рулетка", callback_data="game_roulette")],
        [InlineKeyboardButton("🃏Карточная игра 21", callback_data="game_21")],
        [InlineKeyboardButton("🎲Кости", callback_data="game_dice")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите игру 🎮:", reply_markup=reply_markup)

# Обработчик выбора игры
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    logging.info(f"Обработчик кнопки: {query.data}")
    await query.answer()  # Подтвердить обработку запроса

     # Рулетка
    if query.data == "game_roulette":
        await play_roulette(query, context)
    elif query.data.startswith("roulette_"):
        await roulette_category_handler(query, context)
    elif query.data.startswith("color_") or query.data.startswith("number_") or query.data.startswith("range_"):
        await roulette_result_handler(query, context)
    # Карточная игра 21
    elif query.data == "game_21":
        await play_21(query, context)
    # Кости
    elif query.data == "game_dice":
        await play_dice(query, context)
    # Играть снова
    elif query.data.startswith("play_again"):
        game = query.data.split("_")[-1]
        if game == "roulette":
            await play_roulette(query, context)
        elif game == "21":
            await play_21(query, context)
        elif game == "dice":
            await play_dice(query, context)
    # Назад к меню
    elif query.data == "back_to_menu":
        await start(query, context)

# Кнопки "Играть снова" и "Назад"
def end_game_buttons(game: str):
    keyboard = [
        [InlineKeyboardButton("Играть снова", callback_data=f"play_again_{game}")],
        [InlineKeyboardButton("Назад к выбору игры", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Игра Рулетка
async def play_roulette(query, context) -> None:
    # Первый этап: выбор категории ставки
    keyboard = [
        [InlineKeyboardButton("🎨Цвет", callback_data="roulette_color")],
        [InlineKeyboardButton("🔢Числа (чётное/нечётное)", callback_data="roulette_number")],
        [InlineKeyboardButton("🧮Диапазон (1-18, 19-36)", callback_data="roulette_range")],
        [InlineKeyboardButton("Назад к выбору игры", callback_data="back_to_menu")]
    ]
    await query.edit_message_text(
        "Выберите категорию ставки:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["roulette_stage"] = "category"

# Обработка выбора категории ставки
async def roulette_category_handler(query, context) -> None:
    if context.user_data.get("roulette_stage") != "category":
        return

    category = query.data
    context.user_data["roulette_category"] = category
    context.user_data["roulette_stage"] = "value"  # Переход ко второму этапу

    if category == "roulette_color":
        keyboard = [
            [InlineKeyboardButton("♦️Красный♥️", callback_data="color_red")],
            [InlineKeyboardButton("♠️Чёрный♣️", callback_data="color_black")],
            [InlineKeyboardButton("🟩Зеро🟩", callback_data="color_green")],
            [InlineKeyboardButton("Назад", callback_data="game_roulette")]
        ]
        await query.edit_message_text(
            "Выберите цвет для ставки:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif category == "roulette_number":
        keyboard = [
            [InlineKeyboardButton("Чётное", callback_data="number_even")],
            [InlineKeyboardButton("Нечётное", callback_data="number_odd")],
            [InlineKeyboardButton("Назад", callback_data="game_roulette")]
        ]
        await query.edit_message_text(
            "Выберите тип числа для ставки:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif category == "roulette_range":
        keyboard = [
            [InlineKeyboardButton("1-18", callback_data="range_low")],
            [InlineKeyboardButton("19-36", callback_data="range_high")],
            [InlineKeyboardButton("Назад", callback_data="game_roulette")]
        ]
        await query.edit_message_text(
            "Выберите диапазон для ставки:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Обработка ставки и определение результата
async def roulette_result_handler(query, context) -> None:
    if context.user_data.get("roulette_stage") != "value":
        return

    user_choice = query.data
    category = context.user_data["roulette_category"]

    # Генерация результата рулетки
    result_number = random.randint(0, 36)
    result_color = (
        "green" if result_number == 0 else
        "red" if result_number % 2 != 0 else
        "black"
    )

    # Определение выигрыша
    won = False
    if category == "roulette_color":
        won = (
            (user_choice == "color_red" and result_color == "red") or
            (user_choice == "color_black" and result_color == "black") or
            (user_choice == "color_green" and result_color == "green")
        )

    elif category == "roulette_number":
        won = (
            (user_choice == "number_even" and result_number % 2 == 0 and result_number != 0) or
            (user_choice == "number_odd" and result_number % 2 != 0)
        )

    elif category == "roulette_range":
        won = (
            (user_choice == "range_low" and 1 <= result_number <= 18) or
            (user_choice == "range_high" and 19 <= result_number <= 36)
        )

    # Сообщение о результате
    result_message = (
        f"Результат рулетки: {result_number} ({result_color}).\n"
        f"{'Поздравляем, вы выиграли!🎉' if won else 'Вы проиграли!😞'}"
    )
    await query.edit_message_text(
        result_message,
        reply_markup=end_game_buttons("roulette")
    )

# Обработчик команды /hit (добрать карту)
async def hit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "game_21" not in context.user_data:
        await update.message.reply_text("Вы еще не начали игру! Используйте /start, чтобы выбрать игру.")
        return

    user_data = context.user_data["game_21"]
    new_card = random.randint(1, 11)
    user_data["cards"].append(new_card)
    user_data["sum"] += new_card

    if user_data["sum"] > 21:
        await update.message.reply_text(
            f"Вы взяли карту {new_card}. Ваши карты: {user_data['cards']} (сумма: {user_data['sum']}). Вы проиграли!😞 Начните новую игру с /start."
        )
        del context.user_data["game_21"]
    else:
        await update.message.reply_text(
            f"Вы взяли карту {new_card}. Ваши карты: {user_data['cards']} (сумма: {user_data['sum']}). Хотите взять ещё карту? Напишите /hit или завершите игру с /stand."
        )

# Обработчик команды /stand (остановить добор)
async def stand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "game_21" not in context.user_data:
        await update.message.reply_text("Вы еще не начали игру! Используйте /start, чтобы выбрать игру.")
        return

    user_data = context.user_data["game_21"]
    bot_sum = random.randint(17, 23)  # Сумма карт бота
    result = (
        "Вы выиграли!🎉" if user_data["sum"] > bot_sum or bot_sum > 21
        else "Вы проиграли!😞" if user_data["sum"] < bot_sum
        else "Ничья!🤝"
    )
    await update.message.reply_text(
        f"Ваши карты: {user_data['cards']} (сумма: {user_data['sum']}). Карты бота: {bot_sum}. {result}\n"
        "Начните новую игру с /start."
    )
    del context.user_data["game_21"]

# Игра "Карточная игра 21"
async def play_21(query, context) -> None:
    user_cards = [random.randint(1, 11) for _ in range(2)]
    user_sum = sum(user_cards)
    await query.edit_message_text(
        f"Ваши карты: {user_cards}. Сумма: {user_sum}. Хотите добрать карту? Напишите /hit или завершите игру с /stand.",
        reply_markup=end_game_buttons("21")
    )
    context.user_data["game_21"] = {"cards": user_cards, "sum": user_sum}

# Игра "Кости"
async def play_dice(query, context) -> None:
    player_roll = random.randint(1, 6) + random.randint(1, 6)
    bot_roll = random.randint(1, 6) + random.randint(1, 6)
    result = "Вы выиграли!🎉" if player_roll > bot_roll else "Вы проиграли!😞" if player_roll < bot_roll else "Ничья!🤝"
    await query.edit_message_text(
        f"Ваш бросок: {player_roll}. Бросок бота: {bot_roll}. {result}",
        reply_markup=end_game_buttons("dice")
    )

# Основной код
if __name__ == "__main__":
    TOKEN = "7802757253:AAGcbtFt3kikbs6zr4fDpuBZD-DqDDZuZKY"
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("hit", hit))
    app.add_handler(CommandHandler("stand", stand))

    print("Бот запущен!")
    app.run_polling()
