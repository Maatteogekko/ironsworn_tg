import random
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, Application

# Oracle data with full descriptions
ORACLES = {
    "Action Oracle": "ORACLE 1: ACTION\nUse this table to inspire a discovery, event, character goal, or situation. A roll on this table can be combined with a Theme to provide an action and a subject. Then, interpret the result based on the context of the question and your current situation.",
    
    "Theme Oracle": "ORACLE 2: THEME\nAs with the Action oracle, this is an interpretative table which you can use to answer questions or generate new situations. Combined, the Action and Theme tables provide creative prompts suitable for most situations and questions. In fact, with some creative interpretations, it's entirely possible to play with only these two tables.",
    
    "Region Oracle": "ORACLE 3: REGION\nUse this oracle when you want to randomly select a region with the Ironlands.",
    
    "Location Oracle": "ORACLE 4: LOCATION\nUse this oracle when traveling to generate a point-of-interest or to answer a question about a place where someone or something can be found. Your roll may generate a place or geographical feature which doesn't make sense in the context of your current location. If so, follow the guidelines to generate a different result (look at adjacent rows or reverse the digits). Or, play off the original answer to introduce something unexpected.",
    
    "Coastal Oracle": "ORACLE 5: COASTAL WATERS LOCATION\nUse this oracle to identify a point-of-interest or destination when you are traveling by ship or boat along the coast.",
    
    "Description Oracle": "ORACLE 6: LOCATION DESCRIPTION\nUse this oracle to add detail to the Location or Coastal Waters Location oracles, or by itself to generate a description of a location. Roll more than once for extra detail.",
    
    "Settlement Name": "ORACLE 7: SETTLEMENT NAME\nAsk this oracle for a thematic name for an Ironlander settlement. Roll once for the category, and again to pick from the examples. Alternatively, just roll for the category and come up with a name that fits the theme. In either case, consider the meaning of the name and how it impacts this settlement's surroundings, livelihood, culture, or history.",
    
    "Quick Settlement": "ORACLE 8: QUICK SETTLEMENT NAME GENERATOR\nUse this oracle as a simpler alternative for settlement names. Roll once for the prefix, and once for the suffix. If the combination doesn't quite work, look at adjacent rows or reverse the digits. Once you have your answer, envision what feature, person, or event inspired the name.",
    
    "Settlement Trouble": "ORACLE 9: SETTLEMENT TROUBLE\nUse this table to generate a narrative hook for a problem faced by a community. This oracle can help inspire a vow for your character or serve as a prompt for a trouble you encounter when you interact with a settlement. Use other oracles, as appropriate, to help flesh out the answer.",
    
    "Character Role": "ORACLE 10: CHARACTER ROLE\nUse this oracle to define the background for a character, or to generate a random encounter.",
    
    "Character Goal": "ORACLE 11: CHARACTER GOAL\nUse this oracle to define the primary motivation of an NPC or a faction. It can also be used to kick-off a personal quest for your own character.",
    
    "Character Descriptor": "ORACLE 12: CHARACTER DESCRIPTOR\nUse this oracle to help flesh out a character's personality or physical characteristics. Roll more than once to add additional detail. You can combine all three character oracles (10, 11 and 12), plus a roll on an appropriate name table, to build an outline of an NPC.",
    
    "Ironlander Names": "ORACLE 13: IRONLANDER NAMES\nUse this oracle to quickly generate a name for an Ironlander character. Roll on either table. Surnames are not used in the Ironlands and names are often gender-neutral. If a name doesn't fit a character, or you don't like the sound of it, look up or down a row for your answer, or reverse the digits.",
    
    "Elf Names": "ORACLE 14: ELF NAMES\nUse this oracle to generate a name for an elf character.",
    
    "Other Names": "ORACLE 15: OTHER NAMES\nUse this oracle for other firstborn characters, including giants, varou, and trolls.",
    
    "Combat Action": "ORACLE 16: COMBAT ACTION\nUse this oracle to help inspire an action for an NPC in combat. When you're not sure what your foe does next, particularly when they have initiative, roll on this table and interpret the result as appropriate to your foe and the situation.",
    
    "Mystic Backlash": "ORACLE 17: MYSTIC BACKLASH\nThose who deal in magic may find themselves at the mercy of chaos. This oracle can supplement, or replace, the Pay the Price table when resolving the outcome of a failed ritual or other negative interaction with mystical forces. Use this oracle in dramatic moments, or to introduce an unexpected outcome triggered by a match.",
    
    "Major Plot Twist": "ORACLE 18: MAJOR PLOT TWIST\nUse this oracle to introduce a narrative surprise or revelation. Most of these results have a negative implication, and can be used to resolve a match at a crucial moment in your story. This oracle offers similar results to the Pay the Price table, but is more focused on dramatic events tied to your current quests.",
    
    "Challenge Rank": "ORACLE 19: CHALLENGE RANK\nUse this oracle when you want to randomly determine the challenge rank of a quest, journey, or fight."
}

