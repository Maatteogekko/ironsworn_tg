import json
import math

from PIL import Image, ImageDraw, ImageFont
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.utils import cancel, end_conversation

# TODO:
# Assets


# Define conversation states
SHOWING_CHARACTER = 0


async def update_sheet(task, new, chat_id) -> str:
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if task == "changing_name":
        data[chat_id]["name"] = new
    if task == "changing_stats":
        data[chat_id]["stats"] = new
    if task == "exp_minus":
        data[chat_id]["experience"]["gained"] -= 1
    if task == "exp_plus":
        data[chat_id]["experience"]["gained"] += 1
    if task == "spend_minus":
        data[chat_id]["experience"]["used"] -= 1
    if task == "spend_plus":
        data[chat_id]["experience"]["used"] += 1
    if task == "health_plus":
        data[chat_id]["state"]["health"] += 1
    if task == "health_minus":
        data[chat_id]["state"]["health"] -= 1
    if task == "spirit_plus":
        data[chat_id]["state"]["spirit"] += 1
    if task == "spirit_minus":
        data[chat_id]["state"]["spirit"] -= 1
    if task == "supply_plus":
        data[chat_id]["state"]["supply"] += 1
    if task == "supply_minus":
        data[chat_id]["state"]["supply"] -= 1
    if task == "momentum_plus":
        data[chat_id]["momentum"]["current"] += 1
    if task == "momentum_minus":
        data[chat_id]["momentum"]["current"] -= 1
    if task in [
        "wounded",
        "shaken",
        "unprepared",
        "encumbered",
        "maimed",
        "corrupted",
        "cursed",
        "tormented",
    ]:
        data[chat_id]["condition"][task] = int(not data[chat_id]["condition"][task])
    if task == "bonds+":
        data[chat_id]["bonds"] += 1
    if task == "bonds-":
        data[chat_id]["bonds"] -= 1
    if task.startswith("vow"):
        vows = list(data[chat_id]["vows"].keys())
        task_ = task.split("_")
        offset = {
            "troublesome": 12,
            "dangerous": 8,
            "formidable": 4,
            "extreme": 2,
            "epic": 1,
        }
        if task_[1] == "plus":
            data[chat_id]["vows"][vows[int(task_[0][-1])]]["tracker"] += offset[
                data[chat_id]["vows"][vows[int(task_[0][-1])]]["difficulty"]
            ]
        if task_[1] == "minus":
            data[chat_id]["vows"][vows[int(task_[0][-1])]]["tracker"] -= 1
    if task == "add_vow_name":
        data[chat_id]["vows"][new] = {
            "difficulty": None,
            "tracker": 0,
            "description": None,
        }
    if task == "add_vow_difficulty":
        data[chat_id]["vows"][new[0]]["difficulty"] = new[1].split("_")[-1]
    if task == "add_vow_description":
        data[chat_id]["vows"][new[0]]["description"] = new[1]
    if task.startswith("cancel_vow"):
        task_ = task.split("_")
        data[chat_id]["vows"].pop(task_[-1])
    with open("./data/character.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    if task == "changing_momentum_max":
        data[chat_id]["momentum"]["max"]
    if task == "changing_momentum_reset":
        data[chat_id]["momentum"]["reset"]

    return "./data/Ironsworn_sheet.png"


async def create_sheet(chat_id, image_path: str) -> str:

    # Open the character data
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data[chat_id]
    # Open the image
    img = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    def font(size=30):
        try:
            return ImageFont.truetype("./data/Modesto Expanded.ttf", size)
        except IOError:
            return ImageFont.load_default(size)

    color = (45, 45, 45)

    # Insert the name
    draw.text((140, 120), data["name"], fill=color, font=font(50))

    # Insert the Stats
    x = 349
    dx = 237
    draw.text((x, 240), str(data["stats"]["edge"]), fill=color, font=font(80))
    draw.text((x + dx, 240), str(data["stats"]["heart"]), fill=color, font=font(80))
    draw.text((x + 2 * dx, 240), str(data["stats"]["iron"]), fill=color, font=font(80))
    draw.text(
        (x + 3 * dx, 240), str(data["stats"]["shadow"]), fill=color, font=font(80)
    )
    draw.text((x + 4 * dx, 240), str(data["stats"]["wits"]), fill=color, font=font(80))

    # Insert Exp
    dots = data["experience"]["used"]
    xs = data["experience"]["gained"]
    positions_x = [1088.5 + _ * 36.48 for _ in range(15)]
    positions_y = [117, 154]
    for i, y in enumerate(positions_y):
        for j, x in enumerate(positions_x):
            if (j + i * 15) < dots:
                draw.ellipse([x, y, x + 26, y + 26], fill=color)
            elif (j + i * 15) < xs:
                draw.line([(x, y), (x + 26, y + 26)], fill=color, width=5)
                draw.line([(x, y + 26), (x + 26, y)], fill=color, width=5)

    # Insert Momentum
    maximum = data["momentum"]["max"]
    if len(str(maximum)) == 1:
        draw.text((134, 1875), str(maximum), fill=color, font=font(40))
    else:
        draw.text((120, 1875), str(maximum), fill=color, font=font(40))
    reset = data["momentum"]["reset"]
    if len(str(reset)) == 1:
        draw.text((134, 1998), str(reset), fill=color, font=font(40))
    else:
        draw.text((120, 1998), str(reset), fill=color, font=font(40))
    current = data["momentum"]["current"]
    c_c_x = 147.9
    c_c_y = 1214 - current * 94.5 - (0.5 * current if current < 0 else 0)
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=color, width=10)

    # Insert Health
    health = data["state"]["health"]
    c_c_x = 1552
    c_c_y = 785.5 - health * 94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=color, width=10)

    # Insert Spirit
    spirit = data["state"]["spirit"]
    c_c_x = 1552
    c_c_y = 1398.5 - spirit * 94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=color, width=10)

    # Insert Supply
    supply = data["state"]["supply"]
    c_c_x = 1552
    c_c_y = 2011.5 - supply * 94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=color, width=10)

    # Insert Bonds
    bonds = data["bonds"]
    c_y = 574.8
    s_y = 500
    for i in range(int(bonds / 4)):
        for l in ticks([c_y, s_y], 4):
            draw.line(
                l,
                fill=color,
                width=7,
            )
        c_y = c_y + 61.3
    for l in ticks([c_y, s_y], bonds % 4):
        draw.line(
            l,
            fill=color,
            width=7,
        )

    # Insert vows
    cn = [290, 635]
    vows = data["vows"]
    diff_offset = {
        "troublesome": 85,
        "dangerous": 335,
        "formidable": 550,
        "extreme": 770,
        "epic": 949,
    }
    for i, vow in enumerate(vows.keys()):
        draw.text((cn[0], cn[1]), str(vow), fill=color, font=font(40))
        x = cn[0] + diff_offset[vows[vow]["difficulty"]]
        y = cn[1] + 59
        draw.ellipse([x, y, x + 26, y + 26], fill=color)
        c_y = cn[0] + 284.8
        s_y = cn[1] + 128
        for i in range(int(vows[vow]["tracker"] / 4)):
            for l in ticks([c_y, s_y], 4):
                draw.line(
                    l,
                    fill=color,
                    width=7,
                )
            c_y = c_y + 61.3
        for l in ticks([c_y, s_y], vows[vow]["tracker"] % 4):
            draw.line(
                l,
                fill=color,
                width=7,
            )
        cn[1] += 195

    # Insert Conditions
    conditions = [
        "wounded",
        "shaken",
        "unprepared",
        "encumbered",
        "maimed",
        "corrupted",
        "cursed",
        "tormented",
    ]
    pos = [
        [270, 1720],
        [571, 1720],
        [270, 1764],
        [571, 1764],
        [955, 1720],
        [1205, 1720],
        [957, 1825],
        [1205, 1825],
    ]
    for i, cond in enumerate(conditions):
        if data["condition"][cond]:
            draw.ellipse(
                [pos[i][0], pos[i][1], pos[i][0] + 26, pos[i][1] + 26], fill=color
            )

    # Save the modified image
    modified_image_path = "./data/" + data["name"] + "_character_sheet.png"
    img.save(modified_image_path)

    return modified_image_path


