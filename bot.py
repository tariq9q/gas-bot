import datetime
import os
import schedule
import telebot
import threading
import time
from telebot import types


# ==============================
# إعدادات البوت
# ==============================

BOT_TOKEN = "8835971524:AAGdzuuvcBWBlqdHHnoxTigAPdGYUOTa_TI"

# ضع Chat ID مالك هنا
ADMIN_ID = 495109765

bot = telebot.TeleBot(BOT_TOKEN)

BASE_START_DATE = datetime.date(2026, 9, 22)
CYCLE_DAYS = 5
USERS_FILE = "users.txt"


# ==============================
# حفظ المستخدم
# ==============================

def save_user(user_id, username, full_name):
    users = load_users()

    if str(user_id) not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id},{username},{full_name}\n")


# ==============================
# قراءة المستخدمين
# ==============================

def load_users():
    users = {}

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")

                if len(parts) >= 1 and parts[0]:
                    users[parts[0]] = {
                        "username": parts[1] if len(parts) > 1 else "N/A",
                        "name": parts[2] if len(parts) > 2 else "N/A",
                    }

    return users


# ==============================
# حساب الحصة الحالية
# ==============================

def get_current_batch_info():
    today = datetime.date.today()

    if today < BASE_START_DATE:
        return (
            BASE_START_DATE,
            BASE_START_DATE + datetime.timedelta(
                days=CYCLE_DAYS - 1
            )
        )

    days_passed = (today - BASE_START_DATE).days

    batch_index = days_passed // CYCLE_DAYS

    start_date = BASE_START_DATE + datetime.timedelta(
        days=batch_index * CYCLE_DAYS
    )

    end_date = start_date + datetime.timedelta(
        days=CYCLE_DAYS - 1
    )

    return start_date, end_date


# ==============================
# حالة الحصة
# ==============================

def get_gas_status():
    today = datetime.date.today()

    start_date, end_date = get_current_batch_info()

    days_left = (end_date - today).days

    msg = "⛽ *تذكير حصة البنزين - كركوك*\n\n"

    msg += f"📅 *التاريخ اليوم:* {today.strftime('%Y-%m-%d')}\n"

    msg += (
        f"🚀 *تاريخ بداية الوجبة:* "
        f"{start_date.strftime('%Y-%m-%d')}\n"
    )

    msg += (
        f"🏁 *تاريخ نهاية الوجبة:* "
        f"{end_date.strftime('%Y-%m-%d')}\n\n"
    )

    if today == start_date:
        msg += "🟢 *اليوم تبدأ وجبة جديدة! يمكنك التفويل.*\n\n"

    elif days_left == 0:
        msg += "🔴 *اليوم هو آخر يوم في هذه الوجبة!*\n\n"

    else:
        msg += (
            f"⏳ متبقي *{days_left}* أيام "
            f"لتنتهي هذه الوجبة.\n\n"
        )

    msg += "_by tariq nabeil_"

    return msg


# ==============================
# /start
# ==============================

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):

    user_id = str(message.chat.id)

    username = message.from_user.username or "N/A"

    full_name = message.from_user.first_name or "N/A"

    # حفظ المستخدم
    save_user(
        user_id,
        username,
        full_name
    )

    # إنشاء لوحة الأزرار
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn_status = types.KeyboardButton(
        "⛽ حالة الحصة"
    )

    btn_next = types.KeyboardButton(
        "📅 موعد الحصة القادمة"
    )

    markup.add(
        btn_status,
        btn_next
    )

    # زر عدد المستخدمين للمدير فقط
    if message.chat.id == ADMIN_ID:

        btn_users = types.KeyboardButton(
            "📊 عدد المستخدمين"
        )

        markup.add(btn_users)

    bot.send_message(
        message.chat.id,
        "أهلاً بك 👋\n\nاختار الخدمة:",
        reply_markup=markup
    )


# ==============================
# حالة الحصة
# ==============================

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


# ==============================
# موعد الحصة القادمة
# ==============================

@bot.message_handler(
    func=lambda message:
    message.text == "📅 موعد الحصة القادمة"
)
def next_batch_button(message):

    today = datetime.date.today()

    start_date, end_date = get_current_batch_info()

    next_start = end_date + datetime.timedelta(
        days=1
    )

    next_end = next_start + datetime.timedelta(
        days=CYCLE_DAYS - 1
    )

    days_left = (next_start - today).days

    msg = (
        "📅 *موعد الحصة القادمة*\n\n"
        f"🟢 بداية الحصة: "
        f"*{next_start.strftime('%Y-%m-%d')}*\n\n"
        f"🏁 نهاية الحصة: "
        f"*{next_end.strftime('%Y-%m-%d')}*\n\n"
        f"⏳ متبقي: *{days_left} يوم*"
    )

    bot.send_message(
        message.chat.id,
        msg,
        parse_mode="Markdown"
    )


# ==============================
# عدد المستخدمين - المدير فقط
# ==============================

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
        f"👥 *عدد المستخدمين المسجلين: {count}*",
        parse_mode="Markdown"
    )


# ==============================
# إحصائيات المدير
# ==============================

@bot.message_handler(commands=["stats"])
def show_stats(message):

    if message.chat.id != ADMIN_ID:
        return

    users = load_users()

    count = len(users)

    bot.reply_to(
        message,
        f"📊 عدد المستخدمين: {count}"
    )


# ==============================
# إرسال إشعار لجميع المستخدمين
# ==============================

@bot.message_handler(commands=["broadcast"])
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
                user_id,
                text
            )

            sent += 1

        except Exception as e:

            failed += 1

            print(
                f"Error sending to {user_id}: {e}"
            )

    bot.reply_to(
        message,
        f"✅ تم إرسال الرسالة.\n\n"
        f"👥 إجمالي المستخدمين: {len(users)}\n"
        f"📨 تم الإرسال: {sent}\n"
        f"❌ فشل الإرسال: {failed}"
    )


# ==============================
# التذكير اليومي
# ==============================

def send_daily_reminder():

    users = load_users()

    status_msg = (
        "🌅 *التذكير الصباحي للحصة*\n\n"
        + get_gas_status()
    )

    for user_id in users:

        try:

            bot.send_message(
                user_id,
                status_msg,
                parse_mode="Markdown"
            )

        except Exception as e:

            print(
                f"Error sending to {user_id}: {e}"
            )


# ==============================
# التذكير الساعة 08:00
# ==============================

schedule.every().day.at("08:00").do(
    send_daily_reminder
)


# ==============================
# تشغيل الجدولة
# ==============================

def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(1)


# ==============================
# تشغيل البوت
# ==============================

if __name__ == "__main__":

    t = threading.Thread(
        target=run_scheduler
    )

    t.daemon = True

    t.start()

    print("Bot is running...")

    bot.infinity_polling()