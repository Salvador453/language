import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import date, timedelta, datetime
from pathlib import Path
import json
import time
import re
import threading
from flask import Flask
import os
import openpyxl
from io import BytesIO

# ====== мини-вебсервер для Render ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Attendance bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()
# =======================================

# ================== НАСТРОЙКИ ==================
TOKEN = "8235493571:AAEWmFW3zyWw9i4j_JdRaj_4lRK_3mW9XbE"
bot = telebot.TeleBot(TOKEN)

# Удаляем вебхук на всякий случай
try:
    bot.remove_webhook()
except Exception as e:
    print("Ошибка при удалении webhook:", e)

MAIN_ADMIN_ID = 1509389908  # Ваш ID (староста)
ADMIN_IDS = {MAIN_ADMIN_ID}  # Множество админов, сюда можно добавлять заместителя

REFERENCE_MONDAY = date(2026, 1, 12)
REFERENCE_WEEK_TYPE = "чисельник"

# Файлы для хранения данных
USERS_FILE = "users.json"           # информация о пользователях (id, группа, фио, role)
STUDENTS_FILE = "students.json"      # список студентов с привязкой к группе (ФИО, tg_id, группа)
ATTENDANCE_FILE = "attendance.json"  # журнал посещаемости
SCHEDULE_FILE = "schedule.json"      # расписание (может использоваться для получения списка пар)
SUBSTITUTIONS_FILE = "substitutions.json"  # замены на конкретные даты

# ================== РАСПИСАНИЕ (копируем из твоего сообщения) ==================
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

