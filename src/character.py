from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw

from src.utils import cancel, end_conversation, flip_page, split_text

# Define conversation states
SHOWING_CHARACTER = 0

# Sarchiapone modifies the json based on button pressed.
async def update_sheet(button: str) -> str:
    print(button)
    # For now, just return the path to the original image
    return

# Sarchiapone create image based on the content of the character json (and probably the chat_id)
async def create_sheet(image_path: str) -> str:
    # Open the image
    img = Image.open(image_path)
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Draw a black line from (300,300) to (400,400)
    draw.line([(300, 300), (400, 400)], fill="black", width=2)
    
    # Save the modified image
    modified_image_path = "./data/modified_character_sheet.png"
    img.save(modified_image_path)
    
    return modified_image_path

def get_main_keyboard():
    keyboard = [
        ["Ironsworn"],
        ["Momentum"],
        ["Condition"],
        ["Character"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ironsworn_keyboard():
    keyboard = [
        ["Vows"],
        ["Bonds"],
        ["Assets"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_momentum_keyboard():
    keyboard = [
        ["Momentum-", "Momentum+"],
        ["Max Momentum", "Momentum Reset"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_condition_keyboard():
    keyboard = [
        ["Health-", "Health+"],
        ["Spirit-", "Spirit+"],
        ["Supply-", "Supply+"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_character_keyboard():
    keyboard = [
        ["Character Name"],
        ["Character Stats"],
        ["Character Exp"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Create the character sheet
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(image_path)
    
    # Send the message with the image and keyboard
    await update.message.reply_photo(
        photo=open(modified_image_path, 'rb'),
        caption="Here's your character sheet",
        reply_markup=get_main_keyboard()
    )
    
    return SHOWING_CHARACTER

async def character_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    button_pressed = update.message.text

    # Call update_sheet function
    await update_sheet(button_pressed) #Sarchiapone ideally, this modifies the json

    # Create updated sheet
    image_path = "./data/Ironsworn_sheet.png"
    modified_image_path = await create_sheet(image_path)

    if button_pressed == "Ironsworn":
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption="Ironsworn options",
            reply_markup=get_ironsworn_keyboard()
        )
    elif button_pressed == "Momentum":
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption="Momentum options",
            reply_markup=get_momentum_keyboard()
        )
    elif button_pressed == "Condition":
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption="Condition options",
            reply_markup=get_condition_keyboard()
        )
    elif button_pressed == "Character":
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption="Character options",
            reply_markup=get_character_keyboard()
        )
    elif button_pressed == "Back":
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption="Main menu",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_photo(
            photo=open(modified_image_path, 'rb'),
            caption=f"You selected: {button_pressed}",
            reply_markup=get_main_keyboard()
        )
    
    return SHOWING_CHARACTER

character_handler = ConversationHandler(
    entry_points=[CommandHandler("character", character)],
    states={
        SHOWING_CHARACTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_button_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)