import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from moves  import get_moves_handler
from truths import get_truths_handler
import datetime

# Set your bot token here
TOKEN = "7260536676:AAEepM55V7Ud1PD2LF89MYQ5xGHjNtJZYZI"

# Dictionary to store message pairs (command_id, response_id)
message_pairs = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def set_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("moves", "Lista e spiegazione delle mosse"),
        BotCommand("assets", "Lista e spiegazione degli asset"),
        BotCommand("truths", "Spiegazione dell'ambientazione"),
        BotCommand("bonds", "Da fare"),
        BotCommand("oracle", "Chiedi all'oracolo"),
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("IronswornCompanion_bot lanciato.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).post_init(set_bot_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_moves_handler(), group = 2)
    application.add_handler(get_truths_handler(), group = 2)

    application.run_polling(allowed_updates=Update.ALL_TYPES)