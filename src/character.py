from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw, ImageFont
import random
import json

from src.utils import cancel, end_conversation, flip_page, split_text

# Define conversation states
SHOWING_CHARACTER = 0

async def create_sheet(chat_id, image_path: str) -> str:

    # Open the character data
    with open("./data/character.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data = data[chat_id]
    # Open the image
    img = Image.open(image_path)
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    def myfont(size = 30):
        try:
            return ImageFont.truetype("./data/Modesto Expanded.ttf", size)
        except IOError:
            return ImageFont.load_default(size)
    mycolor = (45,45,45)
    
    
    # Insert the name
    draw.text((140, 120), data["name"], fill = mycolor, font = myfont(50))
    
    # Insert the Stats
    x = 349
    dx = 237
    draw.text((x, 240), str(data["stats"]["edge"]), fill = mycolor, font = myfont(80))
    draw.text((x+dx, 240), str(data["stats"]["hearth"]), fill = mycolor, font = myfont(80))
    draw.text((x+2*dx, 240), str(data["stats"]["iron"]), fill = mycolor, font = myfont(80))
    draw.text((x+3*dx, 240), str(data["stats"]["shadow"]), fill = mycolor, font = myfont(80))
    draw.text((x+4*dx, 240), str(data["stats"]["wits"]), fill = mycolor, font = myfont(80))

    # Insert Exp
    dots = data['experience']['used']
    xs = data['experience']['gained']
    positions_x = [1088.5+_*36.48 for _ in range(15)]
    positions_y = [117,154]
    for i,y in enumerate(positions_y):
        for j,x in enumerate(positions_x):
            if (j+i*15)<dots:
                draw.ellipse([x,y,x+26,y+26], fill=mycolor)
            elif (j+i*15)<xs:
                draw.line([(x, y), (x+26, y+26)], fill=mycolor, width=5)
                draw.line([(x, y+26), (x+26, y)], fill=mycolor, width=5)

    # Insert Momentum
    max =  data['momentum']['max']
    if len(str(max))==1:
        draw.text((134, 1875), str(max), fill = mycolor, font = myfont(40))
    else:
        draw.text((120, 1875), str(max), fill = mycolor, font = myfont(40))
    reset =  data['momentum']['reset']
    if len(str(reset))==1: 
        draw.text((134, 1998), str(reset), fill = mycolor, font = myfont(40))
    else:
        draw.text((120, 1998), str(reset), fill = mycolor, font = myfont(40))
    current =  data['momentum']['current']
    c_c_x = 147.9
    c_c_y = 1214-current*94.5-(0.5*current if current<0 else 0)
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=mycolor, width=10)

    # Insert Health
    health =  data['state']['health']
    c_c_x = 1552
    c_c_y = 785.5-health*94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=mycolor, width=10)

    # Insert Spirit
    spirit =  data['state']['spirit']
    c_c_x = 1552
    c_c_y = 1398.5-spirit*94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=mycolor, width=10)

    # Insert Supply
    supply =  data['state']['supply']
    c_c_x = 1552
    c_c_y = 2011.5-supply*94.5
    top_left = (c_c_x - 110 // 2, c_c_y - 55 // 2)
    bottom_right = (c_c_x + 110 // 2, c_c_y + 55 // 2)
    draw.rectangle([top_left, bottom_right], outline=mycolor, width=10)

    # Draw a black line from (300,300) to (400,400)
    draw.line([(random.random()*1000, random.random()*1000), (random.random()*1000, random.random()*1000)], fill="black", width=2)
    
    # Save the modified image
    modified_image_path = "./data/"+data['name']+"_character_sheet.png"
    img.save(modified_image_path)
    
    return modified_image_path

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ironsworn", callback_data='ironsworn')],
        [InlineKeyboardButton("Momentum", callback_data='momentum')],
        [InlineKeyboardButton("State", callback_data='state')],
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
        [InlineKeyboardButton("Momentum-", callback_data='momentum_minus'),
         InlineKeyboardButton("Momentum+", callback_data='momentum_plus')],
        [InlineKeyboardButton("Max Momentum", callback_data='max_momentum'),
         InlineKeyboardButton("Momentum Reset", callback_data='momentum_reset')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_state_keyboard():
    keyboard = [
        [InlineKeyboardButton("Health-", callback_data='health_minus'),
         InlineKeyboardButton("Health+", callback_data='health_plus')],
        [InlineKeyboardButton("Spirit-", callback_data='spirit_minus'),
         InlineKeyboardButton("Spirit+", callback_data='spirit_plus')],
        [InlineKeyboardButton("Supply-", callback_data='supply_minus'),
         InlineKeyboardButton("Supply+", callback_data='supply_plus')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_character_keyboard():
    keyboard = [
        [InlineKeyboardButton("Character Name", callback_data='character_name')],
        [InlineKeyboardButton("Character Stats", callback_data='character_stats')],
        [InlineKeyboardButton("Character Exp", callback_data='character_exp')],
        [InlineKeyboardButton("Back", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def update_sheet(button: str) -> str:
    print(button)
    # For now, just return the path to the original image
    return "./data/Ironsworn_sheet.png"

async def character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Create the character sheet
    image_path = "./data/Ironsworn_sheet.png"
    chat_id = str(update.effective_user.id)
    modified_image_path = await create_sheet(chat_id, image_path)
    
    # Send the message with the image and keyboard
    message = await update.message.reply_photo(
        photo=open(modified_image_path, 'rb'),
        caption="Here's your character sheet",
        reply_markup=get_main_keyboard()
    )
    
    # Store the message IDs for later deletion
    context.user_data['bot_message_id'] = message.message_id 
    
    return SHOWING_CHARACTER

async def character_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'ironsworn':

        # PASSAGGI PER UPDATE DELLL'IMMAGINE
        # Call update_sheet function
        #updated_image_path = await update_sheet(query.data)

        # Create updated sheet
        #modified_image_path = await create_sheet(updated_image_path)
        #await query.edit_message_media(
            #media=InputMediaPhoto(open(modified_image_path, 'rb'), caption="Ironsworn options"),
            #reply_markup=get_ironsworn_keyboard()
        #)
        await query.edit_message_caption("Test Ironsworn",reply_markup=get_ironsworn_keyboard())
    elif query.data == 'momentum':
        await query.edit_message_caption("Test momentum",reply_markup=get_momentum_keyboard())
    elif query.data == 'state':
        await query.edit_message_caption("Test state",reply_markup=get_state_keyboard())
    elif query.data == 'character':
        await query.edit_message_caption("Test character",reply_markup=get_character_keyboard())
    elif query.data == 'back_to_main':
        await query.edit_message_caption("Test back",reply_markup=get_main_keyboard())
    else:
        await query.edit_message_caption("Test impossibile arrivarci?",reply_markup=get_main_keyboard())

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