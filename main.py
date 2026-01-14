import telebot
import requests
import json

# --- ТВОИ ДАННЫЕ ---
TOKEN = "8546238557:AAGwgj4r9oOYVYmcsI6RSZDUHozWELQl6m0"
GROQ_KEY = "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"
BOT_USERNAME = "@MyGenius_AI_bot"

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения истории сообщений {chat_id: [список сообщений]}
group_memory = {}

def ask_ai_with_memory(chat_id, text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    
    # Если чата нет в памяти, создаем для него пустой список
    if chat_id not in group_memory:
        group_memory[chat_id] = []
    
    # Добавляем новое сообщение пользователя в историю
    group_memory[chat_id].append({"role": "user", "content": text})
    
    # Ограничиваем память (храним только последние 10 сообщений, чтобы не перегружать)
    if len(group_memory[chat_id]) > 10:
        group_memory[chat_id] = group_memory[chat_id][-10:]
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": group_memory[chat_id]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        res_json = response.json()
        bot_answer = res_json['choices'][0]['message']['content']
        
        # Запоминаем ответ бота
        group_memory[chat_id].append({"role": "assistant", "content": bot_answer})
        
        return bot_answer
    except Exception as e:
        print(f"Ошибка памяти: {e}")
        return "⚠️ Произошел сбой в памяти, попробуй еще раз."

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.from_user.is_bot or not message.text: return

    is_private = message.chat.type == "private"
    is_reply = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id
    is_tagged = BOT_USERNAME in message.text

    if is_private or is_reply or is_tagged:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            query = message.text.replace(BOT_USERNAME, "").strip()
            
            # Передаем ID чата, чтобы бот знал, чью историю поднять
            answer = ask_ai_with_memory(message.chat.id, query if query else "Привет!")
            bot.reply_to(message, answer)
        except Exception as e:
            print(f"Ошибка в боте: {e}")

print(">>> БОТ С ПАМЯТЬЮ ЗАПУЩЕН!")
bot.infinity_polling()