ACTION_ORACLE = {
    100: "Summon",
    1: "Scheme", 2: "Clash", 3: "Weaken", 4: "Initiate", 5: "Create",
    6: "Swear", 7: "Avenge", 8: "Guard", 9: "Defeat", 10: "Control",
    11: "Break", 12: "Risk", 13: "Surrender", 14: "Inspect", 15: "Raid",
    16: "Evade", 17: "Assault", 18: "Deflect", 19: "Threaten", 20: "Attack",
    21: "Leave", 22: "Preserve", 23: "Manipulate", 24: "Remove", 25: "Eliminate",
    26: "Withdraw", 27: "Abandon", 28: "Investigate", 29: "Hold", 30: "Focus",
    31: "Uncover", 32: "Breach", 33: "Aid", 34: "Uphold", 35: "Falter",
    36: "Suppress", 37: "Hunt", 38: "Share", 39: "Destroy", 40: "Avoid",
    41: "Reject", 42: "Demand", 43: "Explore", 44: "Bolster", 45: "Seize",
    46: "Mourn", 47: "Reveal", 48: "Gather", 49: "Defy", 50: "Transform",
    51: "Persevere", 52: "Serve", 53: "Begin", 54: "Move", 55: "Coordinate",
    56: "Resist", 57: "Await", 58: "Impress", 59: "Take", 60: "Oppose",
    61: "Capture", 62: "Overwhelm", 63: "Challenge", 64: "Acquire", 65: "Protect",
    66: "Finish", 67: "Strengthen", 68: "Restore", 69: "Advance", 70: "Command",
    71: "Refuse", 72: "Find", 73: "Deliver", 74: "Hide", 75: "Fortify",
    76: "Betray", 77: "Secure", 78: "Arrive", 79: "Affect", 80: "Change",
    81: "Defend", 82: "Debate", 83: "Support", 84: "Follow", 85: "Construct",
    86: "Locate", 87: "Endure", 88: "Release", 89: "Lose", 90: "Reduce",
    91: "Escalate", 92: "Distract", 93: "Journey", 94: "Escort", 95: "Learn",
    96: "Communicate", 97: "Depart", 98: "Search", 99: "Charge"
}

THEME_ORACLE = {
    1: "Risk", 2: "Ability", 3: "Price", 4: "Ally", 5: "Battle",
    6: "Safety", 7: "Survival", 8: "Weapon", 9: "Wound", 10: "Shelter",
    11: "Leader", 12: "Fear", 13: "Time", 14: "Duty", 15: "Secret",
    16: "Innocence", 17: "Renown", 18: "Direction", 19: "Death", 20: "Honor",
    21: "Labor", 22: "Solution", 23: "Tool", 24: "Balance", 25: "Love",
    26: "Barrier", 27: "Creation", 28: "Decay", 29: "Trade", 30: "Bond",
    31: "Hope", 32: "Superstition", 33: "Peace", 34: "Deception", 35: "History",
    36: "World", 37: "Vow", 38: "Protection", 39: "Nature", 40: "Opinion",
    41: "Burden", 42: "Vengeance", 43: "Opportunity", 44: "Faction", 45: "Danger",
    46: "Corruption", 47: "Freedom", 48: "Debt", 49: "Hate", 50: "Possession",
    51: "Stranger", 52: "Passage", 53: "Land", 54: "Creature", 55: "Disease",
    56: "Advantage", 57: "Blood", 58: "Language", 59: "Rumor", 60: "Weakness",
    61: "Greed", 62: "Family", 63: "Resource", 64: "Structure", 65: "Dream",
    66: "Community", 67: "War", 68: "Portent", 69: "Prize", 70: "Destiny",
    71: "Momentum", 72: "Power", 73: "Memory", 74: "Ruin", 75: "Mysticism",
    76: "Rival", 77: "Problem", 78: "Idea", 79: "Revenge", 80: "Health",
    81: "Fellowship", 82: "Enemy", 83: "Religion", 84: "Spirit", 85: "Fame",
    86: "Desolation", 87: "Strength", 88: "Knowledge", 89: "Truth", 90: "Quest",
    91: "Pride", 92: "Loss", 93: "Law", 94: "Path", 95: "Warning",
    96: "Relationship", 97: "Wealth", 98: "Home", 99: "Strategy", 100: "Supply"
}

