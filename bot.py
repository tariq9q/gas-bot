import datetime
import os
import schedule
import telebot
import threading
import time
from telebot import types


# ==================================================
# إعدادات البوت
# ==================================================

BOT_TOKEN = "8835971524:AAFx5vV1tUeT1skCFCLtBcf-SjG3TL9dDBc"

# Chat ID الخاص بالمدير
ADMIN_ID = 495109765

# تاريخ بداية أول وجبة
BASE_START_DATE = datetime.date(2026, 9, 22)

# مدة الوجبة بالأيام
CYCLE_DAYS = 5

# ملف حفظ المستخدمين
USERS_FILE = "users.txt"


# ==================================================
# تشغيل البوت
# ==================================================

bot = telebot.TeleBot(BOT_TOKEN)


# ==================================================
# حفظ المستخدم
# ==================================================

def save_user(user_id, username, full_name):

    users = load_users()

    if str(user_id) not in users:

        with open(USERS_FILE, "a", encoding="utf-8") as f:

            f.write(
                f"{user_id}|{username}|{full_name}\n"
            )


# ==================================================
# قراءة المستخدمين
# ==================================================

def load_users():

    users = {}

    if not os.path.exists(USERS_FILE):
        return users

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                user_id = parts[0]

                username = (
                    parts[1]
                    if len(parts) > 1
                    else "N/A"
                )

                name = (
                    parts[2]
                    if len(parts) > 2
                    else "N/A"
                )

                users[user_id] = {
                    "username": username,
                    "name": name
                }

    except Exception as e:

        print("Error reading users:", e)

    return users


# ==================================================
# حساب الوجبة الحالية
# ==================================================

def get_current_batch_info():

    today = datetime.date.today()

    # إذا التاريخ قبل بداية النظام
    if today < BASE_START_DATE:

        start_date = BASE_START_DATE

        end_date = (
            start_date
            + datetime.timedelta(
                days=CYCLE_DAYS - 1
            )
        )

        return start_date, end_date

    # عدد الأيام منذ بداية النظام
    days_passed = (
        today - BASE_START_DATE
    ).days

    # رقم الوجبة
    batch_index = (
        days_passed // CYCLE_DAYS
    )

    # بداية الوجبة
    start_date = (
        BASE_START_DATE
        + datetime.timedelta(
            days=batch_index * CYCLE_DAYS
        )
    )

    # نهاية الوجبة
    end_date = (
        start_date
        + datetime.timedelta(
            days=CYCLE_DAYS - 1
        )
    )

    return start_date, end_date


# ==================================================
# حالة الحصة
# ==================================================

def get_gas_status():

    today = datetime.date.today()

    start_date, end_date = (
        get_current_batch_info()
    )

    days_left = (
        end_date - today
    ).days

    msg = (
        "⛽ *حالة حصة البنزين - كركوك*\n\n"
    )

    msg += (
        f"📅 *التاريخ اليوم:*\n"
        f"{today.strftime('%Y-%m-%d')}\n\n"
    )

    msg += (
        f"🟢 *بداية الوجبة:*\n"
        f"{start_date.strftime('%Y-%m-%d')}\n\n"
    )

    msg += (
        f"🏁 *نهاية الوجبة:*\n"
        f"{end_date.strftime('%Y-%m-%d')}\n\n"
    )

    if today == start_date:

        msg += (
            "🟢 *اليوم تبدأ وجبة جديدة!*\n"
            "يمكنك التفويل ⛽"
        )

    elif today == end_date:

        msg += (
            "🔴 *اليوم هو آخر يوم "
            "في هذه الوجبة!*"
        )

    else:

        msg += (
            f"⏳ *متبقي {days_left} يوم "
            f"لانتهاء الوجبة.*"
        )

    return msg


# ==================================================
# إنشاء لوحة الأزرار
# ==================================================

def create_main_keyboard(user_id):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    # الأزرار الأساسية
    btn_status = types.KeyboardButton(
        "⛽ حالة الحصة"
    )

    btn_next = types.KeyboardButton(
        "📅 موعد الحصة القادمة"
    )

    markup.row(
        btn_status,
        btn_next
    )

    # أزرار المدير
    if user_id == ADMIN_ID:

        btn_users = types.KeyboardButton(
            "📊 عدد المستخدمين"
        )

        btn_help_admin = types.KeyboardButton(
            "⚙️ أوامر المدير"
        )

        markup.row(
            btn_users,
            btn_help_admin
        )

    return markup


# ==================================================
# START
# ==================================================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    user_id = message.chat.id

    username = (
        message.from_user.username
        or "N/A"
    )

    full_name = (
        message.from_user.first_name
        or "N/A"
    )

    # حفظ المستخدم
    save_user(
        user_id,
        username,
        full_name
    )

    # إنشاء الكيبورد
    markup = create_main_keyboard(
        user_id
    )

    bot.send_message(
        message.chat.id,
        "👋 *أهلاً بك*\n\n"
        "⛽ بوت متابعة حصة البنزين\n\n"
        "👇 *اختار الخدمة من الأزرار بالأسفل:*",
        parse_mode="Markdown",
        reply_markup=markup
    )


# ==================================================
# HELP
# ==================================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    markup = create_main_keyboard(
        message.chat.id
    )

    bot.send_message(
        message.chat.id,
        "ℹ️ *الخدمات المتوفرة:*\n\n"
        "⛽ حالة الحصة\n"
        "📅 موعد الحصة القادمة",
        parse_mode="Markdown",
        reply_markup=markup
    )


# ==================================================
# حالة الحصة
# ==================================================

