from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import BotCommand, Update
from moves  import moves_handler
from truths import truths_handler
from challenge import challenge_handler
import logging
import datetime

TOKEN = None
with open("token.txt") as f:
    TOKEN = f.read().strip()

# Dictionary to store message pairs (command_id, response_id)
# message_pairs = {} #

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def set_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("challenge", "Passa all'azione!"),
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
    application.add_handler(moves_handler, group = 1)
    application.add_handler(truths_handler, group = 2)
    application.add_handler(challenge_handler, group = 3)

    # Add command handlers
    #application.add_handler(CommandHandler("moves", moves),group = 1)
    #application.add_handler(CallbackQueryHandler(moves_button_callback),group = 1)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)