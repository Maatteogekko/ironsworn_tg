import random
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ContextTypes,
    CallbackContext,
)

# Oracle data with full descriptions
ORACLES = {
    "Action Oracle": "\n\nUse this table to inspire a discovery, event, character goal, or situation. A roll on this table can be combined with a Theme to provide an action and a subject. Then, interpret the result based on the context of the question and your current situation.",
    "Theme Oracle": "\n\nAs with the Action oracle, this is an interpretative table which you can use to answer questions or generate new situations. Combined, the Action and Theme tables provide creative prompts suitable for most situations and questions. In fact, with some creative interpretations, it's entirely possible to play with only these two tables.",
    "Region Oracle": "\n\nUse this oracle when you want to randomly select a region with the Ironlands.",
    "Location Oracle": "\n\nUse this oracle when traveling to generate a point-of-interest or to answer a question about a place where someone or something can be found. Your roll may generate a place or geographical feature which doesn't make sense in the context of your current location. If so, follow the guidelines to generate a different result (look at adjacent rows or reverse the digits). Or, play off the original answer to introduce something unexpected.",
    "Coastal Oracle": "\n\nUse this oracle to identify a point-of-interest or destination when you are traveling by ship or boat along the coast.",
    "Description Oracle": "\n\nUse this oracle to add detail to the Location or Coastal Waters Location oracles, or by itself to generate a description of a location. Roll more than once for extra detail.",
    "Settlement Name": "\n\nAsk this oracle for a thematic name for an Ironlander settlement. Roll once for the category, and again to pick from the examples. Alternatively, just roll for the category and come up with a name that fits the theme. In either case, consider the meaning of the name and how it impacts this settlement's surroundings, livelihood, culture, or history.",
    "Quick Settlement": "\n\nUse this oracle as a simpler alternative for settlement names. Roll once for the prefix, and once for the suffix. If the combination doesn't quite work, look at adjacent rows or reverse the digits. Once you have your answer, envision what feature, person, or event inspired the name.",
    "Settlement Trouble": "\n\nUse this table to generate a narrative hook for a problem faced by a community. This oracle can help inspire a vow for your character or serve as a prompt for a trouble you encounter when you interact with a settlement. Use other oracles, as appropriate, to help flesh out the answer.",
    "Character Role": "\n\nUse this oracle to define the background for a character, or to generate a random encounter.",
    "Character Goal": "\n\nUse this oracle to define the primary motivation of an NPC or a faction. It can also be used to kick-off a personal quest for your own character.",
    "Character Descriptor": "\n\nUse this oracle to help flesh out a character's personality or physical characteristics. Roll more than once to add additional detail. You can combine all three character oracles (10, 11 and 12), plus a roll on an appropriate name table, to build an outline of an NPC.",
    "Ironlander Names": "\n\nUse this oracle to quickly generate a name for an Ironlander character. Roll on either table. Surnames are not used in the Ironlands and names are often gender-neutral. If a name doesn't fit a character, or you don't like the sound of it, look up or down a row for your answer, or reverse the digits.",
    "Elf Names": "\n\nUse this oracle to generate a name for an elf character.",
    "Other Names": "\n\nUse this oracle for other firstborn characters, including giants, varou, and trolls.",
    "Combat Action": "\n\nUse this oracle to help inspire an action for an NPC in combat. When you're not sure what your foe does next, particularly when they have initiative, roll on this table and interpret the result as appropriate to your foe and the situation.",
    "Mystic Backlash": "\n\nThose who deal in magic may find themselves at the mercy of chaos. This oracle can supplement, or replace, the Pay the Price table when resolving the outcome of a failed ritual or other negative interaction with mystical forces. Use this oracle in dramatic moments, or to introduce an unexpected outcome triggered by a match.",
    "Major Plot Twist": "\n\nUse this oracle to introduce a narrative surprise or revelation. Most of these results have a negative implication, and can be used to resolve a match at a crucial moment in your story. This oracle offers similar results to the Pay the Price table, but is more focused on dramatic events tied to your current quests.",
    "Challenge Rank": "\n\nUse this oracle when you want to randomly determine the challenge rank of a quest, journey, or fight.",
    "Yes/No": '\n\n■ *Almost Certain*: The answer is "yes" if you roll *11 or greater*.\n\n■ *Likely*: The answer is "yes" if you roll *26 or greater*.\n\n■ *50/50*: The answer is "yes" if you roll *51 or greater*.\n\n■ *Unlikely*: The answer is "yes" if you roll *76 or greater*.\n\n■ *Small Chance*: The answer is "yes" if you roll *91 or greater*.',
}

ACTION_ORACLE = {
    100: "Summon",
    1: "Scheme",
    2: "Clash",
    3: "Weaken",
    4: "Initiate",
    5: "Create",
    6: "Swear",
    7: "Avenge",
    8: "Guard",
    9: "Defeat",
    10: "Control",
    11: "Break",
    12: "Risk",
    13: "Surrender",
    14: "Inspect",
    15: "Raid",
    16: "Evade",
    17: "Assault",
    18: "Deflect",
    19: "Threaten",
    20: "Attack",
    21: "Leave",
    22: "Preserve",
    23: "Manipulate",
    24: "Remove",
    25: "Eliminate",
    26: "Withdraw",
    27: "Abandon",
    28: "Investigate",
    29: "Hold",
    30: "Focus",
    31: "Uncover",
    32: "Breach",
    33: "Aid",
    34: "Uphold",
    35: "Falter",
    36: "Suppress",
    37: "Hunt",
    38: "Share",
    39: "Destroy",
    40: "Avoid",
    41: "Reject",
    42: "Demand",
    43: "Explore",
    44: "Bolster",
    45: "Seize",
    46: "Mourn",
    47: "Reveal",
    48: "Gather",
    49: "Defy",
    50: "Transform",
    51: "Persevere",
    52: "Serve",
    53: "Begin",
    54: "Move",
    55: "Coordinate",
    56: "Resist",
    57: "Await",
    58: "Impress",
    59: "Take",
    60: "Oppose",
    61: "Capture",
    62: "Overwhelm",
    63: "Challenge",
    64: "Acquire",
    65: "Protect",
    66: "Finish",
    67: "Strengthen",
    68: "Restore",
    69: "Advance",
    70: "Command",
    71: "Refuse",
    72: "Find",
    73: "Deliver",
    74: "Hide",
    75: "Fortify",
    76: "Betray",
    77: "Secure",
    78: "Arrive",
    79: "Affect",
    80: "Change",
    81: "Defend",
    82: "Debate",
    83: "Support",
    84: "Follow",
    85: "Construct",
    86: "Locate",
    87: "Endure",
    88: "Release",
    89: "Lose",
    90: "Reduce",
    91: "Escalate",
    92: "Distract",
    93: "Journey",
    94: "Escort",
    95: "Learn",
    96: "Communicate",
    97: "Depart",
    98: "Search",
    99: "Charge",
}

