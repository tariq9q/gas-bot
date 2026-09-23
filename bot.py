import datetime
import telebot

"BOT_TOKEN = "8835971524:AAFx5vV1tUeT1skCFCLtBcf-SjG3TL9dDBc""
bot = telebot.TeleBot(BOT_TOKEN)

# قائمة الوجبات المحدثة (تاريخ البداية وتاريخ النهاية)
PERIODS_2026 = [
    (datetime.date(2026, 9, 22), datetime.date(2026, 9, 26)),
    # يمكنك إضافة وجبات أخرى هنا لاحقاً بنفس الصيغة
]


def get_gas_status():
  today = datetime.date.today()
  current_period = None

  for start_date, end_date in PERIODS_2026:
    if start_date <= today <= end_date:
      current_period = (start_date, end_date)
      break

  if current_period:
    start_date, end_date = current_period
    days_left = (end_date - today).days

    msg = f"⛽ *تذكير حصة البنزين - كركوك*\n\n"
    msg += f"📅 *التاريخ اليوم:* {today.strftime('%Y-%m-%d')}\n"
    msg += f"🚀 *تاريخ بداية الوجبة:* {start_date.strftime('%Y-%m-%d')}\n"
    msg += f"🏁 *تاريخ نهاية الوجبة:* {end_date.strftime('%Y-%m-%d')}\n\n"

    if today == start_date:
      msg += "🟢 *اليوم تبدأ وجبة جديدة! يمكنك التفويل.*"
    elif days_left == 0:
      msg += "🔴 *اليوم هو آخر يوم في هذه الوجبة!*"
    else:
      msg += f"⏳ متبقي *{days_left}* أيام لتنتهي هذه الوجبة (تنتهي يوم 26)."
  else:
    msg = f"ℹ️ لا توجد وجبة مسجلة لليوم ({today.strftime('%Y-%m-%d')}). الوجبة الحالية تبدأ من 2026-09-22 وتنتهي في 2026-09-26."

  return msg


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  status_msg = get_gas_status()
  bot.reply_to(message, status_msg, parse_mode='Markdown')


if __name__ == '__main__':
  bot.infinity_polling()
