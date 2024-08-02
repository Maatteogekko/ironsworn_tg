from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


def split_text(text, max_length=4096):
    """Split the text by lines."""

    lines = text.split("\n\n")
    parts = []
    current_part = ""

    for line in lines:
        # Check if the current line itself is longer than max_length
        if len(line) > max_length:
            # If so, split the line itself into smaller chunks
            while len(line) > max_length:
                parts.append(line[:max_length])
                line = line[max_length:]
            current_part += line + "\n\n"
        else:
            # Check if adding this line will exceed the max_length
            if len(current_part) + len(line) + 1 > max_length:
                # If it exceeds, add the current part to the parts list
                parts.append(current_part.strip())
                # Start a new part with the current line
                current_part = line + "\n\n"
            else:
                # Otherwise, add the line to the current part
                current_part += line + "\n\n"

    # Add the last part to the parts list
    if current_part:
        parts.append(current_part.strip())

    return parts


async def flip_page(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page: int, back="back"
):
    """Provide UI to navigate multiple pages."""

    query = update.callback_query
    await query.answer()

    parts = context.user_data["parts"]

    if query.data == "page+":
        context.user_data["page"] += 1
    else:
        context.user_data["page"] -= 1

    if context.user_data["page"] <= 0:
        context.user_data["page"] = 0
        keyboard = [
            [InlineKeyboardButton("Page +", callback_data="page+")],
            [InlineKeyboardButton("Back", callback_data=back)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=parts[context.user_data["page"]],
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    elif context.user_data["page"] >= len(parts) - 1:
        context.user_data["page"] = len(parts) - 1
        keyboard = [
            [InlineKeyboardButton("Page -", callback_data="page-")],
            [InlineKeyboardButton("Back", callback_data=back)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=parts[context.user_data["page"]],
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton("Page -", callback_data="page-"),
                InlineKeyboardButton("Page +", callback_data="page+"),
            ],
            [InlineKeyboardButton("Back", callback_data=back)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=parts[context.user_data["page"]],
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del update

    context.user_data.clear()
    return ConversationHandler.END


async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del update, context

    return ConversationHandler.END