THEME_ORACLE = {
    1: "Risk",
    2: "Ability",
    3: "Price",
    4: "Ally",
    5: "Battle",
    6: "Safety",
    7: "Survival",
    8: "Weapon",
    9: "Wound",
    10: "Shelter",
    11: "Leader",
    12: "Fear",
    13: "Time",
    14: "Duty",
    15: "Secret",
    16: "Innocence",
    17: "Renown",
    18: "Direction",
    19: "Death",
    20: "Honor",
    21: "Labor",
    22: "Solution",
    23: "Tool",
    24: "Balance",
    25: "Love",
    26: "Barrier",
    27: "Creation",
    28: "Decay",
    29: "Trade",
    30: "Bond",
    31: "Hope",
    32: "Superstition",
    33: "Peace",
    34: "Deception",
    35: "History",
    36: "World",
    37: "Vow",
    38: "Protection",
    39: "Nature",
    40: "Opinion",
    41: "Burden",
    42: "Vengeance",
    43: "Opportunity",
    44: "Faction",
    45: "Danger",
    46: "Corruption",
    47: "Freedom",
    48: "Debt",
    49: "Hate",
    50: "Possession",
    51: "Stranger",
    52: "Passage",
    53: "Land",
    54: "Creature",
    55: "Disease",
    56: "Advantage",
    57: "Blood",
    58: "Language",
    59: "Rumor",
    60: "Weakness",
    61: "Greed",
    62: "Family",
    63: "Resource",
    64: "Structure",
    65: "Dream",
    66: "Community",
    67: "War",
    68: "Portent",
    69: "Prize",
    70: "Destiny",
    71: "Momentum",
    72: "Power",
    73: "Memory",
    74: "Ruin",
    75: "Mysticism",
    76: "Rival",
    77: "Problem",
    78: "Idea",
    79: "Revenge",
    80: "Health",
    81: "Fellowship",
    82: "Enemy",
    83: "Religion",
    84: "Spirit",
    85: "Fame",
    86: "Desolation",
    87: "Strength",
    88: "Knowledge",
    89: "Truth",
    90: "Quest",
    91: "Pride",
    92: "Loss",
    93: "Law",
    94: "Path",
    95: "Warning",
    96: "Relationship",
    97: "Wealth",
    98: "Home",
    99: "Strategy",
    100: "Supply",
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
    100: "Anomaly",
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
    100: "Anomaly",
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
    100: "Elsewhere",
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
    **{i: "Isolated" for i in range(99, 101)},
}

SETTLEMENT_CATEGORIES = {
    **{i: "A feature of the landscape" for i in range(1, 16)},
    **{i: "A manmade edifice" for i in range(16, 31)},
    **{i: "A creature" for i in range(31, 46)},
    **{i: "A historical event" for i in range(46, 61)},
    **{i: "A word in an Old World language" for i in range(61, 76)},
    **{i: "A season or environmental aspect" for i in range(79, 91)},
    **{i: "Something Else..." for i in range(91, 101)},
}

SETTLEMENT_FEATURES_ORACLE = {
    "A feature of the landscape": (
        "Envision what it is. What makes it unusual or distinctive?",
        {
            **{i: "Highmount" for i in range(1, 11)},
            **{i: "Brackwater" for i in range(11, 21)},
            **{i: "Frostwood" for i in range(21, 31)},
            **{i: "Redcrest" for i in range(31, 41)},
            **{i: "Grimtree" for i in range(41, 51)},
            **{i: "Stoneford" for i in range(51, 61)},
            **{i: "Deepwater" for i in range(61, 71)},
            **{i: "Whitefall" for i in range(71, 81)},
            **{i: "Graycliff" for i in range(81, 91)},
            **{i: "Three Rivers" for i in range(91, 101)},
        },
    ),
    "A manmade edifice": (
        "What is it? Why is it important to this settlement’s history?",
        {
            **{i: "Whitebridge" for i in range(1, 11)},
            **{i: "Lonefort" for i in range(11, 21)},
            **{i: "Highcairn" for i in range(21, 31)},
            **{i: "Redhall" for i in range(31, 41)},
            **{i: "Darkwell" for i in range(41, 51)},
            **{i: "Timberwall" for i in range(51, 61)},
            **{i: "Stonetower" for i in range(61, 71)},
            **{i: "Thornhall" for i in range(71, 81)},
            **{i: "Cinderhome" for i in range(81, 91)},
            **{i: "Fallowfield" for i in range(91, 101)},
        },
    ),
    "A creature": (
        "Why have the people of this settlement chosen this creature as their totem? How is it represented in art or rituals?",
        {
            **{i: "Ravencliff" for i in range(1, 11)},
            **{i: "Bearmark" for i in range(11, 21)},
            **{i: "Wolfcrag" for i in range(21, 31)},
            **{i: "Eaglespire" for i in range(31, 41)},
            **{i: "Wyvern's Rest" for i in range(41, 51)},
            **{i: "Boarwood" for i in range(51, 61)},
            **{i: "Foxhollow" for i in range(61, 71)},
            **{i: "Elderwatch" for i in range(71, 81)},
            **{i: "Elkfield" for i in range(81, 91)},
            **{i: "Dragonshadow" for i in range(91, 101)},
        },
    ),
    "A historical event": (
        "What happened here? What place or practice commemorates this event?",
        {
            **{i: "Swordbreak" for i in range(1, 11)},
            **{i: "Fool's Fall" for i in range(11, 21)},
            **{i: "Firstmeet" for i in range(21, 31)},
            **{i: "Brokenhelm" for i in range(31, 41)},
            **{i: "Mournhaunt" for i in range(41, 51)},
            **{i: "Olgar's Stand" for i in range(51, 61)},
            **{i: "Lostwater" for i in range(61, 71)},
            **{i: "Rojirra's Lament" for i in range(71, 81)},
            **{i: "Lastmarch" for i in range(81, 91)},
            **{i: "Rockfall" for i in range(91, 101)},
        },
    ),
    "A word in an Old World language": (
        "What culture is represented by this word? What does it translate to?",
        {
            **{i: "Abon" for i in range(1, 11)},
            **{i: "Daveza" for i in range(11, 21)},
            **{i: "Damula" for i in range(21, 31)},
            **{i: "Essus" for i in range(31, 41)},
            **{i: "Sina" for i in range(41, 51)},
            **{i: "Kazeera" for i in range(51, 61)},
            **{i: "Khazu" for i in range(61, 71)},
            **{i: "Sova" for i in range(71, 81)},
            **{i: "Nabuma" for i in range(81, 91)},
            **{i: "Tiza" for i in range(91, 101)},
        },
    ),
    "A season or environmental aspect": (
        "What influence does the weather have on this settlement?",
        {
            **{i: "Winterhome" for i in range(1, 11)},
            **{i: "Windhaven" for i in range(11, 21)},
            **{i: "Stormrest" for i in range(21, 31)},
            **{i: "Bleakfrost" for i in range(31, 41)},
            **{i: "Springtide" for i in range(41, 51)},
            **{i: "Duskmoor" for i in range(51, 61)},
            **{i: "Frostcrag" for i in range(61, 71)},
            **{i: "Springbrook" for i in range(71, 81)},
            **{i: "Icebreak" for i in range(81, 91)},
            **{i: "Summersong" for i in range(91, 101)},
        },
    ),
    "Something Else...": (
        "A different kind of inspiration for the settlement's name.",
        {
            **{i: "A trade good (Ironhome)" for i in range(1, 11)},
            **{i: "An Old World city (New Arkesh)" for i in range(11, 21)},
            **{i: "A founder or famous settler (Kei's Hall)" for i in range(21, 31)},
            **{i: "A god (Elisora)" for i in range(31, 41)},
            **{i: "A historical item (Blackhelm)" for i in range(41, 51)},
            **{i: "A firstborn race (Elfbrook)" for i in range(51, 61)},
            **{i: "An elvish word or name (Nessana)" for i in range(61, 71)},
            **{i: "A mythic belief or event (Ghostwalk)" for i in range(71, 81)},
            **{i: "A positive term (Hope)" for i in range(81, 91)},
            **{i: "A negative term (Forsaken)" for i in range(91, 101)},
        },
    ),
}

