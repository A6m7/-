
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ضع التوكن و ID مباشرة هنا
BOT_TOKEN = "7432147532:AAH5Oc5zLJdqYr7HpAQkoRz6DQEiZCsEmm4"
USER_ID = 6661012567  # ضع هنا آيدي المدير (رقم صحيح)
REQUEST_GROUP_ID = None  # يمكنك وضع رقم مجموعة التليجرام هنا أو تركها None

# نص الرسالة الترحيبية
WELCOME_TEXT = (
    "مرحبًا بك في بوت مكتبة سيسي للكتابة والتصميم!\n"
    "مكتبة سيسي: خدمات احترافية للطلبة والمعلمين، بسرعة ودقة.\n\n"
    "يرجى اختيار الخدمة التي تحتاجها من القائمة أدناه:"
)

# الخدمات المتاحة
services = [
    ("✍️ كتابة البحوث", "research"),
    ("🖋️ تصميم القصائد", "poetry"),
    ("📘 إعداد المذكرات", "notes"),
    ("📢 تصميم الإعلانات", "ads"),
    ("☎️ تواصل مع المدير", "contact_admin"),
]

# توليد لوحة الأزرار التفاعلية
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=label, callback_data=callback)]
        for label, callback in services
    ])

# الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_keyboard()
    )

# التعامل مع اختيار الخدمة
async def handle_service_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "contact_admin":
        contact_link = f"tg://user?id={USER_ID}"
        await query.edit_message_text(
            f"يمكنك التواصل مع المدير مباشرة عبر الرابط التالي:\n\n"
            f"[اضغط هنا للتواصل مع المدير]({contact_link})",
            parse_mode="Markdown"
        )
        return

    context.user_data.clear()
    context.user_data['chosen_service'] = query.data
    context.user_data['awaiting_service_text'] = True
    context.user_data['user_id'] = query.from_user.id
    context.user_data['username'] = f"@{query.from_user.username}" if query.from_user.username else "لا يوجد"

    service_name = {
        "research": "✍️ كتابة البحوث",
        "poetry": "🖋️ تصميم القصائد",
        "notes": "📘 إعداد المذكرات",
        "ads": "📢 تصميم الإعلانات"
    }.get(query.data, "خدمة غير معروفة")

    await query.edit_message_text(
        f"تم اختيار: {service_name}\n\nيرجى الآن إرسال تفاصيل الخدمة المطلوبة نصًّا."
    )

# التعامل مع الرسائل النصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_service_text'):
        service = context.user_data.get('chosen_service', 'غير محدد')
        text = update.message.text
        user_id = context.user_data.get('user_id', 'غير معروف')
        username = context.user_data.get('username', 'لا يوجد')
        full_name = update.message.from_user.full_name

        message = (
            f"✨ طلب جديد ✨\n\n"
            f"📌 الخدمة المطلوبة: {service}\n"
            f"👤 اسم العميل: {full_name}\n"
            f"📱 اليوزرنيم: {username}\n"
            f"🆔 الآيدي: {user_id}\n\n"
            f"📄 تفاصيل الطلب:\n{text}\n\n"
            f"[↩️ الرد على العميل](tg://user?id={user_id})"
        )

        # إرسال الرسالة إلى المجموعة أو المدير
        chat_id = REQUEST_GROUP_ID if REQUEST_GROUP_ID else USER_ID
        
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            
            await update.message.reply_text(
                "✅ تم استلام طلبك بنجاح\n\n"
                "سيتم مراجعة طلبك والرد عليك في أقرب وقت ممكن.\n"
                "يمكنك التواصل مباشرة مع المدير عبر:\n"
                f"[هذا الرابط](tg://user?id={USER_ID})",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending message: {e}")
            await update.message.reply_text("حدث خطأ أثناء إرسال طلبك، يرجى المحاولة لاحقاً.")
        
        context.user_data.clear()
    else:
        await update.message.reply_text("يرجى الضغط على /start لاختيار الخدمة المطلوبة.")

# تشغيل البوت
if __name__ == "__main__":
    if not BOT_TOKEN or not USER_ID:
        raise ValueError("يرجى التأكد من إدخال BOT_TOKEN و USER_ID في الكود.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_service_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("تم تشغيل البوت بنجاح...")
    app.run_polling()
