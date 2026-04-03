import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("8450660558:AAE3Hoz-xp8tnyws34UbVbjm84KEcVH2xU4")  # توکن از سرور
ADMIN_ID = 832244920  # آیدی عددی تلگرام خودت

# تابع قیمت پلکانی
def get_price_per_gb(gb):
    if gb >= 10:
        return 700
    elif gb >= 5:
        return 800
    elif gb >= 2:
        return 850
    else:
        return 900

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 خوش اومدی\n\n"
        "💰 تعرفه‌ها:\n"
        "1GB = 900\n"
        "2GB+ = 850\n"
        "5GB+ = 800\n"
        "10GB+ = 700\n\n"
        "🔢 چند گیگ میخوای؟"
    )
    context.user_data["step"] = "get_gb"

# مدیریت پیام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # گرفتن حجم
    if context.user_data.get("step") == "get_gb":
        if text and text.isdigit():
            gb = int(text)
            price_per_gb = get_price_per_gb(gb)
            total_price = gb * price_per_gb

            context.user_data.update({
                "gb": gb,
                "price": total_price,
                "ppg": price_per_gb,
                "step": "wait_receipt"
            })

            await update.message.reply_text(
                f"📦 {gb} گیگ\n"
                f"💵 هر گیگ: {price_per_gb}\n"
                f"💰 مبلغ کل: {total_price} تومان\n\n"
                "💳 شماره کارت:\n"
                "6037-xxxx-xxxx-xxxx\n"
                "به نام: ...\n\n"
                "📩 رسید رو ارسال کن (عکس یا متن)"
            )
        else:
            await update.message.reply_text("❌ فقط عدد بفرست")

    # دریافت رسید
    elif context.user_data.get("step") == "wait_receipt":
        await update.message.reply_text("✅ رسید دریافت شد، بررسی میشه")

        caption = (
            f"📥 سفارش جدید\n\n"
            f"👤 @{user.username}\n"
            f"🆔 {user.id}\n"
            f"📦 {context.user_data['gb']} گیگ\n"
            f"💵 هر گیگ: {context.user_data['ppg']}\n"
            f"💰 مبلغ: {context.user_data['price']}"
        )

        # اگر عکس فرستاده
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption)
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption + "\n\n📩 رسید متنی")

        context.user_data.clear()

# اجرا
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

app.run_polling()