# Загружаем или создаём расписание
def load_schedule():
    path = Path(SCHEDULE_FILE)
    if not path.exists():
        return {
            "БЦІГ-25": create_schedule_bcig(),
            "БЦІСТ-25": create_schedule_bcis()
        }
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_schedule(data):
    path = Path(SCHEDULE_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

schedule = load_schedule()

# Замены на конкретные даты (хранятся в виде: {date_str: {group: {pair_num: subject, room, teacher}})
def load_substitutions():
    path = Path(SUBSTITUTIONS_FILE)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_substitutions():
    path = Path(SUBSTITUTIONS_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(substitutions, f, ensure_ascii=False, indent=2)

substitutions = load_substitutions()

# Пользователи (кто писал боту, с их ролью)
def load_users():
    path = Path(USERS_FILE)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_users():
    path = Path(USERS_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

# Студенты (ФИО, tg_id, группа)
def load_students():
    path = Path(STUDENTS_FILE)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_students():
    path = Path(STUDENTS_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)

students = load_students()

# Журнал посещаемости
def load_attendance():
    path = Path(ATTENDANCE_FILE)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_attendance():
    path = Path(ATTENDANCE_FILE)
    with path.open("w", encoding="utf-8") as f:
        json.dump(attendance, f, ensure_ascii=False, indent=2)

attendance = load_attendance()

# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================
def get_week_type(target_date=None):
    if target_date is None:
        target_date = date.today()
    delta_days = (target_date - REFERENCE_MONDAY).days
    weeks_passed = delta_days // 7
    if weeks_passed % 2 == 0:
        return REFERENCE_WEEK_TYPE
    else:
        return "знаменник" if REFERENCE_WEEK_TYPE == "чисельник" else "чисельник"

def get_day_key(target_date=None):
    if target_date is None:
        target_date = date.today()
    weekday = target_date.weekday()
    mapping = {0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"}
    return mapping[weekday]

def get_students_by_group(group):
    return [s for s in students if s["group"] == group]

def is_admin(user_id):
    return user_id in ADMIN_IDS

def remember_user(message):
    u = message.from_user
    uid = str(u.id)
    if uid not in users:
        users[uid] = {
            "id": u.id,
            "username": u.username or "",
            "first_name": u.first_name or "",
            "role": "student",  # по умолчанию студент
            "group": None,
            "full_name": None,
            "registered": False
        }
        save_users()

# ================== КОМАНДЫ ДЛЯ ВСЕХ ==================
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    remember_user(message)
    uid = str(message.from_user.id)
    user = users[uid]
    
    if user.get("registered"):
        # Пользователь уже зарегистрирован
        text = (
            f"Привіт, {user.get('full_name', '')}!\n"
            f"Твоя група: {user.get('group', 'не вказана')}\n\n"
            "Команди:\n"
            "/my_stats – моя статистика відвідування\n"
            "/mygroup – показати мою групу\n"
        )
        if is_admin(message.from_user.id):
            text += "\n👑 Адмін-команди:\n/adminhelp"
        bot.reply_to(message, text)
    else:
        # Предлагаем зарегистрироваться: ввести ФИО и выбрать группу
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("БЦІГ-25", callback_data="reg_group_БЦІГ-25"),
            InlineKeyboardButton("БЦІСТ-25 (включая ТЕ-25)", callback_data="reg_group_БЦІСТ-25")
        )
        bot.reply_to(
            message,
            "Привіт! Я бот для обліку відвідування занять 📚\n\n"
            "Спочатку зареєструйся: обери свою групу:",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: 
    call.data.startswith("mark_group_") or 
    call.data.startswith("mark_date_") or 
    call.data == "mark_cancel" or 
    call.data == "mark_date_manual")
def mark_callback(call):
    # ... остальной код без изменений
    
    # Теперь запрашиваем ФИО
    bot.edit_message_text(
        f"Групу вибрано: {group}\n\nТепер введи своє прізвище та ім'я повністю (наприклад, Петренко Іван).",
        call.message.chat.id,
        call.message.message_id
    )
    # Устанавливаем состояние ожидания ввода ФИО
    users[uid]["awaiting_name"] = True
    save_users()

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("awaiting_name"))
def process_full_name(message):
    uid = str(message.from_user.id)
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        bot.reply_to(message, "Будь ласка, введи ім'я та прізвище (наприклад, Петренко Іван)")
        return
    
    users[uid]["full_name"] = full_name
    users[uid]["registered"] = True
    users[uid]["awaiting_name"] = False
    # Добавляем в список студентов, если ещё нет
    # Проверяем, нет ли уже студента с таким tg_id
    existing = next((s for s in students if s.get("tg_id") == message.from_user.id), None)
    if not existing:
        students.append({
            "tg_id": message.from_user.id,
            "full_name": full_name,
            "group": users[uid]["group"],
            "username": users[uid].get("username", ""),
        })
        save_students()
    
    save_users()
    
    bot.reply_to(message, f"✅ Реєстрація завершена! Ти {full_name}, група {users[uid]['group']}.\nТепер ти можеш дивитися свою статистику через /my_stats.")

@bot.message_handler(commands=["mygroup"])
def mygroup_cmd(message):
    remember_user(message)
    uid = str(message.from_user.id)
    if users[uid].get("group"):
        bot.reply_to(message, f"📚 Твоя група: {users[uid]['group']}")
    else:
        bot.reply_to(message, "Ти ще не вибрав групу. Виконай /start для реєстрації.")

@bot.message_handler(commands=["my_stats"])
def my_stats_cmd(message):
    remember_user(message)
    uid = str(message.from_user.id)
    user = users.get(uid, {})
    if not user.get("registered"):
        bot.reply_to(message, "Спочатку зареєструйся через /start.")
        return
    
    # Получаем статистику для этого пользователя
    student_attendance = [a for a in attendance if a.get("student_id") == message.from_user.id]
    
    # Подсчёт за неделю, месяц, полугодие
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    half_year_ago = today - timedelta(days=182)
    
    def count_for_period(start_date):
        total = 0
        present = 0
        for rec in student_attendance:
            rec_date = datetime.strptime(rec["date"], "%Y-%m-%d").date()
            if rec_date >= start_date:
                total += 1
                if rec.get("status") == "present":
                    present += 1
        return total, present
    
    week_total, week_present = count_for_period(week_ago)
    month_total, month_present = count_for_period(month_ago)
    half_total, half_present = count_for_period(half_year_ago)
    
    response = (
        f"📊 Статистика відвідування для {user.get('full_name', '')}\n\n"
        f"За останній тиждень:\n"
        f"   Всього пар: {week_total}, був: {week_present}, пропустив: {week_total - week_present}\n\n"
        f"За останній місяць:\n"
        f"   Всього пар: {month_total}, був: {month_present}, пропустив: {month_total - month_present}\n\n"
        f"За останнє півріччя:\n"
        f"   Всього пар: {half_total}, був: {half_present}, пропустив: {half_total - half_present}\n"
    )
    
    bot.reply_to(message, response)

# ================== АДМИН-КОМАНДЫ ==================
@bot.message_handler(commands=["adminhelp"])
def admin_help(message):
    if not is_admin(message.from_user.id):
        return
    text = (
        "👑 Адмін-команди для обліку відвідування:\n\n"
        "/mark – відмітити присутніх на парі (починає процес)\n"
        "/add_deputy <id> – додати заступника (по id Telegram)\n"
        "/remove_deputy <id> – видалити заступника\n"
        "/list_deputies – список заступників\n"
        "/add_student – додати студента вручну (після команди введеш ФІО та групу)\n"
        "/list_students <група> – список студентів групи\n"
        "/export <група> <дата> – вивантажити журнал за день у Excel\n"
        "/substitution – створити заміну пари на сьогодні (або на дату)\n"
        "/view_substitutions – переглянути активні заміни\n\n"
        "Примітка: для відмітки використовуй /mark, далі вибери групу, дату, пару, і потім відмічай студентів."
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=["add_deputy"])
def add_deputy(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Формат: /add_deputy <id користувача>")
        return
    try:
        deputy_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "ID має бути числом")
        return
    ADMIN_IDS.add(deputy_id)
    bot.reply_to(message, f"✅ Користувач {deputy_id} доданий як заступник.")

@bot.message_handler(commands=["remove_deputy"])
def remove_deputy(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Формат: /remove_deputy <id>")
        return
    try:
        deputy_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "ID має бути числом")
        return
    if deputy_id in ADMIN_IDS and deputy_id != MAIN_ADMIN_ID:
        ADMIN_IDS.remove(deputy_id)
        bot.reply_to(message, f"✅ Заступник {deputy_id} видалений.")
    else:
        bot.reply_to(message, "Не можна видалити головного адміна або неіснуючого заступника.")

@bot.message_handler(commands=["list_deputies"])
def list_deputies(message):
    if not is_admin(message.from_user.id):
        return
    deputies = list(ADMIN_IDS - {MAIN_ADMIN_ID})
    if not deputies:
        bot.reply_to(message, "Заступників поки немає.")
    else:
        text = "👥 Список заступників (ID):\n" + "\n".join(str(d) for d in deputies)
        bot.reply_to(message, text)

@bot.message_handler(commands=["add_student"])
def add_student_cmd(message):
    if not is_admin(message.from_user.id):
        return
    # Ожидаем ввод: ФИО и группа через запятую или пробел
    bot.reply_to(message, "Введіть дані студента у форматі:\nПрізвище Ім'я, Група\nНаприклад: Петренко Іван, БЦІГ-25")
    # Устанавливаем состояние для админа
    users[str(message.from_user.id)]["awaiting_student"] = True
    save_users()

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("awaiting_student"))
def process_add_student(message):
    uid = str(message.from_user.id)
    text = message.text.strip()
    parts = text.split(',', 1)
    if len(parts) != 2:
        bot.reply_to(message, "Неправильний формат. Використовуйте: Прізвище Ім'я, Група")
        return
    full_name = parts[0].strip()
    group = parts[1].strip()
    if group not in ["БЦІГ-25", "БЦІСТ-25"]:
        bot.reply_to(message, "Група має бути БЦІГ-25 або БЦІСТ-25")
        return
    
    # Добавляем студента без tg_id (пока не зарегистрирован)
    students.append({
        "tg_id": None,
        "full_name": full_name,
        "group": group,
        "username": "",
    })
    save_students()
    users[uid]["awaiting_student"] = False
    save_users()
    bot.reply_to(message, f"✅ Студента {full_name} додано до групи {group}.")

@bot.message_handler(commands=["list_students"])
def list_students_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.reply_to(message, "Формат: /list_students <група>")
        return
    group = parts[1].strip()
    group_students = get_students_by_group(group)
    if not group_students:
        bot.reply_to(message, f"У групі {group} немає студентів.")
        return
    text = f"📋 Студенти групи {group}:\n"
    for s in group_students:
        status = " (зареєстрований)" if s.get("tg_id") else " (не зареєстрований)"
        text += f"• {s['full_name']}{status}\n"
    bot.reply_to(message, text)

# ================== ОТМЕТКА ПОСЕЩАЕМОСТИ ==================
# Храним состояние процесса отметки для каждого админа
mark_states = {}

class MarkState:
    def __init__(self):
        self.step = 0          # 0: выбор группы, 1: выбор даты, 2: выбор пары, 3: отметка
        self.group = None
        self.date = None       # объект date
        self.pair_num = None   # номер пары (строкой)
        self.subject = None    # предмет (для отображения)
        self.students = []     # список студентов для отметки
        self.attendance = {}   # словарь {student_id: status} (present/absent)

@bot.message_handler(commands=["mark"])
def mark_start(message):
    if not is_admin(message.from_user.id):
        return
    mark_states[message.from_user.id] = MarkState()
    # Шаг 1: выбор группы
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("БЦІГ-25", callback_data="mark_group_БЦІГ-25"),
        InlineKeyboardButton("БЦІСТ-25", callback_data="mark_group_БЦІСТ-25"),
        InlineKeyboardButton("❌ Скасувати", callback_data="mark_cancel")
    )
    bot.reply_to(message, "Оберіть групу для відмітки:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mark_"))