QUICK_SETTLEMENT_PREFIXES = {
    **{i: "Bleak-" for i in range(1, 5)},
    **{i: "Green-" for i in range(5, 9)},
    **{i: "Wolf-" for i in range(9, 13)},
    **{i: "Raven-" for i in range(13, 17)},
    **{i: "Gray-" for i in range(17, 21)},
    **{i: "Red-" for i in range(21, 25)},
    **{i: "Axe-" for i in range(25, 29)},
    **{i: "Great-" for i in range(29, 33)},
    **{i: "Wood-" for i in range(33, 37)},
    **{i: "Low-" for i in range(37, 41)},
    **{i: "White-" for i in range(41, 45)},
    **{i: "Storm-" for i in range(45, 49)},
    **{i: "Black-" for i in range(49, 53)},
    **{i: "Mourn-" for i in range(53, 57)},
    **{i: "New-" for i in range(57, 61)},
    **{i: "Stone-" for i in range(61, 65)},
    **{i: "Grim-" for i in range(65, 69)},
    **{i: "Lost-" for i in range(69, 73)},
    **{i: "High-" for i in range(73, 77)},
    **{i: "Rock-" for i in range(77, 81)},
    **{i: "Shield-" for i in range(81, 85)},
    **{i: "Sword-" for i in range(85, 89)},
    **{i: "Frost-" for i in range(89, 93)},
    **{i: "Thorn-" for i in range(93, 97)},
    **{i: "Long-" for i in range(97, 101)},
}

QUICK_SETTLEMENT_SUFFIXES = {
    **{i: "-moor" for i in range(1, 5)},
    **{i: "-ford" for i in range(5, 9)},
    **{i: "-crag" for i in range(9, 13)},
    **{i: "-watch" for i in range(13, 17)},
    **{i: "-hope" for i in range(17, 21)},
    **{i: "-wood" for i in range(21, 25)},
    **{i: "-ridge" for i in range(25, 29)},
    **{i: "-stone" for i in range(29, 33)},
    **{i: "-haven" for i in range(33, 37)},
    **{i: "-fall(s)" for i in range(37, 41)},
    **{i: "-river" for i in range(41, 45)},
    **{i: "-field" for i in range(45, 49)},
    **{i: "-hill" for i in range(49, 53)},
    **{i: "-bridge" for i in range(53, 57)},
    **{i: "-mark" for i in range(57, 61)},
    **{i: "-cairn" for i in range(61, 65)},
    **{i: "-land" for i in range(65, 69)},
    **{i: "-hall" for i in range(69, 73)},
    **{i: "-mount" for i in range(73, 77)},
    **{i: "-rock" for i in range(77, 81)},
    **{i: "-brook" for i in range(81, 85)},
    **{i: "-barrow" for i in range(85, 89)},
    **{i: "-stead" for i in range(89, 93)},
    **{i: "-home" for i in range(93, 97)},
    **{i: "-wick" for i in range(97, 101)},
}

SETTLEMENT_TROUBLES = {
    **{i: "Outsiders rejected" for i in range(1, 3)},
    **{i: "Dangerous discovery" for i in range(3, 5)},
    **{i: "Dreadful omens" for i in range(5, 7)},
    **{i: "Natural disaster" for i in range(7, 9)},
    **{i: "Old wounds reopened" for i in range(9, 11)},
    **{i: "Important object is lost" for i in range(11, 13)},
    **{i: "Someone is captured" for i in range(13, 15)},
    **{i: "Mysterious phenomenon" for i in range(15, 17)},
    **{i: "Revolt against a leader" for i in range(17, 19)},
    **{i: "Vengeful outcast" for i in range(19, 21)},
    **{i: "Rival settlement" for i in range(21, 23)},
    **{i: "Nature strikes back" for i in range(23, 25)},
    **{i: "Someone is missing" for i in range(25, 27)},
    **{i: "Production halts" for i in range(27, 29)},
    **{i: "Mysterious murders" for i in range(29, 31)},
    **{i: "Debt comes due" for i in range(31, 33)},
    **{i: "Unjust leadership" for i in range(33, 35)},
    **{i: "Disastrous accident" for i in range(35, 37)},
    **{i: "In league with the enemy" for i in range(37, 39)},
    **{i: "Raiders prey on the weak" for i in range(39, 41)},
    **{i: "Cursed past" for i in range(41, 43)},
    **{i: "An innocent is accused" for i in range(43, 45)},
    **{i: "Corrupted by dark magic" for i in range(45, 47)},
    **{i: "Isolated by brutal weather" for i in range(47, 49)},
    **{i: "Provisions are scarce" for i in range(49, 51)},
    **{i: "Sickness runs amok" for i in range(51, 53)},
    **{i: "Allies become enemies" for i in range(53, 55)},
    **{i: "Attack is imminent" for i in range(55, 57)},
    **{i: "Lost caravan" for i in range(57, 59)},
    **{i: "Dark secret revealed" for i in range(59, 61)},
    **{i: "Urgent expedition" for i in range(61, 63)},
    **{i: "A leader falls" for i in range(63, 65)},
    **{i: "Families in conflict" for i in range(65, 67)},
    **{i: "Incompetent leadership" for i in range(67, 69)},
    **{i: "Reckless warmongering" for i in range(69, 71)},
    **{i: "Beast on the hunt" for i in range(71, 73)},
    **{i: "Betrayed from within" for i in range(73, 75)},
    **{i: "Broken truce" for i in range(75, 77)},
    **{i: "Wrathful haunt" for i in range(77, 79)},
    **{i: "Conflict with firstborn" for i in range(79, 81)},
    **{i: "Trade route blocked" for i in range(81, 83)},
    **{i: "In the crossfire" for i in range(83, 85)},
    **{i: "Stranger causes discord" for i in range(85, 87)},
    **{i: "Important event threatened" for i in range(87, 89)},
    **{i: "Dangerous tradition" for i in range(89, 91)},
    **{i: "Roll twice" for i in range(91, 101)},
}

