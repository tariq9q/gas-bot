import datetime
import time
import threading
import telebot
import schedule

BOT_TOKEN = "8835971524:AAFx5vV1tUeT1skCFCLtBcf-SjG3TL9dDBc"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_START_DATE = datetime.date(2026, 9, 22)
CYCLE_DAYS = 5

# حفظ معرفات المستخدمين الذين تفاعلوا مع البوت لكي يرسل لهم التذكير الصباحي
# (ملاحظة: إذا أعد تشغيل السيرفر، ستحتاج لإرسال /start مرة أخرى لتسجيل المستخدمين)
known_users = set()


def get_current_batch_info():
  today = datetime.date.today()
  if today < BASE_START_DATE:
    return BASE_START_DATE, BASE_START_DATE + datetime.timedelta(
        days=CYCLE_DAYS - 1
    )

  days_passed = (today - BASE_START_DATE).days
  batch_index = days_passed // CYCLE_DAYS

  start_date = BASE_START_DATE + datetime.timedelta(
      days=batch_index * CYCLE_DAYS
  )
  end_date = start_date + datetime.timedelta(days=CYCLE_DAYS - 1)
  return start_date, end_date


def get_gas_status():
  today = datetime.date.today()
  start_date, end_date = get_current_batch_info()
  days_left = (end_date - today).days

  msg = f"⛽ *تذكير حصة البنزين - كركوك*\n\n"
  msg += f"📅 *التاريخ اليوم:* {today.strftime('%Y-%m-%d')}\n"
  msg += f"🚀 *تاريخ بداية الوجبة:* {start_date.strftime('%Y-%m-%d')}\n"
  msg += f"🏁 *تاريخ نهاية الوجبة:* {end_date.strftime('%Y-%m-%d')}\n\n"

  if today == start_date:
    msg += "🟢 *اليوم تبدأ وجبة جديدة! يمكنك التفويل.*\n\n"
  elif days_left == 0:
    msg += "🔴 *اليوم هو آخر يوم في هذه الوجبة!*\n\n"
  elif today > end_date:
    msg += "⏳ *انتهت هذه الوجبة، وتبدأ الوجبة الجديدة فوراً.*\n\n"
  else:
    msg += (
        f"⏳ متبقي *{days_left}* أيام لتنتهي هذه الوجبة (تنتهي يوم"
        f" {end_date.strftime('%Y-%m-%d')}).\n\n"
    )

  msg += "_by tariq nabeil_"
  return msg


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  known_users.add(message.chat.id)
  status_msg = get_gas_status()
  bot.reply_to(message, status_msg, parse_mode='Markdown')


# دالة الإرسال التذكيري الصباحي لكل المستخدمين المسجلين
def send_daily_reminder():
  status_msg = f"🌅 *التذكير الصباحي للحصة*\n\n" + get_gas_status()
  for user_id in known_users:
    try:
      bot.send_message(user_id, status_msg, parse_mode='Markdown')
    except Exception as e:
      print(f'Error sending to {user_id}: {e}')


# جدولدها لتعمل كل يوم الساعة 8:00 صباحاً
schedule.every().day.at('08:00').do(send_daily_reminder)


def run_scheduler():
  while True:
    schedule.run_pending()
    time.sleep(1)


if __name__ == '__main__':
  # تشغيل الجدولة في خلفية البوت
  t = threading.Thread(target=run_scheduler)
  t.daemon = True
  t.start()

  # تشغيل البوت باستمرار
  bot.infinity_polling()
