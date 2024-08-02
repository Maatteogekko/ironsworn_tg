from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from src.utils import *
import random
import json

ACTION_DICE_STATE = 0


async def challenge(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Generate two random numbers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    # Send stickers (placeholder stickers)
    with open('./data/d8_sticker_id.json', 'r') as file:
        d8_sticker_id = json.load(file)
    await update.message.reply_sticker(d8_sticker_id[str(num1)])
    await update.message.reply_sticker(d8_sticker_id[str(num2)])
    
    context.user_data['num1'] = num1
    context.user_data['num2'] = num1

    # Create an inline keyboard button
    keyboard = [
        [
            InlineKeyboardButton(
                "Lancia l'action dice", callback_data="action_dice_callback"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline button
    await update.message.reply_text(
        f"I due challenge dice sono {num1} e {num2}", reply_markup=reply_markup
    )
    return ACTION_DICE_STATE


async def action_dice_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(f"Action dice lanciato!")
    # Generate a random number between 1 and 6
    action_number = random.randint(1, 6)

    # Send sticker (placeholder sticker)
    with open('./data/d8_sticker_id.json', 'r') as file:
        d6_sticker_id = json.load(file)
    await query.message.reply_sticker(d6_sticker_id[str(action_number)])

    # Send the message with the action number
    await query.message.reply_text(f"È uscito {action_number}")

    return ConversationHandler.END
    


challenge_handler = ConversationHandler(
    entry_points=[CommandHandler("challenge", challenge)],
    states={ACTION_DICE_STATE: [CallbackQueryHandler(action_dice_callback)]},
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