CHARACTER_ROLE = {
    **{i: "Criminal" for i in range(1, 3)},
    **{i: "Healer" for i in range(3, 5)},
    **{i: "Bandit" for i in range(5, 7)},
    **{i: "Guide" for i in range(7, 10)},
    **{i: "Performer" for i in range(10, 13)},
    **{i: "Miner" for i in range(13, 16)},
    **{i: "Mercenary" for i in range(16, 19)},
    **{i: "Outcast" for i in range(19, 22)},
    **{i: "Vagrant" for i in range(22, 25)},
    **{i: "Forester" for i in range(25, 28)},
    **{i: "Traveler" for i in range(28, 31)},
    **{i: "Mystic" for i in range(31, 34)},
    **{i: "Priest" for i in range(34, 37)},
    **{i: "Sailor" for i in range(37, 40)},
    **{i: "Pilgrim" for i in range(40, 43)},
    **{i: "Thief" for i in range(43, 46)},
    **{i: "Adventurer" for i in range(46, 49)},
    **{i: "Forager" for i in range(49, 52)},
    **{i: "Leader" for i in range(52, 55)},
    **{i: "Guard" for i in range(55, 59)},
    **{i: "Artisan" for i in range(59, 63)},
    **{i: "Scout" for i in range(63, 67)},
    **{i: "Herder" for i in range(67, 71)},
    **{i: "Fisher" for i in range(71, 75)},
    **{i: "Warrior" for i in range(75, 80)},
    **{i: "Hunter" for i in range(80, 85)},
    **{i: "Raider" for i in range(85, 90)},
    **{i: "Trader" for i in range(90, 95)},
    **{i: "Farmer" for i in range(95, 100)},
    100: "Unusual role",
}

CHARACTER_GOAL = {
    **{i: "Obtain an object" for i in range(1, 4)},
    **{i: "Make an agreement" for i in range(4, 7)},
    **{i: "Build a relationship" for i in range(7, 10)},
    **{i: "Undermine a relationship" for i in range(10, 13)},
    **{i: "Seek a truth" for i in range(13, 16)},
    **{i: "Pay a debt" for i in range(16, 19)},
    **{i: "Refute a falsehood" for i in range(19, 22)},
    **{i: "Harm a rival" for i in range(22, 25)},
    **{i: "Cure an ill" for i in range(25, 28)},
    **{i: "Find a person" for i in range(28, 31)},
    **{i: "Find a home" for i in range(31, 34)},
    **{i: "Seize power" for i in range(34, 37)},
    **{i: "Restore a relationship" for i in range(37, 40)},
    **{i: "Create an item" for i in range(40, 43)},
    **{i: "Travel to a place" for i in range(43, 46)},
    **{i: "Secure provisions" for i in range(46, 49)},
    **{i: "Rebel against power" for i in range(49, 52)},
    **{i: "Collect a debt" for i in range(52, 55)},
    **{i: "Protect a secret" for i in range(55, 58)},
    **{i: "Spread faith" for i in range(58, 61)},
    **{i: "Enrich themselves" for i in range(61, 64)},
    **{i: "Protect a person" for i in range(64, 67)},
    **{i: "Protect the status quo" for i in range(67, 70)},
    **{i: "Advance status" for i in range(70, 73)},
    **{i: "Defend a place" for i in range(73, 76)},
    **{i: "Avenge a wrong" for i in range(76, 79)},
    **{i: "Fulfill a duty" for i in range(79, 82)},
    **{i: "Gain knowledge" for i in range(82, 85)},
    **{i: "Prove worthiness" for i in range(85, 88)},
    **{i: "Find redemption" for i in range(88, 91)},
    **{i: "Escape from something" for i in range(91, 93)},
    **{i: "Resolve a dispute" for i in range(93, 96)},
    **{i: "Roll twice" for i in range(96, 101)},
}

CHARACTER_DESCRIPTOR = {
    1: "Stoic",
    2: "Attractive",
    3: "Passive",
    4: "Aloof",
    5: "Affectionate",
    6: "Generous",
    7: "Smug",
    8: "Armed",
    9: "Clever",
    10: "Brave",
    11: "Ugly",
    12: "Sociable",
    13: "Doomed",
    14: "Connected",
    15: "Bold",
    16: "Jealous",
    17: "Angry",
    18: "Active",
    19: "Suspicious",
    20: "Hostile",
    21: "Hardhearted",
    22: "Successful",
    23: "Talented",
    24: "Experienced",
    25: "Deceitful",
    26: "Ambitious",
    27: "Aggressive",
    28: "Conceited",
    29: "Proud",
    30: "Stern",
    31: "Dependent",
    32: "Wary",
    33: "Strong",
    34: "Insightful",
    35: "Dangerous",
    36: "Quirky",
    37: "Cheery",
    38: "Disfigured",
    39: "Intolerant",
    40: "Skilled",
    41: "Stingy",
    42: "Timid",
    43: "Insensitive",
    44: "Wild",
    45: "Bitter",
    46: "Cunning",
    47: "Remorseful",
    48: "Kind",
    49: "Charming",
    50: "Oblivious",
    51: "Critical",
    52: "Cautious",
    53: "Resourceful",
    54: "Weary",
    55: "Wounded",
    56: "Anxious",
    57: "Powerful",
    58: "Athletic",
    59: "Driven",
    60: "Cruel",
    61: "Quiet",
    62: "Honest",
    63: "Infamous",
    64: "Dying",
    65: "Reclusive",
    66: "Artistic",
    67: "Disabled",
    68: "Confused",
    69: "Manipulative",
    70: "Relaxed",
    71: "Stealthy",
    72: "Confident",
    73: "Weak",
    74: "Friendly",
    75: "Wise",
    76: "Influential",
    77: "Young",
    78: "Adventurous",
    79: "Oppressed",
    80: "Vengeful",
    81: "Cooperative",
    82: "Armored",
    83: "Apathetic",
    84: "Determined",
    85: "Loyal",
    86: "Sick",
    87: "Religious",
    88: "Selfish",
    89: "Old",
    90: "Fervent",
    91: "Violent",
    92: "Agreeable",
    93: "Hot-tempered",
    94: "Stubborn",
    95: "Incompetent",
    96: "Greedy",
    97: "Cowardly",
    98: "Obsessed",
    99: "Careless",
    100: "Ironsworn",
}

