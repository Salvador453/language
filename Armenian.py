import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, timedelta, datetime
from pathlib import Path
import json
import threading
from flask import Flask
import os

# ====== Flask для Render ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Attendance Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ====== НАСТРОЙКИ ======
TOKEN = "8235493571:AAEWmFW3zyWw9i4j_JdRaj_4lRK_3mW9XbE"  # <-- замените на токен нового бота
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception as e:
    print("Ошибка при удалении webhook:", e)

# Главный староста (ты) — ID можно изменить
MAIN_STAROSTA_ID = 1509389908  # <-- твой Telegram ID

# Файлы данных
USERS_FILE = "attendance_users.json"
ATTENDANCE_FILE = "attendance.json"
REPLACEMENTS_FILE = "replacements.json"
STUDENTS_LIST_FILE = "students.json"

# ====== РАСПИСАНИЯ (как в оригинале) ======
def create_schedule_bcig():
    return {
        "monday": {
            "чисельник": {
                "1": {"subject": "Фізика і астрономія",  "room": "129", "teacher": "Гуленко І.А."},
                "2": {"subject": "Українська література","room": "115", "teacher": "Лосєва К.С."},
                "3": {"subject": "Історія України",      "room": "114", "teacher": "Мелещук Ю.Л."},
                "org": {"subject": "Організаційна година","room": "205", "teacher": "Крамаренко Л.О."},
                "4": {"subject": "Зарубіжна література", "room": "116", "teacher": "Мещерякова О.В."},
            },
            "знаменник": {
                "1": {"subject": "Фізика і астрономія",  "room": "129", "teacher": "Гуленко І.А."},
                "2": {"subject": "Українська література","room": "115", "teacher": "Лосєва К.С."},
                "3": {"subject": "Всесвітня історія",    "room": "114", "teacher": "Мелещук Ю.Л."},
                "org": {"subject": "Організаційна година","room": "205", "teacher": "Крамаренко Л.О."},
            },
        },
        "tuesday": {
            "чисельник": {
                "2": {"subject": "Фізична культура", "room": "с/з №2", "teacher": "Багрін В.С."},
                "3": {"subject": "Математика",       "room": "121",  "teacher": "Приймак О.В."},
                "4": {"subject": "Українська мова",  "room": "307",  "teacher": "Гавриленко С.Т."},
            },
            "знаменник": {
                "2": {"subject": "Фізична культура", "room": "с/з №2", "teacher": "Багрін В.С."},
                "3": {"subject": "Математика",       "room": "121",  "teacher": "Приймак О.В."},
                "4": {"subject": "Українська мова",  "room": "307",  "teacher": "Гавриленко С.Т."},
            },
        },
        "wednesday": {
            "чисельник": {
                "2": {"subject": "Технології",          "room": "208", "teacher": "Потапова А.О."},
                "3": {"subject": "Біологія і екологія", "room": "16",  "teacher": "Золотова К.В."},
                "4": {"subject": "Захист України",      "room": "242 / 201", "teacher": "Санко / Киянчук"},
            },
            "знаменник": {
                "2": {"subject": "Математика",          "room": "121", "teacher": "Приймак О.В."},
                "3": {"subject": "Біологія і екологія", "room": "16",  "teacher": "Золотова К.В."},
                "4": {"subject": "Захист України",      "room": "242 / 201", "teacher": "Санко / Киянчук"},
            },
        },
        "thursday": {
            "чисельник": {
                "1": {"subject": "Історія України",     "room": "114", "teacher": "Мелещук Ю.Л."},
                "2": {"subject": "Громадянська освіта", "room": "142", "teacher": "Зубко Г.М."},
                "3": {"subject": "Інформатика",         "room": "39",  "teacher": "Короленко / Єреп"},
            },
            "знаменник": {
                "1": {"subject": "Історія України",     "room": "114", "teacher": "Мелещук Ю.Л."},
                "2": {"subject": "Громадянська освіта", "room": "142", "teacher": "Зубко Г.М."},
                "3": {"subject": "Інформатика",         "room": "39",  "teacher": "Короленко / Єреп"},
                "4": {"subject": "Географія",           "room": "123", "teacher": "Баранець Т.О."},
            },
        },
        "friday": {
            "чисельник": {
                "2": {"subject": "Іноземна мова",       "room": "224 a", "teacher": "Криваноченкова Л.І."},
                "3": {"subject": "Хімія",               "room": "16",    "teacher": "Золотова К.В."},
                "4": {"subject": "Фізика і астрономія", "room": "129",   "teacher": "Гуленко І.А."},
            },
            "знаменник": {
                "2": {"subject": "Іноземна мова",       "room": "224 a", "teacher": "Криваноченкова Л.І."},
                "3": {"subject": "Хімія",               "room": "16",    "teacher": "Золотова К.В."},
                "4": {"subject": "Фізична культура",    "room": "с/з №2", "teacher": "Багрін В.С."},
            },
        },
        "saturday": {},
        "sunday":   {},
    }

