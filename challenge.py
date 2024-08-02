import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, MessageHandler, filters


# Placeholder sticker IDs (replace with actual sticker IDs)
sticker_placeholder = "CAADAgADQAADyIsGAAE7MpzFPFQX5QI"

ACTION_DICE = 0

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    return ConversationHandler.END

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #context.user_data.clear()
    return ConversationHandler.END

def get_truths_handler():
    """Create and return the truths command handler."""
    return ConversationHandler(
        entry_points=[CommandHandler('challenge', challenge)],
        states={
            ACTION_DICE: [CallbackQueryHandler(action_dice)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
        allow_reentry = True
    )

def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE,) -> None:
    # Generate two random numbers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    # Send stickers (placeholder stickers)
    update.message.reply_sticker(sticker_placeholder)
    update.message.reply_sticker(sticker_placeholder)

    # Create an inline keyboard button
    keyboard = [
        [InlineKeyboardButton("Lancia l'action dice", callback_data='action_dice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline button
    update.message.reply_text(
        f"I due challenge dices sono {num1} e {num2}",
        reply_markup=reply_markup
    )
    return ACTION_DICE

def action_dice(update: Update, context: ContextTypes.DEFAULT_TYPE,) -> None:
    query = update.callback_query
    query.answer()

    # Generate a random number between 1 and 6
    action_number = random.randint(1, 6)

    # Send sticker (placeholder sticker)
    query.message.reply_sticker(sticker_placeholder)

    # Send the message with the action number
    query.message.reply_text(f"Il numero dell'action dice è {action_number}")

    return ConversationHandler.End