IRONLANDER_NAMES = {
    1: "Solana",
    2: "Keelan",
    3: "Cadigan",
    4: "Sola",
    5: "Kodroth",
    6: "Kione",
    7: "Katja",
    8: "Tio",
    9: "Artiga",
    10: "Eos",
    11: "Bastien",
    12: "Elli",
    13: "Maura",
    14: "Haleema",
    15: "Abella",
    16: "Morter",
    17: "Wulan",
    18: "Mai",
    19: "Farina",
    20: "Pearce",
    21: "Wynne",
    22: "Haf",
    23: "Aeddon",
    24: "Khinara",
    25: "Milla",
    26: "Nakata",
    27: "Kynan",
    28: "Kiah",
    29: "Jaggar",
    30: "Beca",
    31: "Ikram",
    32: "Melia",
    33: "Sidan",
    34: "Deshi",
    35: "Tessa",
    36: "Sibila",
    37: "Morien",
    38: "Mona",
    39: "Padma",
    40: "Avella",
    41: "Naila",
    42: "Lio",
    43: "Cera",
    44: "Ithela",
    45: "Zhan",
    46: "Kaivan",
    47: "Valeri",
    48: "Hirsham",
    49: "Pemba",
    50: "Edda",
    51: "Lestara",
    52: "Lago",
    53: "Elstan",
    54: "Saskia",
    55: "Kabeera",
    56: "Caldas",
    57: "Nisus",
    58: "Serene",
    59: "Chenda",
    60: "Themon",
    61: "Erin",
    62: "Alban",
    63: "Parcell",
    64: "Jelma",
    65: "Willa",
    66: "Nadira",
    67: "Gwen",
    68: "Amara",
    69: "Masias",
    70: "Kanno",
    71: "Razeena",
    72: "Mira",
    73: "Perella",
    74: "Myrick",
    75: "Qamar",
    76: "Kormak",
    77: "Zura",
    78: "Zanita",
    79: "Brynn",
    80: "Tegan",
    81: "Pendry",
    82: "Quinn",
    83: "Fanir",
    84: "Glain",
    85: "Emelyn",
    86: "Kendi",
    87: "Althus",
    88: "Leela",
    89: "Ishana",
    90: "Flint",
    91: "Delkash",
    92: "Nia",
    93: "Nan",
    94: "Keeara",
    95: "Katania",
    96: "Morell",
    97: "Temir",
    98: "Bas",
    99: "Sabine",
    100: "Tallus",
}

IRONLANDER_NAMES_EXPANSION = {
    1: "Segura",
    2: "Gethin",
    3: "Bataar",
    4: "Basira",
    5: "Joa",
    6: "Glynn",
    7: "Toran",
    8: "Arasen",
    9: "Kuron",
    10: "Griff",
    11: "Owena",
    12: "Adda",
    13: "Euros",
    14: "Kova",
    15: "Kara",
    16: "Morgan",
    17: "Nanda",
    18: "Tamara",
    19: "Asha",
    20: "Delos",
    21: "Torgan",
    22: "Makari",
    23: "Selva",
    24: "Kimura",
    25: "Rhian",
    26: "Tristan",
    27: "Siorra",
    28: "Sayer",
    29: "Cortina",
    30: "Vesna",
    31: "Kataka",
    32: "Keyshia",
    33: "Mila",
    34: "Lili",
    35: "Vigo",
    36: "Sadia",
    37: "Malik",
    38: "Dag",
    39: "Kuno",
    40: "Reva",
    41: "Kai",
    42: "Kalina",
    43: "Jihan",
    44: "Hennion",
    45: "Abram",
    46: "Aida",
    47: "Myrtle",
    48: "Nekun",
    49: "Menna",
    50: "Tahir",
    51: "Sarria",
    52: "Nakura",
    53: "Akiya",
    54: "Talan",
    55: "Mattick",
    56: "Okoth",
    57: "Khulan",
    58: "Verena",
    59: "Beltran",
    60: "Del",
    61: "Ranna",
    62: "Alina",
    63: "Muna",
    64: "Mura",
    65: "Torrens",
    66: "Yuda",
    67: "Nazmi",
    68: "Ghalen",
    69: "Sarda",
    70: "Shona",
    71: "Kalidas",
    72: "Wena",
    73: "Sendra",
    74: "Kori",
    75: "Setara",
    76: "Lucia",
    77: "Maya",
    78: "Reema",
    79: "Yorath",
    80: "Rhoddri",
    81: "Shekhar",
    82: "Servan",
    83: "Reese",
    84: "Kenrick",
    85: "Indirra",
    86: "Giliana",
    87: "Jebran",
    88: "Kotama",
    89: "Fara",
    90: "Katrin",
    91: "Namba",
    92: "Lona",
    93: "Taylah",
    94: "Kato",
    95: "Esra",
    96: "Eleri",
    97: "Irsia",
    98: "Kayu",
    99: "Bevan",
    100: "Chandra",
}

ELF_NAMES = {
    **{i: "Arsula" for i in range(1, 3)},
    **{i: "Naidita" for i in range(3, 5)},
    **{i: "Belesunna" for i in range(5, 7)},
    **{i: "Vidarna" for i in range(7, 9)},
    **{i: "Ninsunu" for i in range(9, 11)},
    **{i: "Balathu" for i in range(11, 13)},
    **{i: "Dorosi" for i in range(13, 15)},
    **{i: "Gezera" for i in range(15, 17)},
    **{i: "Zursan" for i in range(17, 19)},
    **{i: "Seleeku" for i in range(19, 21)},
    **{i: "Utamara" for i in range(21, 23)},
    **{i: "Nebakay" for i in range(23, 25)},
    **{i: "Dismashk" for i in range(25, 27)},
    **{i: "Mitunu" for i in range(27, 29)},
    **{i: "Atani" for i in range(29, 31)},
    **{i: "Kinzura" for i in range(31, 33)},
    **{i: "Sumula" for i in range(33, 35)},
    **{i: "Ukames" for i in range(35, 37)},
    **{i: "Ahmeshki" for i in range(37, 39)},
    **{i: "Ilsit" for i in range(39, 41)},
    **{i: "Mayatanay" for i in range(41, 43)},
    **{i: "Etana" for i in range(43, 45)},
    **{i: "Gamanna" for i in range(45, 47)},
    **{i: "Nessana" for i in range(47, 49)},
    **{i: "Uralar" for i in range(49, 51)},
    **{i: "Tishetu" for i in range(51, 53)},
    **{i: "Leucia" for i in range(53, 55)},
    **{i: "Sutahe" for i in range(55, 57)},
    **{i: "Dotani" for i in range(57, 59)},
    **{i: "Uktannu" for i in range(59, 61)},
    **{i: "Retenay" for i in range(61, 63)},
    **{i: "Kendalanu" for i in range(63, 65)},
    **{i: "Tahuta" for i in range(65, 67)},
    **{i: "Mattissa" for i in range(67, 69)},
    **{i: "Anatu" for i in range(69, 71)},
    **{i: "Aralu" for i in range(71, 73)},
    **{i: "Arakhi" for i in range(73, 75)},
    **{i: "Ibrahem" for i in range(75, 77)},
    **{i: "Sinosu" for i in range(77, 79)},
    **{i: "Jemshida" for i in range(79, 81)},
    **{i: "Visapni" for i in range(81, 83)},
    **{i: "Hullata" for i in range(83, 85)},
    **{i: "Sidura" for i in range(85, 87)},
    **{i: "Kerihu" for i in range(87, 89)},
    **{i: "Ereshki" for i in range(89, 91)},
    **{i: "Cybela" for i in range(91, 93)},
    **{i: "Anunna" for i in range(93, 95)},
    **{i: "Otani" for i in range(95, 97)},
    **{i: "Ditani" for i in range(97, 99)},
    99: "Faraza",
    100: "Faraza",
}

