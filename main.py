from config import *
from useLLM import process

import asyncio
import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message


cache = "" # all 15 mins cache
processed_cache = [] # all not .in proccessed 

last_ids = {}  # {"chat_id": last_message_id}

app = Client("userbot", api_id=API_ID, api_hash=API_HASH)

def load_chats():
    if not os.path.exists(CHATS_FILE):
        return []
    with open(CHATS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def save_chat(chat_id):
    chats = load_chats()
    if chat_id not in chats:
        with open(CHATS_FILE, "a") as f:
            f.write(f"{chat_id}\n")


def get_chat_name(chat):
    if hasattr(chat, "title") and chat.title:
        return chat.title
    if hasattr(chat, "first_name"):
        return chat.first_name or str(chat.id)
    return str(chat.id)


def add_to_cache(chat_name, user_name, text):
    global cache
    cache += f"[{chat_name}] {user_name}: {text}\n"


def get_cache_stats(proc_cache):
    words = len(" ".join(proc_cache).split())
    chars = len(" ".join(proc_cache))
    eters = len(proc_cache)
    return words, chars, eters


def cache_to_text(proc_cache):
    return "\n".join(proc_cache)


async def check_chats():
    global cache, last_ids, processed_cache
    print(last_ids)
    chats = load_chats()
    if not chats:
        print("No chats to check")
        return
    
    for chat_id in chats:
        try:
            print("check chat", chat_id)
            if chat_id not in last_ids:
                messages_for_id = []
                async for msg in app.get_chat_history(chat_id, limit=1):
                    messages_for_id.append(msg)
                
                if messages_for_id:
                    last_ids[chat_id] = messages_for_id[0].id
                    print("new last_id for chat", chat_id, last_ids[chat_id])
                    continue 
            
            last_id = last_ids.get(chat_id, 0)
            messages = []
            
            async for msg in app.get_chat_history(chat_id, limit=50):
                if msg.id > last_id: 
                    messages.append(msg)
                    print("new msg", msg.id, "in chat", chat_id, msg.text)
            
            if messages:
                print("new messages found in chat", messages)
                last_ids[chat_id] = max(msg.id for msg in messages)
                
                chat = await app.get_chat(chat_id)
                chat_name = get_chat_name(chat)
                
                for msg in reversed(messages):
                    if msg.text and not msg.text.startswith("."):
                        user_name = msg.from_user.first_name if msg.from_user else "Unknown"
                        text = msg.text[:200] 
                        
                        add_to_cache(chat_name, user_name, text)
        
        except Exception as e:
            print(f"Ошибка при проверке чата {chat_id}: {e}")
    
    if cache:
        print("cache to process", cache)
        
        result = process(cache)
        
        processed_cache.append(result)
        
        if "IMPORTANT" in result:
            important_part = result.split("IMPORTANT", 1)[1].strip()
            if important_part:
                await app.send_message("me", important_part)
        
        cache = ""




@app.on_message(filters.me & filters.command("add", prefixes="."))
async def add_chat(client, message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.edit("❌ Использование: .add chat_id")
        return
    
    chat_id = parts[1]
    save_chat(chat_id)
    await message.edit(f"✅ Чат {chat_id} добавлен в список")


@app.on_message(filters.me & filters.command("status", prefixes="."))
async def show_status(client, message: Message):
    words, chars, eters = get_cache_stats(processed_cache)
    text = f"📊 Статистика:\n"
    text += f"📝 Слов: {words}\n"
    text += f"🔤 Символов: {chars}\n"
    text += f"💬 Итераций: {eters}"
    await message.edit(text)


@app.on_message(filters.me & filters.command("in", prefixes="."))
async def show_in(client, message: Message):
    global processed_cache, cache
    await check_chats()
    
    if not processed_cache:
        await message.edit("❌ Кэш пуст")
        return
    
    input_text = cache_to_text(processed_cache)
    result = process(input_text)
    
    await message.edit(result)
    
    processed_cache = []


async def periodic_check():
    while True:
        await asyncio.sleep(TIME_SECONDS)  # 15 минут
        await check_chats()


def main():
    print("🚀 Запуск юзербота...")
    
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_check())
    
    app.run()


if __name__ == "__main__":
    main()