def mark_callback(call):
    admin_id = call.from_user.id
    state = mark_states.get(admin_id)
    if not state:
        bot.answer_callback_query(call.id, "Спочатку почніть /mark")
        return
    
    if call.data == "mark_cancel":
        del mark_states[admin_id]
        bot.edit_message_text("❌ Відміну скасовано.", call.message.chat.id, call.message.message_id)
        return
    
    if call.data.startswith("mark_group_"):
        state.group = call.data.split("_")[2]
        state.step = 1
        # Шаг 2: выбор даты
        markup = InlineKeyboardMarkup(row_width=3)
        today = date.today()
        # Предлагаем сегодня, вчера, завтра и ручной ввод
        buttons = [
            InlineKeyboardButton("Сьогодні", callback_data=f"mark_date_{today.isoformat()}"),
            InlineKeyboardButton("Вчора", callback_data=f"mark_date_{(today - timedelta(days=1)).isoformat()}"),
            InlineKeyboardButton("Завтра", callback_data=f"mark_date_{(today + timedelta(days=1)).isoformat()}"),
        ]
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("🔢 Інша дата (введи вручну)", callback_data="mark_date_manual"))
        markup.add(InlineKeyboardButton("❌ Скасувати", callback_data="mark_cancel"))
        bot.edit_message_text(
            f"Група: {state.group}\nТепер оберіть дату:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif call.data.startswith("mark_date_"):
        if call.data == "mark_date_manual":
            # Переходим к ручному вводу даты
            bot.edit_message_text(
                "Введіть дату у форматі РРРР-ММ-ДД (наприклад 2025-03-20):",
                call.message.chat.id,
                call.message.message_id
            )
            state.step = 2  # ожидаем ввод даты
            return
        else:
            date_str = call.data.split("_")[2]
            state.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            state.step = 2
            # Переходим к выбору пары
            choose_pair(call.message.chat.id, admin_id, call.message.message_id)
    
    # Обработка ручного ввода даты будет в отдельном хендлере

def choose_pair(chat_id, admin_id, message_id=None):
    state = mark_states[admin_id]
    # Получаем список пар на этот день с учётом замен
    day_key = get_day_key(state.date)
    week_type = get_week_type(state.date)
    group_schedule = schedule[state.group].get(day_key, {}).get(week_type, {})
    
    # Применяем замены, если есть
    date_str = state.date.isoformat()
    if date_str in substitutions and state.group in substitutions[date_str]:
        for pair_num, sub in substitutions[date_str][state.group].items():
            group_schedule[pair_num] = sub  # заменяем информацию о паре
    
    pairs = []
    for p in sorted(group_schedule.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        if p == "org":
            pairs.append(("org", "Організаційна година"))
        else:
            subject = group_schedule[p].get("subject", "Невідомо")
            pairs.append((p, f"{p} пара — {subject}"))
    
    if not pairs:
        bot.send_message(chat_id, "На цей день немає пар.")
        del mark_states[admin_id]
        return
    
    markup = InlineKeyboardMarkup(row_width=1)
    for p_val, p_text in pairs:
        markup.add(InlineKeyboardButton(p_text, callback_data=f"mark_pair_{p_val}"))
    markup.add(InlineKeyboardButton("❌ Скасувати", callback_data="mark_cancel"))
    
    if message_id:
        bot.edit_message_text(
            f"Група: {state.group}\nДата: {state.date.strftime('%d.%m.%Y')}\nОберіть пару:",
            chat_id,
            message_id,
            reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id,
            f"Група: {state.group}\nДата: {state.date.strftime('%d.%m.%Y')}\nОберіть пару:",
            reply_markup=markup
        )
    state.step = 3

@bot.callback_query_handler(func=lambda call: call.data.startswith("mark_pair_"))
def mark_pair_callback(call):
    admin_id = call.from_user.id
    state = mark_states.get(admin_id)
    if not state:
        return
    
    pair_num = call.data.split("_")[2]
    state.pair_num = pair_num
    # Получаем предмет (для информации)
    day_key = get_day_key(state.date)
    week_type = get_week_type(state.date)
    group_schedule = schedule[state.group].get(day_key, {}).get(week_type, {})
    date_str = state.date.isoformat()
    if date_str in substitutions and state.group in substitutions[date_str] and pair_num in substitutions[date_str][state.group]:
        subj = substitutions[date_str][state.group][pair_num].get("subject", "Невідомо")
    else:
        subj = group_schedule.get(pair_num, {}).get("subject", "Невідомо")
    state.subject = subj
    
    # Получаем список студентов группы
    group_students = get_students_by_group(state.group)
    if not group_students:
        bot.edit_message_text("У цій групі немає студентів. Спочатку додайте через /add_student.", call.message.chat.id, call.message.message_id)
        del mark_states[admin_id]
        return
    
    state.students = group_students
    # Инициализируем всех как absent (потом будем отмечать присутствующих)
    for s in group_students:
        state.attendance[s["full_name"]] = "absent"
    
    state.step = 4
    # Показываем первого студента для отметки
    show_next_student(call.message.chat.id, admin_id, call.message.message_id)

def show_next_student(chat_id, admin_id, message_id=None):
    state = mark_states[admin_id]
    # Находим первого неотмеченного
    for student in state.students:
        if student["full_name"] not in state.attendance:
            # такого не должно быть, но на всякий случай
            state.attendance[student["full_name"]] = "absent"
    
    # Список студентов, которые ещё не имеют статуса (хотя у всех уже есть статус)
    # Мы будем показывать по одному, предлагая отметить присутствующим/отсутствующим
    # Для удобства сделаем список ещё не рассмотренных: это те, у кого статус "absent" (изначально все)
    # Но чтобы можно было изменить, будем просто проходиться по списку и ждать действий.
    # Упростим: будем последовательно показывать каждого студента с кнопками "Присутній", "Відсутній", "Завершити"
    
    # Найдём первого студента, по которому ещё не было действия? Но у всех уже есть статус по умолчанию.
    # Лучше будем проходиться по списку и давать возможность изменить статус.
    # Сделаем переменную current_index
    if not hasattr(state, "current_index"):
        state.current_index = 0
    
    if state.current_index >= len(state.students):
        # Все обработаны, завершаем
        finish_marking(chat_id, admin_id, message_id)
        return
    
    student = state.students[state.current_index]
    full_name = student["full_name"]
    current_status = state.attendance.get(full_name, "absent")
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Присутній", callback_data=f"mark_student_present"),
        InlineKeyboardButton("❌ Відсутній", callback_data=f"mark_student_absent")
    )
    markup.add(
        InlineKeyboardButton("⏩ Завершити", callback_data=f"mark_student_finish")
    )
    
    text = f"📌 {full_name}\nПоточний статус: {'Присутній' if current_status == 'present' else 'Відсутній'}\n\nОберіть статус:"
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mark_student_"))
def mark_student_callback(call):
    admin_id = call.from_user.id
    state = mark_states.get(admin_id)
    if not state:
        return
    
    action = call.data.split("_")[2]
    student = state.students[state.current_index]
    
    if action == "present":
        state.attendance[student["full_name"]] = "present"
        state.current_index += 1
    elif action == "absent":
        state.attendance[student["full_name"]] = "absent"
        state.current_index += 1
    elif action == "finish":
        # Завершаем отметку досрочно
        finish_marking(call.message.chat.id, admin_id, call.message.message_id)
        return
    
    # Переходим к следующему студенту
    if state.current_index < len(state.students):
        show_next_student(call.message.chat.id, admin_id, call.message.message_id)
    else:
        finish_marking(call.message.chat.id, admin_id, call.message.message_id)

def finish_marking(chat_id, admin_id, message_id=None):
    state = mark_states[admin_id]
    # Сохраняем запись в attendance
    date_str = state.date.isoformat()
    # Для каждого студента создаём запись
    for student in state.students:
        status = state.attendance.get(student["full_name"], "absent")
        # Проверяем, есть ли уже запись за этот день на эту пару для этого студента
        # Если есть - обновляем, иначе добавляем
        existing = None
        for idx, rec in enumerate(attendance):
            if (rec.get("date") == date_str and
                rec.get("pair_num") == state.pair_num and
                rec.get("group") == state.group and
                rec.get("student_id") == student.get("tg_id")):
                existing = idx
                break
        if existing is not None:
            attendance[existing]["status"] = status
        else:
            attendance.append({
                "date": date_str,
                "pair_num": state.pair_num,
                "group": state.group,
                "subject": state.subject,
                "student_id": student.get("tg_id"),
                "student_name": student["full_name"],
                "status": status
            })
    save_attendance()
    
    # Подводим итог
    total = len(state.students)
    present = sum(1 for v in state.attendance.values() if v == "present")
    absent = total - present
    
    summary = (
        f"✅ Відмітка завершена!\n"
        f"Група: {state.group}\n"
        f"Дата: {state.date.strftime('%d.%m.%Y')}\n"
        f"Пара: {state.pair_num} ({state.subject})\n\n"
        f"Присутні: {present}\n"
        f"Відсутні: {absent}"
    )
    
    if message_id:
        bot.edit_message_text(summary, chat_id, message_id)
    else:
        bot.send_message(chat_id, summary)
    
    # Предлагаем выгрузить в Excel
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Вивантажити в Excel", callback_data=f"export_{date_str}_{state.group}_{state.pair_num}"))
    bot.send_message(chat_id, "Бажаєте вивантажити журнал?", reply_markup=markup)
    
    del mark_states[admin_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("export_"))
def export_callback(call):
    if not is_admin(call.from_user.id):
        return
    parts = call.data.split("_")
    date_str = parts[1]
    group = parts[2]
    pair_num = parts[3]
    
    # Формируем Excel файл
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Відвідування"
    
    # Заголовки
    ws['A1'] = "Дата"
    ws['B1'] = "Група"
    ws['C1'] = "Пара"
    ws['D1'] = "Предмет"
    ws['E1'] = "Студент"
    ws['F1'] = "Статус"
    
    # Данные
    row = 2
    for rec in attendance:
        if rec.get("date") == date_str and rec.get("group") == group and rec.get("pair_num") == pair_num:
            ws[f'A{row}'] = rec["date"]
            ws[f'B{row}'] = rec["group"]
            ws[f'C{row}'] = rec["pair_num"]
            ws[f'D{row}'] = rec.get("subject", "")
            ws[f'E{row}'] = rec["student_name"]
            ws[f'F{row}'] = "Присутній" if rec["status"] == "present" else "Відсутній"
            row += 1
    
    # Сохраняем в BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    bot.send_document(call.message.chat.id, output, visible_file_name=f"attendance_{date_str}_{group}_pair{pair_num}.xlsx")
    bot.answer_callback_query(call.id, "Файл надіслано")

# ================== ЗАМЕНЫ ПАР ==================
@bot.message_handler(commands=["substitution"])
def substitution_cmd(message):
    if not is_admin(message.from_user.id):
        return
    # Запускаем процесс создания замены
    users[str(message.from_user.id)]["subst_state"] = "awaiting_date"
    bot.reply_to(message, "Введіть дату заміни у форматі РРРР-ММ-ДД (наприклад, 2025-03-20) або 'сьогодні'/'завтра':")
    # Будем хранить временные данные в users

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("subst_state") == "awaiting_date")
def subst_date(message):
    uid = str(message.from_user.id)
    text = message.text.strip().lower()
    if text in ["сьогодні", "сегодня"]:
        subst_date = date.today()
    elif text in ["завтра", "tomorrow"]:
        subst_date = date.today() + timedelta(days=1)
    else:
        try:
            subst_date = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            bot.reply_to(message, "Неправильний формат дати. Спробуйте ще раз або введіть 'сьогодні'/'завтра'.")
            return
    users[uid]["subst_date"] = subst_date.isoformat()
    users[uid]["subst_state"] = "awaiting_group"
    bot.reply_to(message, f"Дата: {subst_date.strftime('%d.%m.%Y')}\nТепер оберіть групу:", reply_markup=group_keyboard())