def ticks(center, ticks):
    lines = []
    if ticks >= 1:
        lines.append(
            [(center[0] - 19, center[1] - 19), (center[0] + 19, center[1] + 19)]
        )
    if ticks >= 2:
        lines.append(
            [(center[0] + 19, center[1] - 19), (center[0] - 19, center[1] + 19)]
        )
    if ticks >= 3:
        lines.append([(center[0] - 22, center[1]), (center[0] + 22, center[1])])
    if ticks >= 4:
        lines.append([(center[0], center[1] - 22), (center[0], center[1] + 22)])

    return lines


def create_collage(
    image_names, output_filename="./collage.jpg", thumbnail_size=(300, 410), spacing=5
):
    # Open all images and resize them
    images = [
        Image.open(name).resize(thumbnail_size, Image.Resampling.LANCZOS)
        for name in image_names
    ]

    # Calculate the number of rows and columns
    num_images = len(images)
    cols = 3
    rows = math.ceil(num_images / cols)

    # Create a new image with the appropriate size
    collage_width = cols * thumbnail_size[0] + (cols + 1) * spacing
    collage_height = rows * thumbnail_size[1] + (rows + 1) * spacing
    collage = Image.new("RGB", (collage_width, collage_height), color="white")

    # Paste the images into the collage
    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        x = spacing + col * (thumbnail_size[0] + spacing)
        y = spacing + row * (thumbnail_size[1] + spacing)
        collage.paste(img, (x, y))

    # Save the collage
    collage.save(output_filename)

    return output_filename


