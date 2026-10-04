import telebot
import time
import os

# ==========================================
# 1. ضع توكن البوت الخاص بك هنا (من BotFather)
BOT_TOKEN = '8835971524:AAFr_Pyh9XyzTYKEnfd1H17C1tljOhflDgk'
bot = telebot.TeleBot(BOT_TOKEN)

# 2. ضع رقم الآيدي (ID) الخاص بك هنا لتكون أنت الإدمن الوحيد
# (يمكنك معرفته من خلال إرسال رسالة لبوت @userinfobot)
ADMIN_ID = 495109765 
# ==========================================

# --- أمر البداية وحفظ المشتركين ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    
    # التأكد من وجود ملف users.txt أو إنشائه
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as file:
            pass # إنشاء ملف فارغ

    # قراءة الملف للتأكد من أن المستخدم ليس مسجلاً مسبقاً
    with open("users.txt", "r") as file:
        users = file.read().splitlines()

    # إذا كان المستخدم جديداً، قم بحفظ الآيدي الخاص به
    if chat_id not in users:
        with open("users.txt", "a") as file:
            file.write(chat_id + "\n")
            
    bot.reply_to(message, "أهلاً بك في بوت تنبيهات البنزين - كركوك ⛽️\nتم تسجيلك بنجاح لاستلام الإشعارات عند توفر البنزين.")


# --- أمر الإدمن لإرسال الإشعارات للجميع ---
@bot.message_handler(commands=['send'])
def broadcast_message(message):
    # التأكد من أن مرسل الأمر هو الإدمن
    if message.chat.id == ADMIN_ID:
        # استخراج الرسالة التي كتبها الإدمن بعد أمر /send
        text_to_send = message.text.replace('/send', '').strip()
        
        if not text_to_send:
            bot.reply_to(message, "يرجى كتابة الرسالة بعد الأمر.\nمثال:\n/send تم إطلاق وجبة بنزين جديدة في محطة كذا!")
            return

        # التأكد من وجود مشتركات
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
                time.sleep(0.1) # مهم جداً لتجنب حظر البوت من تيليجرام
            except Exception as e:
                # يتم تجاهل الخطأ إذا قام المستخدم بحظر البوت
                pass
        
        bot.reply_to(message, f"✅ اكتمل النشر!\nتم إرسال الإشعار بنجاح إلى {success_count} مشترك.")
    else:
        bot.reply_to(message, "⛔️ عذراً، هذا الأمر مخصص للإدمن فقط.")


# --- تشغيل البوت باستمرار ---
print("Bot is running...")
bot.infinity_polling()
