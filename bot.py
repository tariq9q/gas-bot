import datetime
import re
import bs4
import requests
import telebot

BOT_TOKEN = "8835971524:AAGdzuuvcBWBlqdlHInoxTigAPdGYUOTa_TI"
bot = telebot.TeleBot(BOT_TOKEN)


def fetch_gas_info_from_web():
  url = "https://siartna.com/%D8%AD%D8%B5%D8%A9-%D8%A8%D8%A7%D9%86%D8%B2%D9%8A%D9%86/?srsltid=AU7gw4USVzOELAOP45djD5FBFFO5aIWoNthYDTUJYI8ORileiic0EpEs"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = bs4.BeautifulSoup(response.text, "html.parser")
      # البحث عن النصوص المتعلقة بحصة كركوك
      text_content = soup.get_text()

      # استخراج السطور الخاصة بكركوك أو الوجبة الحالية
      lines = [
          line.strip()
          for line in text_content.split("\n")
          if "كركوك" in line or "الوجبة" in line or "البنزين" in line
      ]
      clean_info = "\n".join(lines[:5])  # أخذ أول بضعة سطور رئيسية

      if clean_info:
        return clean_info

    return None
  except Exception as e:
    print(f"Error fetching data: {e}")
    return None


def get_gas_status():
  today = datetime.date.today().strftime("%Y-%m-%d")
  web_data = fetch_gas_info_from_web()

  msg = f"⛽ *تذكير حصة البنزين - كركوك*\n\n"
  msg += f"📅 *تاريخ اليوم:* {today}\n\n"

  if web_data:
    msg += f"📢 *آخر التحديثات المعلنة:*\n{web_data}\n\n"
    msg += "🌐 *المصدر:* موقع سيارتنا"
  else:
    msg += (
        "⚠️ تعذر جلب البيانات المباشرة من الموقع حالياً. يرجى المتابعة لاحقاً."
    )

  return msg


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  status_msg = get_gas_status()
  bot.reply_to(message, status_msg, parse_mode="Markdown")


if __name__ == "__main__":
  bot.infinity_polling()