def generate_vow_text(update: Update):
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)[str(update.effective_user.id)]
    text = ""
    for vow in data["vows"].keys():
        text += f"*{vow}*\n"
        text += data["vows"][vow]["description"] + "\n"
    return text


def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Momentum➖", callback_data="momentum_minus"),
            InlineKeyboardButton("Momentum➕", callback_data="momentum_plus"),
        ],
        [
            InlineKeyboardButton("Health➖", callback_data="health_minus"),
            InlineKeyboardButton("Health➕", callback_data="health_plus"),
        ],
        [
            InlineKeyboardButton("Spirit➖", callback_data="spirit_minus"),
            InlineKeyboardButton("Spirit➕", callback_data="spirit_plus"),
        ],
        [
            InlineKeyboardButton("Supply➖", callback_data="supply_minus"),
            InlineKeyboardButton("Supply➕", callback_data="supply_plus"),
        ],
        [InlineKeyboardButton("Ironsworn", callback_data="ironsworn")],
        [InlineKeyboardButton("Momentum", callback_data="momentum")],
        [InlineKeyboardButton("State", callback_data="state")],
        [InlineKeyboardButton("Character", callback_data="character")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_ironsworn_keyboard():
    keyboard = [
        [InlineKeyboardButton("Vows", callback_data="vows")],
        [
            InlineKeyboardButton("Bonds ➖", callback_data="bonds-"),
            InlineKeyboardButton("Bonds ➕", callback_data="bonds+"),
        ],
        [InlineKeyboardButton("Assets", callback_data="assets")],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_momentum_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Max Momentum", callback_data="max_momentum"),
            InlineKeyboardButton("Momentum Reset", callback_data="momentum_reset"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_state_keyboard():
    keyboard = [
        [InlineKeyboardButton("Conditions", callback_data="conditions")],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_condition_keyboard(update: Update):
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)[str(update.effective_user.id)]
    p = ["❌" if data["condition"][k] == 0 else "✔️" for k in data["condition"].keys()]
    keyboard = [
        [
            InlineKeyboardButton("Wounded" + p[0], callback_data="wounded"),
            InlineKeyboardButton("Shaken" + p[1], callback_data="shaken"),
        ],
        [
            InlineKeyboardButton("Unprepared" + p[2], callback_data="unprepared"),
            InlineKeyboardButton("Encumbered" + p[3], callback_data="encumbered"),
        ],
        [
            InlineKeyboardButton("Maimed" + p[4], callback_data="maimed"),
            InlineKeyboardButton("Corrupted" + p[5], callback_data="corrupted"),
        ],
        [
            InlineKeyboardButton("Cursed" + p[6], callback_data="cursed"),
            InlineKeyboardButton("Tormented" + p[7], callback_data="tormented"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_to_state")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_vows_keyboard(update: Update):
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)[str(update.effective_user.id)]
    keyboard = []
    for i, vow in enumerate(data["vows"].keys()):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "➖ " + vow, callback_data="vow" + str(i) + "_minus"
                ),
                InlineKeyboardButton(
                    "➕ " + vow, callback_data="vow" + str(i) + "_plus"
                ),
            ]
        )
    keyboard.append([InlineKeyboardButton("Add Vow", callback_data="add_vow")])
    keyboard.append([InlineKeyboardButton("Cancel Vow", callback_data="cancel_vow")])
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_ironsworn")])

    return InlineKeyboardMarkup(keyboard)


def get_cancel_vows_keyboard(update: Update):
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)[str(update.effective_user.id)]
    keyboard = []
    for _, vow in enumerate(data["vows"].keys()):
        keyboard.append([InlineKeyboardButton(vow, callback_data="cancel_vow_" + vow)])
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_vows")])

    return InlineKeyboardMarkup(keyboard)


def get_character_keyboard():
    keyboard = [
        [InlineKeyboardButton("Character Name", callback_data="character_name")],
        [InlineKeyboardButton("Character Stats", callback_data="character_stats")],
        [InlineKeyboardButton("Character Exp", callback_data="character_exp")],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_asset_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Asset", callback_data="add_asset")],
        [InlineKeyboardButton("Upgrade Asset", callback_data="upgrade_asset")],
        [InlineKeyboardButton("Back", callback_data="back_to_ironsworn_via_asset")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_exp_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Exp -", callback_data="exp_minus"),
            InlineKeyboardButton("Exp +", callback_data="exp_plus"),
        ],
        [
            InlineKeyboardButton("Spend -", callback_data="spend_minus"),
            InlineKeyboardButton("Spend +", callback_data="spend_plus"),
        ],
        [InlineKeyboardButton("Back", callback_data="back_to_character")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Create the character sheet
    chat_id = str(update.effective_user.id)
    try:
        with open("./data/character.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        image_path = "./data/" + data[chat_id]["name"] + "_character_sheet.png"
    except:
        image_path = "./data/Ironsworn_sheet.png"

    # Send the message with the image and keyboard
    message = await update.message.reply_photo(
        photo=open(image_path, "rb"),
        caption="Here's your character sheet",
        reply_markup=get_main_keyboard(),
    )

    # Store the message IDs for later deletion
    context.user_data["bot_message_id"] = message.message_id

    return SHOWING_CHARACTER

    # PASSAGGI PER UPDATE DELL'IMMAGINE
    # Call update_sheet function
    # updated_image_path = await update_sheet(query.data)

    # Create updated sheet
    # modified_image_path = await create_sheet(updated_image_path)
    # await query.edit_message_media(
    # media=InputMediaPhoto(open(modified_image_path, 'rb'), caption="Ironsworn options"),
    # reply_markup=get_ironsworn_keyboard()
    # )


async def character_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "ironsworn":
        await query.edit_message_caption(
            "Manage your Ironsworn soul", reply_markup=get_ironsworn_keyboard()
        )
    elif query.data == "momentum":
        await query.edit_message_caption(
            "Set momentum reset and ma.", reply_markup=get_momentum_keyboard()
        )
    elif query.data == "state":
        await query.edit_message_caption(
            "Change the conditions of your character", reply_markup=get_state_keyboard()
        )
    elif query.data == "character":
        await query.edit_message_caption(
            "Character options", reply_markup=get_character_keyboard()
        )
    elif query.data == "vows":
        await query.edit_message_caption(
            generate_vow_text(update),
            parse_mode="Markdown",
            reply_markup=get_vows_keyboard(update),
        )
    elif query.data == "back_to_main":
        await query.edit_message_caption("Main menu", reply_markup=get_main_keyboard())
    elif query.data == "back_to_ironsworn":
        await query.edit_message_caption(
            "Ironsworn menu", reply_markup=get_ironsworn_keyboard()
        )
    elif query.data == "back_to_ironsworn_via_asset":
        chat_id = str(update.effective_user.id)
        try:
            with open("./data/character.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            modified_image_path = (
                "./data/" + data[chat_id]["name"] + "_character_sheet.png"
            )
        except:
            image_path = "./data/Ironsworn_sheet.png"
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Ironsworn menu"
            ),
            reply_markup=get_ironsworn_keyboard(),
        )
    elif query.data == "back_to_character":
        await query.edit_message_caption(
            "Character options", reply_markup=get_character_keyboard()
        )
    elif query.data == "back_to_state":
        await query.edit_message_caption(
            "State options", reply_markup=get_state_keyboard()
        )
    elif query.data == "back_to_vows":
        await query.edit_message_caption(
            "Vows options", reply_markup=get_vows_keyboard(update)
        )
    elif query.data == "character_name":
        await query.message.reply_text("Send me the name of the character:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_NAME
    elif query.data == "add_vow":
        await query.message.reply_text("Send me the name of the new vow:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_NEW_VOW_NAME
    elif query.data == "cancel_vow":
        await query.edit_message_caption(
            "Vow cancel", reply_markup=get_cancel_vows_keyboard(update)
        )
    elif query.data == "max_momentum":
        await query.message.reply_text("Send me the new max momentum value:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_MOMENTUM_MAX
    elif query.data == "momentum_reset":
        await query.message.reply_text("Send me the new momentum reset value:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_MOMENTUM_RESET
    elif query.data == "character_stats":
        await query.message.reply_text(
            "Send me the character stats in the format: Edge,Heart,Iron,Shadow,Wits"
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_STATS
    elif query.data == "character_exp":
        await query.edit_message_caption(
            "Experience options", reply_markup=get_exp_keyboard()
        )
    elif query.data == "conditions":
        await query.edit_message_caption(
            "Condition options", reply_markup=get_condition_keyboard(update)
        )
    elif query.data in [
        "health_plus",
        "health_minus",
        "spirit_plus",
        "spirit_minus",
        "supply_plus",
        "supply_minus",
    ]:
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="State updated"
            ),
            reply_markup=get_character_keyboard(),
        )

    elif query.data in ["momentum_plus", "momentum_minus"]:
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="momentum updated"
            ),
            reply_markup=get_character_keyboard(),
        )

    elif query.data in ["bonds+", "bonds-"]:
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Bond updated"
            ),
            reply_markup=get_ironsworn_keyboard(),
        )
    elif query.data.startswith("vow") and query.data != "vows":
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"),
                caption=generate_vow_text(update),
                parse_mode="Markdown",
            ),
            reply_markup=get_vows_keyboard(update),
        )
    elif query.data.startswith("cancel_vow"):
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Vow cancelled"
            ),
            reply_markup=get_vows_keyboard(update),
        )
    elif query.data == "assets":
        with open("./data/character.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        # Refresh the character sheet image
        assets = data[str(update.effective_user.id)]["assets"]
        modified_image_path = create_collage(
            ["./data/assets/" + a.lower() + ".png" for a in assets],
            output_filename="./data/"
            + data[str(update.effective_user.id)]["name"]
            + ".jpg",
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Assets showed"
            ),
            reply_markup=get_asset_keyboard(),
        )

    elif query.data in ["exp_minus", "exp_plus", "spend_minus", "spend_plus"]:
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Experience updated"
            ),
            reply_markup=get_exp_keyboard(),
        )
    elif query.data in [
        "wounded",
        "shaken",
        "unprepared",
        "encumbered",
        "maimed",
        "corrupted",
        "cursed",
        "tormented",
    ]:
        await update_sheet(query.data, "", str(update.effective_user.id))
        # Refresh the character sheet image
        image_path = "./data/Ironsworn_sheet.png"
        modified_image_path = await create_sheet(
            str(update.effective_user.id), image_path
        )
        await query.message.edit_media(
            media=InputMediaPhoto(
                open(modified_image_path, "rb"), caption="Condition updated"
            ),
            reply_markup=get_condition_keyboard(update),
        )
    else:
        await query.edit_message_caption(
            "Yeah we won't implement that", reply_markup=get_main_keyboard()
        )

    return SHOWING_CHARACTER