def group_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("БЦІГ-25", callback_data="subst_group_БЦІГ-25"),
        InlineKeyboardButton("БЦІСТ-25", callback_data="subst_group_БЦІСТ-25"),
        InlineKeyboardButton("❌ Скасувати", callback_data="subst_cancel")
    )
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("subst_"))
def subst_callback(call):
    admin_id = call.from_user.id
    uid = str(admin_id)
    if call.data == "subst_cancel":
        users[uid].pop("subst_state", None)
        users[uid].pop("subst_date", None)
        bot.edit_message_text("❌ Заміну скасовано.", call.message.chat.id, call.message.message_id)
        return
    
    if call.data.startswith("subst_group_"):
        group = call.data.split("_")[2]
        users[uid]["subst_group"] = group
        users[uid]["subst_state"] = "awaiting_pair"
        # Запрашиваем номер пары
        bot.edit_message_text(
            f"Група: {group}\nВведіть номер пари (1-5 або 'org' для організаційної години):",
            call.message.chat.id,
            call.message.message_id
        )

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("subst_state") == "awaiting_pair")
def subst_pair(message):
    uid = str(message.from_user.id)
    pair_input = message.text.strip().lower()
    if pair_input == "org":
        pair_num = "org"
    else:
        try:
            pair_num = str(int(pair_input))
            if int(pair_num) < 1 or int(pair_num) > 5:
                raise ValueError
        except ValueError:
            bot.reply_to(message, "Номер пари має бути від 1 до 5 або 'org'")
            return
    users[uid]["subst_pair"] = pair_num
    users[uid]["subst_state"] = "awaiting_subject"
    bot.reply_to(message, "Введіть новий предмет (або пропустіть, якщо не змінюється):")

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("subst_state") == "awaiting_subject")
def subst_subject(message):
    uid = str(message.from_user.id)
    subject = message.text.strip()
    users[uid]["subst_subject"] = subject if subject else None
    users[uid]["subst_state"] = "awaiting_room"
    bot.reply_to(message, "Введіть нову аудиторію (або пропустіть):")

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("subst_state") == "awaiting_room")
def subst_room(message):
    uid = str(message.from_user.id)
    room = message.text.strip()
    users[uid]["subst_room"] = room if room else None
    users[uid]["subst_state"] = "awaiting_teacher"
    bot.reply_to(message, "Введіть нового викладача (або пропустіть):")