@bot.message_handler(
    func=lambda message:
    message.text == "⛽ حالة الحصة"
)
def gas_status_button(message):

    bot.send_message(
        message.chat.id,
        get_gas_status(),
        parse_mode="Markdown"
    )


# ==================================================
# موعد الحصة القادمة
# ==================================================

@bot.message_handler(
    func=lambda message:
    message.text == "📅 موعد الحصة القادمة"
)
def next_batch_button(message):

    today = datetime.date.today()

    current_start, current_end = (
        get_current_batch_info()
    )

    next_start = (
        current_end
        + datetime.timedelta(days=1)
    )

    next_end = (
        next_start
        + datetime.timedelta(
            days=CYCLE_DAYS - 1
        )
    )

    days_left = (
        next_start - today
    ).days

    msg = (
        "📅 *موعد الحصة القادمة*\n\n"
        f"🟢 بداية الحصة:\n"
        f"*{next_start.strftime('%Y-%m-%d')}*\n\n"
        f"🏁 نهاية الحصة:\n"
        f"*{next_end.strftime('%Y-%m-%d')}*\n\n"
        f"⏳ متبقي:\n"
        f"*{days_left} يوم*"
    )

    bot.send_message(
        message.chat.id,
        msg,
        parse_mode="Markdown"
    )


# ==================================================
# عدد المستخدمين
# ==================================================

@bot.message_handler(
    func=lambda message:
    message.text == "📊 عدد المستخدمين"
)
def users_count_button(message):

    if message.chat.id != ADMIN_ID:
        return

    users = load_users()

    count = len(users)

    bot.send_message(
        message.chat.id,
        "📊 *إحصائيات البوت*\n\n"
        f"👥 عدد المستخدمين:\n"
        f"*{count}*",
        parse_mode="Markdown"
    )


# ==================================================
# أوامر المدير
# ==================================================

@bot.message_handler(
    func=lambda message:
    message.text == "⚙️ أوامر المدير"
)
def admin_commands(message):

    if message.chat.id != ADMIN_ID:
        return

    msg = (
        "⚙️ *أوامر المدير*\n\n"
        "📊 `/stats`\n"
        "عرض عدد المستخدمين.\n\n"
        "📢 `/broadcast نص الرسالة`\n"
        "إرسال رسالة لجميع المستخدمين.\n\n"
        "🔄 `/start`\n"
        "إظهار لوحة الخدمات."
    )

    bot.send_message(
        message.chat.id,
        msg,
        parse_mode="Markdown"
    )


# ==================================================
# STATS
# ==================================================

@bot.message_handler(
    commands=["stats"]
)
def show_stats(message):

    if message.chat.id != ADMIN_ID:
        return

    users = load_users()

    bot.send_message(
        message.chat.id,
        f"📊 عدد المستخدمين: *{len(users)}*",
        parse_mode="Markdown"
    )


# ==================================================
# BROADCAST
# ==================================================

@bot.message_handler(
    commands=["broadcast"]
)
def broadcast(message):

    if message.chat.id != ADMIN_ID:
        return

    text = message.text.replace(
        "/broadcast",
        "",
        1
    ).strip()

    if not text:

        bot.reply_to(
            message,
            "❌ اكتب الرسالة بعد الأمر.\n\n"
            "مثال:\n"
            "/broadcast غداً تبدأ حصة جديدة ⛽"
        )

        return

    users = load_users()

    sent = 0
    failed = 0

    for user_id in users:

        try:

            bot.send_message(
                int(user_id),
                text
            )

            sent += 1

            # حتى لا نرسل بسرعة كبيرة
            time.sleep(0.05)

        except Exception as e:

            failed += 1

            print(
                f"Error sending to {user_id}: {e}"
            )

    bot.reply_to(
        message,
        "✅ *تم إرسال الرسالة*\n\n"
        f"👥 إجمالي المستخدمين: {len(users)}\n"
        f"📨 تم الإرسال: {sent}\n"
        f"❌ فشل الإرسال: {failed}",
        parse_mode="Markdown"
    )


# ==================================================
# التذكير اليومي
# ==================================================

def send_daily_reminder():

    print("Sending daily reminder...")

    users = load_users()

    status_msg = (
        "🌅 *التذكير الصباحي*\n\n"
        + get_gas_status()
    )

    for user_id in users:

        try:

            bot.send_message(
                int(user_id),
                status_msg,
                parse_mode="Markdown"
            )

            time.sleep(0.05)

        except Exception as e:

            print(
                f"Error sending to {user_id}: {e}"
            )


# ==================================================
# جدولة التذكير الساعة 08:00
# ==================================================

schedule.every().day.at(
    "08:00"
).do(
    send_daily_reminder
)


# ==================================================
# تشغيل Scheduler
# ==================================================

def run_scheduler():

    while True:

        try:

            schedule.run_pending()

        except Exception as e:

            print(
                "Scheduler error:",
                e
            )

        time.sleep(1)


# ==================================================
# تشغيل البوت
# ==================================================

if __name__ == "__main__":

    print("==============================")
    print("⛽ Gas Bot")
    print("==============================")
    print("Bot is starting...")
    print("Admin ID:", ADMIN_ID)
    print("Start date:", BASE_START_DATE)
    print("Cycle days:", CYCLE_DAYS)
    print("==============================")

    # تشغيل الجدولة بخيط منفصل
    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True
    )

    scheduler_thread.start()

    print("✅ Scheduler started")
    print("✅ Bot is running")

    # تشغيل Telegram
    bot.infinity_polling(
        skip_pending=True
    )
