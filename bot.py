import datetime
import os
import schedule
import telebot
import threading
import time

# ==============================
# إعدادات البوت
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 495109765

BASE_START_DATE = datetime.date(2026, 9, 22)
CYCLE_DAYS = 5

USERS_FILE = "users.txt"

COPYRIGHT = "\n\n_© By Tariq Nabeel_"

# ==============================
# تشغيل البوت
# ==============================

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في Environment Variables")

bot = telebot.TeleBot(BOT_TOKEN)


# ==============================
# المستخدمين
# ==============================

def load_users():

    users = {}

    if not os.path.exists(USERS_FILE):
        return users

    try:

        with open(USERS_FILE, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                user_id = parts[0]

                username = parts[1] if len(parts) > 1 else "N/A"

                name = parts[2] if len(parts) > 2 else "N/A"

                users[user_id] = {
                    "username": username,
                    "name": name
                }

    except Exception as e:

        print("Error reading users:", e)

    return users


def save_user(message):

    users = load_users()

    user_id = str(message.chat.id)

    if user_id in users:
        return

    username = message.from_user.username or "N/A"

    full_name = (
        message.from_user.first_name or "N/A"
    )

    try:

        with open(USERS_FILE, "a", encoding="utf-8") as f:

            f.write(
                f"{user_id}|{username}|{full_name}\n"
            )

    except Exception as e:

        print("Error saving user:", e)


def delete_user(user_id):

    users = load_users()

    user_id = str(user_id)

    if user_id not in users:
        return False

    del users[user_id]

    try:

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            for uid, data in users.items():

                f.write(
                    f"{uid}|"
                    f"{data['username']}|"
                    f"{data['name']}\n"
                )

        return True

    except Exception as e:

        print("Delete error:", e)

        return False


# ==============================
# التحقق من الأدمن
# ==============================

def is_admin(message):

    return message.chat.id == ADMIN_ID


# ==============================
# نظام حصة البنزين
# ==============================

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


def get_gas_status():

    today = datetime.date.today()

    start, end = get_current_batch()

    days_left = (
        end - today
    ).days

    message = (
        "⛽ *حصة البنزين - كركوك*\n\n"

        f"📅 اليوم:\n"
        f"*{today.strftime('%Y-%m-%d')}*\n\n"

        f"🟢 بداية الحصة:\n"
        f"*{start.strftime('%Y-%m-%d')}*\n\n"

        f"🏁 نهاية الحصة:\n"
        f"*{end.strftime('%Y-%m-%d')}*\n\n"
    )

    if today == start:

        message += (
            "🟢 *اليوم تبدأ حصة جديدة!*\n"
            "⛽ يمكنك التفويل."
        )

    elif today == end:

        message += (
            "🔴 *اليوم آخر يوم من الحصة!*"
        )

    else:

        message += (
            f"⏳ متبقي *{days_left} يوم* "
            "لانتهاء الحصة."
        )

    message += COPYRIGHT

    return message


# ==============================
# /start
# ==============================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    save_user(message)

    bot.send_message(
        message.chat.id,
        get_gas_status(),
        parse_mode="Markdown"
    )


# ==============================
# /gas
# ==============================

@bot.message_handler(
    commands=["gas"]
)
def gas_command(message):

    save_user(message)

    bot.send_message(
        message.chat.id,
        get_gas_status(),
        parse_mode="Markdown"
    )


# ==============================
# /next
# ==============================

@bot.message_handler(
    commands=["next"]
)
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

    message_text = (

        "📅 *الحصة القادمة*\n\n"

        f"🟢 البداية:\n"
        f"*{next_start.strftime('%Y-%m-%d')}*\n\n"

        f"🏁 النهاية:\n"
        f"*{next_end.strftime('%Y-%m-%d')}*\n\n"

        f"⏳ متبقي:\n"
        f"*{days_left} يوم*"

        + COPYRIGHT
    )

    bot.send_message(
        message.chat.id,
        message_text,
        parse_mode="Markdown"
    )


# ==============================
# /users
# ==============================

@bot.message_handler(
    commands=["users"]
)
def users_command(message):

    if not is_admin(message):
        return

    users = load_users()

    text = (
        "📊 *إحصائيات المستخدمين*\n\n"
        f"👥 عدد المستخدمين: *{len(users)}*"
        + COPYRIGHT
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )


# ==============================
# /userlist
# ==============================

@bot.message_handler(
    commands=["userlist"]
)
def userlist_command(message):

    if not is_admin(message):
        return

    users = load_users()

    if not users:

        bot.send_message(
            message.chat.id,
            "👥 لا يوجد مستخدمين."
        )

        return

    text = "👥 *قائمة المستخدمين*\n\n"

    number = 1

    for user_id, data in users.items():

        username = data["username"]

        name = data["name"]

        text += (
            f"{number}. "
            f"{name}\n"
            f"🆔 `{user_id}`\n"
            f"👤 @{username}\n\n"
        )

        number += 1

    text += COPYRIGHT

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )


