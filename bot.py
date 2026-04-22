# -*- coding: utf-8 -*-
import asyncio
import random
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

TOKEN = "8605122850:AAFbRNdIJP0E-WsD7hHTFnOuYm7C0saJ-wA"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_attacks = {}

def generate_progress_bar(percent: int, length: int = 20) -> str:
    filled = int(percent / 100 * length)
    return "█" * filled + "░" * (length - filled)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 НАЧАТЬ АТАКУ", callback_data="start_attack")],
        [InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="stats")],
        [InlineKeyboardButton("📢 НАШ КАНАЛ", url="https://t.me/Fant1kKanal")],
        [InlineKeyboardButton("❓ ПОМОЩЬ", callback_data="help")]
    ])
    await update.message.reply_text(
        "🔥 **DDOS TOOL v3.0** 🔥\n\n"
        "Мощный инструмент для нагрузги серверов.\n"
        "Выберите цель и количество потоков.\n\n"
        "⚠️ Используйте только на своих ресурсах!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

async def start_attack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "🎯 **ВВЕДИТЕ URL ЦЕЛИ**\n\n"
        "Пример: `https://example.com`\n"
        "Или `example.com`\n\n"
        "Отправьте ссылку одним сообщением.",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data["awaiting_url"] = True

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_url"):
        return
    url = update.message.text.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    context.user_data["target_url"] = url
    context.user_data["awaiting_url"] = False
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧵 50 потоков", callback_data="threads_50")],
        [InlineKeyboardButton("🧵 100 потоков", callback_data="threads_100")],
        [InlineKeyboardButton("🧵 250 потоков", callback_data="threads_250")],
        [InlineKeyboardButton("🧵 500 потоков", callback_data="threads_500")],
        [InlineKeyboardButton("🔙 НАЗАД", callback_data="cancel")]
    ])
    await update.message.reply_text(
        f"🎯 Цель: `{url}`\n\n"
        "Выберите количество потоков:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

async def threads_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    threads = int(query.data.split("_")[1])
    context.user_data["threads"] = threads
    url = context.user_data["target_url"]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 ЗАПУСТИТЬ АТАКУ", callback_data="run_attack")],
        [InlineKeyboardButton("🔙 НАЗАД", callback_data="back_to_url")]
    ])
    await query.message.edit_text(
        f"🎯 Цель: `{url}`\n"
        f"🧵 Потоков: {threads}\n\n"
        "✅ Готово к запуску. Нажмите кнопку ниже.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

async def run_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    url = context.user_data["target_url"]
    threads = context.user_data["threads"]
    
    active_attacks[user_id] = True
    message = await query.message.edit_text(f"🔥 ИНИЦИАЛИЗАЦИЯ АТАКИ НА {url} 🔥\n\n⚙️ Подготовка...")
    
    total_requests = 0
    total_success = 0
    total_errors = 0
    start_time = datetime.now()
    
    for step in range(1, 101):
        if not active_attacks.get(user_id, True):
            await message.edit_text(f"⏹ АТАКА ОСТАНОВЛЕНА\n📊 Всего запросов: {total_requests}\n✅ Успешно: {total_success}\n❌ Ошибок: {total_errors}")
            return
        
        batch = random.randint(100, 300)
        total_requests += batch
        success_rate = random.uniform(0.85, 0.95)
        success_batch = int(batch * success_rate)
        error_batch = batch - success_batch
        total_success += success_batch
        total_errors += error_batch
        
        elapsed = (datetime.now() - start_time).total_seconds()
        speed = int(total_requests / max(elapsed, 0.1))
        success_percent = int(total_success / max(total_requests, 1) * 100)
        progress = generate_progress_bar(step)
        
        text = f"🔥 **DDOS ATTACK IN PROGRESS** 🔥\n\n"
        text += f"🎯 Target: `{url}`\n"
        text += f"🧵 Threads: {threads}\n"
        text += f"📊 Progress: {progress} {step}%\n"
        text += f"📥 Total requests: `{total_requests:,}`\n"
        text += f"✅ Successful: `{total_success:,}`\n"
        text += f"❌ Errors: `{total_errors:,}`\n"
        text += f"📈 Success rate: `{success_percent}%`\n"
        text += f"⚡ Speed: `{speed:,}` req/sec\n"
        text += f"⏱️ Time elapsed: `{int(elapsed)}` sec\n\n"
        text += f"🟢 STATUS: **ATTACKING**\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🛑 Send /stop to abort"
        
        try:
            await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except:
            pass
        
        await asyncio.sleep(random.uniform(0.2, 0.5))
    
    elapsed = (datetime.now() - start_time).total_seconds()
    success_percent = int(total_success / max(total_requests, 1) * 100)
    avg_speed = int(total_requests / elapsed)
    text = f"✅ **ATTACK COMPLETED** ✅\n\n"
    text += f"🎯 Target: `{url}`\n"
    text += f"📥 Total requests: `{total_requests:,}`\n"
    text += f"✅ Successful: `{total_success:,}`\n"
    text += f"❌ Errors: `{total_errors:,}`\n"
    text += f"📈 Success rate: `{success_percent}%`\n"
    text += f"⚡ Average speed: `{avg_speed:,}` req/sec\n"
    text += f"⏱️ Duration: `{int(elapsed)}` sec\n\n"
    text += f"💢 TARGET MAY BE SLOWED DOWN 💢"
    
    await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    active_attacks.pop(user_id, None)

async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_attacks:
        active_attacks[user_id] = False
        await update.message.reply_text("⏹ Stopping attack...")
    else:
        await update.message.reply_text("No active attack.")

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "📊 **STATISTICS** 📊\n\n"
        "Total attacks executed: 0\n"
        "Total requests sent: 0\n"
        "This demo does not store persistent stats.\n\n"
        "Use /start to launch a new attack.",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "❓ **HELP**\n\n"
        "Commands:\n"
        "/start – Main menu\n"
        "/stop – Stop current attack\n\n"
        "How it works:\n"
        "This tool simulates a high-load attack.\n"
        "Use only on your own servers or with permission.\n\n"
        "⚠️ The developer is not responsible for misuse.",
        parse_mode=ParseMode.MARKDOWN
    )

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.edit_text("❌ Cancelled. Use /start to begin.")

async def back_to_url_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_url"] = True
    await query.message.edit_text(
        "🎯 **ENTER TARGET URL**\n\n"
        "Example: `https://example.com`\n"
        "Send the link as a message.",
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_attack))
    app.add_handler(CallbackQueryHandler(start_attack_callback, pattern="^start_attack$"))
    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(threads_choice, pattern="^threads_"))
    app.add_handler(CallbackQueryHandler(run_attack, pattern="^run_attack$"))
    app.add_handler(CallbackQueryHandler(cancel_callback, pattern="^cancel$"))
    app.add_handler(CallbackQueryHandler(back_to_url_callback, pattern="^back_to_url$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    logger.info("🔥 DDOS VISUAL SIMULATOR БОТ ЗАПУЩЕН")
    app.run_polling()

if __name__ == "__main__":
    main()
