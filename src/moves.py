from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.utils import cancel, end_conversation, flip_page, split_text

# Define states
SHOWING_MOVES = 0


async def moves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    keyboard = [
        [InlineKeyboardButton("Adventure", callback_data="adventure")],
        [InlineKeyboardButton("Relationship", callback_data="relationship")],
        [InlineKeyboardButton("Combat", callback_data="combat")],
        [InlineKeyboardButton("Suffer", callback_data="suffer")],
        [InlineKeyboardButton("Quest", callback_data="quest")],
        [InlineKeyboardButton("Fate", callback_data="fate")],
        [InlineKeyboardButton("Indietro", callback_data="back_to_zero")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message is None:
        # Non so esattamente come fixarlo meglio; Quando premi indietro su adventure_callback o gli altri, dovresti tornare qui. Ma non c'è un messaggio, ergo l'if.
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Scegli il tipo di mossa", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Scegli il tipo di mossa", reply_markup=reply_markup
        )

    return SHOWING_MOVES


async def generic_move_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, move_name: str
):
    del context

    query = update.callback_query
    await query.answer()

    text = f"{move_name} - Placeholder text"
    back_type = "back_to_adventure"  # default
    match move_name:
        case "Face Danger":
            text = (
                "FACE DANGER\n\n"
                "When you attempt something risky or react to an imminent threat, envision your action and roll. If you act...\n\n"
                "• With speed, agility, or precision: Roll +edge.\n"
                "• With charm, loyalty, or courage: Roll +heart.\n"
                "• With aggressive action, forceful defense, strength, or endurance: Roll +iron.\n"
                "• With deception, stealth, or trickery: Roll +shadow.\n"
                "• With expertise, insight, or observation: Roll +wits.\n\n"
                "On a *strong hit*, you are successful. Take +1 momentum.\n\n"
                "On a *weak hit*, you succeed, but face a troublesome cost. Choose one.\n"
                "• You are delayed, lose advantage, or face a new danger: Suffer -1 momentum.\n"
                "• You are tired or hurt: _Endure Harm_ (1 harm).\n"
                "• You are dispirited or afraid: _Endure Stress_ (1 stress).\n"
                "• You sacrifice resources: Suffer -1 supply.\n\n"
                "On a *miss*, you fail, or your progress is undermined by a dramatic and costly turn of events. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Secure Advantage":
            text = (
                "*SECURE AN ADVANTAGE*\n\n"
                "When *you assess a situation, make preparations, or attempt to gain leverage*, envision your action and roll. If you act...\n\n"
                "• With speed, agility, or precision: Roll +edge.\n"
                "• With charm, loyalty, or courage: Roll +heart.\n"
                "• With aggressive action, forceful defense, strength, or endurance: Roll +iron.\n"
                "• With deception, stealth, or trickery: Roll +shadow.\n"
                "• With expertise, insight, or observation: Roll +wits.\n\n"
                "On a *strong hit*, you gain advantage. Choose one.\n"
                "• Take control: Make another move now (not a progress move); when you do, add +1.\n"
                "• Prepare to act: Take +2 momentum.\n\n"
                "On a *weak hit*, your advantage is short-lived. Take +1 momentum.\n\n"
                "On a *miss*, you fail or your assumptions betray you. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Gather Information":
            text = (
                "*GATHER INFORMATION*\n\n"
                "When *you search an area, ask questions, conduct an investigation, or follow a track*, roll +wits. If you act within a community or ask questions of a person with whom you share a bond, add +1.\n\n"
                "On a *strong hit*, you discover something helpful and specific. The path you must follow or action you must take to make progress is made clear. Envision what you learn (_Ask the Oracle_ if unsure), and take +2 momentum.\n\n"
                "On a *weak hit*, the information complicates your quest or introduces a new danger. Envision what you discover (_Ask the Oracle_ if unsure), and take +1 momentum.\n\n"
                "On a *miss*, your investigation unearths a dire threat or reveals an unwelcome truth that undermines your quest. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Heal":
            text = (
                "*HEAL*\n\n"
                "When *you treat an injury or ailment*, roll +wits. If you are mending your own wounds, roll +wits or +iron, whichever is lower.\n\n"
                "On a *strong hit*, your care is helpful. If you (or the ally under your care) have the wounded condition, you may clear it. Then, take or give up to +2 health.\n\n"
                "On a *weak hit*, as above, but you must suffer -1 supply or -1 momentum (your choice).\n\n"
                "On a *miss*, your aid is ineffective. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Resupply":
            text = (
                "*RESUPPLY*\n\n"
                "When *you hunt, forage, or scavenge*, roll +wits.\n\n"
                "On a *strong hit*, you bolster your resources. Take +2 supply.\n\n"
                "On a *weak hit*, take up to +2 supply, but suffer -1 momentum for each.\n\n"
                "On a *miss*, you find nothing helpful. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Make Camp":
            text = (
                "*MAKE CAMP*\n\n"
                "When *you rest and recover for several hours in the wild*, roll +supply.\n\n"
                "On a *strong hit*, you and your allies may each choose two.\n\n"
                "On a *weak hit*, choose one.\n\n"
                "• Recuperate: Take +1 health for you and any companions.\n"
                "• Partake: Suffer -1 supply and take +1 health for you and any companions.\n"
                "• Relax: Take +1 spirit.\n"
                "• Focus: Take +1 momentum.\n"
                "• Prepare: When you break camp, add +1 if you _Undertake a Journey_.\n\n"
                "On a *miss*, you take no comfort. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Undertake Journey":
            text = (
                "*UNDERTAKE A JOURNEY*\n\n"
                "When *you travel across hazardous or unfamiliar lands*, first set the rank of your journey.\n"
                "• Troublesome journey: 3 progress per waypoint.\n"
                "• Dangerous journey: 2 progress per waypoint.\n"
                "• Formidable journey: 1 progress per waypoint.\n"
                "• Extreme journey: 2 ticks per waypoint.\n"
                "• Epic journey: 1 tick per waypoint.\n\n"
                "Then, for each segment of your journey, roll +wits. If you are setting off from a community with which you share a bond, add +1 to your initial roll.\n\n"
                "On a *strong hit*, you reach a waypoint. If the waypoint is unknown to you, envision it (_Ask the Oracle_ if unsure). Then, choose one.\n"
                "• You make good use of your resources: Mark progress.\n"
                "• You move at speed: Mark progress and take +1 momentum, but suffer -1 supply.\n\n"
                "On a *weak hit*, you reach a waypoint and mark progress, but suffer -1 supply.\n\n"
                "On a *miss*, you are waylaid by a perilous event. _Pay the Price_."
            )
            back_type = "back_to_adventure"

        case "Reach Destination":
            text = (
                "*REACH YOUR DESTINATION*\n\n"
                "*Progress Move*\n\n"
                "When *your journey comes to an end*, roll the challenge dice and compare to your progress. Momentum is ignored on this roll.\n\n"
                "On a *strong hit*, the situation at your destination favors you. Choose one.\n"
                "• Make another move now (not a progress move), and add +1.\n"
                "• Take +1 momentum.\n\n"
                "On a *weak hit*, you arrive but face an unforeseen hazard or complication. Envision what you find (_Ask the Oracle_ if unsure).\n\n"
                "On a *miss*, you have gone hopelessly astray, your objective is lost to you, or you were misled about your destination. If your journey continues, clear all but one filled progress, and raise the journey's rank by one (if not already epic)."
            )
            back_type = "back_to_adventure"

        case "Compel":
            text = (
                "*COMPEL*\n\n"
                "When you *attempt to persuade someone to do something*, envision your approach and roll. If you...\n\n"
                "• Charm, pacify, barter, or convince: Roll +heart (add +1 if you share a bond).\n"
                "• Threaten or incite: Roll +iron.\n"
                "• Lie or swindle: Roll +shadow.\n\n"
                "On a *strong hit*, they’ll do what you want or share what they know. Take +1 momentum. If you use this exchange to _Gather Information_, make that move now and add +1.\n\n"
                "On a *weak hit*, as above, but they ask something of you in return. Envision what they want (_Ask the Oracle_ if unsure).\n\n"
                "On a *miss*, they refuse or make a demand which costs you greatly. _Pay the Price_."
            )
            back_type = "back_to_relationship"

        case "Sojourn":
            text = (
                "*SOJOURN*\n\n"
                "When you spend time in a community seeking assistance, roll +heart. If you share a bond, add +1.\n\n"
                "On a *strong hit*, you and your allies may each choose two from within the categories below. On a *weak hit*, choose one. If you share a bond, choose one more.\n\n"
                "On a hit, you and your allies may each focus on one of your chosen recover actions and roll +heart again. If you share a bond, add +1.\n"
                "On a strong hit, take +2 more for that action. On a weak hit, take +1 more. On a miss, it goes badly and you lose all benefits for that action.\n\n"
                "*Clear a Condition*\n"
                "• Mend: Clear a wounded debility and take +1 health.\n"
                "• Hearten: Clear a shaken debility and take +1 spirit.\n"
                "• Equip: Clear an unprepared debility and take +1 supply.\n\n"
                "*Recover*\n"
                "• Recuperate: Take +2 health for yourself and any companions.\n"
                "• Consort: Take +2 spirit.\n"
                "• Provision: Take +2 supply.\n"
                "• Plan: Take +2 momentum.\n\n"
                "*Provide Aid*\n"
                "• Take a quest: Envision what this community needs, or what trouble it is facing (_Ask the Oracle_ if unsure). If you choose to help, Swear an Iron Vow and add +1.\n\n"
                "On a *miss*, you find no help here. Pay the Price."
            )
            back_type = "back_to_relationship"

        case "Draw Circle":
            text = (
                "*DRAW THE CIRCLE*\n\n"
                "When *you challenge someone to a formal duel, or accept a challenge*, roll +heart. If you share a bond with this community, add +1.\n\n"
                "On a *strong hit*, take +1 momentum. You may also choose up to three boasts and take +1 momentum for each.\n\n"
                "On a *weak hit*, you may choose one boast in exchange for +1 momentum.\n\n"
                "• Grant first strike: Your foe has initiative.\n"
                "• Bare yourself: Take no benefit of armor or shield; your foe’s harm is +1.\n"
                "• Hold no iron: Take no benefit of weapons; your harm is 1.\n"
                "• Bloody yourself: Endure Harm (1 harm).\n"
                "• To the death: One way or another, this fight must end with death.\n\n"
                "On a *miss*, you begin the duel at a disadvantage. Your foe has initiative. Pay the Price.\n\n"
                "Then, make moves to resolve the fight. If you are the victor, you may make a lawful demand, and your opponent must comply or forfeit their honor and standing. If you refuse the challenge, surrender, or are defeated, they make a demand of you."
            )
            back_type = "back_to_relationship"
        
        case "Forge Bond":
            text = (
                "*FORGE A BOND*\n\n"
                "When you spend significant time with a person or community, stand together to face hardships, or make sacrifices for their cause, you can attempt to create a bond. When you do, roll +heart. If you make this move after you successfully _Fulfill Your Vow_ to their benefit, you may reroll any dice.\n\n"
                "On a *strong hit*, make note of the bond, mark a tick on your bond progress track, and choose one.\n"
                "• Take +1 spirit.\n"
                "• Take +2 momentum.\n\n"
                "On a *weak hit*, they ask something more of you first. Envision what it is (_Ask the Oracle_ if unsure), do it (or _Swear an Iron Vow_), and mark the bond. If you decline or fail, _Pay the Price_.\n\n"
                "On a *miss*, you are refused. _Pay the Price_."
            )
            back_type = "back_to_relationship"

    keyboard = [
        [InlineKeyboardButton("Manual", callback_data=f"manual_{move_name}")],
        [InlineKeyboardButton("Indietro", callback_data=back_type)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=reply_markup
    )


async def manual_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, move_name: str
):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "Indietro",
                callback_data=f'back_to_{move_name.lower().replace(" ", "_")}',
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"{move_name} Manual - Placeholder text"
    match move_name:
        case "Face Danger":
            text = (
                "The _Face Danger_ move is a catch-all for risky, dramatic, or complex actions not covered by another move. If you’re trying to overcome an obstacle or resist a threat, make this move to see what happens. You select which stat to roll based on how you address the challenge.\n\n"
                "A strong hit means you succeed. You are in control. What do you do next?\n\n"
                "A weak hit means you overcome the obstacle or avoid the threat, but not without cost. Choose an option and envision what happens next. You don’t have complete control. Consider how the situation might escalate, perhaps forcing you to react with another move.\n\n"
                "A miss means you are thwarted in your action, fail to oppose the threat, or make some progress but at great cost. You must _Pay the Price_."
            )

        case "Secure Advantage":
            text = (
                "The structure of _Secure an Advantage_ is similar to _Face Danger_. You envision your action and roll + your most relevant stat. This move, however, is proactive rather than reactive. You’re evaluating the situation or strengthening your position.\n\n"
                "This move gives you an opportunity to build your momentum or improve your chance of success on a subsequent move. It’s a good move to make if you want to take a moment to size up the situation, or if you’re acting to gain control. It will often encompass a moment in time—such as shoving your foe with your shield to setup an attack. Or, it can represent preparation or evaluation spanning minutes, hours, or even days, depending on the narrative circumstances.\n\n"
                "A strong hit means you’ve identified an opportunity or gained the upper hand. You knocked your enemy down. You moved into position for an arrow shot. You built your trap. You scouted the best path through the mountains. Now it’s time to build on your success.\n\n"
                "A weak hit means your action has helped, but your advantage is fleeting or a new danger or complication is revealed. You pushed, and the world pushes back. What happens next?\n\n"
                "A miss means your attempt to gain advantage has backfired. You acted too slowly, presumed too much, or were outwitted or outmatched. _Pay the Price_."
            )

        case "Gather Information":
            text = (
                "Use this move when you’re not sure of your next steps, when the trail has gone cold, when you make a careful search, or when you do fact-finding.\n\n"
                "There’s some overlap with other moves using +wits and involving knowledge, but each has their purpose. When you’re forced to react with awareness or insight to deal with an immediate threat, that’s _Face Danger_. When you size up your options or leverage your expertise and prepare to make a move, that’s _Secure an Advantage_. When you’re spending time searching, investigating, asking questions—especially related to a quest—that’s when you _Gather Information_. Use whichever move is most appropriate to the circumstances and your intent.\n\n"
                "A strong hit means you gain valuable new information. You know what you need to do next. Envision what you learn, or _Ask the Oracle_.\n\n"
                "With a weak hit, you’ve learned something that makes your quest more complicated or dangerous. You know more about the situation, but it’s unwelcome news. To move forward, you need to overcome new obstacles and see where the clues lead.\n\n"
                "On a miss, some event or person acts against you, a dangerous new threat is revealed, or you learn of something which contradicts previous information or severely complicates your quest."
            )

        case "Heal":
            text = (
                "When you tend to physical damage or sickness—for yourself, an ally, or an NPC—make this move. Healing might be represented by staunching bleeding, binding wounds, applying salves, or using herbs to brew a tonic. In the Ironlands, healing is not overtly magical, but some folk know how to treat even the most dire of injuries and illnesses.\n\n"
                "Healing takes time. A few minutes for a quick treatment to get someone on their feet. Hours or perhaps days for more severe injuries. Use what seems appropriate to the circumstances, and consider how this downtime affects your quests and other things going on in your world.\n\n"
                "A miss can mean you’ve caused harm rather than helping, or some perilous event interrupts your care.\n\n"
                "NPCs who are not companions do not have a health track. When you attempt to _Heal_ them, make this move and apply the result through the fiction. They will improve, or not, as appropriate to the move’s outcome."
            )

        case "Resupply":
            text = (
                "When you’re in the field and need to bolster your supply track, make this move. Fictionally, this represents hunting and gathering. You might also search an area where supplies might be found, such as an abandoned camp or field of battle.\n\n"
                "If you’re adventuring with allies, you share the same supply value. When one of you makes this move, each of you adjust your supply track.\n\n"
                "If you have the unprepared condition marked, you can’t _Resupply_. Instead, you need to find help in a community when you _Sojourn_."
            )

        case "Make Camp":
            text = (
                "Making camp can be a purely narrative activity and can be abstracted or roleplayed as you like. However, if you need to recover from the struggle of your adventures while traveling through the wilds, make this move.\n\n"
                "Unlike most moves, you will not roll + a stat. Instead, you roll +supply. This represents your access to provisions and gear. Huddling in your cloak on the cold ground is a different experience than a warm fire, good food, and a dry tent.\n\n"
                "On a strong hit, choose two from the list. You may not select a single option more than once. On a weak hit, choose one. If you recuperate or partake, you can also apply those benefits to your companions (NPC assets—see page 39).\n\n"
                "If you are traveling with allies, only one of you makes this roll for the group. Each of you may then choose your own benefits on a strong or weak hit.\n\n"
                "On a miss, you gain no benefits of your downtime. Perhaps you suffered troubling dreams (_Endure Stress_). Poor weather may have left you weary and cold (_Endure Harm_). Or, you were attacked. If in doubt, roll on the _Pay the Price_ table or _Ask the Oracle_ for inspiration. Depending on what you envision, you can play to see what happens, or jump to the next day as you continue on your journey the worse for wear."
            )

        case "Undertake Journey":
            text = (
                "This is Ironsworn's travel move. When you set off or push on toward a destination, make this move.\n\n"
                "First, give your journey a rank. Decide how far—and how hazardous—it is based on the established fiction. If you're unsure, _Ask the Oracle_. Most of your journeys should be troublesome or dangerous. Formidable or extreme journeys might require weeks within your narrative, with appropriate stops, side quests, and adventures along the way. An epic journey is one of months, or even years. It is the journey of a lifetime.\n\n"
                "If the journey is mundane—a relatively short distance through safe territory—don't make this move. Just narrate the trip and jump to what happens or what you do when you arrive.\n\n"
                "*ALONG FOR THE RIDE?*\n"
                "If you are part of a caravan or party of NPCs, and aren't an active participant in the planning or execution of the journey, you won't make this move or track progress. The journey will be resolved in the fiction. You can *Ask the Oracle* to determine what happens en route or when you arrive.\n\n"
                "*ALLIES AND JOURNEYS*\n"
                "If you are traveling with allies, one of you makes the _Undertake a Journey_ roll for each segment, and you share a progress track. The responsibility for leading the journey can switch from segment to segment as you like.\n\n"
                "Your fellow travelers can assist by making the _Aid Your Ally_ move. Perhaps they are scouting ahead or sustaining you with a lively song. They can also _Resupply_ to represent foraging or hunting for supplies en route. Everyone should offer narrative color for what they do and see on the journey, even if they are not making moves.\n\n"
                "Only the character making the move takes the momentum bonus on a strong hit. But, because your supply track is shared, each of you mark -1 supply when the acting character makes that choice on a strong hit or when they suffer a weak hit.\n\n"
                "*WAYPOINTS*\n"
                "If you score a strong or weak hit on this move, you reach a waypoint. A waypoint is a feature of the landscape, a settlement, or a point-of-interest. Depending on the information you have or whether you have traveled this area before, a specific waypoint may be known to you. If it isn't, envision what you find. If you need inspiration, _Ask the Oracle_.\n\n"
                "You will find random tables for waypoint features on page 176, but do not rely too heavily on these generators. Seek inspiration from your fiction and the landscape you envision around you. If it's interesting, wondrous, or creates new opportunities for drama and adventure, bring it to life.\n\n"
                "Depending on the pace of your story and your current situation, you may choose to focus on this waypoint. A settlement can offer roleplay opportunities or provide a chance to recuperate and provision via the _Sojourn_ move. In the wilds, you might make moves such as _Make Camp_, _Resupply_, or _Secure an Advantage_. Or, you can play out a scene not involving moves as you interact with your allies or the world. Mix it up. Some waypoints will pass as a cinematic montage (doubtlessly depicted in a soaring helicopter shot as you trudge over jagged hills). Other waypoints offer opportunities to zoom in, enriching your story and your world.\n\n"
                "When you roll a match (page 9), take the opportunity to introduce something unexpected. This could be an encounter, a surprising or dramatic feature of the landscape, or a turn of events in your current quest.\n\n"
                "*MARKING PROGRESS*\n"
                "When you score a hit and reach a waypoint, you mark progress per the rank of the journey. For example, on a dangerous journey you mark 2 progress (filling two boxes on your progress track) for each waypoint. When you feel you have accumulated enough progress and are ready to make a final push towards your destination, make the _Reach Your Destination_ move. For more on progress tracks and progress moves, see page 14.\n\n"
                "*TRAVEL TIME*\n"
                "Travel time can largely be abstracted. The time between waypoints might be hours or days, depending on the terrain and the distance. If it's important, make a judgment call based on what you know of your journey, or _Ask the Oracle_.\n\n"
                "*MOUNTS AND TRANSPORT*\n"
                "Horses, mules, and transport (such as boats) influence the fiction of your journey—the logistics of travel and how long it takes. They do not provide a mechanical benefit unless you have an asset which gives you a bonus (such as a *Horse* companion).\n\n"
                "*MANAGING RESOURCES*\n"
                "You can intersperse _Resupply_ or _Make Camp_ moves during your journey to manage your health, spirit and supply, or to create new scenes as diversions. Don't be concerned with using the _Make Camp_ move as an automatic capstone to a day of travel. You can be assumed to rest and camp as appropriate without making the move, and you can roleplay out those scenes or gloss over them as you like. When you want the mechanical benefit of the _Make Camp_ move, or you're interested in playing the move out through the fiction, then do it.\n\n"
                "*ON A MISS...*\n"
                "You do not mark progress on a miss. Instead, you encounter a new danger. You might face hazards through the weather, the terrain, encounters with creatures or people, attacks from your enemies, strange discoveries, or supernatural events. Decide what happens based on your current circumstances and surroundings, roll on the _Pay the Price_ table, or _Ask the Oracle_ for inspiration. Depending on your desired narrative pace, you can then play out the event to see what happens, or summarize and apply the consequences immediately.\n\n"
                "For example, you roll a miss and decide you encounter a broad, wild river which must be crossed to continue on your journey. If you want to focus on how you deal with the situation, play to see what happens by making moves. You might _Secure an Advantage_ by exploring upriver for a ford and then _Face Danger_ to cross. Or, if want to quickly push the story forward, you could fast-forward to a perilous outcome such as losing some provisions during the crossing (suffer -supply). Mix things up, especially on long journeys."
            )

        case "Reach Destination":
            text = (
                "When you have made progress on your journey progress track and are ready to complete your expedition, make this move. Since this is a progress move, you tally the number of filled boxes on your progress track. This is your progress score. Only add fully filled boxes (those with four ticks). Then, roll your challenge dice, compare to your progress score, and resolve a strong hit, weak hit, or miss as normal. You may not burn momentum on this roll, and you are not affected by negative momentum.\n\n"
                "When you score a strong hit, you arrive at your destination and are well-positioned for success. This should be reflected in the mechanical benefit offered by the move, but also in how you envision your arrival. If this has been a long, arduous journey, make this moment feel rewarding.\n\n"
                "On a weak hit, something complicates your arrival or your next steps. Things are not what you expected, or a new danger reveals itself. Perhaps the village is occupied by a raiding party, or the mystic whose counsel you sought is initially hostile to you. Envision what you find and play to see what happens.\n\n"
                "On a miss, something has gone horribly wrong. You realize you are off-course, you had bad information about your destination, or you face a turn of events undermining your purpose here. Depending on the circumstances, this might mean your journey ends in failure, or that you must push on while clearing all but one of your filled progress and raising the journey’s rank.\n\n"
                "If you are traveling with allies, one of you makes this move. Each of you benefit (or suffer) from the narrative outcome of the roll. Only the character making the move gets the mechanical benefit of a strong hit."
            )

        case "Compel":
            text = (
                "When you act to persuade someone to do as you ask, or give you something, make this move. It might be through bargaining, or intimidation, charm, diplomacy, or trickery. Use the appropriate stat based on your approach, and roll to see what happens.\n\n"
                "This move doesn’t give you free rein to control the actions of other characters in your world. Remember: Fiction first. Consider their motivations. What is your leverage over them? What do they stand to gain or avoid? Do you have an existing relationship? If your argument has no merit, or your threat or promise carries no weight, you can’t make this move. You can’t intimidate your way out of a situation where you are at a clear disadvantage. You can’t barter when you have nothing of value to offer. If you are unsure, _Ask the Oracle_, 'Would they consider this?' If the answer is yes, make the move.\n\n"
                "On the other hand, if their positive response is all but guaranteed—you are acting obviously in their best interest or offering a trade of fair value—don’t make this move. Just make it happen. Save the move for times when the situation is uncertain and dramatic.\n\n"
                "On a weak hit, success is hinged on their counter-proposal. Again, look to the fiction. What would they want? What would satisfy their concerns or motivate them to comply? If you accept their offer, you gain ground. If not, you’ve encountered an obstacle in your quest and need to find another path forward.\n\n"
                "If you promise them something as part of this move, but then fail to do as you promised, they should respond accordingly. Perhaps it means a rude welcome when next you return to this community. If they are powerful, they may even act against you. If you share a bond, you would most certainly _Test Your Bond_. Your actions, good or bad, should have ramifications for your story beyond the scope of the move.\n\n"
                "On a miss, they are insulted, angered, inflexible, see through your lies, or demand something of you which costs you dearly. Their response should introduce new dangers or complications.\n\n"
                "_Compel_ may also be used to bring combat to a non-violent conclusion. Your approach dictates the stat you use—typically +iron when you threaten with further violence, +heart when you attempt to surrender or reason with them, and +shadow when you use trickery. Your foe must have a reason to be open to your approach. If unsure, _Ask the Oracle_. To learn more, see page 88."
            )

        case "Sojourn":
            text = (
                "Communities stand as an oasis within the perilous wilds of the Ironlands. They are a source of protection, trade, and fellowship. However, there are no grand cities like those that stood in the Old World. Life here is too harsh. Resources too few.\n\n"
                "When you rest, replenish, and share fellowship within a community, make this move. Depending on your level of success, you can choose one or more debilities to clear or tracks to increase. If you share a bond with this community and score a hit, you may select one more.\n\n"
                "You may select an option only once. If you recuperate, you can also apply those benefits to your companions (NPC assets—see page 39). If you _Sojourn_ with allies, only one of you makes this move, but all of you can make your own choices on a strong or weak hit.\n\n"
                "Your _Sojourn_ should require several hours or several days, depending on your current circumstances and level of aid and recovery required. Make this move only once when visiting a community, unless the situation changes.\n\n"
                "On a hit, this move also includes an option to roll again for one of your selected recover actions. The second roll either provides a bonus to that activity (on a hit), or causes you to lose all benefits for your recovery. For example, if you are suffering from low spirit, you might choose to focus on the consort action, representing time in the mead hall or intimacy with a lover. Roll +heart again, and take the bonus if you score a hit.\n\n"
                "You should envision what makes this community and its people unique. Give every community at least one memorable characteristic. If you need inspiration, _Ask the Oracle_. You will find creative prompts, along with generators for community names and troubles in chapter 6 (page 165).\n\n"
                "Narratively, you can imagine much of the time in this community passing as a montage. If you choose to focus on a recovery action, zoom into that scene and envision what happens. You might be in the healer’s house, at the market, dancing at a festival, or speaking with the clan leader and making plans. Envision how this scene begins, make your roll, and then narrate the conclusion of the scene—good or bad—based on the result of your focus roll.\n\n"
                "You can also perform additional moves while in the community. If you need to _Gather Information_, _Compel someone_, or _Draw the Circle_ to resolve a feud, zoom into those scenes and play to see what happens. _Sojourn_ is an overarching move that sets the tone for your stay and defines the mechanics of your recovery. It is not the only move you can make.\n\n"
                "On a miss, something goes wrong. You are not welcomed. The citizens are hostile to you. Your dark mood alienates you. A perilous event threatens you all. Envision what happens based on your current circumstances, or _Ask the Oracle_."
            )

        case "Draw Circle":
            text = (
                "Ritualized duels are a common way of dealing with disputes among Ironlanders. When you challenge someone or accept a challenge, you each trace one-half of the outline of a circle into the ground with the point of an iron blade. Then, you face each other in the center of the circle and fight.\n\n"
                "You setup your foe’s progress track per the _Enter the Fray_ move, but use this move instead of _Enter the Fray_ to begin the fight. You have initiative at the start of combat unless you score a miss or choose the option to grant first strike.\n\n"
                "Duels are usually stopped when one of the duelists surrenders or is clearly defeated. The victor may then make a demand which the loser must abide by. Not complying with this demand means ostracism and shame. If you lose a duel, envision what your opponent demands of you. If you’re unsure, _Ask the Oracle_. Then, do it or face the narrative cost of your dishonor.\n\n"
                "Duels may also be to the death. If one of the combatants declares their intent to fight to the death, the other must agree or forfeit."
            )
        
        case "Forge Bond":
            text = (
                "Bonds connect you to the people of the Ironlands. They provide a story benefit by enriching your interactions and creating connections with a recurring cast of characters and familiar places. They also provide mechanical benefits by giving you adds when you make moves such as _Sojourn_ or _Compel_. And, perhaps most importantly, your bonds help determine your ultimate fate when you retire from adventuring and _Write Your Epilogue_.\n\n"
                "Bonds can be created through narrative circumstances or through sworn vows. If you’ve established a strong relationship with a person or community, you may _Forge a Bond_ to give it significance. If you make this move after you successfully _Fulfill Your Vow_ in service to them, you have proven yourself worthy and may reroll any dice.\n\n"
                "When you _Forge a Bond_ and score a strong hit, mark a tick on your bond progress track (page 36) and make note of your bond.\n\n"
                "On a weak hit, they ask more of you. It might be a task, an item, a concession, or even a vow. Envision what they need, or _Ask the Oracle_. If you do it, or _Swear an Iron Vow_, you can mark the bond.\n\n"
                "On a miss, they have refused you. Why? The answer should introduce new complications or dangers."
            )

    if len(text) < 4096:
        await query.edit_message_text(
            text=text, parse_mode="Markdown", reply_markup=reply_markup
        )
    else:
        context.user_data["page"] = 0
        context.user_data["move"] = move_name
        parts = split_text(text)
        context.user_data["parts"] = parts
        keyboard = [
            [InlineKeyboardButton("Pagina +", callback_data="page+")],
            [
                InlineKeyboardButton(
                    "Indietro",
                    callback_data=f'back_to_{move_name.lower().replace(" ", "_")}',
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=parts[0], parse_mode="Markdown", reply_markup=reply_markup
        )


# Generate callback functions for each Adventure move
move_names = [
    "face_danger",
    "secure_advantage",
    "gather_information",
    "heal",
    "resupply",
    "make_camp",
    "undertake_journey",
    "reach_destination",
    "compel",
    "sojourn",
    "draw_circle",
    "forge_bond",
    "test_bond",
    "aid_ally",
    "write_epilogue",
]

for move in move_names:
    # pylint: disable=exec-used
    exec(
        f"""
async def {move}_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generic_move_callback(update, context, '{move.replace("_", " ").title()}')

async def manual_{move}_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manual_callback(update, context, '{move.replace("_", " ").title()}')

async def back_to_{move}_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await {move}_callback(update, context)
"""
    )


async def adventure_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Face Danger", callback_data="face_danger")],
        [InlineKeyboardButton("Secure an Advantage", callback_data="secure_advantage")],
        [
            InlineKeyboardButton(
                "Gather Information", callback_data="gather_information"
            )
        ],
        [InlineKeyboardButton("Heal", callback_data="heal")],
        [InlineKeyboardButton("Resupply", callback_data="resupply")],
        [InlineKeyboardButton("Make Camp", callback_data="make_camp")],
        [
            InlineKeyboardButton(
                "Undertake a Journey", callback_data="undertake_journey"
            )
        ],
        [
            InlineKeyboardButton(
                "Reach Your Destination", callback_data="reach_destination"
            )
        ],
        [InlineKeyboardButton("Indietro", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Adventure moves:", reply_markup=reply_markup)


async def relationship_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Compel", callback_data="compel")],
        [InlineKeyboardButton("Sojourn", callback_data="sojourn")],
        [InlineKeyboardButton("Draw the Circle", callback_data="draw_circle")],
        [InlineKeyboardButton("Forge a Bond", callback_data="forge_bond")],
        [InlineKeyboardButton("Test your Bond", callback_data="test_bond")],
        [InlineKeyboardButton("Aid your Ally", callback_data="aid_ally")],
        [InlineKeyboardButton("Write your Epilogue", callback_data="write_epilogue")],
        [InlineKeyboardButton("Indietro", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Relationship moves:", reply_markup=reply_markup)


async def combat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Combat moves will be implemented here.")


async def suffer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Suffer moves will be implemented here.")


async def quest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Quest moves will be implemented here.")


async def fate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Fate moves will be implemented here.")


async def back_to_zero_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    print("closing_all")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Conversation closed.")


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await moves(update, context)


async def back_to_adventure_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await adventure_callback(update, context)


async def back_to_relationship_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await relationship_callback(update, context)


# This dictionary maps callback data to their respective functions
callback_functions = {
    "adventure": adventure_callback,
    "relationship": relationship_callback,
    "combat": combat_callback,
    "suffer": suffer_callback,
    "quest": quest_callback,
    "fate": fate_callback,
    "back_to_zero": back_to_zero_callback,
    "back_to_main": back_to_main_callback,
    "back_to_adventure": back_to_adventure_callback,
    "back_to_relationship": back_to_relationship_callback,
}

# Add move-specific callbacks to the dictionary
for move in move_names:
    # pylint: disable=eval-used
    callback_functions[move] = eval(f"{move}_callback")
    callback_functions[f"manual_{move}"] = eval(f"manual_{move}_callback")
    callback_functions[f"back_to_{move}"] = eval(f"back_to_{move}_callback")


async def moves_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data.startswith("page"):
        move_name = context.user_data["move"]
        await flip_page(
            update,
            context,
            callback_data,
            f'back_to_{move_name.lower().replace(" ", "_")}',
        )
    elif callback_data.startswith("manual_"):
        move_name = callback_data[7:]  # Remove 'manual_' prefix
        await manual_callback(update, context, move_name.replace("_", " ").title())
    else:
        await callback_functions.get(callback_data, lambda u, c: None)(update, context)
    return SHOWING_MOVES


moves_handler = ConversationHandler(
    entry_points=[CommandHandler("moves", moves)],
    states={
        SHOWING_MOVES: [CallbackQueryHandler(moves_button_callback)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, end_conversation),
    ],
    allow_reentry=True,
)