COMBAT_ACTION = {
    **{i: "Compel a surrender." for i in range(1, 4)},
    **{i: "Coordinate with allies." for i in range(4, 7)},
    **{i: "Gather reinforcements." for i in range(7, 10)},
    **{i: "Seize something or someone." for i in range(10, 14)},
    **{i: "Provoke a reckless response." for i in range(14, 18)},
    **{i: "Intimidate or frighten." for i in range(18, 22)},
    **{i: "Reveal a surprising truth." for i in range(22, 26)},
    **{i: "Shift focus to someone or something else." for i in range(26, 30)},
    **{i: "Destroy something, or render it useless." for i in range(30, 34)},
    **{i: "Take a decisive action." for i in range(34, 40)},
    **{i: "Reinforce defenses." for i in range(40, 46)},
    **{i: "Ready an action." for i in range(46, 53)},
    **{i: "Use the terrain to gain advantage." for i in range(53, 61)},
    **{i: "Leverage the advantage of a weapon or ability." for i in range(61, 69)},
    **{i: "Create an opportunity." for i in range(69, 79)},
    **{i: "Attack with precision." for i in range(79, 90)},
    **{i: "Attack with power." for i in range(90, 100)},
    100: "Take a completely unexpected action.",
}

MYSTIC_BACKLASH = {
    **{i: "Your ritual has the opposite effect." for i in range(1, 5)},
    **{i: "You are sapped of strength." for i in range(5, 9)},
    **{
        i: "Your friend, ally, or companion is adversely affected."
        for i in range(9, 13)
    },
    **{i: "You destroy an important object." for i in range(13, 17)},
    **{i: "You inadvertently summon a horror." for i in range(17, 21)},
    **{i: "You collapse, and drift into a troubled sleep." for i in range(21, 25)},
    **{
        i: "You undergo a physical torment which leaves its mark upon you."
        for i in range(25, 29)
    },
    **{
        i: "You hear ghostly voices whispering of dark portents." for i in range(29, 33)
    },
    **{
        i: "You are lost in shadow, and find yourself in another place without memory of how you got there."
        for i in range(33, 37)
    },
    **{i: "You alert someone or something to your presence." for i in range(37, 41)},
    **{
        i: "You are not yourself, and act against a friend, ally, or companion."
        for i in range(41, 45)
    },
    **{
        i: "You affect or damage your surroundings, causing a disturbance or potential harm."
        for i in range(45, 49)
    },
    **{i: "You waste resources." for i in range(49, 53)},
    **{i: "You suffer the loss of a sense for several hours." for i in range(53, 57)},
    **{
        i: "You lose your connection to magic for a day or so, and cannot perform rituals."
        for i in range(57, 61)
    },
    **{
        i: "Your ritual affects the target in an unexpected and problematic way."
        for i in range(61, 65)
    },
    **{
        i: "Your ritual reveals a surprising and troubling truth."
        for i in range(65, 69)
    },
    **{i: "You are tempted by dark powers." for i in range(69, 73)},
    **{i: "You see a troubling vision of your future." for i in range(73, 77)},
    **{
        i: "You can't perform this ritual again until you acquire an important component."
        for i in range(77, 81)
    },
    **{i: "You develop a strange fear or compulsion." for i in range(81, 85)},
    **{
        i: "Your ritual causes creatures to exhibit strange or aggressive behavior."
        for i in range(85, 89)
    },
    **{i: "You are tormented by an apparition from your past." for i in range(89, 93)},
    **{i: "You are wracked with sudden sickness." for i in range(93, 97)},
    **{
        i: "Roll twice more on this table. Both results occur. If they are the same result, make it worse."
        for i in range(97, 101)
    },
}

MAJOR_PLOT_TWIST = {
    **{i: "It was all a diversion." for i in range(1, 6)},
    **{i: "A dark secret is revealed." for i in range(6, 11)},
    **{i: "A trap is sprung." for i in range(11, 16)},
    **{i: "An assumption is revealed to be false." for i in range(16, 21)},
    **{i: "A secret alliance is revealed." for i in range(21, 26)},
    **{i: "Your actions benefit an enemy." for i in range(26, 31)},
    **{i: "Someone returns unexpectedly." for i in range(31, 36)},
    **{i: "A more dangerous foe is revealed." for i in range(36, 41)},
    **{i: "You and an enemy share a common goal." for i in range(41, 46)},
    **{i: "A true identity is revealed." for i in range(46, 51)},
    **{i: "You are betrayed by someone who was trusted." for i in range(51, 56)},
    **{i: "You are too late." for i in range(56, 61)},
    **{i: "The true enemy is revealed." for i in range(61, 66)},
    **{i: "The enemy gains new allies." for i in range(66, 71)},
    **{i: "A new danger appears." for i in range(71, 76)},
    **{i: "Someone or something goes missing." for i in range(76, 81)},
    **{i: "The truth of a relationship is revealed." for i in range(81, 86)},
    **{
        i: "Two seemingly unrelated situations are shown to be connected."
        for i in range(86, 91)
    },
    **{i: "Unexpected powers or abilities are revealed." for i in range(91, 96)},
    **{
        i: "Roll twice more on this table. Both results occur. If they are the same result, make it more dramatic."
        for i in range(96, 101)
    },
}

CHALLENGE_RANK = {
    **{i: "Troublesome" for i in range(1, 21)},
    **{i: "Dangerous" for i in range(21, 56)},
    **{i: "Formidable" for i in range(56, 81)},
    **{i: "Extreme" for i in range(81, 94)},
    **{i: "Epic" for i in range(94, 101)},
}

