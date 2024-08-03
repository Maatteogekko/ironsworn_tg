from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw
import random

from src.utils import cancel, end_conversation, flip_page, split_text

# Define conversation states
SHOWING_CHARACTER = 0

async def create_sheet(image_path: str) -> str:
    # Open the image
    img = Image.open(image_path)
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Draw a black line from (300,300) to (400,400)
    draw.line([(random.random()*1000, random.random()*1000), (random.random()*1000, random.random()*1000)], fill="black", width=2)
    
    # Save the modified image
    modified_image_path = "./data/modified_character_sheet.png"
    img.save(modified_image_path)
    
    return modified_image_path

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ironsworn", callback_data='ironsworn')],
        [InlineKeyboardButton("Momentum", callback_data='momentum')],
        [InlineKeyboardButton("Condition", callback_data='condition')],
        [InlineKeyboardButton("Character", callback_data='character')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_ironsworn_keyboard():
    keyboard = [
        [InlineKeyboardButton("Vows", callback_data='vows')],
        [InlineKeyboardButton("Bonds", callback_data='bonds')],
        [InlineKeyboardButton("Assets", callback_data='assets')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_momentum_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Momentum-", callback_data='momentum_minus'),
            InlineKeyboardButton("Momentum+", callback_data='momentum_plus')
        ],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_condition_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Health-", callback_data='health_minus'),
            InlineKeyboardButton("Health+", callback_data='health_plus')
        ],
        [
            InlineKeyboardButton("Spirit-", callback_data='spirit_minus'),
            InlineKeyboardButton("Spirit+", callback_data='spirit_plus')
        ],
        [
            InlineKeyboardButton("Supply-", callback_data='supply_minus'),
            InlineKeyboardButton("Supply+", callback_data='supply_plus')
        ],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Create the character sheet
    image_path = "./data/Ironsworn_sheet.png"  # Replace with your image path
    modified_image_path = await create_sheet(image_path)
    
    # Send the message with the image and keyboard
    await update.message.reply_photo(
        photo=open(modified_image_path, 'rb'),
        caption="Here's your character sheet",
        reply_markup=get_main_keyboard()
    )
    
    return SHOWING_CHARACTER

async def character_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'ironsworn':
        await query.edit_message_reply_markup(reply_markup=get_ironsworn_keyboard())
    elif query.data == 'momentum':
        await query.edit_message_reply_markup(reply_markup=get_momentum_keyboard())
    elif query.data == 'condition':
        await query.edit_message_reply_markup(reply_markup=get_condition_keyboard())
    elif query.data == 'back_to_main':
        await query.edit_message_reply_markup(reply_markup=get_main_keyboard())
    elif query.data in ['health_minus', 'health_plus', 'spirit_minus', 'spirit_plus', 'supply_minus', 'supply_plus']:
        # Here you would implement the logic to update the character's stats
        # For now, we'll just acknowledge the button press
        stat, direction = query.data.split('_')
        await query.edit_message_text(f"{stat.capitalize()} {'decreased' if direction == 'minus' else 'increased'}.")
        await query.edit_message_reply_markup(reply_markup=get_condition_keyboard())
    else:
        # Handle other button callbacks (character, vows, bonds, assets, momentum+/-)
        await query.edit_message_text(text=f"You clicked: {query.data}")
        await query.edit_message_reply_markup(reply_markup=get_main_keyboard())
    
    return SHOWING_CHARACTER

character_handler = ConversationHandler(
    entry_points=[CommandHandler("character", character)],
    states={
        SHOWING_CHARACTER: [CallbackQueryHandler(character_button_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)