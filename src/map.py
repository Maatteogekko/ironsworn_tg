import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from PIL import Image, ImageDraw, ImageFont

from PIL import Image, ImageDraw, ImageFont
import json

async def create_map(image_path: str) -> str:
    # Open the image
    img = Image.open(image_path)
    # Get image dimensions
    width, height = img.size
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)

    def font(size=30):
        try:
            return ImageFont.truetype("./data/Modesto Expanded.ttf", size)
        except IOError:
            return ImageFont.load_default(size)

    # Grid color - light grey
    grid_color = (128, 128, 128, 50)  # RGBA: semi-transparent grey

    # Draw vertical lines
    for x in range(0, width, 100):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)

    # Draw horizontal lines
    for y in range(0, height, 100):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Waypoint color
    waypoint_color = "black"

    # Draw waypoints
    with open("./data/map.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    for waypoint in data.keys():
        draw.text(
            [data[waypoint]['coords'][0]+15, data[waypoint]['coords'][1]+0], 
            waypoint, 
            fill=waypoint_color, 
            font=font(10)
        )
        draw.ellipse(
            [
                data[waypoint]['coords'][0], 
                data[waypoint]['coords'][1], 
                data[waypoint]['coords'][0] + 10, 
                data[waypoint]['coords'][1] + 10
            ], 
            fill=waypoint_color
        )

    # Save the modified image
    modified_image_path = "./data/modified_map.png"
    img.save(modified_image_path)

    return modified_image_path

# Add a new state for remove waypoint
MAP_NAME, MAP_COORDS, REMOVE_WAYPOINT = range(3)

async def send_map_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create the keyboard
    keyboard = [
        [
            InlineKeyboardButton("Add Waypoint", callback_data='map_add_waypoint'),
            InlineKeyboardButton("Remove Waypoint", callback_data='map_remove_waypoint'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Generate the map image
    modified_image_path = await create_map("./data/map.png")
    
    # Send message with image and buttons
    with open(modified_image_path, 'rb') as image:
        await update.message.reply_photo(
            photo=image,
            reply_markup=reply_markup
        )

async def handle_map_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id  # Get the chat ID from the original message
    
    if query.data == 'map_add_waypoint':
        # Delete the original message
        try:
            await query.message.delete()
        except:
            pass
        
        # Start the conversation for adding a waypoint
        await context.bot.send_message(chat_id,"Please enter the name for the new waypoint:")
        return MAP_NAME
    
    elif query.data == 'map_remove_waypoint':
        # Delete the original message
        try:
            await query.message.delete()
        except:
            pass
        
        # Load and display existing waypoints
        with open('./data/map.json', 'r') as f:
            waypoints = json.load(f)
        
        if not waypoints:
            # If no waypoints exist, just resend the map
            await send_map_command(update, context)
            return ConversationHandler.END
        
        message = "Current waypoints:\n\n"
        for name, data in waypoints.items():
            coords = data['coords']
            message += f"• {name}: ({coords[0]}, {coords[1]})\n"
        
        message += "\nEnter the name of the waypoint you want to remove:"
        
        await context.bot.send_message(chat_id,message)
        return REMOVE_WAYPOINT

async def receive_map_waypoint_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Store the name in context
    context.user_data['waypoint_name'] = update.message.text
    chat_id = update.message.chat.id
    await context.bot.send_message(chat_id,"Please enter the coordinates as 'x,y' (max: 530,870):")
    return MAP_COORDS

async def receive_map_waypoint_coords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    try:
        # Parse coordinates
        x, y = map(int, update.message.text.split(','))
        
        # Get the stored name
        name = context.user_data['waypoint_name']
        
        # Update the JSON file
        with open('./data/map.json', 'r') as f:
            waypoints = json.load(f)
        
        waypoints[name] = {"coords": [x, y]}
        
        with open('./data/map.json', 'w') as f:
            json.dump(waypoints, f)
        
        # Send new map message
        keyboard = [
            [
                InlineKeyboardButton("Add Waypoint", callback_data='map_add_waypoint'),
                InlineKeyboardButton("Remove Waypoint", callback_data='map_remove_waypoint'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        modified_image_path = await create_map("./data/map.png")
        
        with open(modified_image_path, 'rb') as image:
            await update.message.reply_photo(
                photo=image,
                reply_markup=reply_markup
            )
        
        return ConversationHandler.END
    
    except ValueError:
        await context.bot.send_message(chat_id,"Invalid coordinates. Please enter as 'x,y' (e.g., '200,500'):")
        return MAP_COORDS

async def remove_map_waypoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waypoint_to_remove = update.message.text
    
    # Load current waypoints
    with open('./data/map.json', 'r') as f:
        waypoints = json.load(f)
    
    # Try to remove the waypoint
    if waypoint_to_remove in waypoints:
        waypoints.pop(waypoint_to_remove)
        
        # Save updated waypoints
        with open('./data/map.json', 'w') as f:
            json.dump(waypoints, f)
    
    # Regardless of whether we found the waypoint or not, send the updated map
    keyboard = [
        [
            InlineKeyboardButton("Add Waypoint", callback_data='map_add_waypoint'),
            InlineKeyboardButton("Remove Waypoint", callback_data='map_remove_waypoint'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    modified_image_path = await create_map("./data/map.png")
    
    with open(modified_image_path, 'rb') as image:
        await update.message.reply_photo(
            photo=image,
            reply_markup=reply_markup
        )
    
    return ConversationHandler.END

# Updated conversation handler for map waypoints
map_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_map_button)],
    states={
        MAP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_map_waypoint_name)],
        MAP_COORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_map_waypoint_coords)],
        REMOVE_WAYPOINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_map_waypoint)],
    },
    fallbacks=[]
)