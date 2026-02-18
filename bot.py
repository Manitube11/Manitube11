import json
import os
from pyrogram import Client, filters, enums
from pyrogram.raw.types import UpdateReadHistoryOutbox
import config

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            # Convert keys back to (chat_id, msg_id) tuples
            sent = {}
            for k, v in data.get("sent_messages", {}).items():
                chat_id, msg_id = map(int, k.split(":"))
                sent[(chat_id, msg_id)] = v
            return sent, set(data.get("active_chats", []))
    return {}, set()

def save_state(sent_messages, active_chats):
    # Convert tuple keys to string "chat_id:msg_id" for JSON
    sent = {f"{k[0]}:{k[1]}": v for k, v in sent_messages.items()}
    data = {
        "sent_messages": sent,
        "active_chats": list(active_chats)
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

sent_messages, active_chats = load_state()

app = Client("my_account", api_id=config.API_ID, api_hash=config.API_HASH)

@app.on_message(filters.command("start", prefixes=["!", "."]) & filters.me)
async def start(client, message):
    await message.edit_text("Userbot is running!\nUse `.msg @username Hello` to send a message.")

@app.on_message(filters.command("msg", prefixes=["!", "."]) & filters.me)
async def send_msg(client, message):
    if len(message.command) < 3:
        await message.edit_text("Usage: `.msg @username text`")
        return

    target = message.command[1]
    text = " ".join(message.command[2:])

    try:
        sent = await client.send_message(target, text)
        chat_id = sent.chat.id
        sent_messages[(chat_id, sent.id)] = True
        active_chats.add(chat_id)
        save_state(sent_messages, active_chats)

        await message.edit_text(f"✅ Message sent to {target} (ID: `{chat_id}`)\nMessage ID: `{sent.id}`\nI'll notify you when they see it!")
    except Exception as e:
        await message.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("stop", prefixes=["!", "."]) & filters.me)
async def stop_tracking(client, message):
    if len(message.command) < 2:
        await message.edit_text("Usage: `.stop @username` or `.stop chat_id`")
        return

    target = message.command[1]
    try:
        chat = await client.get_chat(target)
        chat_id = chat.id
        if chat_id in active_chats:
            active_chats.remove(chat_id)
            save_state(sent_messages, active_chats)
            await message.edit_text(f"Stopped tracking chat `{chat_id}`.")
        else:
            await message.edit_text(f"Chat `{chat_id}` was not being tracked.")
    except Exception as e:
        await message.edit_text(f"❌ Error: {e}")

@app.on_raw_update()
async def raw_handler(client, update, users, chats):
    if isinstance(update, UpdateReadHistoryOutbox):
        # Peer can be PeerUser, PeerChat, or PeerChannel
        # We need to extract the ID
        peer = update.peer
        if hasattr(peer, "user_id"):
            chat_id = peer.user_id
        elif hasattr(peer, "chat_id"):
            chat_id = -peer.chat_id
        elif hasattr(peer, "channel_id"):
            chat_id = int(f"-100{peer.channel_id}")
        else:
            return

        max_id = update.max_id

        to_remove = []
        for (t_chat_id, msg_id) in sent_messages.keys():
            # Note: MTProto IDs for users are positive, but Pyrogram might use signed IDs.
            # Usually for private chats it's just user_id.
            if t_chat_id == chat_id and msg_id <= max_id:
                await client.send_message(
                    config.OWNER_ID,
                    f"👁‍🗨 Message `{msg_id}` in chat `{chat_id}` has been **seen**!"
                )
                to_remove.append((t_chat_id, msg_id))

        if to_remove:
            for key in to_remove:
                del sent_messages[key]
            save_state(sent_messages, active_chats)

@app.on_message(filters.private & ~filters.me)
async def reply_handler(client, message):
    chat_id = message.chat.id
    if chat_id in active_chats:
        # Send a header
        await client.send_message(
            config.OWNER_ID,
            f"📩 **New reply from {message.from_user.mention if message.from_user else 'Unknown'}** (`{chat_id}`):"
        )
        # Forward the actual message (handles media)
        await message.copy(config.OWNER_ID)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
