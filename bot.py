import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8450660558:AAE3Hoz-xp8tnyws34UbVbjm84KEcVH2xU4"
ADMIN_ID = 832244920  # آیدی خودت

logging.basicConfig(level=logging.INFO)

# ذخیره وضعیت چت زنده و سفارش‌ها
live_chats = {}       # user_id: True/False/"admin_reply"
order_sessions = {}   # user_id: مرحله سفارش
pending_receipts = {} # user_id: اطلاعات سفارش برای رسید

# ----------------------
# منوی اصلی کاربر
MAIN_MENU = [
    [InlineKeyboardButton("💬 پشتیبانی", callback_data="support"),
     InlineKeyboardButton("📦 سفارش جدید", callback_data="order")],
    [InlineKeyboardButton("💰 تعرفه‌ها", callback_data="prices"),
     InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")],
    [InlineKeyboardButton("📝 راهنمای استفاده", callback_data="guide")]
]

# ----------------------
# تابع شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = InlineKeyboardMarkup(MAIN_MENU)
    await update.message.reply_text(
        "🌟 به ربات فروش VPN خوش آمدید! 🌟\n\n"
        "از طریق دکمه‌های زیر می‌توانید سریع و راحت خدمات ما را انتخاب کنید:",
        reply_markup=markup
    )

# ----------------------
# دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "support":
        live_chats[user_id] = True
        await query.message.reply_text(
            "💬 پیام خود را بنویسید تا پشتیبانی ما سریعاً پاسخ دهد.\n"
            "تمام تلاش ما این است که در کوتاه‌ترین زمان به شما کمک کنیم."
        )
        await context.bot.send_message(chat_id=ADMIN_ID,
            text=f"🆘 کاربر @{query.from_user.username} ({user_id}) درخواست پشتیبانی کرد."
        )

    elif data == "order":
        order_sessions[user_id] = "get_gb"
        await query.message.reply_text(
            "📦 عالی! چند گیگ می‌خوای سفارش بدی؟\n"
            "لطفاً فقط عدد وارد کن."
        )

    elif data == "prices":
        await query.message.reply_text(
            "💰 تعرفه‌های ما به شرح زیر است:\n"
            "1GB = 900 تومان\n"
            "2GB+ = 850 تومان\n"
            "5GB+ = 800 تومان\n"
            "10GB+ = 700 تومان\n\n"
            "💡 هرچه حجم بیشتر باشد، قیمت هر گیگ کمتر است!"
        )

    elif data == "about":
        await query.message.reply_text(
            "ℹ️ درباره ما:\n"
            "ربات فروش VPN طراحی شده توسط Jawad\n"
            "هدف: ارائه VPN مطمئن، سریع و آسان برای کاربران عزیز.\n"
            "📱 پشتیبانی و سفارش از طریق همین ربات انجام می‌شود."
        )

    elif data == "guide":
        await query.message.reply_text(
            "📝 راهنمای استفاده از ربات:\n"
            "1️⃣ دکمه 💬 پشتیبانی برای ارسال پیام و ارتباط با ما\n"
            "2️⃣ دکمه 📦 سفارش جدید برای خرید VPN\n"
            "3️⃣ پس از انتخاب حجم، مبلغ و شماره کارت نمایش داده می‌شود\n"
            "4️⃣ رسید خود را ارسال کنید (عکس یا متن)\n"
            "5️⃣ پاسخ پشتیبانی مستقیم به شما ارسال می‌شود"
        )

# ----------------------
# مدیریت پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text
    photo = update.message.photo

    # ----- پشتیبانی زنده -----
    if live_chats.get(user_id) == True:
        # ارسال به ادمین با دکمه پاسخ سریع
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"💬 پاسخ به {user.username}", callback_data=f"reply_{user_id}")]])
        await context.bot.send_message(chat_id=ADMIN_ID,
            text=f"📩 پیام از @{user.username} ({user_id}):\n{text}",
            reply_markup=keyboard
        )
        await update.message.reply_text(
            "✅ پیام شما به پشتیبانی ارسال شد. در کوتاه‌ترین زمان پاسخ دریافت خواهید کرد."
        )
        return

    # ----- ارسال رسید -----
    if user_id in pending_receipts:
        order_info = pending_receipts[user_id]
        if photo:
            file_id = photo[-1].file_id
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id,
                                         caption=f"📥 رسید کاربر @{user.username} ({user_id})\n📦 {order_info['gb']} گیگ\n💰 مبلغ: {order_info['price']}")
        else:
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=f"📥 رسید متنی از @{user.username} ({user_id})\n📦 {order_info['gb']} گیگ\n💰 مبلغ: {order_info['price']}\n\n📩 متن رسید:\n{text}")
        await update.message.reply_text("✅ رسید شما دریافت شد و در حال بررسی است. تشکر!")
        pending_receipts.pop(user_id)
        return

    # ----- سفارش جدید -----
    if order_sessions.get(user_id) == "get_gb":
        if text.isdigit():
            gb = int(text)
            price_per_gb = 700 if gb >= 10 else 800 if gb >= 5 else 850 if gb >= 2 else 900
            total_price = gb * price_per_gb
            order_sessions[user_id] = None
            pending_receipts[user_id] = {"gb": gb, "price": total_price}
            await update.message.reply_text(
                f"📦 سفارش شما: {gb} گیگ\n"
                f"💵 هر گیگ: {price_per_gb} تومان\n"
                f"💰 مبلغ کل: {total_price} تومان\n\n"
                "💳 شماره کارت:\n6037-xxxx-xxxx-xxxx\nبه نام: ...\n\n"
                "📩 لطفاً رسید خود را ارسال کنید (عکس یا متن)."
            )
        else:
            await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید.")
        return

    # ----- پاسخ ادمین -----
    if live_chats.get(user_id) == "admin_reply":
        await context.bot.send_message(chat_id=user_id,
                                       text=f"💬 پاسخ پشتیبانی:\n{text}")
        live_chats[user_id] = True  # بازگشت به حالت چت زنده
        return

# ----------------------
# پاسخ سریع ادمین با دکمه
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("reply_"):
        target_id = int(data.split("_")[1])
        live_chats[target_id] = "admin_reply"
        await query.message.reply_text("✍️ لطفاً متن پاسخ خود را بنویسید. پیام شما مستقیم به کاربر ارسال خواهد شد.")

# ----------------------
# اجرای برنامه
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_button_handler, pattern="^reply_"))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

print("🤖 ربات حرفه‌ای و کامل روشن شد...")
app.run_polling()