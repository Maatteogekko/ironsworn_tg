import json

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


async def update_bonds(task, new=None) -> str:
    with open("./data/bonds.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if task.startswith("remove_bond_"):
        task_ = task.split("_")
        data.pop(task_[-1])
    if task == "add_bond_name":
        new = new.replace("_", "-")
        data[new] = {
            "description": None,
        }
    if task == "add_bond_description":
        data[new[0].replace("_", "-")]["description"] = new[1]
    with open("./data/bonds.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


async def create_bonds() -> str:

    # Open the character data
    with open("./data/bonds.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    text = "Bonds list:\n\n"
    for bond in data.keys():
        text += f"*{bond}*\n"
        text += f"{data[bond]['description']}\n\n"

    return text


def get_bonds_keyboard():
    keyboard = [
        [InlineKeyboardButton("Remove Bond", callback_data="show_remove_bonds")],
        [InlineKeyboardButton("Add Bond", callback_data="add_bond")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_remove_bonds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = "Select the bond to remove:"
    keyboard = get_remove_bonds_keyboard()
    await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return SHOWING_REMOVE_BONDS


def get_remove_bonds_keyboard():
    with open("./data/bonds.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    keyboard = []
    for bond in data.keys():
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Remove " + bond, callback_data="remove_bond_" + bond
                )
            ]
        )
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)


async def bonds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    text = await create_bonds()

    # Send the message with the image and keyboard
    message = await update.message.reply_text(
        text=text,
        reply_markup=get_bonds_keyboard(),
        parse_mode="Markdown",
    )

    # Store the message IDs for later deletion
    context.user_data["bot_message_id"] = message.message_id

    return SHOWING_BONDS

    # PASSAGGI PER UPDATE DELL'IMMAGINE
    # Call update_sheet function
    # updated_image_path = await update_sheet(query.data)

    # Create updated sheet
    # modified_image_path = await create_sheet(updated_image_path)
    # await query.edit_message_media(
    # media=InputMediaPhoto(open(modified_image_path, 'rb'), caption="Ironsworn options"),
    # reply_markup=get_ironsworn_keyboard()
    # )


async def bonds_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("remove_bond_"):
        await update_bonds(query.data)
        text = await create_bonds()
        await query.message.edit_text(
            text=text,
            reply_markup=get_bonds_keyboard(),
            parse_mode="Markdown",
        )
        return SHOWING_BONDS
    elif query.data == "show_remove_bonds":
        return await show_remove_bonds(update, context)
    elif query.data == "back_to_main":
        text = "Select an option:"
        await query.message.edit_text(
            text=text,
            reply_markup=get_bonds_keyboard(),
            parse_mode="Markdown",
        )
        return SHOWING_BONDS
    elif query.data == "add_bond":
        await query.message.reply_text("Send me the name of the new bond:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_NEW_BOND_NAME
    else:
        await query.edit_message_caption(
            "Yeah we won't implement that", reply_markup=get_bonds_keyboard()
        )

    return SHOWING_REMOVE_BONDS


async def handle_new_bond_name_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text
    await update_bonds("add_bond_name", name)

    await update.message.reply_text("Select the new bond description")
    context.user_data["new_bond"] = name
    return WAITING_NEW_BOND_DESCRIPTION


async def handle_new_bond_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = context.user_data["new_bond"]

    description = update.message.text
    await update_bonds("add_bond_description", (name, description))

    text = await create_bonds()

    # Send the message with the image and keyboard
    await update.message.reply_text(
        text=text,
        reply_markup=get_bonds_keyboard(),
        parse_mode="Markdown",
    )

    return SHOWING_BONDS


SHOWING_BONDS = 0
WAITING_NEW_BOND_NAME = 1
WAITING_NEW_BOND_DESCRIPTION = 2
SHOWING_REMOVE_BONDS = 3

bonds_handler = ConversationHandler(
    entry_points=[
        CommandHandler("bonds", bonds),
    ],
    states={
        SHOWING_BONDS: [CallbackQueryHandler(bonds_button_callback)],
        WAITING_NEW_BOND_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_bond_name_input)
        ],
        WAITING_NEW_BOND_DESCRIPTION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_new_bond_description_input
            )
        ],
        SHOWING_REMOVE_BONDS: [CallbackQueryHandler(bonds_button_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
