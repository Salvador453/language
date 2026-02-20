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
MARKING_STATE_FILE = "marking_state.json"  # Временное состояние отметок

# ====== РАСПИСАНИЯ ======
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
marking_state = load_json(MARKING_STATE_FILE, {})  # {user_id: {"pair": "...", "marked": {}}}
students_list = load_json(STUDENTS_LIST_FILE, {
    "БЦІГ-25": [],
    "БЦІСТ-25": []
})

# ====== ПОМОЩНИКИ ======
def is_starosta(user_id):
    uid = str(user_id)
    return int(uid) == MAIN_STAROSTA_ID or users.get(uid, {}).get("role") == "zamestitel"

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

def get_current_schedule(group, day_key, week_type):
    """Получить расписание с учётом замен"""
    schedule = SCHEDULE.get(group, {}).get(day_key, {}).get(week_type, {}).copy()
    
    # Применяем замены на сегодня
    today_str = date.today().isoformat()
    today_replacements = replacements.get(today_str, {})
    
    for pair_num, new_info in today_replacements.items():
        if pair_num in schedule:
            schedule[pair_num] = new_info
    
    return schedule

# ====== ГЛАВНОЕ МЕНЮ ======
@bot.message_handler(commands=["start", "menu"])
def start_cmd(message):
    uid = str(message.from_user.id)
    
    if uid not in users:
        # Новый пользователь — выбор группы
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📘 БЦІГ-25", callback_data="group_БЦІГ-25"),
            InlineKeyboardButton("📗 БЦІСТ-25 / ТЕ-25", callback_data="group_БЦІСТ-25")
        )
        bot.reply_to(message, "👋 Вітаю! Оберіть вашу групу:", reply_markup=markup)
    else:
        show_main_menu(message)

def show_main_menu(message):
    uid = str(message.from_user.id)
    user = users.get(uid, {})
    group = user.get("group", "❓")
    fio = user.get("fio", "❓")
    
    if int(uid) == MAIN_STAROSTA_ID:
        role = "⭐ Головний староста"
    elif user.get("role") == "zamestitel":
        role = "🔄 Заместитель"
    else:
        role = "👤 Студент"
    
    text = f"📚 <b>Група:</b> {group}\n"
    text += f"👤 <b>ПІБ:</b> {fio}\n"
    text += f"🎖 <b>Роль:</b> {role}\n\n"
    text += "Оберіть дію:"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if is_starosta(message.from_user.id):
        markup.add(
            InlineKeyboardButton("📝 Відмітити", callback_data="menu_mark"),
            InlineKeyboardButton("📊 Статистика групи", callback_data="menu_groupstats"),
            InlineKeyboardButton("🔄 Заміна пари", callback_data="menu_replace"),
            InlineKeyboardButton("👥 Студенти", callback_data="menu_students")
        )
        if int(uid) == MAIN_STAROSTA_ID:
            markup.add(InlineKeyboardButton("➕ Заместитель", callback_data="menu_setzam"))
    else:
        markup.add(
            InlineKeyboardButton("📊 Моя статистика", callback_data="menu_mystats"),
            InlineKeyboardButton("📅 Сьогодні", callback_data="menu_today")
        )
    
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

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
    
    # Удаляем старое сообщение
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    if int(uid) == MAIN_STAROSTA_ID:
        bot.send_message(call.message.chat.id, "✅ Ви — головний староста!")
        show_main_menu(call.message)
    else:
        msg = bot.send_message(
            call.message.chat.id,
            "✅ Групу збережено!\n\n"
            "Тепер введіть ваше ПІБ командою:\n"
            "<code>/fio Прізвище Ім'я По-батькові</code>\n\n"
            "Приклад: <code>/fio Шевченко Тарас Григорович</code>",
            parse_mode="HTML"
        )