def create_schedule_bcis():
    return {
        "monday": {
            "чисельник": {
                "1": {"subject": "Фізична культура", "room": "с/з №2", "teacher": "Свиридов А.П."},
                "2": {"subject": "Іноземна мова",    "room": "224 а", "teacher": "Криваноченкова Л.І."},
                "3": {"subject": "Математика",       "room": "121",  "teacher": "Приймак О.В."},
                "org": {"subject": "Організаційна година","room": "205", "teacher": "Крамаренко Л.О."}
            },
            "знаменник": {
                "1": {"subject": "Фізична культура", "room": "с/з №2", "teacher": "Свиридов А.П."},
                "2": {"subject": "Іноземна мова",    "room": "224 а", "teacher": "Криваноченкова Л.І."},
                "3": {"subject": "Математика",       "room": "121",  "teacher": "Приймак О.В."},
                "org": {"subject": "Організаційна година","room": "205", "teacher": "Крамаренко Л.О."},
            },
        },
        "tuesday": {
            "чисельник": {
                "1": {"subject": "Біологія і екологія", "room": "16",  "teacher": "Золотова К.В."},
                "2": {"subject": "Історія України",     "room": "114", "teacher": "Меленчук Ю.Д."},
                "3": {"subject": "Інформатика",         "room": "39",  "teacher": "Короленко / Єреп"},
            },
            "знаменник": {
                "1": {"subject": "Біологія і екологія", "room": "16",  "teacher": "Золотова К.В."},
                "2": {"subject": "Всесвітня історія",   "room": "114", "teacher": "Меленчук Ю.Д."},
                "3": {"subject": "Інформатика",         "room": "39",  "teacher": "Короленко / Єреп"},
            },
        },
        "wednesday": {
            "чисельник": {
                "1": {"subject": "Хімія",               "room": "16",  "teacher": "Золотова К.В."},
                "2": {"subject": "Математика",          "room": "121", "teacher": "Приймак О.В."},
                "3": {"subject": "Захист України",      "room": "242 / 201", "teacher": "Санко / Киянчук"},
            },
            "знаменник": {
                "1": {"subject": "Хімія",               "room": "16",  "teacher": "Золотова К.В."},
                "2": {"subject": "Технології",          "room": "208", "teacher": "Потапова А.О."},
                "3": {"subject": "Захист України",      "room": "242 / 201", "teacher": "Санко / Киянчук"},
                "4": {"subject": "Фізика і астрономія", "room": "129", "teacher": "Гуленко І.А."},
            },
        },
        "thursday": {
            "чисельник": {
                "1": {"subject": "Громадянська освіта", "room": "142", "teacher": "Зубко Г.М."},
                "2": {"subject": "Фізика і астрономія", "room": "129", "teacher": "Гуленко І.А."},
                "3": {"subject": "Українська мова",     "room": "307", "teacher": "Гавриленко С.Т."},
                "4": {"subject": "Зарубіжна література","room": "116", "teacher": "Менцєрякова О.В."},
            },
            "знаменник": {
                "1": {"subject": "Громадянська освіта", "room": "142", "teacher": "Зубко Г.М."},
                "2": {"subject": "Фізика і астрономія", "room": "129", "teacher": "Гуленко І.А."},
                "3": {"subject": "Українська мова",     "room": "307", "teacher": "Гавриленко С.Т."},
            },
        },
        "friday": {
            "чисельник": {
                "1": {"subject": "Фізична культура", "room": "с/з №2", "teacher": "Свиридов А.П."},
                "2": {"subject": "Історія України",   "room": "114", "teacher": "Меленчук Ю.Д."},
                "3": {"subject": "Українська література","room": "115", "teacher": "Лосєва К.С."},
            },
            "знаменник": {
                "1": {"subject": "Географія",         "room": "123", "teacher": "Бараненко Т.О."},
                "2": {"subject": "Історія України",   "room": "114", "teacher": "Меленчук Ю.Д."},
                "3": {"subject": "Українська література","room": "115", "teacher": "Лосєва К.С."},
            },
        },
        "saturday": {},
        "sunday":   {},
    }

