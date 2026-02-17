import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.request import HTTPXRequest
from .config import TELEGRAM_TOKEN, PROXY_URL
from .keyboards import get_main_menu, get_feedback_menu, get_cancel_menu
from .ai_agent import AIAgent

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ai_agent = AIAgent()

# Conversation States
(
    CLIENT_BUSINESS_TYPE,
    CLIENT_TARGET_AUDIENCE,
    SALES_PRODUCT_DETAILS,
    CONTENT_TYPE,
    FEEDBACK_RATING
) = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! 👋"
        "\n\nمن ربات **پول‌ساز** هستم. هدف من کمک به شما برای **کسب درآمد بیشتر** و **پیدا کردن مشتری** است."
        "\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید تا شروع کنیم:",
        reply_markup=get_main_menu()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "عملیات لغو شد. بازگشت به منوی اصلی.",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# --- Client Finder Handlers ---
async def client_finder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 **یافتن مشتری**\n\n"
        "برای اینکه بهترین استراتژی را به شما بدهم، لطفاً بگویید **کسب و کار شما چیست؟**\n"
        "(مثال: فروشگاه پوشاک، خدمات مشاوره املاک، تولید محتوا)",
        reply_markup=get_cancel_menu()
    )
    return CLIENT_BUSINESS_TYPE

async def client_business_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    business_type = update.message.text
    context.user_data['business_type'] = business_type
    await update.message.reply_text(
        "✅ بسیار عالی.\n\n"
        "حالا لطفاً بگویید **مخاطب هدف شما چه کسانی هستند؟**\n"
        "(مثال: نوجوانان، صاحبان کسب و کار کوچک، خانم‌های خانه‌دار)",
        reply_markup=get_cancel_menu()
    )
    return CLIENT_TARGET_AUDIENCE

async def client_target_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_audience = update.message.text
    business_type = context.user_data.get('business_type')

    await update.message.reply_text("⏳ در حال پردازش و تولید استراتژی اختصاصی شما... لطفاً چند لحظه صبر کنید.")

    # Call AI
    result = await ai_agent.generate_client_finding_strategy(business_type, target_audience)

    await update.message.reply_text(
        result,
        parse_mode="Markdown", # Assuming AI returns Markdown formatted text
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# --- Sales Text Handlers ---
async def sales_text_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 **تولید متن فروش**\n\n"
        "لطفاً **مشخصات محصول یا خدمات** خود را وارد کنید.\n"
        "هرچه توضیحات دقیق‌تر باشد، متن فروش بهتری دریافت خواهید کرد.\n"
        "(مثال: کفش ورزشی طبی مخصوص پیاده‌روی، قیمت ۲ میلیون تومان، ارسال رایگان)",
        reply_markup=get_cancel_menu()
    )
    return SALES_PRODUCT_DETAILS

async def sales_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_details = update.message.text

    await update.message.reply_text("⏳ در حال نوشتن متن‌های فروش جذاب برای شما...")

    result = await ai_agent.generate_sales_text(product_details)

    await update.message.reply_text(
        result,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# --- Content Creation Handlers ---
async def content_creation_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 **دستیار تولید محتوا**\n\n"
        "برای چه موضوع یا پلتفرمی محتوا می‌خواهید؟\n"
        "(مثال: پست اینستاگرام درباره فواید قهوه، مقاله برای سایت درباره دیجیتال مارکتینگ)",
        reply_markup=get_cancel_menu()
    )
    return CONTENT_TYPE

async def content_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content_type = update.message.text

    await update.message.reply_text("⏳ در حال ایده‌پردازی و تولید تقویم محتوایی...")

    result = await ai_agent.generate_content_ideas(content_type)

    await update.message.reply_text(
        result,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

# --- Premium and Feedback Handlers ---
async def premium_upsell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 **اشتراک ویژه پول‌ساز**\n\n"
        "با اشتراک ویژه به امکانات زیر دسترسی خواهید داشت:\n"
        "✅ کوچینگ اختصاصی کسب و کار\n"
        "✅ قالب‌های فروش پیشرفته و اختصاصی\n"
        "✅ تقویم محتوایی ۳۰ روزه کامل\n"
        "✅ تحلیل دقیق رقبا\n\n"
        "همین حالا ارتقا دهید و درآمد خود را چند برابر کنید! 🚀\n"
        "برای خرید اشتراک به پشتیبانی پیام دهید: @SupportID",
        reply_markup=get_main_menu()
    )

async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "نظر شما درباره عملکرد ربات چیست؟ 👇",
        reply_markup=get_feedback_menu()
    )
    return FEEDBACK_RATING

async def feedback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback = update.message.text
    if feedback == "🔙 بازگشت به منو":
        await update.message.reply_text("بازگشت به منوی اصلی.", reply_markup=get_main_menu())
        return ConversationHandler.END

    await update.message.reply_text(
        "ممنون از بازخورد شما! ❤️\nما همواره در تلاشیم تا بهتر شویم.",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

def main():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not set in .env file.")
        return

    # Initialize ApplicationBuilder
    builder = ApplicationBuilder().token(TELEGRAM_TOKEN)

    if PROXY_URL:
        request = HTTPXRequest(proxy_url=PROXY_URL)
        builder.request(request)
        builder.get_updates_request(request)

    app = builder.build()

    # Handlers
    app.add_handler(CommandHandler("start", start))

    client_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔎 یافتن مشتری$"), client_finder_start)],
        states={
            CLIENT_BUSINESS_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^❌ لغو عملیات$"), client_business_type)],
            CLIENT_TARGET_AUDIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^❌ لغو عملیات$"), client_target_audience)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو عملیات$"), cancel)]
    )
    app.add_handler(client_handler)

    sales_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 تولید متن فروش$"), sales_text_start)],
        states={
            SALES_PRODUCT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^❌ لغو عملیات$"), sales_product_details)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو عملیات$"), cancel)]
    )
    app.add_handler(sales_handler)

    content_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 دستیار محتوا$"), content_creation_start)],
        states={
            CONTENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^❌ لغو عملیات$"), content_type_handler)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو عملیات$"), cancel)]
    )
    app.add_handler(content_handler)

    app.add_handler(MessageHandler(filters.Regex("^💎 اشتراک ویژه$"), premium_upsell))

    feedback_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^⭐️ بازخورد$"), feedback_start)],
        states={
            FEEDBACK_RATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_handle)]
        },
        fallbacks=[MessageHandler(filters.Regex("^🔙 بازگشت به منو$"), feedback_handle)]
    )
    app.add_handler(feedback_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
