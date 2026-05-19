import telebot
import re

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "BU_YERGA_TOKENINGIZNI_YOZING"
CHANNEL_ID = -1003650131875
# ====================================================

bot = telebot.TeleBot(BOT_TOKEN)

post_cache = {}


def parse_caption(caption: str):
    kod = None
    nom = None
    for line in caption.splitlines():
        line = line.strip()
        if re.match(r'^[Kk]od\s*:', line):
            kod = re.sub(r'^[Kk]od\s*:\s*', '', line).strip()
        elif re.match(r'^[Aa]nime\s*:', line):
            nom = re.sub(r'^[Aa]nime\s*:\s*', '', line).strip()
    return kod, nom


@bot.channel_post_handler(content_types=['video', 'photo', 'document', 'animation'])
def handle_channel_post(message):
    if message.chat.id != CHANNEL_ID:
        return

    caption = message.caption or ""
    kod, nom = parse_caption(caption)

    if not kod:
        print(f"⚠️ Kod topilmadi: {caption[:60]}")
        return

    file_id = None
    file_type = None

    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "animation"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"

    if file_id:
        post_cache[kod] = {
            "kod": kod,
            "nom": nom or "Nomsiz",
            "file_id": file_id,
            "file_type": file_type,
        }
        print(f"✅ Saqlandi → Kod:{kod} | Anime:{nom}")


def find_anime(query: str):
    query = query.strip()
    results = []
    for kod, data in post_cache.items():
        if query == kod:
            results.append(data)
            continue
        if data["nom"] and query.lower() in data["nom"].lower():
            results.append(data)
    return results


def send_anime(chat_id, data):
    caption = f"🎌 *{data['nom']}*\n📌 Kod: `{data['kod']}`"
    if data["file_type"] == "video":
        bot.send_video(chat_id, data["file_id"], caption=caption, parse_mode="Markdown")
    elif data["file_type"] == "animation":
        bot.send_animation(chat_id, data["file_id"], caption=caption, parse_mode="Markdown")
    elif data["file_type"] == "photo":
        bot.send_photo(chat_id, data["file_id"], caption=caption, parse_mode="Markdown")
    elif data["file_type"] == "document":
        bot.send_document(chat_id, data["file_id"], caption=caption, parse_mode="Markdown")


@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "🎌 *Anime Bot*\n\n"
        "Anime *kodi* yoki *nomini* yozing:\n\n"
        "Misol:\n"
        "`47` — kod bo'yicha\n"
        "`Naruto` — nom bo'yicha"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['count'])
def count_cache(message):
    bot.send_message(
        message.chat.id,
        f"📦 Bazada *{len(post_cache)}* ta anime bor.",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: True)
def handle_search(message):
    query = message.text.strip()
    if not query:
        return

    bot.send_chat_action(message.chat.id, "typing")
    results = find_anime(query)

    if not results:
        bot.send_message(
            message.chat.id,
            f"❌ *'{query}'* topilmadi.\n\nKod yoki nom to'g'ri ekanligini tekshiring.",
            parse_mode="Markdown"
        )
        return

    if len(results) == 1:
        send_anime(message.chat.id, results[0])
        return

    lines = [f"📋 *{len(results)} ta natija topildi:*\n"]
    for d in results[:10]:
        lines.append(f"• `{d['kod']}` — {d['nom']}")
    lines.append("\nAniqroq kod yozing.")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")


if __name__ == "__main__":
    print("🤖 Anime bot ishga tushdi...")
    print(f"📡 Kanal ID: {CHANNEL_ID}")
    bot.infinity_polling()