# ====== ФИО ======
@bot.message_handler(commands=["fio"])
def set_fio_cmd(message):
    uid = str(message.from_user.id)
    
    if uid not in users:
        bot.reply_to(message, "❌ Спочатку оберіть групу: /start")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, 
            "❌ Формат: <code>/fio Прізвище Ім'я По-батькові</code>\n"
            "Приклад: <code>/fio Шевченко Тарас Григорович</code>",
            parse_mode="HTML"
        )
        return
    
    fio = parts[1].strip()
    
    # Проверяем, что ФИО не слишком короткое
    if len(fio) < 5:
        bot.reply_to(message, "❌ ПІБ занадто короткий. Введіть повністю.")
        return
    
    users[uid]["fio"] = fio
    save_json(USERS_FILE, users)
    
    bot.reply_to(message, f"✅ ПІБ збережено: <b>{fio}</b>", parse_mode="HTML")
    
    # Показываем меню
    show_main_menu(message)

# ====== ОТМЕТКА ПРИСУТСТВИЯ ======
@bot.callback_query_handler(func=lambda call: call.data == "menu_mark")
def start_marking(call):
    if not is_starosta(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Немає доступу!")
        return
    
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    
    day_key = get_day_key()
    week_type = get_week_type()
    schedule = get_current_schedule(group, day_key, week_type)
    
    if not schedule:
        bot.edit_message_text("📭 Сьогодні пар немає!", call.message.chat.id, call.message.message_id)
        return
    
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Сортируем: сначала числовые пары, потом org
    pairs = []
    for k in schedule.keys():
        if k == "org":
            pairs.append((0, "org", "🔸 Організаційна година"))
        else:
            pairs.append((int(k), k, f"{k}) {schedule[k]['subject']}"))
    
    pairs.sort()
    
    for _, pair_num, text in pairs:
        markup.add(InlineKeyboardButton(text, callback_data=f"markpair_{pair_num}"))
    
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_menu"))
    
    bot.edit_message_text(
        "📋 Оберіть пару для відмітки:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("markpair_"))
def select_pair(call):
    pair_num = call.data.split("_")[1]
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    
    students = students_list.get(group, [])
    
    if not students:
        bot.edit_message_text(
            "⚠️ Список студентів порожній!\n\n"
            "Додайте студентів командою:\n"
            "<code>/addstudent Прізвище Ім'я По-батькові</code>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        return
    
    # Инициализируем состояние отметки
    marking_state[uid] = {
        "pair": pair_num,
        "group": group,
        "date": date.today().isoformat(),
        "marked": {}  # {fio: "present"/"absent"}
    }
    save_json(MARKING_STATE_FILE, marking_state)
    
    show_marking_page(call, 0)

def show_marking_page(call, page):
    uid = str(call.from_user.id)
    state = marking_state.get(uid, {})
    students = students_list.get(state.get("group"), [])
    marked = state.get("marked", {})
    pair = state.get("pair", "?")
    
    per_page = 6
    start = page * per_page
    end = min(start + per_page, len(students))
    total_pages = (len(students) + per_page - 1) // per_page
    
    # Формируем текст
    text = f"📝 <b>Відмітка присутності</b>\n"
    text += f"📚 Пара: <b>{pair}</b>\n"
    text += f"📅 {date.today().strftime('%d.%m.%Y')}\n"
    text += f"👥 Сторінка {page+1}/{total_pages}\n\n"
    
    # Считаем статистику
    present_count = sum(1 for v in marked.values() if v == "present")
    absent_count = sum(1 for v in marked.values() if v == "absent")
    total_marked = present_count + absent_count
    
    text += f"✅ Присутні: {present_count} | ❌ Відсутні: {absent_count}\n"
    text += f"📊 Всього відмічено: {total_marked}/{len(students)}\n\n"
    
    markup = InlineKeyboardMarkup(row_width=3)
    
    for i in range(start, end):
        student = students[i]
        status = marked.get(student)
        
        if status == "present":
            emoji = "✅"
            btn_text = f"{emoji} {student[:15]}"
        elif status == "absent":
            emoji = "❌"
            btn_text = f"{emoji} {student[:15]}"
        else:
            emoji = "⚪"
            btn_text = f"{emoji} {student[:15]}"
        
        # Кнопки: Присутній | Студент | Відсутній
        markup.row(
            InlineKeyboardButton("✅", callback_data=f"st_{i}_yes_{page}"),
            InlineKeyboardButton(btn_text, callback_data=f"st_{i}_info_{page}"),
            InlineKeyboardButton("❌", callback_data=f"st_{i}_no_{page}")
        )
    
    # Навигация
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="page_info"))
    if end < len(students):
        nav.append(InlineKeyboardButton("➡️", callback_data=f"page_{page+1}"))
    markup.row(*nav)
    
    # Сохранить и назад
    markup.row(
        InlineKeyboardButton("💾 Зберегти всі відмітки", callback_data="save_all"),
        InlineKeyboardButton("◀️ Меню", callback_data="back_menu")
    )
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("st_"))
def mark_student(call):
    parts = call.data.split("_")
    idx, action, page = int(parts[1]), parts[2], int(parts[3])
    
    uid = str(call.from_user.id)
    state = marking_state.get(uid, {})
    students = students_list.get(state.get("group"), [])
    
    if idx >= len(students):
        bot.answer_callback_query(call.id, "Помилка!")
        return
    
    student = students[idx]
    
    if action == "yes":
        state["marked"][student] = "present"
        bot.answer_callback_query(call.id, f"✅ {student} — Присутній")
    elif action == "no":
        state["marked"][student] = "absent"
        bot.answer_callback_query(call.id, f"❌ {student} — Відсутній")
    else:
        bot.answer_callback_query(call.id, student)
        return
    
    save_json(MARKING_STATE_FILE, marking_state)
    show_marking_page(call, page)

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def change_page(call):
    if call.data == "page_info":
        bot.answer_callback_query(call.id, "Поточна сторінка")
        return
    
    page = int(call.data.split("_")[1])
    show_marking_page(call, page)