SCHEDULE = {
    "БЦІГ-25": create_schedule_bcig(),
    "БЦІСТ-25": create_schedule_bcis()
}

# ====== ЗАГРУЗКА/СОХРАНЕНИЕ ======
def load_json(filename, default):
    path = Path(filename)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    path = Path(filename)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(USERS_FILE, {})  # {user_id: {"group": "...", "role": "...", "fio": "..."}}
attendance = load_json(ATTENDANCE_FILE, [])  # [{"date": "...", "group": "...", "pair": "...", "fio": "...", "status": "...", "marked_by": ...}]
replacements = load_json(REPLACEMENTS_FILE, {})  # {"date": {"pair": {"subject": "...", "room": "...", "teacher": "..."}}}
students_list = load_json(STUDENTS_LIST_FILE, {  # Предзагруженные списки студентов
    "БЦІГ-25": [
        "Іванов Іван Іванович",
        "Петров Петро Петрович",
        # ... добавьте всех
    ],
    "БЦІСТ-25": [
        "Сидоров Сидір Сидорович",
        # ... добавьте всех
    ]
})

# ====== ПОМОЩНИКИ ======
def is_starosta(user_id):
    return user_id == MAIN_STAROSTA_ID or users.get(str(user_id), {}).get("role") == "zamestitel"

def get_user_group(user_id):
    return users.get(str(user_id), {}).get("group")

def get_week_type(d=None):
    if d is None:
        d = date.today()
    ref_monday = date(2026, 1, 12)
    ref_type = "чисельник"
    weeks = (d - ref_monday).days // 7
    return ref_type if weeks % 2 == 0 else "знаменник"

def get_day_key(d=None):
    if d is None:
        d = date.today()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return days[d.weekday()]

def get_current_pair_info(group, day_key, week_type):
    """Получить инфу о текущей паре с учётом замен"""
    schedule = SCHEDULE.get(group, {}).get(day_key, {}).get(week_type, {})
    
    # Проверяем замены на сегодня
    today_str = date.today().isoformat()
    today_replacements = replacements.get(today_str, {})
    
    result = {}
    for pair_num, info in schedule.items():
        # Если есть замена — используем её
        if today_replacements.get(pair_num):
            result[pair_num] = today_replacements[pair_num]
        else:
            result[pair_num] = info
    
    return result

# ====== КОМАНДЫ ======
@bot.message_handler(commands=["start"])
def start_cmd(message):
    uid = str(message.from_user.id)
    
    if uid not in users:
        # Новый пользователь — выбор группы
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("БЦІГ-25", callback_data="group_БЦІГ-25"),
            InlineKeyboardButton("БЦІСТ-25 / ТЕ-25", callback_data="group_БЦІСТ-25")
        )
        bot.reply_to(message, "👋 Вітаю! Оберіть вашу групу:", reply_markup=markup)
    else:
        show_main_menu(message)

