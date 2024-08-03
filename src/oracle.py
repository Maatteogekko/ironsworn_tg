from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

# Existing functions remain the same
async def oracle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.lower()
    if command == '/oracle':
        # Main oracle command without specific theme
        themes = ['/oracle_love', '/oracle_career', '/oracle_health', '/oracle_wealth']
        response = "Welcome to the Oracle! Choose a theme:\n" + "\n".join(themes)
    elif command.startswith('/oracle_'):
        # Handle specific oracle themes
        theme = command.split('_')[1]
        response = get_oracle_response(theme)
    else:
        response = "Invalid oracle command. Try /oracle for options."
    
    await update.message.reply_text(response)

def get_oracle_response(theme: str) -> str:
    # Dictionary of possible responses for each theme
    responses = {
        'love': [
            "Love is in the air!",
            "Your soulmate is closer than you think.",
            "Focus on self-love and the rest will follow."
        ],
        'career': [
            "A new opportunity is on the horizon.",
            "Your hard work will pay off soon.",
            "Consider learning a new skill to advance your career."
        ],
        'health': [
            "Remember to stay hydrated and exercise regularly.",
            "A good night's sleep will do wonders for your health.",
            "Consider trying meditation for mental well-being."
        ],
        'wealth': [
            "An unexpected financial gain is coming your way.",
            "Invest wisely and your wealth will grow.",
            "Budget carefully to achieve your financial goals."
        ]
    }
    
    if theme in responses:
        return random.choice(responses[theme])
    else:
        return f"No predictions available for the theme: {theme}"