@bot.message_handler(func=lambda msg: users.get(str(msg.from_user.id), {}).get("subst_state") == "awaiting_teacher")
def subst_teacher(message):
    uid = str(message.from_user.id)
    teacher = message.text.strip()
    users[uid]["subst_teacher"] = teacher if teacher else None
    
    # Сохраняем замену
    date_str = users[uid]["subst_date"]
    group = users[uid]["subst_group"]
    pair_num = users[uid]["subst_pair"]
    
    if date_str not in substitutions:
        substitutions[date_str] = {}
    if group not in substitutions[date_str]:
        substitutions[date_str][group] = {}
    
    # Берём исходные данные из расписания, чтобы не потерять, если какие-то поля не указаны
    day_key = get_day_key(datetime.strptime(date_str, "%Y-%m-%d").date())
    week_type = get_week_type(datetime.strptime(date_str, "%Y-%m-%d").date())
    original = schedule.get(group, {}).get(day_key, {}).get(week_type, {}).get(pair_num, {})
    
    sub_entry = {
        "subject": users[uid]["subst_subject"] if users[uid]["subst_subject"] else original.get("subject", ""),
        "room": users[uid]["subst_room"] if users[uid]["subst_room"] else original.get("room", ""),
        "teacher": users[uid]["subst_teacher"] if users[uid]["subst_teacher"] else original.get("teacher", "")
    }
    substitutions[date_str][group][pair_num] = sub_entry
    save_substitutions()
    
    bot.reply_to(message, f"✅ Заміну для {date_str}, група {group}, пара {pair_num} збережено.")
    
    # Очищаем состояние
    del users[uid]["subst_state"]
    for k in ["subst_date", "subst_group", "subst_pair", "subst_subject", "subst_room", "subst_teacher"]:
        users[uid].pop(k, None)