def show_main_menu(message):
    uid = str(message.from_user.id)
    user = users.get(uid, {})
    group = user.get("group", "Невідомо")
    role = "⭐ Староста" if int(uid) == MAIN_STAROSTA_ID else "👤 Студент"
    if user.get("role") == "zamestitel":
        role = "🔄 Заместитель старосты"
    
    text = f"📚 Група: {group}\n👤 Роль: {role}\n\nОберіть дію:"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if is_starosta(message.from_user.id):
        # Меню для старосты/заместителя
        markup.add(
            InlineKeyboardButton("📝 Відмітити присутність", callback_data="mark_attendance"),
            InlineKeyboardButton("📊 Статистика групи", callback_data="group_stats"),
            InlineKeyboardButton("🔄 Заміна пари", callback_data="add_replacement"),
            InlineKeyboardButton("👥 Список студентів", callback_data="students_list")
        )
        if int(uid) == MAIN_STAROSTA_ID:
            markup.add(InlineKeyboardButton("➕ Призначити заместителя", callback_data="set_zamestitel"))
    else:
        # Меню для обычного студента
        markup.add(
            InlineKeyboardButton("📊 Моя статистика", callback_data="my_stats"),
            InlineKeyboardButton("📅 Розклад на сьогодні", callback_data="today_schedule")
        )
    
    bot.reply_to(message, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def set_group(call):
    group = call.data.split("_")[1]
    uid = str(call.from_user.id)
    
    users[uid] = {
        "group": group,
        "role": "student",
        "fio": None,
        "username": call.from_user.username or ""
    }
    save_json(USERS_FILE, users)
    
    # Предлагаем ввести ФИО для обычных студентов
    if int(uid) != MAIN_STAROSTA_ID:
        bot.edit_message_text(
            "✅ Групу збережено!\n\n"
            "Для перегляду статистики введіть ваше ПІБ однією командою:\n"
            "/fio Іванов Іван Іванович",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.edit_message_text(
            "✅ Групу збережено! Ви — головний староста.",
            call.message.chat.id,
            call.message.message_id
        )
        show_main_menu(call.message)

@bot.message_handler(commands=["fio"])
def set_fio_cmd(message):
    uid = str(message.from_user.id)
    if uid not in users:
        bot.reply_to(message, "Спочатку оберіть групу: /start")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /fio Іванов Іван Іванович")
        return
    
    fio = parts[1].strip()
    users[uid]["fio"] = fio
    save_json(USERS_FILE, users)
    
    bot.reply_to(f"✅ ПІБ збережено: {fio}\nТепер ви можете дивитися свою статистику!")

# ====== ОТМЕТКА ПРИСУТСТВИЯ (для старосты) ======
@bot.callback_query_handler(func=lambda call: call.data == "mark_attendance")
def start_marking(call):
    if not is_starosta(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Немає доступу!")
        return
    
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    
    # Определяем текущую пару
    day_key = get_day_key()
    week_type = get_week_type()
    schedule = get_current_pair_info(group, day_key, week_type)
    
    if not schedule:
        bot.edit_message_text("📭 Сьогодні пар немає!", call.message.chat.id, call.message.message_id)
        return
    
    # Показываем список пар на сегодня
    markup = InlineKeyboardMarkup(row_width=1)
    for pair_num in sorted(schedule.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        info = schedule[pair_num]
        text = f"{pair_num}) {info['subject']}"
        markup.add(InlineKeyboardButton(text, callback_data=f"markpair_{pair_num}"))
    
    bot.edit_message_text(
        "📋 Оберіть пару для відмітки:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("markpair_"))
def select_pair_for_marking(call):
    pair_num = call.data.split("_")[1]
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    
    # Получаем список студентов группы
    students = students_list.get(group, [])
    
    if not students:
        bot.edit_message_text(
            "⚠️ Список студентів порожній! Додайте через /addstudent ПІБ",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Показываем студентов для отметки
    show_students_for_marking(call, pair_num, students, 0, {})

def show_students_for_marking(call, pair_num, students, page, marked):
    """Показываем студентов страницами по 5 человек"""
    per_page = 5
    start = page * per_page
    end = min(start + per_page, len(students))
    
    text = f"📝 Відмітка присутності — пара {pair_num}\n"
    text += f"Сторінка {page + 1}/{(len(students) + per_page - 1) // per_page}\n\n"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    for i in range(start, end):
        student = students[i]
        status = marked.get(student, "❓")
        text += f"{i+1}. {student} — {status}\n"
        
        # Кнопки для отметки
        markup.add(
            InlineKeyboardButton(f"✅ {student[:20]}", callback_data=f"status_{pair_num}_{i}_present_{page}"),
            InlineKeyboardButton(f"❌ {student[:20]}", callback_data=f"status_{pair_num}_{i}_absent_{page}")
        )
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"markpage_{pair_num}_{page-1}"))
    if end < len(students):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"markpage_{pair_num}_{page+1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    # Сохранить
    markup.add(InlineKeyboardButton("💾 Зберегти відмітки", callback_data=f"savemarks_{pair_num}"))
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("status_"))
def set_student_status(call):
    parts = call.data.split("_")
    pair_num, idx, status, page = parts[1], int(parts[2]), parts[3], int(parts[4])
    
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    students = students_list.get(group, [])
    student = students[idx]
    
    # Сохраняем во временное хранилище (в памяти бота)
    # Для простоты используем callback_data как хранилище, 
    # но лучше бы использовать Redis или словарь в памяти
    
    # Перезагружаем страницу с отметкой
    bot.answer_callback_query(call.id, f"{student} — {'Присутній' if status == 'present' else 'Відсутній'}")
    
    # Здесь нужно хранить состояние — для простоты сделаем через глобальный словарь
    # Но в продакшене лучше использовать Redis или другой способ

# ====== СТАТИСТИКА (для студентов) ======
@bot.callback_query_handler(func=lambda call: call.data == "my_stats")
def show_my_stats(call):
    uid = str(call.from_user.id)
    user = users.get(uid, {})
    fio = user.get("fio")
    group = user.get("group")
    
    if not fio:
        bot.edit_message_text(
            "⚠️ Спочатку введіть ПІБ: /fio Іванов Іван Іванович",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Фильтруем записи по ФИО
    my_attendance = [a for a in attendance if a["fio"] == fio and a["group"] == group]
    
    if not my_attendance:
        bot.edit_message_text(
            "📭 Поки що немає записів про вашу присутність.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Считаем статистику
    total = len(my_attendance)
    present = len([a for a in my_attendance if a["status"] == "present"])
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0
    
    # За периоды
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    week_total = len([a for a in my_attendance if date.fromisoformat(a["date"]) >= week_ago])
    week_present = len([a for a in my_attendance if date.fromisoformat(a["date"]) >= week_ago and a["status"] == "present"])
    
    month_total = len([a for a in my_attendance if date.fromisoformat(a["date"]) >= month_ago])
    month_present = len([a for a in my_attendance if date.fromisoformat(a["date"]) >= month_ago and a["status"] == "present"])
    
    text = f"📊 Статистика відвідування для {fio}\n\n"
    text += f"📅 За весь час: {present}/{total} ({percentage:.1f}%)\n"
    text += f"📆 За місяць: {month_present}/{month_total}\n"
    text += f"🗓️ За тиждень: {week_present}/{week_total}\n\n"
    
    # Последние 5 записей
    text += "📝 Останні записи:\n"
    for a in sorted(my_attendance, key=lambda x: x["date"], reverse=True)[:5]:
        status_emoji = "✅" if a["status"] == "present" else "❌"
        text += f"{a['date']}: {a['pair']} — {status_emoji}\n"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

# ====== ЗАМЕНЫ ПАР (для старосты) ======
@bot.callback_query_handler(func=lambda call: call.data == "add_replacement")
def start_replacement(call):
    if not is_starosta(call.from_user.id):
        return
    
    bot.edit_message_text(
        "🔄 Введіть заміну у форматі:\n"
        "/replace <номер пари> <предмет> ; <аудиторія> ; <викладач>\n\n"
        "Приклад:\n"
        "/replace 3 Фізика ; 129 ; Гуленко І.А.",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(commands=["replace"])
def add_replacement_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /replace 3 Фізика ; 129 ; Гуленко І.А.")
        return
    
    rest = parts[1]
    try:
        pair_num, rest = rest.split(maxsplit=1)
        info_parts = [p.strip() for p in rest.split(";")]
        
        replacement_info = {
            "subject": info_parts[0],
            "room": info_parts[1] if len(info_parts) > 1 else "",
            "teacher": info_parts[2] if len(info_parts) > 2 else ""
        }
        
        today_str = date.today().isoformat()
        if today_str not in replacements:
            replacements[today_str] = {}
        
        replacements[today_str][pair_num] = replacement_info
        save_json(REPLACEMENTS_FILE, replacements)
        
        bot.reply_to(message, f"✅ Заміну на пару {pair_num} додано на сьогодні!")
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")

# ====== УПРАВЛЕНИЕ СТУДЕНТАМИ ======
@bot.message_handler(commands=["addstudent"])
def add_student_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    uid = str(message.from_user.id)
    group = users[uid]["group"]
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /addstudent Іванов Іван Іванович")
        return
    
    fio = parts[1].strip()
    
    if group not in students_list:
        students_list[group] = []
    
    if fio not in students_list[group]:
        students_list[group].append(fio)
        students_list[group].sort()
        save_json(STUDENTS_LIST_FILE, students_list)
        bot.reply_to(message, f"✅ {fio} додано до групи {group}")
    else:
        bot.reply_to(message, f"⚠️ {fio} вже є в списку")

@bot.callback_query_handler(func=lambda call: call.data == "students_list")
def show_students(call):
    if not is_starosta(call.from_user.id):
        return
    
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    students = students_list.get(group, [])
    
    text = f"👥 Список студентів {group} ({len(students)} чол.):\n\n"
    for i, s in enumerate(students, 1):
        text += f"{i}. {s}\n"
    
    text += "\nДодати: /addstudent ПІБ"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

# ====== ЗАМЕСТИТЕЛЬ ======
@bot.callback_query_handler(func=lambda call: call.data == "set_zamestitel")
def set_zamestitel_start(call):
    if call.from_user.id != MAIN_STAROSTA_ID:
        bot.answer_callback_query(call.id, "Тільки головний староста!")
        return
    
    bot.edit_message_text(
        "➕ Введіть ID заместителя:\n/setzam <ID Telegram>",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(commands=["setzam"])
def set_zamestitel_cmd(message):
    if message.from_user.id != MAIN_STAROSTA_ID:
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Формат: /setzam 123456789")
        return
    
    zam_id = parts[1]
    
    if zam_id in users:
        users[zam_id]["role"] = "zamestitel"
        save_json(USERS_FILE, users)
        bot.reply_to(message, f"✅ Користувач {zam_id} призначений заместителем!")
        try:
            bot.send_message(int(zam_id), "🎉 Вас призначено заместителем старости!")
        except:
            pass
    else:
        bot.reply_to(message, "❌ Користувач ще не запускав бота. Нехай напише /start")

# ====== СТАРТ ======
print("🤖 Бот журнала посещаемости запущен!")
bot.infinity_polling()