LOCATION_ORACLE = {
    1: "Hideout",
    2: "Ruin",
    3: "Mine",
    4: "Waste",
    5: "Mystical Site",
    6: "Path",
    7: "Outpost",
    8: "Wall",
    9: "Battlefield",
    10: "Hovel",
    11: "Spring",
    12: "Lair",
    13: "Fort",
    14: "Bridge",
    15: "Camp",
    16: "Cairn/Grave",
    **{i: "Caravan" for i in range(17, 19)},
    **{i: "Waterfall" for i in range(19, 21)},
    **{i: "Cave" for i in range(21, 23)},
    **{i: "Swamp" for i in range(23, 25)},
    **{i: "Fen" for i in range(25, 27)},
    **{i: "Ravine" for i in range(27, 29)},
    **{i: "Road" for i in range(29, 31)},
    **{i: "Tree" for i in range(31, 33)},
    **{i: "Pond" for i in range(33, 35)},
    **{i: "Fields" for i in range(35, 37)},
    **{i: "Marsh" for i in range(37, 39)},
    **{i: "Steading" for i in range(39, 41)},
    **{i: "Rapids" for i in range(41, 43)},
    **{i: "Pass" for i in range(43, 45)},
    **{i: "Trail" for i in range(45, 47)},
    **{i: "Glade" for i in range(47, 49)},
    **{i: "Plain" for i in range(49, 51)},
    **{i: "Ridge" for i in range(51, 53)},
    **{i: "Cliff" for i in range(53, 55)},
    **{i: "Grove" for i in range(55, 57)},
    **{i: "Village" for i in range(57, 59)},
    **{i: "Moor" for i in range(59, 61)},
    **{i: "Thicket" for i in range(61, 63)},
    **{i: "River Ford" for i in range(63, 65)},
    **{i: "Valley" for i in range(65, 67)},
    **{i: "Bay/Fjord" for i in range(67, 69)},
    **{i: "Foothills" for i in range(69, 71)},
    **{i: "Lake" for i in range(71, 73)},
    **{i: "River" for i in range(73, 76)},
    **{i: "Forest" for i in range(76, 80)},
    **{i: "Coast" for i in range(80, 84)},
    **{i: "Hill" for i in range(84, 89)},
    **{i: "Mountain" for i in range(89, 94)},
    **{i: "Woods" for i in range(94, 100)},
    100: "Anomaly"
}


COASTAL_ORACLE = {
    1: "Fleet",
    2: "Sargassum",
    3: "Flotsam",
    4: "Mystical Site",
    5: "Lair",
    **{i: "Wreck" for i in range(6, 11)},
    **{i: "Harbor" for i in range(11, 16)},
    **{i: "Ship" for i in range(16, 24)},
    **{i: "Rocks" for i in range(24, 31)},
    **{i: "Fjord" for i in range(31, 39)},
    **{i: "Estuary" for i in range(39, 47)},
    **{i: "Cove" for i in range(47, 55)},
    **{i: "Bay" for i in range(55, 63)},
    **{i: "Ice" for i in range(63, 71)},
    **{i: "Island" for i in range(71, 86)},
    **{i: "Open Water" for i in range(86, 100)},
    100: "Anomaly"
}

REGION_ORACLE = {
    **{i: "Barrier Islands" for i in range(1, 13)},
    **{i: "Ragged Coast" for i in range(13, 25)},
    **{i: "Deep Wilds" for i in range(25, 35)},
    **{i: "Flooded Lands" for i in range(35, 47)},
    **{i: "Havens" for i in range(47, 61)},
    **{i: "Hinterlands" for i in range(61, 73)},
    **{i: "Tempest Hills" for i in range(73, 85)},
    **{i: "Veiled Mountains" for i in range(85, 95)},
    **{i: "Shattered Wastes" for i in range(95, 100)},
    100: "Elsewhere"
}