# ==============================
# /delete ID
# ==============================

@bot.message_handler(
    commands=["delete"]
)
def delete_command(message):

    if not is_admin(message):
        return

    parts = message.text.split()

    if len(parts) != 2:

        bot.send_message(
            message.chat.id,
            "❌ الاستخدام الصحيح:\n\n"
            "`/delete USER_ID`",
            parse_mode="Markdown"
        )

        return

    user_id = parts[1]

    if delete_user(user_id):

        bot.send_message(
            message.chat.id,
            f"✅ تم حذف المستخدم:\n`{user_id}`",
            parse_mode="Markdown"
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ المستخدم غير موجود."
        )


# ==============================
# /broadcast رسالة
# ==============================

@bot.message_handler(
    commands=["broadcast"]
)
def broadcast_command(message):

    if not is_admin(message):
        return

    text = message.text[
        len("/broadcast"):
    ].strip()

    if not text:

        bot.send_message(
            message.chat.id,
            "❌ اكتب الرسالة بعد الأمر.\n\n"
            "مثال:\n"
            "`/broadcast مساء الخير للجميع`",
            parse_mode="Markdown"
        )

        return

    users = load_users()

    sent = 0

    failed = 0

    for user_id in users:

        try:

            bot.send_message(
                int(user_id),
                text,
                parse_mode="Markdown"
            )

            sent += 1

            time.sleep(0.05)

        except Exception as e:

            failed += 1

            print(
                f"Broadcast error "
                f"{user_id}: {e}"
            )

    bot.send_message(
        message.chat.id,
        "📢 *تم إرسال الرسالة*\n\n"
        f"✅ تم الإرسال: *{sent}*\n"
        f"❌ فشل: *{failed}*",
        parse_mode="Markdown"
    )


# ==============================
# /stats
# ==============================

@bot.message_handler(
    commands=["stats"]
)
def stats_command(message):

    if not is_admin(message):
        return

    users = load_users()

    today = datetime.date.today()

    start, end = get_current_batch()

    bot.send_message(
        message.chat.id,

        "📊 *إحصائيات البوت*\n\n"

        f"👥 المستخدمين: *{len(users)}*\n\n"

        f"📅 اليوم:\n"
        f"*{today}*\n\n"

        f"🟢 بداية الحصة:\n"
        f"*{start}*\n\n"

        f"🏁 نهاية الحصة:\n"
        f"*{end}*\n\n"

        f"🔄 مدة الدورة: *{CYCLE_DAYS} أيام*"

        + COPYRIGHT,

        parse_mode="Markdown"
    )


# ==============================
# الإشعار اليومي
# ==============================

def send_daily_reminder():

    today = datetime.date.today()

    start, end = get_current_batch()

    # إرسال فقط في أول يوم من الحصة

    if today != start:

        print(
            f"ℹ️ اليوم {today} "
            f"ليس يوم بداية الحصة."
        )

        return

    users = load_users()

    print(
        f"🔔 إرسال إشعار بداية الحصة "
        f"إلى {len(users)} مستخدم..."
    )

    text = (
        "🔔 *تنبيه حصة البنزين*\n\n"

        "🟢 *اليوم تبدأ حصة جديدة!*\n\n"

        "⛽ يمكنك التفويل الآن.\n\n"

        f"📅 من: *{start}*\n"
        f"🏁 إلى: *{end}*"

        + COPYRIGHT
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
                f"❌ Reminder error "
                f"{user_id}: {e}"
            )


# ==============================
# Scheduler
# ==============================

# توقيت العراق = UTC+3

schedule.every().day.at(
    "08:00"
).do(
    send_daily_reminder
)


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


# ==============================
# تشغيل البوت
# ==============================

if __name__ == "__main__":

    print(
        "=============================="
    )

    print(
        "⛽ Gas Bot Started"
    )

    print(
        "=============================="
    )

    print(
        "👤 Admin ID:",
        ADMIN_ID
    )

    print(
        "📅 Base date:",
        BASE_START_DATE
    )

    print(
        "🔄 Cycle:",
        CYCLE_DAYS,
        "days"
    )

    print(
        "=============================="
    )

    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True
    )

    scheduler_thread.start()

    print(
        "✅ Scheduler started"
    )

    print(
        "🔔 Reminder: 08:00"
    )

    print(
        "=============================="
    )

    bot.infinity_polling(
        skip_pending=True
    )
