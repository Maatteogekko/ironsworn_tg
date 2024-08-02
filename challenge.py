from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, MessageHandler, filters
from utils import *
import random

# Placeholder sticker IDs (replace with actual sticker IDs)
sticker_placeholder = "CAACAgQAAxkBAAEs7Vxmq-5f3Rk0lmeUDu3EsHD5tiYJiAACrxgAAmGbYVE_O0nLRdaoqDUE"

ACTION_DICE_STATE = 0

async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE,) -> None:
    # Generate two random numbers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    print(num1,num2)

    # Send stickers (placeholder stickers)
    await update.message.reply_sticker(sticker_placeholder)
    await update.message.reply_sticker(sticker_placeholder)

    # Create an inline keyboard button
    keyboard = [
        [InlineKeyboardButton("Lancia l'action dice", callback_data='action_dice_callback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline button
    await update.message.reply_text(
        f"I due challenge dice sono {num1} e {num2}",
        reply_markup=reply_markup
    )
    return ACTION_DICE_STATE

async def action_dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE,) -> None:
    query = update.callback_query
    await query.answer()

    # Generate a random number between 1 and 6
    action_number = random.randint(1, 6)

    # Send sticker (placeholder sticker)
    await query.message.reply_sticker(sticker_placeholder)

    # Send the message with the action number
    await query.message.reply_text(f"Il numero dell'action dice è {action_number}")

    return ConversationHandler.END

challenge_handler = ConversationHandler(
    entry_points=[CommandHandler('challenge', challenge)],
    states={
        ACTION_DICE_STATE: [CallbackQueryHandler(action_dice_callback)]
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry = True
)