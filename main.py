import logging

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.rules import rules_command
from src.moves import moves_handler
from src.truths import truths_handler
from src.challenge import challenge_handler
from src.oracle import oracle_command
from src.character import character_handler
from src.trackers import trackers_handler
from src.bonds import bonds_handler

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
        BotCommand("character", "Modify you character"),
        BotCommand("challenge", "Take action!"),
        BotCommand("oracle", "Ask the oracle"),
        BotCommand("trackers", "Set a tracker for later"),
        BotCommand("bonds", "To do"),
        BotCommand("rules", "Need a quick refresher?"),
        BotCommand("moves", "List and explanation of moves"),
        BotCommand("assets", "List and explanation of assets"),
        BotCommand("truths", "Explanation of the setting"),

    ]
    await app.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context

    await update.message.reply_text("Welcome to the Ironlands!")


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).post_init(set_bot_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rules", rules_command), group=1)
    application.add_handler(moves_handler, group=2)
    application.add_handler(truths_handler, group=3)
    application.add_handler(challenge_handler, group=4)
    application.add_handler(CommandHandler("oracle", oracle_command), group=5)
    application.add_handler(character_handler, group=6)
    application.add_handler(trackers_handler, group=7)
    application.add_handler(bonds_handler, group=8)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