@bot.callback_query_handler(func=lambda call: call.data == "save_all")
def save_attendance(call):
    uid = str(call.from_user.id)
    state = marking_state.get(uid, {})
    
    if not state or not state.get("marked"):
        bot.answer_callback_query(call.id, "Немає відміток для збереження!")
        return
    
    # Сохраняем все отметки
    saved_count = 0
    for fio, status in state["marked"].items():
        record = {
            "date": state["date"],
            "group": state["group"],
            "pair": state["pair"],
            "fio": fio,
            "status": status,
            "marked_by": uid,
            "timestamp": datetime.now().isoformat()
        }
        attendance.append(record)
        saved_count += 1
    
    save_json(ATTENDANCE_FILE, attendance)
    
    # Очищаем состояние
    marking_state.pop(uid, None)
    save_json(MARKING_STATE_FILE, marking_state)
    
    bot.edit_message_text(
        f"✅ <b>Збережено!</b>\n\n"
        f"📅 Дата: {state['date']}\n"
        f"📚 Пара: {state['pair']}\n"
        f"👥 Відмічено: {saved_count} студентів\n\n"
        f"Для перегляду статистики використовуйте меню.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )

# ====== СТАТИСТИКА СТУДЕНТА ======
@bot.callback_query_handler(func=lambda call: call.data == "menu_mystats")
def show_my_stats(call):
    uid = str(call.from_user.id)
    user = users.get(uid, {})
    fio = user.get("fio")
    group = user.get("group")
    
    if not fio:
        bot.edit_message_text(
            "⚠️ Спочатку введіть ПІБ командою:\n"
            "<code>/fio Прізвище Ім'я По-батькові</code>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        return
    
    # Фильтруем по ФИО и группе
    my_records = [a for a in attendance if a["fio"] == fio and a["group"] == group]
    
    if not my_records:
        bot.edit_message_text(
            "📭 Поки що немає записів про вашу присутність.\n\n"
            "Статистика з'явиться після першої відмітки старостою.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Считаем статистику
    total = len(my_records)
    present = len([r for r in my_records if r["status"] == "present"])
    absent = total - present
    percent = (present / total * 100) if total > 0 else 0
    
    # По периодам
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    week_records = [r for r in my_records if date.fromisoformat(r["date"]) >= week_ago]
    week_present = len([r for r in week_records if r["status"] == "present"])
    
    month_records = [r for r in my_records if date.fromisoformat(r["date"]) >= month_ago]
    month_present = len([r for r in month_records if r["status"] == "present"])
    
    text = f"📊 <b>Статистика відвідування</b>\n"
    text += f"👤 <b>{fio}</b>\n"
    text += f"📚 {group}\n\n"
    
    text += f"<b>📅 За весь час:</b>\n"
    text += f"  ✅ Присутній: {present}/{total} ({percent:.1f}%)\n"
    text += f"  ❌ Відсутній: {absent}/{total}\n\n"
    
    text += f"<b>📆 За місяць:</b> {month_present}/{len(month_records)}\n"
    text += f"<b>🗓️ За тиждень:</b> {week_present}/{len(week_records)}\n\n"
    
    # Последние записи
    text += "<b>📝 Останні 5 записів:</b>\n"
    recent = sorted(my_records, key=lambda x: x["date"], reverse=True)[:5]
    for r in recent:
        emoji = "✅" if r["status"] == "present" else "❌"
        d = date.fromisoformat(r["date"]).strftime("%d.%m")
        text += f"{emoji} {d} — {r['pair']}\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_menu"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode="HTML")

# ====== ЗАМЕНЫ ======
@bot.callback_query_handler(func=lambda call: call.data == "menu_replace")
def show_replace_menu(call):
    if not is_starosta(call.from_user.id):
        return
    
    bot.edit_message_text(
        "🔄 <b>Заміна пари</b>\n\n"
        "Введіть команду:\n"
        "<code>/replace НомерПари Предмет ; Аудиторія ; Викладач</code>\n\n"
        "<b>Приклади:</b>\n"
        "<code>/replace 3 Фізика ; 129 ; Гуленко І.А.</code>\n"
        "<code>/replace org Історія ; 114 ; Мелещук Ю.Л.</code>\n\n"
        "Щоб скасувати заміну:\n"
        "<code>/cancelreplace 3</code>",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )

@bot.message_handler(commands=["replace"])
def add_replace_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /replace 3 Фізика ; 129 ; Гуленко І.А.")
        return
    
    rest = parts[1].strip()
    
    try:
        # Парсим: номер пары и остальное
        pair_part = rest.split()[0]
        info_part = rest[len(pair_part):].strip()
        
        # Разбираем по ;
        info_parts = [p.strip() for p in info_part.split(";")]
        
        new_info = {
            "subject": info_parts[0],
            "room": info_parts[1] if len(info_parts) > 1 else "",
            "teacher": info_parts[2] if len(info_parts) > 2 else ""
        }
        
        today_str = date.today().isoformat()
        if today_str not in replacements:
            replacements[today_str] = {}
        
        replacements[today_str][pair_part] = new_info
        save_json(REPLACEMENTS_FILE, replacements)
        
        bot.reply_to(message, 
            f"✅ <b>Заміну додано!</b>\n\n"
            f"📅 На сьогодні ({today_str})\n"
            f"📚 Пара {pair_part}: <b>{new_info['subject']}</b>\n"
            f"🏫 Ауд. {new_info['room']}, {new_info['teacher']}",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")

@bot.message_handler(commands=["cancelreplace"])
def cancel_replace_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /cancelreplace 3")
        return
    
    pair_num = parts[1]
    today_str = date.today().isoformat()
    
    if today_str in replacements and pair_num in replacements[today_str]:
        del replacements[today_str][pair_num]
        save_json(REPLACEMENTS_FILE, replacements)
        bot.reply_to(message, f"✅ Заміну для пари {pair_num} скасовано!")
    else:
        bot.reply_to(message, "❌ Заміни для цієї пари не знайдено.")

# ====== СТУДЕНТЫ ======
@bot.callback_query_handler(func=lambda call: call.data == "menu_students")
def show_students_menu(call):
    if not is_starosta(call.from_user.id):
        return
    
    uid = str(call.from_user.id)
    group = users[uid]["group"]
    students = students_list.get(group, [])
    
    text = f"👥 <b>Список студентів {group}</b>\n"
    text += f"Всього: {len(students)} чол.\n\n"
    
    for i, s in enumerate(students, 1):
        text += f"{i}. {s}\n"
    
    text += "\n<b>Команди:</b>\n"
    text += "<code>/addstudent Прізвище Ім'я По-батькові</code>\n"
    text += "<code>/delstudent Номер</code>"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_menu"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                         reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=["addstudent"])
def add_student_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    uid = str(message.from_user.id)
    group = users[uid]["group"]
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /addstudent Шевченко Тарас Григорович")
        return
    
    fio = parts[1].strip()
    
    if group not in students_list:
        students_list[group] = []
    
    if fio in students_list[group]:
        bot.reply_to(message, f"⚠️ {fio} вже є в списку!")
        return
    
    students_list[group].append(fio)
    students_list[group].sort()
    save_json(STUDENTS_LIST_FILE, students_list)
    
    bot.reply_to(message, f"✅ <b>{fio}</b> додано до групи {group}!", parse_mode="HTML")

@bot.message_handler(commands=["delstudent"])
def del_student_cmd(message):
    if not is_starosta(message.from_user.id):
        return
    
    uid = str(message.from_user.id)
    group = users[uid]["group"]
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /delstudent 5 (номер у списку)")
        return
    
    try:
        idx = int(parts[1]) - 1
        students = students_list.get(group, [])
        
        if 0 <= idx < len(students):
            removed = students.pop(idx)
            save_json(STUDENTS_LIST_FILE, students_list)
            bot.reply_to(message, f"✅ <b>{removed}</b> видалено зі списку!", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Невірний номер!")
    except ValueError:
        bot.reply_to(message, "❌ Введіть число!")

# ====== ЗАМЕСТИТЕЛЬ ======
@bot.callback_query_handler(func=lambda call: call.data == "menu_setzam")
def set_zam_start(call):
    if call.from_user.id != MAIN_STAROSTA_ID:
        bot.answer_callback_query(call.id, "Тільки головний староста!")
        return
    
    bot.edit_message_text(
        "➕ <b>Призначення заместителя</b>\n\n"
        "Введіть ID користувача:\n"
        "<code>/setzam 123456789</code>\n\n"
        "ID можна дізнатися через бота @userinfobot",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )

@bot.message_handler(commands=["setzam"])
def set_zam_cmd(message):
    if message.from_user.id != MAIN_STAROSTA_ID:
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /setzam 123456789")
        return
    
    zam_id = parts[1]
    
    if zam_id not in users:
        bot.reply_to(message, 
            "❌ Користувач ще не запускав бота!\n\n"
            "Нехай спочатку напише мені /start і обере групу."
        )
        return
    
    users[zam_id]["role"] = "zamestitel"
    save_json(USERS_FILE, users)
    
    # Уведомляем заместителя
    try:
        bot.send_message(int(zam_id), 
            "🎉 <b>Вітаємо!</b>\n\n"
            "Вас призначено заместителем старости!\n"
            "Тепер ви можете відмічати присутність групи.",
            parse_mode="HTML"
        )
    except:
        pass
    
    bot.reply_to(message, f"✅ Користувач {zam_id} призначений заместителем!")

# ====== НАЗАД В МЕНЮ ======
@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_to_menu(call):
    show_main_menu(call.message)

# ====== СТАРТ ======
print("🤖 Бот журнала посещаемости запущен!")
bot.infinity_polling()
