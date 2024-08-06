import os
from telegram import Update
from telegram.ext import ContextTypes


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(os.path.join("./data/rules_summary.jpg"), "rb") as photo:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
