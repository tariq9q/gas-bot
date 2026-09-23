import datetime
import telebot

BOT_TOKEN = "8835971524:AAFx5vV1tUeT1skCFCLtBcf-SjG3TL9dDBc"
bot = telebot.TeleBot(BOT_TOKEN)

# نقطة بداية محسوبة (أول وجبة معتمدة تبدأ في 2026-09-22 وتنتهي في 2026-09-26)
BASE_START_DATE = datetime.date(2026, 9, 22)
CYCLE_DAYS = 5  # كل وجبة تستغرق 5 أيام


def get_current_batch_info():
  today = datetime.date.today()

  # إذا كان التاريخ قبل أول وجبة
  if today < BASE_START_DATE:
    return BASE_START_DATE, BASE_START_DATE + datetime.timedelta(
        days=CYCLE_DAYS - 1
    )

  # حساب الفرق بالأيام لمعرفة الوجبة الحالية تلقائياً
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
    msg += "🟢 *اليوم تبدأ وجبة جديدة! يمكنك التفويل.*"
  elif days_left == 0:
    msg += "🔴 *اليوم هو آخر يوم في هذه الوجبة!*"
  elif today > end_date:
    # احتياطاً لو حصل أي تأخير بالحساب
    msg += "⏳ *انتهت هذه الوجبة، وتبدأ الوجبة الجديدة فوراً.*"
  else:
    msg += (
        f"⏳ متبقي *{days_left}* أيام لتنتهي هذه الوجبة (تنتهي يوم"
        f" {end_date.strftime('%Y-%m-%d')})."
    )

  return msg


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  status_msg = get_gas_status()
  bot.reply_to(message, status_msg, parse_mode='Markdown')


if __name__ == '__main__':
  bot.infinity_polling()