async def handle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context

    name = update.message.text
    await update_sheet("changing_name", name, str(update.effective_user.id))

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await update.message.reply_photo(
        photo=open(modified_image_path, "rb"),
        caption="Character name updated",
        reply_markup=get_character_keyboard(),
    )
    return SHOWING_CHARACTER


async def handle_new_vow_name_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text
    await update_sheet("add_vow_name", name, str(update.effective_user.id))

    keyboard = [
        [
            InlineKeyboardButton(
                "Troublesome", callback_data="new_vow_difficulty_troublesome"
            )
        ],
        [
            InlineKeyboardButton(
                "Dangerous", callback_data="new_vow_difficulty_dangerous"
            )
        ],
        [
            InlineKeyboardButton(
                "Formidable", callback_data="new_vow_difficulty_formidable"
            )
        ],
        [InlineKeyboardButton("Extreme", callback_data="new_vow_difficulty_extreme")],
        [InlineKeyboardButton("Epic", callback_data="new_vow_difficulty_epic")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select the new vow difficulty", reply_markup=reply_markup
    )
    context.user_data["new_vow"] = name
    return WAITING_NEW_VOW_DIFFICULTY


async def handle_new_vow_difficulty_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = context.user_data["new_vow"]
    query = update.callback_query
    await query.answer()
    await update_sheet(
        "add_vow_difficulty", (name, query.data), str(update.effective_user.id)
    )

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await query.message.reply_text(
        text="Please tell me a brief description of the vow:"
    )
    return WAITING_NEW_VOW_DESCRIPTION


async def handle_new_vow_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = context.user_data["new_vow"]
    del context

    desc = update.message.text
    await update_sheet(
        "add_vow_description", (name, desc), str(update.effective_user.id)
    )

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await update.message.reply_photo(
        photo=open(modified_image_path, "rb"),
        caption="Vows updated",
        reply_markup=get_vows_keyboard(update),
    )
    return SHOWING_CHARACTER


async def handle_momentum_max_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    del context

    momentum_max = update.message.text
    await update_sheet(
        "changing_momentum_max", momentum_max, str(update.effective_user.id)
    )

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await update.message.reply_photo(
        photo=open(modified_image_path, "rb"),
        caption="Max momentum updated",
        reply_markup=get_momentum_keyboard(),
    )
    return SHOWING_CHARACTER


async def handle_momentum_reset_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    del context

    momentum_reset = update.message.text
    await update_sheet(
        "changing_momentum_reset", momentum_reset, str(update.effective_user.id)
    )

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await update.message.reply_photo(
        photo=open(modified_image_path, "rb"),
        caption="Momentum Reset updated",
        reply_markup=get_momentum_keyboard(),
    )
    return SHOWING_CHARACTER


async def handle_stats_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    del context

    stats = str(update.message.text)
    stats = stats.replace(" ", "")
    stats = stats.replace(",", "")
    stats = stats.replace("/n", "")
    if len(stats) != 5:
        await update.message.reply_text(
            "Invalid format. Please send stats in the format: Edge, Heart, Iron, Shadow, Wits"
        )
        return WAITING_STATS

    stats_dict = {
        "edge": int(stats[0]),
        "heart": int(stats[1]),
        "iron": int(stats[2]),
        "shadow": int(stats[3]),
        "wits": int(stats[4]),
    }

    await update_sheet("changing_stats", stats_dict, str(update.effective_user.id))

    # Refresh the character sheet image
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(str(update.effective_user.id), image_path)

    await update.message.reply_photo(
        photo=open(modified_image_path, "rb"),
        caption="Character stats updated",
        reply_markup=get_character_keyboard(),
    )
    return SHOWING_CHARACTER


# Define new states
WAITING_NAME = 1
WAITING_STATS = 2
WAITING_MOMENTUM_MAX = 3
WAITING_MOMENTUM_RESET = 4
WAITING_NEW_VOW_NAME = 5
WAITING_NEW_VOW_DIFFICULTY = 6
WAITING_NEW_VOW_DESCRIPTION = 7

character_handler = ConversationHandler(
    entry_points=[
        CommandHandler("character", character),
    ],
    states={
        SHOWING_CHARACTER: [CallbackQueryHandler(character_button_callback)],
        WAITING_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name_input)
        ],
        WAITING_STATS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stats_input)
        ],
        WAITING_MOMENTUM_MAX: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_momentum_max_input)
        ],
        WAITING_MOMENTUM_RESET: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_momentum_reset_input)
        ],
        WAITING_NEW_VOW_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_vow_name_input)
        ],
        WAITING_NEW_VOW_DIFFICULTY: [
            CallbackQueryHandler(handle_new_vow_difficulty_input)
        ],
        WAITING_NEW_VOW_DESCRIPTION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_new_vow_description_input
            )
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
