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

async def update_trackers(task,new = None) -> str:
    with open("./data/trackers.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if task.startswith("remove_tracker_"):
        task_ = task.split("_")
        data.pop(task_[-1])
    if task.startswith("tracker_"):
        offset = {'troublesome':12,'dangerous':8,'formidable':4,'extreme':2,'epic':1}
        task_ = task.split("_")
        if task_[1]=='plus':
            data[task_[-1]]['tracker'] += offset[data[task_[-1]]["difficulty"]]
        elif task_[1]=='minus':
            data[task_[-1]]['tracker'] -=1
    if task == "add_tracker_name":
        data[new] = {
            "difficulty": None,
            "tracker": 0,
        }
    if task == "add_tracker_difficulty":
        data[new[0]]["difficulty"] = new[1].split("_")[-1]
    with open("./data/trackers.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

async def create_trackers() -> str:

    # Open the character data
    with open("./data/trackers.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    # Open the image

    image_path = create_collage(['./data/trackers_template.png' for _ in range(len(data.keys()))], output_filename="./data/trackers.png", thumbnail_size=(725, 107), spacing=5)
    
    img = Image.open(image_path)

    def font(size=30):
        try:
            return ImageFont.truetype("./data/Modesto Expanded.ttf", size)
        except IOError:
            return ImageFont.load_default(size)

    color = (45, 45, 45)

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Insert trackers
    cn = [30, 13]
    diff_offset = {'troublesome':54.8,'dangerous':201,'formidable':330,'extreme':462,'epic':572}
    for i, tracker in enumerate(data.keys()):
        draw.text((cn[0], cn[1]), str(tracker), fill=color, font=font(20))
        x = cn[0]+diff_offset[data[tracker]["difficulty"]]
        y = cn[1]+33
        draw.ellipse([x, y, x + 16, y + 16], fill=color)
        c_y = cn[0] + 171
        s_y = cn[1] + 74
        for i in range(int(data[tracker]["tracker"] / 4)):
            for l in ticks([c_y, s_y], 4):
                draw.line(
                    l,
                    fill=color,
                    width=4,
                )
            c_y = c_y + 37
        for l in ticks([c_y, s_y], data[tracker]["tracker"] % 4):
            draw.line(
                l,
                fill=color,
                width=4,
            )
        cn[1] += 112

    # Save the modified image
    modified_image_path = "./data/trackers.png"
    img.save(modified_image_path)

    print("modified_image_path",modified_image_path)
    return modified_image_path


def ticks(center, ticks):
    lines = []
    if ticks >= 1:
        lines.append(
            [(center[0] - 11, center[1] - 11), (center[0] + 11, center[1] + 11)]
        )
    if ticks >= 2:
        lines.append(
            [(center[0] + 11, center[1] - 11), (center[0] - 11, center[1] + 11)]
        )
    if ticks >= 3:
        lines.append([(center[0] - 13, center[1]), (center[0] + 13, center[1])])
    if ticks >= 4:
        lines.append([(center[0], center[1] - 13), (center[0], center[1] + 13)])

    return lines


def create_collage(
    image_names, output_filename="./collage.jpg", thumbnail_size=(100, 1000), spacing=5
):
    # Open all images and resize them
    print(image_names)
    images = [
        Image.open(name).resize(thumbnail_size, Image.Resampling.LANCZOS)
        for name in image_names
    ]

    # Calculate the number of rows and columns
    num_images = len(images)
    cols = 1
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

def get_trackers_keyboard():
    with open("./data/trackers.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    keyboard = []
    for tracker in data.keys():
        keyboard.append([InlineKeyboardButton("➖ "+tracker, callback_data="tracker_minus_"+tracker),
                         InlineKeyboardButton("➕ "+tracker, callback_data="tracker_plus_"+tracker),
                         InlineKeyboardButton("Remove", callback_data="remove_tracker_"+tracker)
                         ])

    keyboard.append([InlineKeyboardButton("Add tracker", callback_data="add_tracker")])

    return InlineKeyboardMarkup(keyboard)

async def trackers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Create trackers and get the image path
    image_path = await create_trackers()
    
    # Open the image and check its height
    with Image.open(image_path) as img:
        width, height = img.size  # Get width and height of the image

    print(f"Image path: {image_path}, Image height: {height}")

    # Check if the image height is below 10 pixels
    if height < 10:
        # Send a message without the image
        message = await update.message.reply_text(
            text="No Trackers found",
            reply_markup=get_trackers_keyboard(),
        )
    else:
        # Send the message with the image
        message = await update.message.reply_photo(
            photo=open(image_path, "rb"),
            caption="Trackers",
            reply_markup=get_trackers_keyboard(),
        )

    # Store the message IDs for later deletion
    context.user_data["bot_message_id"] = message.message_id

    return SHOWING_TRACKERS

    # PASSAGGI PER UPDATE DELL'IMMAGINE
    # Call update_sheet function
    # updated_image_path = await update_sheet(query.data)

    # Create updated sheet
    # modified_image_path = await create_sheet(updated_image_path)
    # await query.edit_message_media(
    # media=InputMediaPhoto(open(modified_image_path, 'rb'), caption="Ironsworn options"),
    # reply_markup=get_ironsworn_keyboard()
    # )

async def trackers_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("remove_tracker_") or query.data.startswith("tracker_"):
        # Update the trackers
        await update_trackers(query.data)
        
        # Create trackers and get the image path
        image_path = await create_trackers()
        
        # Open the image and check its height
        with Image.open(image_path) as img:
            width, height = img.size  # Get width and height of the image

        print(f"Image path: {image_path}, Image height: {height}")

        # Check if the image height is below 10 pixels
        if height < 10:
            # Edit the message without updating the image
            await query.message.edit_caption(
                caption="Tracker removed/updated (Sorry for the image, will be fixed.)",
                reply_markup=get_trackers_keyboard(),
            )
        else:
            # Edit the message with the updated image
            await query.message.edit_media(
                media=InputMediaPhoto(
                    open(image_path, "rb"), caption="Tracker removed/updated"
                ),
                reply_markup=get_trackers_keyboard(),
            )
    elif query.data == "add_tracker":
        await query.message.reply_text("Send me the name of the new tracker:")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        return WAITING_NEW_TRACKER_NAME
    else:
        await query.edit_message_caption(
            "Yeah we won't implement that", reply_markup=get_trackers_keyboard()
        )

    return SHOWING_TRACKERS

async def handle_new_tracker_name_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text
    await update_trackers("add_tracker_name", name)

    keyboard = [
        [
            InlineKeyboardButton(
                "Troublesome", callback_data="new_tracker_difficulty_troublesome"
            )
        ],
        [
            InlineKeyboardButton(
                "Dangerous", callback_data="new_tracker_difficulty_dangerous"
            )
        ],
        [
            InlineKeyboardButton(
                "Formidable", callback_data="new_tracker_difficulty_formidable"
            )
        ],
        [InlineKeyboardButton("Extreme", callback_data="new_tracker_difficulty_extreme")],
        [InlineKeyboardButton("Epic", callback_data="new_tracker_difficulty_epic")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select the new tracker difficulty", reply_markup=reply_markup
    )
    context.user_data["new_tracker"] = name
    return WAITING_NEW_TRACKER_DIFFICULTY


async def handle_new_tracker_difficulty_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = context.user_data["new_tracker"]

    print("aspettando la risposta ai pulsanti credo")
    query = update.callback_query
    await query.answer()
    await update_trackers(
        "add_tracker_difficulty", (name, query.data)
    )

    # Create trackers and get the modified image path
    modified_image_path = await create_trackers()
    
    # Open the image and check its height
    with Image.open(modified_image_path) as img:
        width, height = img.size  # Get width and height of the image

    print(f"Modified image path: {modified_image_path}, Image height: {height}")

    # Check if the image height is below 10 pixels
    if height < 10:
        # Send a message without the image
        await query.message.reply_text(
            text="No Trackes found",
            reply_markup=get_trackers_keyboard(),
        )
    else:
        # Send the message with the image
        await query.message.reply_photo(
            photo=open(modified_image_path, "rb"),
            caption="Trackers updated",
            reply_markup=get_trackers_keyboard(),
        )
    return SHOWING_TRACKERS

SHOWING_TRACKERS = 0 
WAITING_NEW_TRACKER_NAME =1 
WAITING_NEW_TRACKER_DIFFICULTY =2
trackers_handler = ConversationHandler(
    entry_points=[
        CommandHandler("trackers", trackers),
    ],
    states={
        SHOWING_TRACKERS: [CallbackQueryHandler(trackers_button_callback)],
        WAITING_NEW_TRACKER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_tracker_name_input)
        ],
        WAITING_NEW_TRACKER_DIFFICULTY: [
            CallbackQueryHandler(handle_new_tracker_difficulty_input)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)