@bot.message_handler(commands=["view_substitutions"])
def view_substitutions(message):
    if not is_admin(message.from_user.id):
        return
    if not substitutions:
        bot.reply_to(message, "Немає активних замін.")
        return
    text = "📅 Активні заміни:\n"
    for date_str, groups in substitutions.items():
        text += f"\n{date_str}:\n"
        for group, pairs in groups.items():
            for pair_num, sub in pairs.items():
                text += f"  {group}, пара {pair_num}: {sub.get('subject')} ({sub.get('room')}) – {sub.get('teacher')}\n"
    bot.reply_to(message, text)

# ================== ВЫГРУЗКА ЗА ДЕНЬ ==================
@bot.message_handler(commands=["export"])
def export_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Формат: /export <група> <дата РРРР-ММ-ДД>")
        return
    group = parts[1]
    date_str = parts[2]
    try:
        export_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        bot.reply_to(message, "Неправильний формат дати. Використовуйте РРРР-ММ-ДД")
        return
    
    # Собираем все записи за этот день для этой группы
    day_records = [r for r in attendance if r.get("date") == date_str and r.get("group") == group]
    if not day_records:
        bot.reply_to(message, "За цей день немає записів про відвідування.")
        return
    
    # Группируем по парам
    pairs = set((r["pair_num"], r.get("subject", "")) for r in day_records)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Відвідування {date_str}"
    
    # Заголовки: Студент | потом по парам
    students_list = sorted(set(r["student_name"] for r in day_records))
    # Сортируем пары по номеру
    sorted_pairs = sorted(pairs, key=lambda x: int(x[0]) if x[0] != "org" else 0)
    
    # Строка заголовков
    ws.cell(row=1, column=1, value="Студент")
    for col, (pair_num, subject) in enumerate(sorted_pairs, start=2):
        ws.cell(row=1, column=col, value=f"{pair_num} ({subject})")
    
    # Данные по студентам
    for row, student_name in enumerate(students_list, start=2):
        ws.cell(row=row, column=1, value=student_name)
        for col, (pair_num, subject) in enumerate(sorted_pairs, start=2):
            # Находим статус
            status = next((r["status"] for r in day_records if r["student_name"] == student_name and r["pair_num"] == pair_num), None)
            ws.cell(row=row, column=col, value="Присутній" if status == "present" else ("Відсутній" if status == "absent" else ""))
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    bot.send_document(message.chat.id, output, visible_file_name=f"attendance_{group}_{date_str}.xlsx")

# ================== ЗАПУСК БОТА ==================
if __name__ == "__main__":
    print("Attendance bot started")
    bot.infinity_polling()
