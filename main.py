import logging

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.moves import moves_handler
from src.truths import truths_handler
from src.challenge import challenge_handler

TOKEN = None
with open("./data/token.txt", encoding="utf-8") as f:
    TOKEN = f.read().strip()

# Dictionary to store message pairs (command_id, response_id)
# message_pairs = {} ##

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def set_bot_commands(app: Application) -> None:
    commands = [
        BotCommand("challenge", "Passa all'azione!"),
        BotCommand("moves", "Lista e spiegazione delle mosse"),
        BotCommand("assets", "Lista e spiegazione degli asset"),
        BotCommand("truths", "Spiegazione dell'ambientazione"),
        BotCommand("bonds", "Da fare"),
        BotCommand("oracle", "Chiedi all'oracolo"),
    ]
    await app.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context

    await update.message.reply_text("IronswornCompanion_bot lanciato.")


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).post_init(set_bot_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(moves_handler, group=1)
    application.add_handler(truths_handler, group=2)
    application.add_handler(challenge_handler, group=3)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
