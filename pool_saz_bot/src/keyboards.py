from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton("🔎 یافتن مشتری"), KeyboardButton("💰 تولید متن فروش")],
        [KeyboardButton("📝 دستیار محتوا"), KeyboardButton("💎 اشتراک ویژه")],
        [KeyboardButton("⭐️ بازخورد")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_feedback_menu():
    keyboard = [
        [KeyboardButton("👍 عالی"), KeyboardButton("👎 ضعیف")],
        [KeyboardButton("🔙 بازگشت به منو")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_menu():
    keyboard = [[KeyboardButton("❌ لغو عملیات")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
