import json
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.utils import cancel, end_conversation

ACTION_DICE_STATE = 0


async def challenge(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    # Generate two random numbers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    # Send stickers (placeholder stickers)
    with open("./data/d10_sticker_id.json", "r", encoding="utf-8") as file:
        d10_sticker_id = json.load(file)
    await update.message.reply_sticker(d10_sticker_id[str(num1)])
    await update.message.reply_sticker(d10_sticker_id[str(num2)])

    context.user_data["num1"] = num1
    context.user_data["num2"] = num1

    # Create an inline keyboard button
    keyboard = [
        [
            InlineKeyboardButton(
                "Roll the action dice", callback_data="action_dice_callback"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline button
    await update.message.reply_text(
        f"Your challenge dice are {num1} & {num2}", reply_markup=reply_markup
    )
    return ACTION_DICE_STATE


async def action_dice_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    query = update.callback_query
    await query.answer()
    await query.message.edit_text("Rolling action dice!")
    # Generate a random number between 1 and 6
    action_number = random.randint(1, 6)

    # Send sticker (placeholder sticker)
    with open("./data/d6_sticker_id.json", "r", encoding="utf-8") as file:
        d6_sticker_id = json.load(file)
    await query.message.reply_sticker(d6_sticker_id[str(action_number)])

    # Send the message with the action number
    await query.message.reply_text(f"It came out {action_number}")

    return ConversationHandler.END


challenge_handler = ConversationHandler(
    entry_points=[CommandHandler("challenge", challenge)],
    states={
        ACTION_DICE_STATE: [CallbackQueryHandler(action_dice_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
