import datetime
import os
import schedule
import telebot
import threading
import time


# ==========================================
# إعدادات البوت
# ==========================================

BOT_TOKEN = "8835971524:AAFx5vV1tUeT1skCFCLtBcf-SjG3TL9dDBc"

# Chat ID الخاص بك
ADMIN_ID = 495109765

# بداية أول حصة
BASE_START_DATE = datetime.date(2026, 9, 22)

# مدة الحصة
CYCLE_DAYS = 5

# ملف المستخدمين
USERS_FILE = "users.txt"


# ==========================================
# تشغيل البوت
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)


# ==========================================
# قراءة المستخدمين
# ==========================================

def load_users():

    users = {}

    if not os.path.exists(USERS_FILE):
        return users

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

    return users


# ==========================================
# حفظ مستخدم جديد
# ==========================================

def save_user(message):

    users = load_users()

    user_id = str(message.chat.id)

    if user_id in users:
        return

    username = (
        message.from_user.username
        or "N/A"
    )

    full_name = (
        message.from_user.first_name
        or "N/A"
    )

    with open(
        USERS_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{user_id}|{username}|{full_name}\n"
        )


# ==========================================
# حساب الحصة الحالية
# ==========================================

def get_current_batch():

    today = datetime.date.today()

    if today < BASE_START_DATE:

        start = BASE_START_DATE

    else:

        days_passed = (
            today - BASE_START_DATE
        ).days

        batch_number = (
            days_passed // CYCLE_DAYS
        )

        start = (
            BASE_START_DATE
            + datetime.timedelta(
                days=batch_number * CYCLE_DAYS
            )
        )

    end = (
        start
        + datetime.timedelta(
            days=CYCLE_DAYS - 1
        )
    )

    return start, end


# ==========================================
# رسالة الحصة
# ==========================================

def get_gas_status():

    today = datetime.date.today()

    start, end = get_current_batch()

    days_left = (
        end - today
    ).days

    message = (
        "⛽ *حصة البنزين - كركوك*\n\n"
        f"📅 اليوم: *{today.strftime('%Y-%m-%d')}*\n\n"
        f"🟢 بداية الحصة: "
        f"*{start.strftime('%Y-%m-%d')}*\n\n"
        f"🏁 نهاية الحصة: "
        f"*{end.strftime('%Y-%m-%d')}*\n\n"
    )

    if today == start:

        message += (
            "🟢 *اليوم تبدأ حصة جديدة*\n"
            "⛽ يمكنك التفويل"
        )

    elif today == end:

        message += (
            "🔴 *اليوم آخر يوم من الحصة*"
        )

    else:

        message += (
            f"⏳ متبقي *{days_left} يوم*"
        )

    return message


# ==========================================
# /start
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    # حفظ المستخدم
    save_user(message)

    # إرسال الحصة مباشرة
    bot.send_message(
        message.chat.id,
        get_gas_status(),
        parse_mode="Markdown"
    )


# ==========================================
# /gas
# المستخدم يقدر يطلب الحصة بأي وقت
# ==========================================

@bot.message_handler(commands=["gas"])
def gas_command(message):

    save_user(message)

    bot.send_message(
        message.chat.id,
        get_gas_status(),
        parse_mode="Markdown"
    )


# ==========================================
# /users
# المدير فقط
# ==========================================

@bot.message_handler(commands=["users"])
def users_command(message):

    if message.chat.id != ADMIN_ID:
        return

    users = load_users()

    count = len(users)

    bot.send_message(
        message.chat.id,
        f"👥 *عدد المستخدمين المسجلين: {count}*",
        parse_mode="Markdown"
    )


# ==========================================
# /next
# موعد الحصة القادمة
# ==========================================

@bot.message_handler(commands=["next"])
def next_command(message):

    save_user(message)

    today = datetime.date.today()

    current_start, current_end = (
        get_current_batch()
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

    text = (
        "📅 *الحصة القادمة*\n\n"
        f"🟢 البداية: "
        f"*{next_start.strftime('%Y-%m-%d')}*\n\n"
        f"🏁 النهاية: "
        f"*{next_end.strftime('%Y-%m-%d')}*\n\n"
        f"⏳ متبقي: *{days_left} يوم*"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )


# ==========================================
# إرسال التذكير اليومي
# ==========================================

def send_daily_reminder():

    users = load_users()

    text = (
        "🌅 *التذكير اليومي*\n\n"
        + get_gas_status()
    )

    print(
        f"Sending reminder to {len(users)} users..."
    )

    for user_id in users:

        try:

            bot.send_message(
                int(user_id),
                text,
                parse_mode="Markdown"
            )

            time.sleep(0.05)

        except Exception as e:

            print(
                f"Error sending to {user_id}: {e}"
            )


# ==========================================
# التذكير الساعة 08:00
# ==========================================

schedule.every().day.at(
    "08:00"
).do(
    send_daily_reminder
)


# ==========================================
# تشغيل الجدولة
# ==========================================

def scheduler():

    while True:

        try:

            schedule.run_pending()

        except Exception as e:

            print(
                "Scheduler error:",
                e
            )

        time.sleep(1)


# ==========================================
# تشغيل البوت
# ==========================================

if __name__ == "__main__":

    print("==============================")
    print("⛽ Gas Bot Started")
    print("==============================")
    print("Admin ID:", ADMIN_ID)
    print("Start date:", BASE_START_DATE)
    print("Cycle:", CYCLE_DAYS, "days")
    print("==============================")

    thread = threading.Thread(
        target=scheduler,
        daemon=True
    )

    thread.start()

    print("✅ Scheduler started")
    print("✅ Bot is running")

    bot.infinity_polling(
        skip_pending=True
    )