OTHER_NAMES = {
    "Giants": {
        **{i: "Chony" for i in range(1, 5)},
        **{i: "Banda" for i in range(5, 9)},
        **{i: "Jochu" for i in range(9, 13)},
        **{i: "Kira" for i in range(13, 17)},
        **{i: "Khatir" for i in range(17, 21)},
        **{i: "Chaidu" for i in range(21, 25)},
        **{i: "Atan" for i in range(25, 29)},
        **{i: "Buandu" for i in range(29, 33)},
        **{i: "Javyn" for i in range(33, 37)},
        **{i: "Khashin" for i in range(37, 41)},
        **{i: "Bayara" for i in range(41, 45)},
        **{i: "Temura" for i in range(45, 49)},
        **{i: "Kidha" for i in range(49, 53)},
        **{i: "Kathos" for i in range(53, 57)},
        **{i: "Tanua" for i in range(57, 61)},
        **{i: "Bashtu" for i in range(61, 65)},
        **{i: "Jaran" for i in range(65, 69)},
        **{i: "Othos" for i in range(69, 73)},
        **{i: "Khutan" for i in range(73, 77)},
        **{i: "Otaan" for i in range(77, 81)},
        **{i: "Martu" for i in range(81, 85)},
        **{i: "Baku" for i in range(85, 89)},
        **{i: "Tuban" for i in range(89, 93)},
        **{i: "Qudan" for i in range(93, 97)},
        **{i: "Denua" for i in range(97, 101)},
    },
    "Varou": {
        **{i: "Vata" for i in range(1, 5)},
        **{i: "Zora" for i in range(5, 9)},
        **{i: "Jasna" for i in range(9, 13)},
        **{i: "Charna" for i in range(13, 17)},
        **{i: "Tana" for i in range(17, 21)},
        **{i: "Soveen" for i in range(21, 25)},
        **{i: "Radka" for i in range(25, 29)},
        **{i: "Zlata" for i in range(29, 33)},
        **{i: "Leesla" for i in range(33, 37)},
        **{i: "Byna" for i in range(37, 41)},
        **{i: "Meeka" for i in range(41, 45)},
        **{i: "Iskra" for i in range(45, 49)},
        **{i: "Jarek" for i in range(49, 53)},
        **{i: "Darva" for i in range(53, 57)},
        **{i: "Neda" for i in range(57, 61)},
        **{i: "Keha" for i in range(61, 65)},
        **{i: "Zhivka" for i in range(65, 69)},
        **{i: "Kvata" for i in range(69, 73)},
        **{i: "Staysa" for i in range(73, 77)},
        **{i: "Evka" for i in range(77, 81)},
        **{i: "Vuksha" for i in range(81, 85)},
        **{i: "Muko" for i in range(85, 89)},
        **{i: "Dreko" for i in range(89, 93)},
        **{i: "Aleko" for i in range(93, 97)},
        **{i: "Vojan" for i in range(97, 101)},
    },
    "Trolls": {
        **{i: "Rattle" for i in range(1, 5)},
        **{i: "Scratch" for i in range(5, 9)},
        **{i: "Wallow" for i in range(9, 13)},
        **{i: "Groak" for i in range(13, 17)},
        **{i: "Gimble" for i in range(17, 21)},
        **{i: "Scar" for i in range(21, 25)},
        **{i: "Cratch" for i in range(25, 29)},
        **{i: "Creech" for i in range(29, 33)},
        **{i: "Shush" for i in range(33, 37)},
        **{i: "Glush" for i in range(37, 41)},
        **{i: "Slar" for i in range(41, 45)},
        **{i: "Gnash" for i in range(45, 49)},
        **{i: "Stoad" for i in range(49, 53)},
        **{i: "Grig" for i in range(53, 57)},
        **{i: "Bleat" for i in range(57, 61)},
        **{i: "Chortle" for i in range(61, 65)},
        **{i: "Cluck" for i in range(65, 69)},
        **{i: "Slith" for i in range(69, 73)},
        **{i: "Mongo" for i in range(73, 77)},
        **{i: "Creak" for i in range(77, 81)},
        **{i: "Burble" for i in range(81, 85)},
        **{i: "Vrusk" for i in range(85, 89)},
        **{i: "Snuffle" for i in range(89, 93)},
        **{i: "Leech" for i in range(93, 97)},
        **{i: "Herk" for i in range(97, 101)},
    },
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
    await update.message.reply_text(
        "*ASK THE ORACLE*\n\nSelect your Oracle:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def oracle_button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles button callbacks."""
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id  # Get the chat ID from the original message

    if query.data.startswith("oracle_"):

        oracle_name = query.data.replace("oracle_", "")

        if oracle_name == "Settlement Name":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "A feature of the landscape",
                        callback_data="settlement_feature",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "A manmade edifice", callback_data="settlement_edifice"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "A creature", callback_data="settlement_creature"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "A historical event", callback_data="settlement_event"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "A word in an Old World language",
                        callback_data="settlement_word",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "A season or environmental aspect",
                        callback_data="settlement_season",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Something Else...", callback_data="settlement_else"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🎲 Roll category", callback_data="settlement_roll"
                    )
                ],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles")],
            ]
            text = "*Settlement name* \n\nYou can either choose a category, or roll for it."
        elif oracle_name == "Quick Settlement":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎲🎲 Roll", callback_data=f"roll_{oracle_name}"
                    ),
                    InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles"),
                ]
            ]
            text = f"{'*'+oracle_name+'*'}{ORACLES[oracle_name]}"

        elif oracle_name == "Other Names":
            keyboard = [
                [InlineKeyboardButton("Giants", callback_data="other_names_Giants")],
                [InlineKeyboardButton("Varou", callback_data="other_names_Varou")],
                [InlineKeyboardButton("Trolls", callback_data="other_names_Trolls")],
            ]
            text = "*Other Names* \n\nPick a race from which to choose."
        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎲 Roll", callback_data=f"roll_{oracle_name}"
                    ),
                    InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles"),
                ]
            ]
            text = f"{'*'+oracle_name+'*'}{ORACLES[oracle_name]}"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=reply_markup
        )

    elif query.data.startswith("settlement_"):
        try:
            await query.message.delete()
        except Exception:
            pass
        if query.data == "settlement_roll":
            # Generate two random numbers between 1 and 10
            num1 = random.randint(0, 9)
            num2 = random.randint(0, 9)
            with open("./data/d10_sticker_id.json", "r", encoding="utf-8") as file:
                d10_sticker_id = json.load(file)
            await context.bot.send_sticker(chat_id, d10_sticker_id[str(num1)])
            await context.bot.send_sticker(chat_id, d10_sticker_id[str(num2)])
            result_num = num1 * 10 + num2 if num1 != 0 or num2 != 0 else 100
            oracle_result = SETTLEMENT_CATEGORIES[result_num]
            # Send the result
        else:
            sett_results = {
                "feature": "A feature of the landscape",
                "edifice": "A manmade edifice",
                "creature": "A creature",
                "event": "A historical event",
                "word": "A word in an Old World language",
                "season": "A season or environmental aspect",
                "else": "Something Else...",
            }
            oracle_result = sett_results[query.data.replace("settlement_", "")]

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎲 Roll", callback_data=f"roll_settlement_{oracle_result}"
                ),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_settlements"),
            ]
        ]
        text = f"{'*'+oracle_result+'*' }\n\n{SETTLEMENT_FEATURES_ORACLE[oracle_result][0]}"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id, text, parse_mode="Markdown", reply_markup=reply_markup
        )

    elif query.data.startswith("other_names_"):
        try:
            await query.message.delete()
        except Exception:
            pass
        other_names = query.data.replace("other_names_", "")

        keyboard = [
            [
                InlineKeyboardButton(
                    "Giants" + (" ✅" if other_names == "Giants" else " ❌"),
                    callback_data="other_names_Giants",
                )
            ],
            [
                InlineKeyboardButton(
                    "Varou" + (" ✅" if other_names == "Varou" else " ❌"),
                    callback_data="other_names_Varou",
                )
            ],
            [
                InlineKeyboardButton(
                    "Trolls" + (" ✅" if other_names == "Trolls" else " ❌"),
                    callback_data="other_names_Trolls",
                )
            ],
            [InlineKeyboardButton("🎲 Roll", callback_data=f"roll_{query.data}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles")],
        ]
        text = f"{'*Other Names: '+other_names+'*' }\n\nYou can roll for {other_names} names or choose another race."
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id, text, parse_mode="Markdown", reply_markup=reply_markup
        )

    elif query.data.startswith("roll_"):
        oracle_name = query.data.replace("roll_", "")
        await handle_oracle_roll(query, oracle_name, context)

    elif query.data == "back_to_settlements":
        keyboard = [
            [
                InlineKeyboardButton(
                    "A feature of the landscape", callback_data="settlement_feature"
                )
            ],
            [
                InlineKeyboardButton(
                    "A manmade edifice", callback_data="settlement_edifice"
                )
            ],
            [InlineKeyboardButton("A creature", callback_data="settlement_creature")],
            [
                InlineKeyboardButton(
                    "A historical event", callback_data="settlement_event"
                )
            ],
            [
                InlineKeyboardButton(
                    "A word in an Old World language", callback_data="settlement_word"
                )
            ],
            [
                InlineKeyboardButton(
                    "A season or environmental aspect",
                    callback_data="settlement_season",
                )
            ],
            [
                InlineKeyboardButton(
                    "Something Else...", callback_data="settlement_else"
                )
            ],
            [InlineKeyboardButton("🎲 Roll category", callback_data="settlement_roll")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles")],
        ]
        text = "*Settlement name* \n\nYou can either choose a category, or roll for it."
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=reply_markup
        )

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
        await query.edit_message_text(
            "*ASK THE ORACLE*\n\nSelect your Oracle:",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


# Update the handle_oracle_roll function
async def handle_oracle_roll(
    query: CallbackQuery, oracle_name: str, context: CallbackContext
) -> None:
    """Handle the roll for an oracle"""
    # Generate two random numbers between 1 and 10
    num1 = random.randint(0, 9)
    num2 = random.randint(0, 9)

    # Try to delete the original message
    try:
        await query.message.delete()
    except Exception:
        pass

    # Load the dice stickers
    with open("./data/d10_sticker_id.json", "r", encoding="utf-8") as file:
        d10_sticker_id = json.load(file)

    # Use the chat ID from the query to send the stickers directly
    chat_id = query.message.chat.id  # Get the chat ID from the original message

    # Send the stickers directly to the chat
    await context.bot.send_sticker(chat_id, d10_sticker_id[str(num1)])
    await context.bot.send_sticker(chat_id, d10_sticker_id[str(num2)])

    # Calculate the result number
    result_num = num1 * 10 + num2 if num1 != 0 or num2 != 0 else 100

    # Get and send the oracle-specific result
    oracle_results = {
        "Action Oracle": ACTION_ORACLE,
        "Theme Oracle": THEME_ORACLE,
        "Region Oracle": REGION_ORACLE,
        "Location Oracle": LOCATION_ORACLE,
        "Coastal Oracle": COASTAL_ORACLE,
        "Description Oracle": DESCRIPTOR_ORACLE,
        "Settlement Troubles": SETTLEMENT_TROUBLES,
        "Character Role": CHARACTER_ROLE,
        "Character Goal": CHARACTER_GOAL,
        "Character Descriptor": CHARACTER_DESCRIPTOR,
        "Elf Names": ELF_NAMES,
        "Combat Action": COMBAT_ACTION,
        "Mystic Backlash": MYSTIC_BACKLASH,
        "Major Plot Twist": MAJOR_PLOT_TWIST,
        "Challenge Rank": CHALLENGE_RANK,
    }

    result_num2 = -1
    chat_id = query.message.chat.id  # Get the chat ID from the original message
    if oracle_name in oracle_results:
        oracle_result = oracle_results[oracle_name][result_num]
        await context.bot.send_message(
            chat_id, f"{oracle_name.split()[0]}: {oracle_result}"
        )
    elif oracle_name.startswith("settlement_"):
        oracle_sett = oracle_name.split("_")[1]
        await context.bot.send_message(
            chat_id,
            f"{oracle_sett}: {SETTLEMENT_FEATURES_ORACLE[oracle_sett][1][result_num]}",
        )
    elif oracle_name.startswith("other_names_"):
        oracle_other = oracle_name.replace("other_names_", "")
        await context.bot.send_message(
            chat_id, f"{oracle_other}: {OTHER_NAMES[oracle_other][result_num]}"
        )
    elif oracle_name == "Quick Settlement":
        num1 = random.randint(0, 9)
        num2 = random.randint(0, 9)
        with open("./data/d10_sticker_id.json", "r", encoding="utf-8") as file:
            d10_sticker_id = json.load(file)
        chat_id = query.message.chat.id  # Get the chat ID from the original message
        await context.bot.send_sticker(chat_id, d10_sticker_id[str(num1)])
        await context.bot.send_sticker(chat_id, d10_sticker_id[str(num2)])
        result_num2 = num1 * 10 + num2 if num1 != 0 or num2 != 0 else 100
        await context.bot.send_message(
            chat_id,
            f"{oracle_name}: {QUICK_SETTLEMENT_PREFIXES[result_num].replace('-','')}{QUICK_SETTLEMENT_SUFFIXES[result_num2].replace('-','')}",
        )
    elif oracle_name == "Ironlander Names":
        num = random.randint(0, 1)
        if num == 0:
            await context.bot.send_message(
                chat_id, f"{oracle_name}: {IRONLANDER_NAMES[result_num]}"
            )
        else:
            await context.bot.send_message(
                chat_id, f"{oracle_name}: {IRONLANDER_NAMES_EXPANSION[result_num]}"
            )

    if result_num2 != -1:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎲🎲 Roll Again", callback_data=f"roll_{oracle_name}"
                ),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id,
            f"First Roll result: {result_num}\nSecond Roll result: {result_num2}",
            reply_markup=reply_markup,
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎲 Roll Again", callback_data=f"roll_{oracle_name}"
                ),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_oracles"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id, f"Roll result: {result_num}", reply_markup=reply_markup
        )
