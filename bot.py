
import datetime
import requests
import urllib3

# إخفاء تحذيرات شهادة الأمان
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# بيانات البوت
BOT_TOKEN = "8835971524:AAGdzuuvcBWBlqdlHInoxTigAPdGYUOTa_TI"
CHAT_ID = "495109765"

# جدول حصص البنزين لسنة 2026 في كركوك
PERIODS_2026 = [
    (datetime.date(2026, 1, 1), datetime.date(2026, 1, 2)),
    (datetime.date(2026, 1, 3), datetime.date(2026, 1, 7)),
    (datetime.date(2026, 1, 8), datetime.date(2026, 1, 12)),
    (datetime.date(2026, 1, 13), datetime.date(2026, 1, 17)),
    (datetime.date(2026, 1, 18), datetime.date(2026, 1, 22)),
    (datetime.date(2026, 1, 23), datetime.date(2026, 1, 27)),
    (datetime.date(2026, 1, 28), datetime.date(2026, 1, 31)),
    (datetime.date(2026, 2, 1), datetime.date(2026, 2, 5)),
    (datetime.date(2026, 2, 6), datetime.date(2026, 2, 10)),
    (datetime.date(2026, 2, 11), datetime.date(2026, 2, 15)),
    (datetime.date(2026, 2, 16), datetime.date(2026, 2, 20)),
    (datetime.date(2026, 2, 21), datetime.date(2026, 2, 25)),
    (datetime.date(2026, 2, 26), datetime.date(2026, 2, 28)),
    (datetime.date(2026, 3, 1), datetime.date(2026, 3, 5)),
    (datetime.date(2026, 3, 6), datetime.date(2026, 3, 10)),
    (datetime.date(2026, 3, 11), datetime.date(2026, 3, 15)),
    (datetime.date(2026, 3, 16), datetime.date(2026, 3, 20)),
    (datetime.date(2026, 3, 21), datetime.date(2026, 3, 25)),
    (datetime.date(2026, 3, 26), datetime.date(2026, 3, 31)),
    (datetime.date(2026, 4, 1), datetime.date(2026, 4, 3)),
    (datetime.date(2026, 4, 4), datetime.date(2026, 4, 10)),
    (datetime.date(2026, 4, 11), datetime.date(2026, 4, 17)),
    (datetime.date(2026, 4, 18), datetime.date(2026, 4, 24)),
    (datetime.date(2026, 4, 25), datetime.date(2026, 4, 30)),
    (datetime.date(2026, 9, 1), datetime.date(2026, 9, 4)),
    (datetime.date(2026, 9, 5), datetime.date(2026, 9, 11)),
    (datetime.date(2026, 9, 12), datetime.date(2026, 9, 18)),
    (datetime.date(2026, 9, 19), datetime.date(2026, 9, 25)),
    (datetime.date(2026, 9, 26), datetime.date(2026, 9, 30)),
]


def send_gas_notification():
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
      msg += f"⏳ متبقي *{days_left}* أيام لتنتهي هذه الوجبة."
  else:
    msg = f"ℹ️ لا توجد بيانات مسجلة لليوم ({today.strftime('%Y-%m-%d')})."

  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}

  try:
    res = requests.post(url, data=payload, timeout=15)
    print("Status Code:", res.status_code)
    print("Response:", res.text)
  except Exception as e:
    print("حدث خطأ أثناء الإرسال:", e)


if __name__ == "__main__":
  send_gas_notification()
