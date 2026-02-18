import json
import os
import logging
from pyrogram import Client, filters, enums, idle
from pyrogram.raw.types import UpdateReadHistoryOutbox, PeerUser, PeerChat, PeerChannel
import config

# Setup logging to see errors without crashing
logging.basicConfig(level=logging.ERROR)

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                sent = {}
                for k, v in data.get("sent_messages", {}).items():
                    try:
                        chat_id, msg_id = map(int, k.split(":"))
                        sent[(chat_id, msg_id)] = v
                    except: continue
                return sent, set(data.get("active_chats", []))
        except: pass
    return {}, set()

def save_state(sent_messages, active_chats):
    try:
        sent = {f"{k[0]}:{k[1]}": v for k, v in sent_messages.items()}
        data = {
            "sent_messages": sent,
            "active_chats": list(active_chats)
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving state: {e}")

sent_messages, active_chats = load_state()

app = Client(
    "my_account",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    proxy=config.PROXY
)

# Helper to check if a message is from the owner
def owner_filter(_, __, message):
    if config.OWNER_ID == "me":
        return message.from_user and message.from_user.is_self
    return message.from_user and (message.from_user.id == config.OWNER_ID or message.from_user.is_self)

is_owner = filters.create(owner_filter)

@app.on_message(filters.command("start", prefixes=["!", "."]) & is_owner)
async def start(client, message):
    text = "Bot is running!\nUse `.msg @username Hello` to send a message."
    if message.from_user and message.from_user.is_self:
        await message.edit_text(text)
    else:
        await message.reply_text(text)

@app.on_message(filters.command("msg", prefixes=["!", "."]) & is_owner)
async def send_msg(client, message):
    if len(message.command) < 3:
        usage = "Usage: `.msg @username text`"
        if message.from_user and message.from_user.is_self:
            await message.edit_text(usage)
        else:
            await message.reply_text(usage)
        return

    target = message.command[1]
    text = " ".join(message.command[2:])

    try:
        sent = await client.send_message(target, text)
        chat_id = sent.chat.id
        sent_messages[(chat_id, sent.id)] = True
        active_chats.add(chat_id)
        save_state(sent_messages, active_chats)

        response = f"✅ Message sent to {target} (ID: `{chat_id}`)\nMessage ID: `{sent.id}`"
        me = await client.get_me()
        if not me.is_bot:
            response += "\nI'll notify you when they see it!"

        if message.from_user and message.from_user.is_self:
            await message.edit_text(response)
        else:
            await message.reply_text(response)
    except Exception as e:
        err_msg = f"❌ Error: {e}"
        if message.from_user and message.from_user.is_self:
            await message.edit_text(err_msg)
        else:
            await message.reply_text(err_msg)

@app.on_message(filters.command("stop", prefixes=["!", "."]) & is_owner)
async def stop_tracking(client, message):
    if len(message.command) < 2:
        usage = "Usage: `.stop @username` or `.stop chat_id`"
        if message.from_user and message.from_user.is_self:
            await message.edit_text(usage)
        else:
            await message.reply_text(usage)
        return

    target = message.command[1]
    try:
        chat = await client.get_chat(target)
        chat_id = chat.id
        if chat_id in active_chats:
            active_chats.remove(chat_id)
            save_state(sent_messages, active_chats)
            res = f"Stopped tracking chat `{chat_id}`."
        else:
            res = f"Chat `{chat_id}` was not being tracked."

        if message.from_user and message.from_user.is_self:
            await message.edit_text(res)
        else:
            await message.reply_text(res)
    except Exception as e:
        err_msg = f"❌ Error: {e}"
        if message.from_user and message.from_user.is_self:
            await message.edit_text(err_msg)
        else:
            await message.reply_text(err_msg)

@app.on_raw_update()
async def raw_handler(client, update, users, chats):
    try:
        if isinstance(update, UpdateReadHistoryOutbox):
            peer = update.peer
            if isinstance(peer, PeerUser):
                chat_id = peer.user_id
            elif isinstance(peer, PeerChat):
                chat_id = -peer.chat_id
            elif isinstance(peer, PeerChannel):
                chat_id = int(f"-100{peer.channel_id}")
            else:
                return

            max_id = update.max_id

            to_remove = []
            for (t_chat_id, msg_id) in list(sent_messages.keys()):
                if t_chat_id == chat_id and msg_id <= max_id:
                    try:
                        await client.send_message(
                            config.OWNER_ID,
                            f"👁‍🗨 Message `{msg_id}` in chat `{chat_id}` has been **seen**!"
                        )
                        to_remove.append((t_chat_id, msg_id))
                    except Exception as e:
                        print(f"Error notifying owner: {e}")

            if to_remove:
                for key in to_remove:
                    sent_messages.pop(key, None)
                save_state(sent_messages, active_chats)
    except Exception as e:
        # Silently ignore raw update errors to prevent crashing
        pass

@app.on_message(filters.private & ~is_owner)
async def reply_handler(client, message):
    try:
        chat_id = message.chat.id
        if chat_id in active_chats:
            await client.send_message(
                config.OWNER_ID,
                f"📩 **New reply from {message.from_user.mention if message.from_user else 'Unknown'}** (`{chat_id}`):"
            )
            await message.copy(config.OWNER_ID)
    except Exception as e:
        print(f"Error in reply handler: {e}")

async def main():
    # Basic validation
    if config.API_ID == 1234567 or config.API_HASH == "your_api_hash_here":
        print("\n" + "!" * 50)
        print("❌ ERROR: API_ID or API_HASH is NOT set in config.py!")
        print("Please go to https://my.telegram.org, get your keys, and put them in config.py.")
        print("!" * 50 + "\n")
        return

    print("Bot is starting...")
    await app.start()

    me = await app.get_me()
    if me.is_bot:
        print(f"Logged in as BOT: {me.first_name} (@{me.username})")
        if config.OWNER_ID == "me":
            print("\n" + "!" * 50)
            print("⚠️ IMPORTANT: You are using a BOT TOKEN but OWNER_ID is not set!")
            print("Please set your numeric User ID in config.py so you can control the bot.")
            print("!" * 50 + "\n")
    else:
        print(f"Logged in as USER: {me.first_name} (@{me.username or 'NoUsername'})")

    print("Everything is ready! Send .msg @username to the bot to use it.")

    await idle()

if __name__ == "__main__":
    import asyncio
    try:
        app.run(main())
    except KeyboardInterrupt:
        pass
