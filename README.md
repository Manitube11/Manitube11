# Telegram Seen Detector Userbot

This is a Telegram Userbot (using Pyrogram) that allows you to send messages to users and get notified when they see (read) them. It also forwards any replies back to you.

## Features
- Send messages to any user by ID or Username.
- Get a notification when the message is "Seen".
- Forward replies from the target user.

## Setup Instructions

1. **Get API Keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and log in.
   - Click on "API development tools".
   - Create a new application (you can use any name).
   - Copy your `API_ID` and `API_HASH`.

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Bot:**
   - Open `config.py`.
   - Replace `API_ID` and `API_HASH` with your values.
   - You can leave `OWNER_ID = "me"` to receive notifications on your own account.
   - **Proxy (Optional):** If Telegram is filtered in your region, configure the `PROXY` variable in `config.py`.

4. **Run the Bot:**
   ```bash
   python bot.py
   ```
   - On the first run, it will ask for your phone number and the login code sent to your Telegram.

## How to Use

- **Start the bot:** Send `.start` in any chat (only you can trigger it).
- **Send a message:** Use the command `.msg @username Your message here`.
- **Seen Status:** When the user reads your message, the bot will send you a notification: `👁‍🗨 Message ... has been seen!`.
- **Replies:** Any message the user sends back will be forwarded to you.

---

## راهنمای فارسی

این یک یوزربات تلگرام است که به شما اجازه می‌دهد به بقیه پیام دهید و متوجه شوید چه زمانی پیام شما را دیده‌اند.

### مراحل راه‌اندازی:
1. دریافت **API_ID** و **API_HASH** از سایت [my.telegram.org](https://my.telegram.org).
2. نصب کتابخانه‌های مورد نیاز: `pip install -r requirements.txt`.
3. تنظیم فایل `config.py` با اطلاعات خودتان.
   - **پروکسی:** اگر تلگرام برای شما فیلتر است، تنظیمات پروکسی را در `config.py` وارد کنید.
4. اجرای ربات: `python bot.py`.

### نحوه استفاده:
- برای ارسال پیام از دستور زیر استفاده کنید:
  `.msg @username متن پیام شما`
- هر زمان طرف مقابل پیام را بخواند، ربات به شما اطلاع می‌دهد.
- جواب‌های طرف مقابل هم برای شما فرستاده می‌شود.
