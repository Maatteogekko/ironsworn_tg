import os
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

from PIL import Image, ImageDraw, ImageFont
from src.utils import cancel, end_conversation, flip_page, split_text

async def create_map(image_path: str) -> str:

    img = Image.open(image_path)
    # Create a drawing object
    draw = ImageDraw.Draw(img)

    def font(size=30):
        try:
            return ImageFont.truetype("./data/Modesto Expanded.ttf", size)
        except IOError:
            return ImageFont.load_default(size)

    color = (45, 45, 45)


    with open("./data/map.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    for waypoint in data.keys():
        draw.text(data[waypoint]['coords'], waypoint, fill=color, font=font(20))
        draw.ellipse(
                [data[waypoint]['coords'][0], data[waypoint]['coords'][1], data[waypoint]['coords'][0] + 26, data[waypoint]['coords'][1] + 26], fill=color
            )


    # Save the modified image
    modified_image_path = "./data/modified_map.png"
    img.save(modified_image_path)

    return modified_image_path

# Define states
SHOWING_TRUTHS = 0

async def truths(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context

    keyboard = [
        [
            InlineKeyboardButton("The Old World", callback_data="old_world"),
            InlineKeyboardButton("Iron", callback_data="iron"),
        ],
        [
            InlineKeyboardButton("Legacies", callback_data="legacies"),
            InlineKeyboardButton("Communities", callback_data="communities"),
        ],
        [
            InlineKeyboardButton("Leaders", callback_data="leaders"),
            InlineKeyboardButton("Defense", callback_data="defense"),
        ],
        [
            InlineKeyboardButton("Mysticism", callback_data="mysticism"),
            InlineKeyboardButton("Religion", callback_data="religion"),
        ],
        [
            InlineKeyboardButton("Firstborn", callback_data="firstborn"),
            InlineKeyboardButton("Beasts", callback_data="beasts"),
        ],
        [
            InlineKeyboardButton("Horrors", callback_data="horrors"),
            InlineKeyboardButton("Map", callback_data="map"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message is None:
        # TODO Non so esattamente come fixarlo meglio; Quando premi indietro su callback o gli altri, dovresti tornare qui. Ma non c'è un messaggio, ergo l'if.
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Choose category", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Choose category", reply_markup=reply_markup)

    return SHOWING_TRUTHS


async def truths_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    # GESTISCE TUTTO QUI (WOW)

    # Page+-
    if query.data.startswith("page"):
        if context.user_data["truth"] in (
            "old_world",
            "iron",
            "legacies",
            "communities",
            "leaders",
            "defense",
            "mysticism",
            "religion",
            "firstborn",
            "beasts",
            "horrors",
        ):
            await flip_page(update, context, query.data)
        # TODO Sarchiapone e se non sto in quelle mosse ma in map?

    # Backs
    elif query.data == "back":
        return await truths(update, context)

    elif query.data == "back_to_map":
        return await truths_button_callback(update, context)

    # PARTE NON DI MAPPA: --------------------------------------------------------------------------

    if query.data in (
        "old_world",
        "iron",
        "legacies",
        "communities",
        "leaders",
        "defense",
        "mysticism",
        "religion",
        "firstborn",
        "beasts",
        "horrors",
    ):
        text = "Placeholder non map: " + str(query.data)
        if query.data == "old_world":
            text = (
                """
The savage clans called the Skulde invaded the kingdoms of the Old World. 
Our armies fell. Most were killed or taken into slavery. Those who escaped 
set sail aboard anything that would float. After an arduous months-long voyage, 
the survivors made landfall upon the Ironlands.
"""
                * 100
            )

        if len(text) < 4096:
            back_button = [[InlineKeyboardButton("Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(
                text=text, parse_mode="Markdown", reply_markup=reply_markup
            )
        else:
            context.user_data["page"] = 0
            context.user_data["truth"] = query.data
            parts = split_text(text)
            context.user_data["parts"] = parts
            keyboard = [
                [InlineKeyboardButton("Page +", callback_data="page+")],
                [InlineKeyboardButton("Back", callback_data="back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=parts[0], parse_mode="Markdown", reply_markup=reply_markup
            )

    # PARTE DI MAPPA: ------------------------------------------------------------------------------
    elif query.data == "map_1":
        text = """
BARRIER ISLANDS

Features:
• Crashing waves and treacherous currents
• Jagged rocks hidden just beneath the surface
• Snow-dappled cliffs jutting out of the sea
• Low clouds and curling mists
• Ferocious winds
• Gliding seabirds
• Decaying wrecks of wooden ships
• Fisher-folk braving the wild sea
• Lurking seaborne raiders

This long string of islands parallels the Ragged Coast. They are beautiful, but imposing. 
The slate-gray cliffs rise dramatically out of the water, topped by treeless moors. 
Waterfalls, fed by persistent rains, plunge over these cliffs into the raging sea. 
The winds are fierce and ever-present. In the winter, sleet, snow, and ocean mist can 
cut visibility to the length of one's arm. The islands are sparsely populated by Ironlanders, 
mostly fisher-folk who brave the surrounding waters. Their settlements cling to narrow, 
rock-strewn shores or lie on high overlooks. At night, the dim lights of their fires and 
torches glimmer pitifully against the wild, storm-tossed sea.
"""
        back_button = [[InlineKeyboardButton("Back", callback_data="back_to_map")]]
        reply_markup = InlineKeyboardMarkup(back_button)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    if query.data == "map":

        modified_image_path = create_map("./data/map.png")
        # Send the map image from local storage
        with open(os.path.join(modified_image_path), "rb") as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)

        map_keyboard = [
            [
                InlineKeyboardButton("1", callback_data="map_1"),
                InlineKeyboardButton("2", callback_data="map_2"),
                InlineKeyboardButton("3", callback_data="map_3"),
            ],
            [
                InlineKeyboardButton("4", callback_data="map_4"),
                InlineKeyboardButton("5", callback_data="map_5"),
                InlineKeyboardButton("6", callback_data="map_6"),
            ],
            [
                InlineKeyboardButton("7", callback_data="map_7"),
                InlineKeyboardButton("8", callback_data="map_8"),
                InlineKeyboardButton("9", callback_data="map_9"),
            ],
            [InlineKeyboardButton("Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(map_keyboard)
        await query.edit_message_text(text="Here's the map:", reply_markup=reply_markup)

    elif query.data.startswith("map_"):
        back_button = [[InlineKeyboardButton("Back", callback_data="back_to_map")]]
        reply_markup = InlineKeyboardMarkup(back_button)
        await query.edit_message_text(
            text=f"Information for map section {query.data[-1]}",
            reply_markup=reply_markup,
        )

    return SHOWING_TRUTHS


truths_handler = ConversationHandler(
    entry_points=[CommandHandler("truths", truths)],
    states={
        SHOWING_TRUTHS: [CallbackQueryHandler(truths_button_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
