# Telegram Seen Detector Userbot

This is a Telegram Userbot (using Pyrogram) that allows you to send messages to users and get notified when they see (read) them. It also forwards any replies back to you.

## Features
- Send messages to any user by ID or Username.
- Get a notification when the message is "Seen".
- Forward replies from the target user.
- Persistent state (remembers tracked messages after restart).

## Anonymity Warning ⚠️
- This is a **Userbot**, which means it uses a real Telegram account.
- The person you message **will see the profile** (name, photo, etc.) of the account you use.
- If you want to remain **Anonymous**, you must use a **Secondary/Fake account** to log in to the bot.
- You can configure `OWNER_ID` in `config.py` to receive notifications on your main account while the bot runs on your fake account.

## Setup Instructions

1. **Get API Keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and log in.
   - Click on "API development tools".
   - Create a new application.
   - Copy your `API_ID` and `API_HASH`.

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Bot:**
   - Open `config.py`.
   - Replace `API_ID` and `API_HASH` with your values.
   - Set `OWNER_ID` to your main account's numeric ID if you want notifications there.
   - **Proxy:** If you are in a filtered region (like Iran), set the `PROXY` variable.

4. **Run the Bot:**
   ```bash
   python bot.py
   ```
   - Enter the **Phone Number** of the account you want to use for messaging.
   - Enter the confirmation code sent to your Telegram app.

## How to Use

- **Start the bot:** Send `.start` in any chat (only you can trigger it).
- **Send a message:** Use the command `.msg @username Your message here`.
- **Seen Status:** When the user reads your message, the bot will notify the `OWNER_ID`.
- **Replies:** Any message the user sends back will be forwarded to the `OWNER_ID`.
- **Ghost Reading**: The bot does **not** mark incoming replies as "Seen". You can read the forwarded messages without the sender knowing you have seen them.

---

## راهنمای فارسی

این یک یوزربات تلگرام است که به شما اجازه می‌دهد به بقیه پیام دهید و متوجه شوید چه زمانی پیام شما را دیده‌اند.

### نکته مهم در مورد ناشناس ماندن ⚠️
این برنامه با **اکانت تلگرام** کار می‌کند. یعنی طرف مقابل اسم و عکس اکانتی که باهاش وارد شدی رو میبینه. اگه می‌خوای ناشناس بمونی، باید با یک **اکانت فرعی یا فیک** وارد بشی.

### مراحل راه‌اندازی:
۱. دریافت **API_ID** و **API_HASH** از سایت [my.telegram.org](https://my.telegram.org).
۲. نصب کتابخانه‌ها: `pip install -r requirements.txt`.
۳. تنظیم فایل `config.py` (آیدی‌ها و پروکسی).
۴. اجرای ربات: `python bot.py`.
   - شماره موبایل اکانتی که می‌خوای باهاش پیام بدی رو وارد کن.

### نحوه استفاده:
- ارسال پیام: `.msg @username متن پیام`
- وقتی پیام خونده بشه، ربات بهت خبر میده.
- جواب‌های طرف هم برات فوروارد میشه.
- **حالت روح (Ghost Mode):** ربات پیام‌های دریافتی را برای طرف مقابل "سین" نمی‌کند. بنابراین شما می‌توانید جواب‌ها را بخوانید بدون اینکه طرف مقابل متوجه شود.