DESCRIPTOR_ORACLE = {
    **{i: "High" for i in range(1, 3)},
    **{i: "Remote" for i in range(3, 5)},
    **{i: "Exposed" for i in range(5, 7)},
    **{i: "Small" for i in range(7, 9)},
    **{i: "Broken" for i in range(9, 11)},
    **{i: "Diverse" for i in range(11, 13)},
    **{i: "Rough" for i in range(13, 15)},
    **{i: "Dark" for i in range(15, 17)},
    **{i: "Shadowy" for i in range(17, 19)},
    **{i: "Contested" for i in range(19, 21)},
    **{i: "Grim" for i in range(21, 23)},
    **{i: "Wild" for i in range(23, 25)},
    **{i: "Fertile" for i in range(25, 27)},
    **{i: "Blocked" for i in range(27, 29)},
    **{i: "Ancient" for i in range(29, 31)},
    **{i: "Perilous" for i in range(31, 33)},
    **{i: "Hidden" for i in range(33, 35)},
    **{i: "Occupied" for i in range(35, 37)},
    **{i: "Rich" for i in range(37, 39)},
    **{i: "Big" for i in range(39, 41)},
    **{i: "Savage" for i in range(41, 43)},
    **{i: "Defended" for i in range(43, 45)},
    **{i: "Withered" for i in range(45, 47)},
    **{i: "Mystical" for i in range(47, 49)},
    **{i: "Inaccessible" for i in range(49, 51)},
    **{i: "Protected" for i in range(51, 53)},
    **{i: "Abandoned" for i in range(53, 55)},
    **{i: "Wide" for i in range(55, 57)},
    **{i: "Foul" for i in range(57, 59)},
    **{i: "Dead" for i in range(59, 61)},
    **{i: "Ruined" for i in range(61, 63)},
    **{i: "Barren" for i in range(63, 65)},
    **{i: "Cold" for i in range(65, 67)},
    **{i: "Blighted" for i in range(67, 69)},
    **{i: "Low" for i in range(69, 71)},
    **{i: "Beautiful" for i in range(71, 73)},
    **{i: "Abundant" for i in range(73, 75)},
    **{i: "Lush" for i in range(75, 77)},
    **{i: "Flooded" for i in range(77, 79)},
    **{i: "Empty" for i in range(79, 81)},
    **{i: "Strange" for i in range(81, 83)},
    **{i: "Corrupted" for i in range(83, 85)},
    **{i: "Peaceful" for i in range(85, 87)},
    **{i: "Forgotten" for i in range(87, 89)},
    **{i: "Expansive" for i in range(89, 91)},
    **{i: "Settled" for i in range(91, 93)},
    **{i: "Dense" for i in range(93, 95)},
    **{i: "Civilized" for i in range(95, 97)},
    **{i: "Desolate" for i in range(97, 99)},
    **{i: "Isolated" for i in range(99, 101)}
}

async def oracle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the main oracle selection menu."""
    keyboard = []
    row = []
    for i, oracle in enumerate(ORACLES.keys(), 1):
        row.append(InlineKeyboardButton(oracle, callback_data=f"oracle_{oracle}"))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:  # Add any remaining buttons
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔮 Select your Oracle:", reply_markup=reply_markup)

async def oracle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("oracle_"):
        oracle_name = query.data.replace("oracle_", "")
        keyboard = [
            [
                InlineKeyboardButton("🎲 Roll", callback_data=f"roll_{oracle_name}"),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🔮 {oracle_name}\n\n{ORACLES[oracle_name]}",
            reply_markup=reply_markup
        )
    elif query.data.startswith("roll_"):
        oracle_name = query.data.replace("roll_", "")
        await handle_oracle_roll(query, oracle_name)
    elif query.data == "back_to_oracles":
        keyboard = []
        row = []
        for i, oracle in enumerate(ORACLES.keys(), 1):
            row.append(InlineKeyboardButton(oracle, callback_data=f"oracle_{oracle}"))
            if i % 2 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🔮 Select your Oracle:", reply_markup=reply_markup)

# Update the handle_oracle_roll function
async def handle_oracle_roll(query: CallbackQuery, oracle_name: str) -> None:
    """Handle the roll for an oracle"""
    # Generate two random numbers between 1 and 10
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    # Try to delete the original message
    try:
        await query.message.delete()
    except Exception:
        pass

    # Send the dice stickers
    with open("./data/d10_sticker_id.json", "r", encoding="utf-8") as file:
        d10_sticker_id = json.load(file)
    await query.message.reply_sticker(d10_sticker_id[str(num1)])
    await query.message.reply_sticker(d10_sticker_id[str(num2)])

    # Calculate the result number
    result_num = num1 * 10 + num2 if num1 != 10 or num2 != 10 else 100

    # Send the numerical result
    await query.message.reply_text(f"Roll result: {result_num}")

    # Get and send the oracle-specific result
    oracle_results = {
        "Action Oracle": ACTION_ORACLE,
        "Theme Oracle": THEME_ORACLE,
        "Region Oracle": REGION_ORACLE,
        "Location Oracle": LOCATION_ORACLE,
        "Coastal Oracle": COASTAL_ORACLE,
        "Description Oracle": DESCRIPTOR_ORACLE
    }
    
    if oracle_name in oracle_results:
        oracle_result = oracle_results[oracle_name][result_num]
        await query.message.reply_text(f"{oracle_name.split()[0]}: {oracle_result}")
    else:
        await query.message.reply_text("Oracle table not yet implemented")

    # Add buttons to roll again or go back
    keyboard = [
        [
            InlineKeyboardButton("🎲 Roll Again", callback_data=f"roll_{oracle_name}"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    new_message = await query.message.reply_text(text="\u200b", reply_markup=reply_markup)
