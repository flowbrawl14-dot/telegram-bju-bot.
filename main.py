import telebot
from telebot import types

# ⚠️ Ваш токен бота
TOKEN = "8881982081:AAGXI-WI21RXlT2nYsUgMvSTX0sYC6LtFug"

bot = telebot.TeleBot(TOKEN)
user_data = {}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_calc = types.KeyboardButton("📊 Рассчитать БЖУ")
    markup.add(btn_calc)

    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой продвинутый бот для расчета БЖУ, воды и целей.\n\n"
        "Нажми кнопку ниже, чтобы начать расчет:",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == "📊 Рассчитать БЖУ")
def ask_gender(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_male = types.KeyboardButton("👨 Мужчина")
    btn_female = types.KeyboardButton("👩 Женщина")
    markup.add(btn_male, btn_female)

    bot.send_message(
        message.chat.id,
        "**Шаг 1 из 7.** Укажи свой пол:",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(func=lambda message: message.text in ["👨 Мужчина", "👩 Женщина"])
def process_gender(message):
    gender = "male" if message.text == "👨 Мужчина" else "female"
    user_data[message.chat.id] = {"gender": gender}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_loss = types.KeyboardButton("🔥 Похудение (дефицит 15%)")
    btn_maintain = types.KeyboardButton("⚖️ Поддержание формы")
    btn_gain = types.KeyboardButton("💪 Массонабор (профицит 15%)")
    markup.add(btn_loss, btn_maintain, btn_gain)

    bot.send_message(
        message.chat.id,
        f"Выбран пол: {'Мужской 👨' if gender == 'male' else 'Женский 👩'}\n\n"
        "**Шаг 2 из 7.** Выбери свою главную цель:",
        reply_markup=markup,
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(message, process_goal)


def process_goal(message):
    text = message.text
    if "Похудение" in text:
        goal_type = "goal_loss"
    elif "Массонабор" in text:
        goal_type = "goal_gain"
    else:
        goal_type = "goal_maintain"

    user_data[message.chat.id]["goal"] = goal_type

    markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(
        message.chat.id,
        "**Шаг 3 из 7.** Введи свой **текущий вес в килограммах**:",
        reply_markup=markup,
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(msg, process_current_weight)


def process_current_weight(message):
    try:
        weight = float(message.text)
        if not (30 <= weight <= 200):
            msg = bot.send_message(
                message.chat.id,
                "❌ Похоже, это нереалистичный вес. Пожалуйста, введи настоящие данные:",
            )
            bot.register_next_step_handler(msg, process_current_weight)
            return

        user_data[message.chat.id]["weight"] = weight
        msg = bot.send_message(
            message.chat.id,
            "**Шаг 4 из 7.** Введи свой **желаемый вес в килограммах**:",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(msg, process_target_weight)
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Ошибка! Пожалуйста, введи число (например: 75):",
        )
        bot.register_next_step_handler(msg, process_current_weight)


def process_target_weight(message):
    try:
        target_weight = float(message.text)
        if not (30 <= target_weight <= 200):
            msg = bot.send_message(
                message.chat.id,
                "❌ Похоже, это нереалистичный вес. Пожалуйста, введи настоящие данные:",
            )
            bot.register_next_step_handler(msg, process_target_weight)
            return

        user_data[message.chat.id]["target_weight"] = target_weight

        msg = bot.send_message(
            message.chat.id,
            "**Шаг 5 из 7.** Введи свой **рост в сантиметрах**:",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(msg, process_height)
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Ошибка! Пожалуйста, введи число (например: 70):",
        )
        bot.register_next_step_handler(msg, process_target_weight)


def process_height(message):
    try:
        height = float(message.text)
        if not (140 <= height <= 230):
            msg = bot.send_message(
                message.chat.id,
                "❌ Похоже, это нереалистичный рост. Пожалуйста, введи настоящие данные:",
            )
            bot.register_next_step_handler(msg, process_height)
            return

        user_data[message.chat.id]["height"] = height

        msg = bot.send_message(
            message.chat.id,
            "**Шаг 6 из 7.** Введи свой **возраст** (лет):",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(msg, process_age)
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Ошибка! Пожалуйста, введи число (например: 175):",
        )
        bot.register_next_step_handler(msg, process_height)


def process_age(message):
    try:
        age = float(message.text)
        if not (10 <= age <= 120):
            msg = bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введи реальный возраст:",
            )
            bot.register_next_step_handler(msg, process_age)
            return

        user_data[message.chat.id]["age"] = age

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🛋️ Минимальная (сидячая работа, без спорта)")
        btn2 = types.KeyboardButton("🚶 Легкая (тренировки 1-3 раза в неделю)")
        btn3 = types.KeyboardButton("🏃 Умеренная (тренировки 3-5 раз в неделю)")
        btn4 = types.KeyboardButton("🏋️ Высокая (тяжелые тренировки 6-7 раз)")
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(
            message.chat.id,
            "**Шаг 7 из 7.** Выбери свой **уровень физической активности**:",
            reply_markup=markup,
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(message, process_activity)
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Ошибка! Пожалуйста, введи число (например: 25):",
        )
        bot.register_next_step_handler(msg, process_age)


def process_activity(message):
    text = message.text
    if "Минимальная" in text:
        activity_coef = 1.2
        activity_text = "Минимальная (1.2)"
    elif "Легкая" in text:
        activity_coef = 1.375
        activity_text = "Легкая (1.375)"
    elif "Высокая" in text:
        activity_coef = 1.725
        activity_text = "Высокая (1.725)"
    else:
        activity_coef = 1.55
        activity_text = "Умеренная (1.55)"

    chat_id = message.chat.id
    data = user_data[chat_id]

    gender = data["gender"]
    goal_type = data["goal"]
    weight = data["weight"]
    target_weight = data["target_weight"]
    height = data["height"]
    age = data["age"]

    # 1. Формула Миффлина-Сан Жеора
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    base_calories = bmr * activity_coef

    # 2. Корректировка под цель
    if goal_type == "goal_loss":
        calories = round(base_calories * 0.85)
        goal_text = "Похудение (дефицит 15%) 🔥"
    elif goal_type == "goal_gain":
        calories = round(base_calories * 1.15)
        goal_text = "Массонабор (профицит 15%) 💪"
    else:
        calories = round(base_calories)
        goal_text = "Поддержание формы ⚖️"

    # 3. БЖУ
    protein = round((calories * 0.30) / 4)
    fat = round((calories * 0.30) / 9)
    carbs = round((calories * 0.40) / 4)

    # 4. Норма воды
    water_liters = round(weight * 0.035, 1)

    # Разница веса
    diff = round(abs(weight - target_weight), 1)
    if weight > target_weight:
        weight_comment = f"📉 До желаемого веса осталось скинуть: **{diff} кг**"
    elif weight < target_weight:
        weight_comment = f"📈 До желаемого веса нужно набрать: **{diff} кг**"
    else:
        weight_comment = "🎯 У тебя идеальный целевой вес! Держим форму."

    # Возвращаем стартовую кнопку внизу
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_calc = types.KeyboardButton("📊 Рассчитать БЖУ")
    markup.add(btn_calc)

    res_message = (
        f"📊 **Твой индивидуальный план:**\n\n"
        f"🎯 **Цель:** {goal_text}\n"
        f"⚖️ **Текущий вес:** {weight} кг | 🏁 **Желаемый:** {target_weight} кг\n"
        f"{weight_comment}\n\n"
        f"🔥 **Суточная норма:** {calories} ккал\n"
        f"🥩 **Белки:** {protein} г\n"
        f"🥑 **Жиры:** {fat} г\n"
        f"🍞 **Углеводы:** {carbs} г\n\n"
        f"💧 **Норма воды:** примерно {water_liters} л в день\n\n"
        f"💡 *Активность: {activity_text}*"
    )

    photo_url = "https://i.postimg.cc/HkB9XHg2/tvoj-bzu.png"

    try:
        bot.send_photo(
            chat_id,
            photo_url,
            caption=res_message,
            parse_mode="Markdown",
            reply_markup=markup,
        )
    except Exception:
        bot.send_message(chat_id, res_message, parse_mode="Markdown", reply_markup=markup)


print("Бот успешно запущен!")
bot.infinity_polling()