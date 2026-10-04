import telebot
import time
import os
from datetime import date

# ==========================================
# 1. ضع توكن البوت الخاص بك هنا بين علامات التنصيص
BOT_TOKEN = '8835971524:AAFr_Pyh9XyzTYKEnfd1H17C1tljOhflDgk'
bot = telebot.TeleBot(BOT_TOKEN)

# 2. الآيدي الخاص بك (أنت الإدمن)
ADMIN_ID = 495109765
# ==========================================

# --- أمر البداية (عرض الحصة وحفظ المشترك) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    
    # 1. حفظ الآيدي الخاص بالمشترك في ملف إذا لم يكن موجوداً
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as file:
            pass # إنشاء ملف فارغ

    with open("users.txt", "r") as file:
        users = file.read().splitlines()

    if chat_id not in users:
        with open("users.txt", "a") as file:
            file.write(chat_id + "\n")

    # 2. إعداد تواريخ الحصة (قم بتعديل بداية ونهاية الوجبة من هنا عند كل تحديث)
    today = date.today()
    start_date = date(2026, 10, 2) # سنة، شهر، يوم (بداية الوجبة)
    end_date = date(2026, 10, 6)   # سنة، شهر، يوم (نهاية الوجبة)
    
    # حساب الأيام المتبقية
    days_remaining = (end_date - today).days
    
    # تنسيق الرسالة كما في صورتك بالضبط
    msg = f"""⛽ تذكير حصة البنزين - كركوك

📅 التاريخ اليوم: {today.strftime('%d-%m-%Y')}
⛽ تاريخ بداية الوجبة: {start_date.strftime('%d-%m-%Y')}
🏁 تاريخ نهاية الوجبة: {end_date.strftime('%d-%m-%Y')}

⏳ متبقي {days_remaining} أيام لتنتهي هذه الوجبة (تنتهي يوم {end_date.strftime('%d-%m-%Y')}).

by tariq nabeil"""

    bot.reply_to(message, msg)


# --- أمر الإدمن لإرسال الإشعارات للجميع ---
@bot.message_handler(commands=['send'])
def broadcast_message(message):
    # التأكد من أن مرسل الأمر هو أنت (الإدمن)
    if message.chat.id == ADMIN_ID:
        text_to_send = message.text.replace('/send', '').strip()
        
        if not text_to_send:
            bot.reply_to(message, "يرجى كتابة الرسالة بعد الأمر.\nمثال:\n/send تم إطلاق وجبة بنزين جديدة!")
            return

        if not os.path.exists("users.txt"):
            bot.reply_to(message, "لا يوجد مشتركون مسجلون حتى الآن.")
            return

        with open("users.txt", "r") as file:
            users = file.read().splitlines()
        
        if not users:
            bot.reply_to(message, "قائمة المشتركين فارغة.")
            return

        bot.reply_to(message, "جاري إرسال الإشعار للمشتركين... ⏳")
        
        success_count = 0
        for user_id in users:
            try:
                bot.send_message(user_id, text_to_send)
                success_count += 1
                time.sleep(0.1) # لتجنب حظر البوت من تيليجرام
            except Exception as e:
                pass # تجاهل الأشخاص الذين قاموا بحظر البوت
        
        bot.reply_to(message, f"✅ اكتمل النشر!\nتم إرسال الإشعار بنجاح إلى {success_count} مشترك.")
    else:
        bot.reply_to(message, "⛔️ عذراً، هذا الأمر مخصص للإدمن فقط.")


# --- تشغيل البوت ---
print("Bot is running...")
bot.infinity_polling()import telebot
import time
import os
from datetime import date

# ==========================================
# 1. ضع توكن البوت الخاص بك هنا بين علامات التنصيص
BOT_TOKEN = 'ضع_التوكن_هنا'
bot = telebot.TeleBot(BOT_TOKEN)

# 2. الآيدي الخاص بك (أنت الإدمن)
ADMIN_ID = 495109765
# ==========================================

# --- أمر البداية (عرض الحصة وحفظ المشترك) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    
    # 1. حفظ الآيدي الخاص بالمشترك في ملف إذا لم يكن موجوداً
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as file:
            pass # إنشاء ملف فارغ

    with open("users.txt", "r") as file:
        users = file.read().splitlines()

    if chat_id not in users:
        with open("users.txt", "a") as file:
            file.write(chat_id + "\n")

    # 2. إعداد تواريخ الحصة (قم بتعديل بداية ونهاية الوجبة من هنا عند كل تحديث)
    today = date.today()
    start_date = date(2026, 10, 2) # سنة، شهر، يوم (بداية الوجبة)
    end_date = date(2026, 10, 6)   # سنة، شهر، يوم (نهاية الوجبة)
    
    # حساب الأيام المتبقية
    days_remaining = (end_date - today).days
    
    # تنسيق الرسالة كما في صورتك بالضبط
    msg = f"""⛽ تذكير حصة البنزين - كركوك

📅 التاريخ اليوم: {today.strftime('%d-%m-%Y')}
⛽ تاريخ بداية الوجبة: {start_date.strftime('%d-%m-%Y')}
🏁 تاريخ نهاية الوجبة: {end_date.strftime('%d-%m-%Y')}

⏳ متبقي {days_remaining} أيام لتنتهي هذه الوجبة (تنتهي يوم {end_date.strftime('%d-%m-%Y')}).

by tariq nabeil"""

    bot.reply_to(message, msg)


# --- أمر الإدمن لإرسال الإشعارات للجميع ---
@bot.message_handler(commands=['send'])
def broadcast_message(message):
    # التأكد من أن مرسل الأمر هو أنت (الإدمن)
    if message.chat.id == ADMIN_ID:
        text_to_send = message.text.replace('/send', '').strip()
        
        if not text_to_send:
            bot.reply_to(message, "يرجى كتابة الرسالة بعد الأمر.\nمثال:\n/send تم إطلاق وجبة بنزين جديدة!")
            return

        if not os.path.exists("users.txt"):
            bot.reply_to(message, "لا يوجد مشتركون مسجلون حتى الآن.")
            return

        with open("users.txt", "r") as file:
            users = file.read().splitlines()
        
        if not users:
            bot.reply_to(message, "قائمة المشتركين فارغة.")
            return

        bot.reply_to(message, "جاري إرسال الإشعار للمشتركين... ⏳")
        
        success_count = 0
        for user_id in users:
            try:
                bot.send_message(user_id, text_to_send)
                success_count += 1
                time.sleep(0.1) # لتجنب حظر البوت من تيليجرام
            except Exception as e:
                pass # تجاهل الأشخاص الذين قاموا بحظر البوت
        
        bot.reply_to(message, f"✅ اكتمل النشر!\nتم إرسال الإشعار بنجاح إلى {success_count} مشترك.")
    else:
        bot.reply_to(message, "⛔️ عذراً، هذا الأمر مخصص للإدمن فقط.")


# --- تشغيل البوت ---
print("Bot is running...")
bot.infinity_polling()
