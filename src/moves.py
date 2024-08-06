import logging
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
        [InlineKeyboardButton("Back", callback_data="back_to_zero")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message is None:
        # Non so esattamente come fixarlo meglio; Quando premi Back su adventure_callback o gli altri, dovresti tornare qui. Ma non c'è un messaggio, ergo l'if.
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Choose move type", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Choose move type", reply_markup=reply_markup)

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
            text = """
*FACE DANGER*

When you attempt something risky or react to an imminent threat, envision your action and roll.

If you act...
• With speed, agility, or precision: Roll +edge.
• With charm, loyalty, or courage: Roll +heart.
• With aggressive action, forceful defense, strength, or endurance: Roll +iron.
• With deception, stealth, or trickery: Roll +shadow.
• With expertise, insight, or observation: Roll +wits.

On a *strong hit*, you are successful. Take +1 momentum.

On a *weak hit*, you succeed, but face a troublesome cost. Choose one.
• You are delayed, lose advantage, or face a new danger: Suffer -1 momentum.
• You are tired or hurt: _Endure Harm_ (1 harm).
• You are dispirited or afraid: _Endure Stress_ (1 stress).
• You sacrifice resources: Suffer -1 supply.

On a *miss*, you fail, or your progress is undermined by a dramatic and costly turn of events. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Secure Advantage":
            text = """
*SECURE AN ADVANTAGE*

When *you assess a situation, make preparations, or attempt to gain leverage*, envision your action and roll.

If you act...
• With speed, agility, or precision: Roll +edge.
• With charm, loyalty, or courage: Roll +heart.
• With aggressive action, forceful defense, strength, or endurance: Roll +iron.
• With deception, stealth, or trickery: Roll +shadow.
• With expertise, insight, or observation: Roll +wits.

On a *strong hit*, you gain advantage. Choose one.
• Take control: Make another move now (not a progress move); when you do, add +1.
• Prepare to act: Take +2 momentum.

On a *weak hit*, your advantage is short-lived. Take +1 momentum.

On a *miss*, you fail or your assumptions betray you. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Gather Information":
            text = """
*GATHER INFORMATION*

When *you search an area, ask questions, conduct an investigation, or follow a track*, roll +wits. If you act within a community or ask questions of a person with whom you share a bond, add +1.

On a *strong hit*, you discover something helpful and specific. The path you must follow or action you must take to make progress is made clear. Envision what you learn (_Ask the Oracle_ if unsure), and take +2 momentum.

On a *weak hit*, the information complicates your quest or introduces a new danger. Envision what you discover (_Ask the Oracle_ if unsure), and take +1 momentum.

On a *miss*, your investigation unearths a dire threat or reveals an unwelcome truth that undermines your quest. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Heal":
            text = """
*HEAL*

When *you treat an injury or ailment*, roll +wits. If you are mending your own wounds, roll +wits or +iron, whichever is lower.

On a *strong hit*, your care is helpful. If you (or the ally under your care) have the wounded condition, you may clear it. Then, take or give up to +2 health.

On a *weak hit*, as above, but you must suffer -1 supply or -1 momentum (your choice).

On a *miss*, your aid is ineffective. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Resupply":
            text = """
*RESUPPLY*

When *you hunt, forage, or scavenge*, roll +wits.

On a *strong hit*, you bolster your resources. Take +2 supply.

On a *weak hit*, take up to +2 supply, but suffer -1 momentum for each.

On a *miss*, you find nothing helpful. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Make Camp":
            text = """
*MAKE CAMP*

When *you rest and recover for several hours in the wild*, roll +supply.

On a *strong hit*, you and your allies may each choose two.

On a *weak hit*, choose one.
• Recuperate: Take +1 health for you and any companions.
• Partake: Suffer -1 supply and take +1 health for you and any companions.
• Relax: Take +1 spirit.
• Focus: Take +1 momentum.
• Prepare: When you break camp, add +1 if you _Undertake a Journey_.

On a *miss*, you take no comfort. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Undertake Journey":
            text = """
*UNDERTAKE A JOURNEY*

When *you travel across hazardous or unfamiliar lands*, first set the rank of your journey.
• Troublesome journey: 3 progress per waypoint.
• Dangerous journey: 2 progress per waypoint.
• Formidable journey: 1 progress per waypoint.
• Extreme journey: 2 ticks per waypoint.
• Epic journey: 1 tick per waypoint.

Then, for each segment of your journey, roll +wits. If you are setting off from a community with which you share a bond, add +1 to your initial roll.

On a *strong hit*, you reach a waypoint. If the waypoint is unknown to you, envision it (_Ask the Oracle_ if unsure). Then, choose one.
• You make good use of your resources: Mark progress.
• You move at speed: Mark progress and take +1 momentum, but suffer -1 supply.

On a *weak hit*, you reach a waypoint and mark progress, but suffer -1 supply.

On a *miss*, you are waylaid by a perilous event. _Pay the Price_.
"""
            back_type = "back_to_adventure"

        case "Reach Destination":
            text = """
*REACH YOUR DESTINATION*

*Progress Move*

When *your journey comes to an end*, roll the challenge dice and compare to your progress. Momentum is ignored on this roll.

On a *strong hit*, the situation at your destination favors you. Choose one.\n
• Make another move now (not a progress move), and add +1.\n
• Take +1 momentum.

On a *weak hit*, you arrive but face an unforeseen hazard or complication. Envision what you find (_Ask the Oracle_ if unsure).

On a *miss*, you have gone hopelessly astray, your objective is lost to you, or you were misled about your destination. If your journey continues, clear all but one filled progress, and raise the journey's rank by one (if not already epic).
"""
            back_type = "back_to_adventure"

        case "Compel":
            text = """
*COMPEL*

When you *attempt to persuade someone to do something*, envision your approach and roll. If you...
• Charm, pacify, barter, or convince: Roll +heart (add +1 if you share a bond).
• Threaten or incite: Roll +iron.
• Lie or swindle: Roll +shadow.

On a *strong hit*, they'll do what you want or share what they know. Take +1 momentum. If you use this exchange to _Gather Information_, make that move now and add +1.

On a *weak hit*, as above, but they ask something of you in return. Envision what they want (_Ask the Oracle_ if unsure).

On a *miss*, they refuse or make a demand which costs you greatly. _Pay the Price_.
"""
            back_type = "back_to_relationship"

        case "Sojourn":
            text = """
*SOJOURN*

When you spend time in a community seeking assistance, roll +heart. If you share a bond, add +1.

On a *strong hit*, you and your allies may each choose two from within the categories below. On a *weak hit*, choose one. If you share a bond, choose one more.

On a hit, you and your allies may each focus on one of your chosen recover actions and roll +heart again. If you share a bond, add +1.
On a strong hit, take +2 more for that action. On a weak hit, take +1 more. On a miss, it goes badly and you lose all benefits for that action.

*Clear a Condition*
• Mend: Clear a wounded debility and take +1 health.
• Hearten: Clear a shaken debility and take +1 spirit.
• Equip: Clear an unprepared debility and take +1 supply.

*Recover*
• Recuperate: Take +2 health for yourself and any companions.
• Consort: Take +2 spirit.
• Provision: Take +2 supply.
• Plan: Take +2 momentum.

*Provide Aid*
• Take a quest: Envision what this community needs, or what trouble it is facing (_Ask the Oracle_ if unsure). If you choose to help, Swear an Iron Vow and add +1.

On a *miss*, you find no help here. Pay the Price.
"""
            back_type = "back_to_relationship"

        case "Draw Circle":
            text = """
*DRAW THE CIRCLE*

When *you challenge someone to a formal duel, or accept a challenge*, roll +heart. If you share a bond with this community, add +1.

On a *strong hit*, take +1 momentum. You may also choose up to three boasts and take +1 momentum for each.

On a *weak hit*, you may choose one boast in exchange for +1 momentum.
• Grant first strike: Your foe has initiative.
• Bare yourself: Take no benefit of armor or shield; your foe's harm is +1.
• Hold no iron: Take no benefit of weapons; your harm is 1.
• Bloody yourself: Endure Harm (1 harm).
• To the death: One way or another, this fight must end with death.

On a *miss*, you begin the duel at a disadvantage. Your foe has initiative. Pay the Price.

Then, make moves to resolve the fight. If you are the victor, you may make a lawful demand, and your opponent must comply or forfeit their honor and standing. If you refuse the challenge, surrender, or are defeated, they make a demand of you.
"""
            back_type = "back_to_relationship"

        case "Forge Bond":
            text = """
*FORGE A BOND*

When you spend significant time with a person or community, stand together to face hardships, or make sacrifices for their cause, you can attempt to create a bond. When you do, roll +heart. If you make this move after you successfully _Fulfill Your Vow_ to their benefit, you may reroll any dice.

On a *strong hit*, make note of the bond, mark a tick on your bond progress track, and choose one.
• Take +1 spirit.
• Take +2 momentum.

On a *weak hit*, they ask something more of you first. Envision what it is (_Ask the Oracle_ if unsure), do it (or _Swear an Iron Vow_), and mark the bond. If you decline or fail, _Pay the Price_.

On a *miss*, you are refused. _Pay the Price_.
                """
            back_type = "back_to_relationship"

        case "Test Bond":
            text = """
*TEST YOUR BOND*

When *your bond is tested through conflict, betrayal, or 
circumstance*, roll +heart.

On a *strong hit*, this test has strengthened your bond. Choose one.
• Take +1 spirit.
• Take +2 momentum.

On a *weak hit*, your bond is fragile and you must prove your loyalty. Envision what they ask of you (_Ask the Oracle_ if unsure), and do it (or _Swear an Iron Vow_). If you decline or fail, clear the bond and _Pay the Price_.

On a *miss*, or if you have no interest in maintaining this relationship, clear the bond and _Pay the Price_.
                """
            back_type = "back_to_relationship"

        case "Aid Ally":
            text = """
*AID YOUR ALLY*

When *you _Secure an Advantage_ in direct support of an ally*, and score a hit, they (instead of you) can take the benefits of the move. If you are in combat and score a strong hit, you and your ally have initiative.
            """
            back_type = "back_to_relationship"
        case "Write Epilogue":
            text = """
*WRITE YOUR EPILOGUE*

*Progress Move*

When you *retire from your life as Ironsworn*, envision two things: What you hope for, and what you fear. Then, roll the challenge dice and compare to your bonds. Momentum is ignored on this roll.

On a *strong hit*, things come to pass as you hoped.

On a *weak hit*, your life takes an unexpected turn, but not necessarily for the worse. You find yourself spending your days with someone or in a place you did not foresee. Envision it (_Ask the Oracle_ if unsure).

On a miss, your fears are realized.
            """
            back_type = "back_to_relationship"

        case "Enter Fray":
            text = """
*ENTER THE FRAY*

When *you enter into combat*, first set the rank of each of your foes.
• Troublesome foe: 3 progress per harm; inflicts 1 harm.
• Dangerous foe: 2 progress per harm; inflicts 2 harm.
• Formidable foe: 1 progress per harm; inflicts 3 harm.
• Extreme foe: 2 ticks per harm; inflicts 4 harm.
• Epic foe: 1 tick per harm; inflicts 5 harm.

Then, roll to determine who is in control. If you are...
• Facing off against your foe: Roll +heart.
• Moving into position against an unaware foe, or striking without 
warning: Roll +shadow.
• Ambushed: Roll +wits.

On a *strong hit*, take +2 momentum. You have initiative.

On a *weak hit*, choose one.
• Bolster your position: Take +2 momentum.
• Prepare to act: Take initiative.

On a *miss*, combat begins with you at a disadvantage. _Pay the Price_. Your foe has initiative.
"""
            back_type = "back_to_combat"
        case "Strike":
            text = """
*STRIKE*

When *you have initiative and attack in close quarters*, roll +iron 
When *you have initiative and attack at range*, roll +edge.

On a *strong hit*, inflict +1 harm. You retain initiative.

On a *weak hit*, inflict your harm and lose initiative.

On a *miss*, your attack fails and you must _Pay the Price_. Your foe has initiative.
"""
            back_type = "back_to_combat"
        case "Clash":
            text = """
*CLASH*

When *your foe has initiative and you fight with them in close quarters*, roll +iron. When *you exchange a volley at range, or shoot at an advancing foe*, roll +edge.

On a *strong hit*, inflict your harm and choose one. You have the 
initiative.
• You bolster your position: Take +1 momentum.
• You find an opening: Inflict +1 harm.

On a *weak hit*, inflict your harm, but then _Pay the Price_. Your foe has initiative.

On a *miss*, you are outmatched and must _Pay the Price_. Your foe has initiative.
"""
            back_type = "back_to_combat"
        case "Turn the Tide":
            text = """
*TURN THE TIDE*

Once per fight, when *you risk it all*, you may steal initiative from your foe to make a move (not a progress move). When you do, add +1 and take +1 momentum on a hit.

If you fail to score a hit on that move, you must suffer a dire outcome. _Pay the Price_.
"""
            back_type = "back_to_combat"

        case "End the Fight":
            text = """
*END THE FIGHT*

When *you enter into combat*, set the rank of each of your foes.
• Troublesome foe: 3 progress per harm; inflicts 1 harm.
• Dangerous foe: 2 progress per harm; inflicts 2 harm.
• Formidable foe: 1 progress per harm; inflicts 3 harm.
• Extreme foe: 2 ticks per harm; inflicts 4 harm.
• Epic foe: 1 tick per harm; inflicts 5 harm.

Then, roll to determine who is in control. If you are...
• Facing off against your foe: Roll +heart.
• Moving into position against an unaware foe, or striking without warning: Roll +shadow.
• Ambushed: Roll +wits.

On a *strong hit*, take +2 momentum. You have initiative.

On a *weak hit*, choose one.
• Bolster your position: Take +2 momentum.
• Prepare to act: Take initiative.

On a *miss*, combat begins with you at a disadvantage. _Pay the Price_. Your foe has initiative.
"""
            back_type = "back_to_combat"

        case "Battle":
            text = """
*BATTLE*

When you *fight a battle*, and it happens in a blur, envision your objective and roll. If you primarily…
• Fight at range, or using your speed and the terrain to your advantage: Roll +edge.
• Fight depending on your courage, allies, or companions: Roll +heart.
• Fight in close to overpower your opponents: Roll +iron.
• Fight using trickery to befuddle your opponents: Roll +shadow.
• Fight using careful tactics to outsmart your opponents: Roll +wits.

On a *strong hit*, you achieve your objective unconditionally. Take +2 momentum.

On a *weak hit*, you achieve your objective, but not without cost. _Pay the Price_.

On a *miss*, you are defeated and the objective is lost to you. _Pay the Price_.
"""
            back_type = "back_to_combat"

        case "Other moves":
            text = """
*OTHER MOVES*

_*Secure an Advantage*_: When acting to outwit or outmaneuver your foe, or setting up another move.

_*Face Danger*_: When overcoming an obstacle, avoiding a hazard, fleeing, or evading an attack (without fighting back).
_*Aid Your Ally*_: When making a move to give your ally an advantage.
_*Compel*_: When surrendering, coercing your foe to stand down, or negotiating a truce.
*Suffer Moves (all)*: When facing physical damage, mental trauma, or lack of supply.
_*Pay the Price*_: When suffering the outcome of a move.
_*Ask the Oracle*_: When asking questions about combat events or your foe's intent and actions.
"""
            back_type = "back_to_combat"

        case "Endure Harm":
            text = """
*ENDURE HARM*

When *you face physical damage*, suffer -health equal to your foe's rank or as appropriate to the situation. If your health is 0, suffer -momentum equal to any remaining -health.
Then, roll +health or +iron, whichever is higher.

On a *strong hit*, choose one.
• Shake it off: If your health is greater than 0, suffer -1 momentum in
exchange for +1 health.
• Embrace the pain: Take +1 momentum.

On a *weak hit*, you press on.

On a *miss*, also suffer -1 momentum. If you are at 0 health, you must mark wounded or maimed (if currently unmarked) or roll on the following table.
• *1-10*: The harm is mortal. _Face Death_.
• *11-20*: You are dying. You need to _Heal_ within an hour or two or _Face Death_.
• *21-35*: You are unconscious and out of action. If left alone, you come back to your senses in an hour or two. If you are vulnerable to a foe not inclined to show mercy, _Face Death_.
• *36-50*: You are reeling and fighting to stay conscious. If you engage in any vigorous activity (such as running or fighting) before taking a breather for a few minutes, roll on this table again (before resolving the other move).
• *51-00*: You are battered but still standing.
"""
            back_type = "back_to_suffer"

        case "Face Death":
            text = """
*FACE DEATH*

When you *are brought to the brink of death*, and glimpse the world
beyond, roll +heart.

On a *strong hit*, death rejects you. You are cast back into the mortal world.

On a *weak hit*, choose one.
• You die, but not before making a noble sacrifice. Envision your final moments.
• Death desires something of you in exchange for your life. Envision what it wants (_Ask the Oracle_ if unsure), and _Swear an Iron Vow_ (formidable or extreme) to complete that quest. If you fail to score a hit when you _Swear an Iron Vow_, or refuse the quest, you are dead. Otherwise, you return to the mortal world and are now cursed. You may only clear the cursed debility by completing the quest.

On a *miss*, you are dead.
"""
            back_type = "back_to_suffer"

        case "Companion Endure Harm":
            text = """
*COMPANION ENDURE HARM*

When your *companion faces physical damage*, they suffer -health equal to the amount of harm inflicted. If your companion's health is 0, exchange any leftover -health for -momentum.
Then, roll +heart or +your companion's health, whichever is higher.

On a *strong hit*, your companion rallies. Give them +1 health.

On a *weak hit*, your companion is battered. If their health is 0, they cannot assist you until they gain at least +1 health.

On a *miss*, also suffer -1 momentum. If your companion's health is 0, they are gravely wounded and out of action. Without aid, they die in an hour or two.
If you roll a miss with a 1 on your action die, and your companion's health is 0, they are now dead. Take 1 experience for each marked ability on your companion asset, and remove it.
"""
            back_type = "back_to_suffer"

        case "Endure Stress":
            text = """
*ENDURE STRESS*

When you *face mental shock or despair*, suffer -spirit equal to your foe's rank or as appropriate to the situation. If your spirit is 0, suffer -momentum equal to any remaining -spirit.
Then, roll +spirit or +heart, whichever is higher.

On a *strong hit*, choose one.
• Shake it off: If your spirit is greater than 0, suffer -1 momentum in exchange for +1 spirit
• Embrace the darkness: Take +1 momentum

On a *weak hit*, you press on.

On a *miss*, also suffer -1 momentum. If you are at 0 spirit, you must mark shaken or corrupted (if currently unmarked) or roll on the following table.
• *1-10*: You are overwhelmed. _Face Desolation_.
• *11-25*: You give up. _Forsake Your Vow_ (if possible, one relevant to your current crisis).
• *26-50*: You give in to a fear or compulsion, and act against your better instincts.
• *51-00*: You persevere.
"""
            back_type = "back_to_suffer"

        case "Face Desolation":
            text = """
*FACE DESOLATION*

When *you are brought to the brink of desolation*, roll +heart.

On a *strong hit*, you resist and press on.

On a *weak hit*, choose one.
• Your spirit or sanity breaks, but not before you make a noble sacrifice. Envision your final moments.
• You see a vision of a dreaded event coming to pass. Envision that dark future (_Ask the Oracle_ if unsure), and _Swear an Iron Vow_ (formidable or extreme) to prevent it. If you fail to score a hit when you _Swear an Iron Vow_, or refuse the quest, you are lost. Otherwise, you return to your senses and are now tormented. You may only clear the tormented debility by completing the quest.

On a *miss*, you succumb to despair or horror and are lost.
"""
            back_type = "back_to_suffer"

        case "Out of Supply":
            text = """
*OUT OF SUPPLY*

When *your supply is exhausted* (reduced to 0), mark unprepared. If you suffer additional -supply while unprepared, you must exchange each additional -supply for any combination of -health, -spirit or -momentum as appropriate to the circumstances.
"""
            back_type = "back_to_suffer"

        case "Face a Setback":
            text = """
*FACE A SETBACK*

When *your momentum is at its minimum* (-6), and you suffer additional -momentum, choose one.
• Exchange each additional -momentum for any combination of -health, -spirit, or -supply as appropriate to the circumstances.
• Envision an event or discovery (_Ask the Oracle_ if unsure) which undermines your progress in a current quest, journey, or fight. Then, for each additional -momentum, clear 1 unit of progress on that track per its rank (troublesome=clear 3 progress; dangerous=clear 2 progress; formidable=clear 1 progress; extreme=clear 2 ticks; epic=clear 1 tick).
"""
            back_type = "back_to_suffer"

    keyboard = [
        [InlineKeyboardButton("Manual", callback_data=f"manual_{move_name}")],
        [InlineKeyboardButton("Back", callback_data=back_type)],
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
                "Back",
                callback_data=f'back_to_{move_name.lower().replace(" ", "_")}',
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"{move_name} Manual - Placeholder text"
    match move_name:
        case "Face Danger":
            text = """
The _Face Danger_ move is a catch-all for risky, dramatic, or complex actions not covered by another move. If you're trying to overcome an obstacle or resist a threat, make this move to see what happens. You select which stat to roll based on how you address the challenge.

A strong hit means you succeed. You are in control. What do you do next?

A weak hit means you overcome the obstacle or avoid the threat, but not without cost. Choose an option and envision what happens next. You don't have complete control. Consider how the situation might escalate, perhaps forcing you to react with another move.

A miss means you are thwarted in your action, fail to oppose the threat, or make some progress but at great cost. You must _Pay the Price_.
"""

        case "Secure Advantage":
            text = """
The structure of _Secure an Advantage_ is similar to _Face Danger_. You envision your action and roll + your most relevant stat. This move, however, is proactive rather than reactive. You're evaluating the situation or strengthening your position.
                
This move gives you an opportunity to build your momentum or improve your chance of success on a subsequent move. It's a good move to make if you want to take a moment to size up the situation, or if you're acting to gain control. It will often encompass a moment in time—such as shoving your foe with your shield to setup an attack. Or, it can represent preparation or evaluation spanning minutes, hours, or even days, depending on the narrative circumstances.

A strong hit means you've identified an opportunity or gained the upper hand. You knocked your enemy down. You moved into position for an arrow shot. You built your trap. You scouted the best path through the mountains. Now it's time to build on your success.

A weak hit means your action has helped, but your advantage is fleeting or a new danger or complication is revealed. You pushed, and the world pushes back. What happens next?

A miss means your attempt to gain advantage has backfired. You acted too slowly, presumed too much, or were outwitted or outmatched. _Pay the Price_.
"""

        case "Gather Information":
            text = """
Use this move when you're not sure of your next steps, when the trail has gone cold, when you make a careful search, or when you do fact-finding.

There's some overlap with other moves using +wits and involving knowledge, but each has their purpose. When you're forced to react with awareness or insight to deal with an immediate threat, that's _Face Danger_. When you size up your options or leverage your expertise and prepare to make a move, that's _Secure an Advantage_. When you're spending time searching, investigating, asking questions—especially related to a quest—that's when you _Gather Information_. Use whichever move is most appropriate to the circumstances and your intent.

A strong hit means you gain valuable new information. You know what you need to do next. Envision what you learn, or _Ask the Oracle_.

With a weak hit, you've learned something that makes your quest more complicated or dangerous. You know more about the situation, but it's unwelcome news. To move forward, you need to overcome new obstacles and see where the clues lead.

On a miss, some event or person acts against you, a dangerous new threat is revealed, or you learn of something which contradicts previous information or severely complicates your quest.
"""

        case "Heal":
            text = """
When you tend to physical damage or sickness—for yourself, an ally, or an NPC—make this move. Healing might be represented by staunching bleeding, binding wounds, applying salves, or using herbs to brew a tonic. In the Ironlands, healing is not overtly magical, but some folk know how to treat even the most dire of injuries and illnesses.
    
Healing takes time. A few minutes for a quick treatment to get someone on their feet. Hours or perhaps days for more severe injuries. Use what seems appropriate to the circumstances, and consider how this downtime affects your quests and other things going on in your world.

A miss can mean you've caused harm rather than helping, or some perilous event interrupts your care.

NPCs who are not companions do not have a health track. When you attempt to _Heal_ them, make this move and apply the result through the fiction. They will improve, or not, as appropriate to the move's outcome.
"""

        case "Resupply":
            text = """
When you're in the field and need to bolster your supply track, make this move. Fictionally, this represents hunting and gathering. You might also search an area where supplies might be found, such as an abandoned camp or field of battle.
                
If you're adventuring with allies, you share the same supply value. When one of you makes this move, each of you adjust your supply track.

If you have the unprepared condition marked, you can't _Resupply_. Instead, you need to find help in a community when you _Sojourn_.
"""

        case "Make Camp":
            text = """
Making camp can be a purely narrative activity and can be abstracted or roleplayed as you like. However, if you need to recover from the struggle of your adventures while traveling through the wilds, make this move.

Unlike most moves, you will not roll + a stat. Instead, you roll +supply. This represents your access to provisions and gear. Huddling in your cloak on the cold ground is a different experience than a warm fire, good food, and a dry tent.

On a strong hit, choose two from the list. You may not select a single option more than once. On a weak hit, choose one. If you recuperate or partake, you can also apply those benefits to your companions (NPC assets—see page 39).

If you are traveling with allies, only one of you makes this roll for the group. Each of you may then choose your own benefits on a strong or weak hit.

On a miss, you gain no benefits of your downtime. Perhaps you suffered troubling dreams (_Endure Stress_). Poor weather may have left you weary and cold (_Endure Harm_). Or, you were attacked. If in doubt, roll on the _Pay the Price_ table or _Ask the Oracle_ for inspiration. Depending on what you envision, you can play to see what happens, or jump to the next day as you continue on your journey the worse for wear.
"""

        case "Undertake Journey":
            text = """
This is Ironsworn's travel move. When you set off or push on toward a destination, make this move.

First, give your journey a rank. Decide how far—and how hazardous—it is based on the established fiction. If you're unsure, _Ask the Oracle_. Most of your journeys should be troublesome or dangerous. Formidable or extreme journeys might require weeks within your narrative, with appropriate stops, side quests, and adventures along the way. An epic journey is one of months, or even years. It is the journey of a lifetime.

If the journey is mundane—a relatively short distance through safe territory—don't make this move. Just narrate the trip and jump to what happens or what you do when you arrive.

*ALONG FOR THE RIDE?*\n
If you are part of a caravan or party of NPCs, and aren't an active participant in the planning or execution of the journey, you won't make this move or track progress. The journey will be resolved in the fiction. You can *Ask the Oracle* to determine what happens en route or when you arrive.

*ALLIES AND JOURNEYS*\n
If you are traveling with allies, one of you makes the _Undertake a Journey_ roll for each segment, and you share a progress track. The responsibility for leading the journey can switch from segment to segment as you like.

Your fellow travelers can assist by making the _Aid Your Ally_ move. Perhaps they are scouting ahead or sustaining you with a lively song. They can also _Resupply_ to represent foraging or hunting for supplies en route. Everyone should offer narrative color for what they do and see on the journey, even if they are not making moves.

Only the character making the move takes the momentum bonus on a strong hit. But, because your supply track is shared, each of you mark -1 supply when the acting character makes that choice on a strong hit or when they suffer a weak hit.

*WAYPOINTS*\n
If you score a strong or weak hit on this move, you reach a waypoint. A waypoint is a feature of the landscape, a settlement, or a point-of-interest. Depending on the information you have or whether you have traveled this area before, a specific waypoint may be known to you. If it isn't, envision what you find. If you need inspiration, _Ask the Oracle_.

You will find random tables for waypoint features on page 176, but do not rely too heavily on these generators. Seek inspiration from your fiction and the landscape you envision around you. If it's interesting, wondrous, or creates new opportunities for drama and adventure, bring it to life.

Depending on the pace of your story and your current situation, you may choose to focus on this waypoint. A settlement can offer roleplay opportunities or provide a chance to recuperate and provision via the _Sojourn_ move. In the wilds, you might make moves such as _Make Camp_, _Resupply_, or _Secure an Advantage_. Or, you can play out a scene not involving moves as you interact with your allies or the world. Mix it up. Some waypoints will pass as a cinematic montage (doubtlessly depicted in a soaring helicopter shot as you trudge over jagged hills). Other waypoints offer opportunities to zoom in, enriching your story and your world.

When you roll a match (page 9), take the opportunity to introduce something unexpected. This could be an encounter, a surprising or dramatic feature of the landscape, or a turn of events in your current quest.

*MARKING PROGRESS*\n
When you score a hit and reach a waypoint, you mark progress per the rank of the journey. For example, on a dangerous journey you mark 2 progress (filling two boxes on your progress track) for each waypoint. When you feel you have accumulated enough progress and are ready to make a final push towards your destination, make the _Reach Your Destination_ move. For more on progress tracks and progress moves, see page 14.

*TRAVEL TIME*\n
Travel time can largely be abstracted. The time between waypoints might be hours or days, depending on the terrain and the distance. If it's important, make a judgment call based on what you know of your journey, or _Ask the Oracle_.

*MOUNTS AND TRANSPORT*\n
Horses, mules, and transport (such as boats) influence the fiction of your journey—the logistics of travel and how long it takes. They do not provide a mechanical benefit unless you have an asset which gives you a bonus (such as a *Horse* companion).

*MANAGING RESOURCES*\n
You can intersperse _Resupply_ or _Make Camp_ moves during your journey to manage your health, spirit and supply, or to create new scenes as diversions. Don't be concerned with using the _Make Camp_ move as an automatic capstone to a day of travel. You can be assumed to rest and camp as appropriate without making the move, and you can roleplay out those scenes or gloss over them as you like. When you want the mechanical benefit of the _Make Camp_ move, or you're interested in playing the move out through the fiction, then do it.

*ON A MISS...*\n
You do not mark progress on a miss. Instead, you encounter a new danger. You might face hazards through the weather, the terrain, encounters with creatures or people, attacks from your enemies, strange discoveries, or supernatural events. Decide what happens based on your current circumstances and surroundings, roll on the _Pay the Price_ table, or _Ask the Oracle_ for inspiration. Depending on your desired narrative pace, you can then play out the event to see what happens, or summarize and apply the consequences immediately.

For example, you roll a miss and decide you encounter a broad, wild river which must be crossed to continue on your journey. If you want to focus on how you deal with the situation, play to see what happens by making moves. You might _Secure an Advantage_ by exploring upriver for a ford and then _Face Danger_ to cross. Or, if want to quickly push the story forward, you could fast-forward to a perilous outcome such as losing some provisions during the crossing (suffer -supply). Mix things up, especially on long journeys.
"""

        case "Reach Destination":
            text = """
When you have made progress on your journey progress track and are ready to complete your expedition, make this move. Since this is a progress move, you tally the number of filled boxes on your progress track. This is your progress score. Only add fully filled boxes (those with four ticks). Then, roll your challenge dice, compare to your progress score, and resolve a strong hit, weak hit, or miss as normal. You may not burn momentum on this roll, and you are not affected by negative momentum.

When you score a strong hit, you arrive at your destination and are well-positioned for success. This should be reflected in the mechanical benefit offered by the move, but also in how you envision your arrival. If this has been a long, arduous journey, make this moment feel rewarding.

On a weak hit, something complicates your arrival or your next steps. Things are not what you expected, or a new danger reveals itself. Perhaps the village is occupied by a raiding party, or the mystic whose counsel you sought is initially hostile to you. Envision what you find and play to see what happens.

On a miss, something has gone horribly wrong. You realize you are off-course, you had bad information about your destination, or you face a turn of events undermining your purpose here. Depending on the circumstances, this might mean your journey ends in failure, or that you must push on while clearing all but one of your filled progress and raising the journey's rank.

If you are traveling with allies, one of you makes this move. Each of you benefit (or suffer) from the narrative outcome of the roll. Only the character making the move gets the mechanical benefit of a strong hit.
"""

        case "Compel":
            text = """
When you act to persuade someone to do as you ask, or give you something, make this move. It might be through bargaining, or intimidation, charm, diplomacy, or trickery. Use the appropriate stat based on your approach, and roll to see what happens.

This move doesn't give you free rein to control the actions of other characters in your world. Remember: Fiction first. Consider their motivations. What is your leverage over them? What do they stand to gain or avoid? Do you have an existing relationship? If your argument has no merit, or your threat or promise carries no weight, you can't make this move. You can't intimidate your way out of a situation where you are at a clear disadvantage. You can't barter when you have nothing of value to offer. If you are unsure, _Ask the Oracle_, 'Would they consider this?' If the answer is yes, make the move.

On the other hand, if their positive response is all but guaranteed—you are acting obviously in their best interest or offering a trade of fair value—don't make this move. Just make it happen. Save the move for times when the situation is uncertain and dramatic.

On a weak hit, success is hinged on their counter-proposal. Again, look to the fiction. What would they want? What would satisfy their concerns or motivate them to comply? If you accept their offer, you gain ground. If not, you've encountered an obstacle in your quest and need to find another path forward.

If you promise them something as part of this move, but then fail to do as you promised, they should respond accordingly. Perhaps it means a rude welcome when next you return to this community. If they are powerful, they may even act against you. If you share a bond, you would most certainly _Test Your Bond_. Your actions, good or bad, should have ramifications for your story beyond the scope of the move.

On a miss, they are insulted, angered, inflexible, see through your lies, or demand something of you which costs you dearly. Their response should introduce new dangers or complications.

_Compel_ may also be used to bring combat to a non-violent conclusion. Your approach dictates the stat you use—typically +iron when you threaten with further violence, +heart when you attempt to surrender or reason with them, and +shadow when you use trickery. Your foe must have a reason to be open to your approach. If unsure, _Ask the Oracle_. To learn more, see page 88.
"""

        case "Sojourn":
            text = """
Communities stand as an oasis within the perilous wilds of the Ironlands. They are a source of protection, trade, and fellowship. However, there are no grand cities like those that stood in the Old World. Life here is too harsh. Resources too few.

When you rest, replenish, and share fellowship within a community, make this move. Depending on your level of success, you can choose one or more debilities to clear or tracks to increase. If you share a bond with this community and score a hit, you may select one more.

You may select an option only once. If you recuperate, you can also apply those benefits to your companions (NPC assets—see page 39). If you _Sojourn_ with allies, only one of you makes this move, but all of you can make your own choices on a strong or weak hit.

Your _Sojourn_ should require several hours or several days, depending on your current circumstances and level of aid and recovery required. Make this move only once when visiting a community, unless the situation changes.

On a hit, this move also includes an option to roll again for one of your selected recover actions. The second roll either provides a bonus to that activity (on a hit), or causes you to lose all benefits for your recovery. For example, if you are suffering from low spirit, you might choose to focus on the consort action, representing time in the mead hall or intimacy with a lover. Roll +heart again, and take the bonus if you score a hit.

You should envision what makes this community and its people unique. Give every community at least one memorable characteristic. If you need inspiration, _Ask the Oracle_. You will find creative prompts, along with generators for community names and troubles in chapter 6 (page 165).

Narratively, you can imagine much of the time in this community passing as a montage. If you choose to focus on a recovery action, zoom into that scene and envision what happens. You might be in the healer's house, at the market, dancing at a festival, or speaking with the clan leader and making plans. Envision how this scene begins, make your roll, and then narrate the conclusion of the scene—good or bad—based on the result of your focus roll.

You can also perform additional moves while in the community. If you need to _Gather Information_, _Compel someone_, or _Draw the Circle_ to resolve a feud, zoom into those scenes and play to see what happens. _Sojourn_ is an overarching move that sets the tone for your stay and defines the mechanics of your recovery. It is not the only move you can make.

On a miss, something goes wrong. You are not welcomed. The citizens are hostile to you. Your dark mood alienates you. A perilous event threatens you all. Envision what happens based on your current circumstances, or _Ask the Oracle_.
"""

        case "Draw Circle":
            text = """
Ritualized duels are a common way of dealing with disputes among Ironlanders. When you challenge someone or accept a challenge, you each trace one-half of the outline of a circle into the ground with the point of an iron blade. Then, you face each other in the center of the circle and fight.

You setup your foe's progress track per the _Enter the Fray_ move, but use this move instead of _Enter the Fray_ to begin the fight. You have initiative at the start of combat unless you score a miss or choose the option to grant first strike.

Duels are usually stopped when one of the duelists surrenders or is clearly defeated. The victor may then make a demand which the loser must abide by. Not complying with this demand means ostracism and shame. If you lose a duel, envision what your opponent demands of you. If you're unsure, _Ask the Oracle_. Then, do it or face the narrative cost of your dishonor.

Duels may also be to the death. If one of the combatants declares their intent to fight to the death, the other must agree or forfeit.
"""

        case "Forge Bond":
            text = """
Bonds connect you to the people of the Ironlands. They provide a story benefit by enriching your interactions and creating connections with a recurring cast of characters and familiar places. They also provide mechanical benefits by giving you adds when you make moves such as _Sojourn_ or _Compel_. And, perhaps most importantly, your bonds help determine your ultimate fate when you retire from adventuring and _Write Your Epilogue_.

Bonds can be created through narrative circumstances or through sworn vows. If you've established a strong relationship with a person or community, you may _Forge a Bond_ to give it significance. If you make this move after you successfully _Fulfill Your Vow_ in service to them, you have proven yourself worthy and may reroll any dice.

When you _Forge a Bond_ and score a strong hit, mark a tick on your bond progress track (page 36) and make note of your bond.

On a weak hit, they ask more of you. It might be a task, an item, a concession, or even a vow. Envision what they need, or _Ask the Oracle_. If you do it, or _Swear an Iron Vow_, you can mark the bond.

On a miss, they have refused you. Why? The answer should introduce new complications or dangers.

*BONDS AND THE FICTION*\n
In the fiction of your world, bonds can be ceremonial. If your bond is with a person, perhaps you trade gifts. When you form a bond with a community, they may honor you in their own way. Envision what these ceremonies look like to add color and texture to the setting.

Also, respect the narrative weight of a bond. Don't declare a bond with everyone in sight to add more ticks to your bond progress track. Your bonds represent true, deep connections.

*BONDS AND ALLIES*\n
If you and your allies act together to _Forge a Bond_ with an NPC or community, only one of you makes the move. Others can _Aid Your Ally_ to provide support. If you are successful, each of you may mark a tick on your bond progress track. Only the character making the move takes the mechanical benefits of a strong hit (+1 spirit or +2 momentum).

Bonds can also be made between allies. One of you makes the move, and both of you may mark the bond on a hit. If you score a weak hit, your ally may decide what they ask of you. On a miss, something still stands between you. What is it? What must you do to form a deeper connection?
"""
        case "Test Bond":
            text = """
Bonds are not necessarily everlasting. Events in your story may cause your bond to be tested. How strong is your commitment? If you seek to maintain this bond, at what cost? When you are forced to act against a community or person you share a bond with, fail in a crucial task for them, or they break faith with you, make this move.

You should _Test Your Bond_ within the community or in the company of the person with whom you share the bond. If an incident forces this test, but you aren't in a position to resolve it, make a note. Then, make this move when you next come in contact. If extended time passes without making the test (days, weeks, or months, depending on the circumstance), clear the bond and be done with it.

If you and your allies share a bond with an NPC or community, and you act together to _Test Your Bond_, only one of you makes this move.
"""
        case "Aid Ally":
            text = """
When you take an action to aid an ally (another player's character) through the _Secure an Advantage_ move, you can hand over the benefits of that move to your ally. This represents setting your ally up for success through a supporting action. You might be distracting a foe in combat, scouting ahead on a journey, or giving them encouragement as you stand against a dire threat.

If you score a strong hit when you _Secure an Advantage_, your ally makes the choice between +2 momentum or making an immediate move with a +1 add. If you have an asset which gives you any additional benefits on the outcome of a _Secure an Advantage_ move, your ally also takes those benefits (instead of you).

In combat, this is a proactive move, made when you have initiative. If you score a strong hit, you and your ally both take or retain initiative.

On a weak hit when you _Secure an Advantage_, your ally takes +1 momentum. But, this advantage is fleeting or your situation becomes more complicated or dangerous. If you are in combat, you both lose initiative.

On a miss, one or both of you should _Pay the Price_ as appropriate to the circumstances and your intent when making the move. If in doubt, _Ask the Oracle_. As with a weak hit, you both lose initiative when in combat.

If multiple characters make this move to contribute to an ally action, all _Secure an Advantage_ bonuses will stack. As long as someone scores a strong hit, the target character can take or retain initiative.

Don't ping pong this move back and forth between two characters in an attempt to build momentum. Envision what you are doing to _Aid Your Ally_, make the _Secure an Advantage_ move, resolve it, and hand the reins over to your ally as they leverage the advantage. Keep it moving. Make things happen.
"""
        case "Write Epilogue":
            text = """
You make this move only once—when all your vows are fulfilled or forsaken and you choose to end your character's adventuring life. For better or worse, the bonds you've made will echo through your days. How have you left your mark? Where are you welcomed and where are you shunned? What remains of you when your quests are at an end? 

This is a progress move. Tally the number of filled boxes on your bonds progress track as your progress score. Only add fully filled boxes (those with four ticks). Then, roll your challenge dice, compare to your progress score, and resolve a strong hit, weak hit, or miss as normal. You may not burn momentum on this roll, and you are not affected by negative momentum.

Based on the result of this move, envision how you spend the remainder of your days.
"""
        case "Enter Fray":
            text = """
Make this move when combat is joined. Set up your progress tracks for your foes and roll to see who is initially in control. Then, play to see what happens.

If you are fighting with allies, each of you make your own move to _Enter the Fray_. The outcome determines your initial positioning and readiness. You and the other players then envision the scene and make moves as appropriate. If you have initiative, you are positioned to make proactive moves. If not, you make moves to defend against attacks or get into position. If you and your allies are fighting against common enemies, you share progress tracks and mark the harm you each inflict.

If you are fighting a group of troublesome or dangerous foes, you can combine them into a single progress track. This is called a *pack*. Managing your progress against a pack is easier than tracking them as individuals, and will make combat go a bit faster. For a small pack (about 3 to 5), increase the rank by one. For a large pack (about 6 to 10) increase the rank by two. If you are facing more than 10 troublesome or dangerous foes, group them into smaller packs and associated progress tracks as appropriate. 

For more about the foes you might face in the Ironlands, see page 133.
"""
        case "Strike":
            text = """
Make this move when you have initiative and act to inflict harm on your foe. Narratively, this move might represent a focused moment in time—a single sweep of your axe or the flight of an arrow. Or, it can depict a flurry of attacks as you put your opponent on the defensive. 

On a strong hit, you strike true. By default you inflict 2 harm if you are armed with a deadly weapon (such as a sword, axe, spear, or bow), and 1 harm if not. A strong hit on this move gives you an additional +1 harm (so, 3 harm with a deadly weapon). You may also have additional bonuses provided by assets.

Each point of harm you inflict is marked as progress on your foe's progress track, as appropriate to their rank. For example, each point of harm equals 2 ticks when fighting an extreme enemy, or 2 full progress boxes when fighting a dangerous enemy. See page 134 for more on NPC ranks and inflicting harm.

Narratively, a strong hit represents wounding your enemy or wearing them down. You have initiative and can make your next move. If this attack was intended as a decisive blow, you can attempt to _End the Fight_.

On a weak hit, you've done some damage but have overextended or your foe counters. You mark your harm, and your foe has initiative. What do they do next?

On a miss, you must _Pay the Price_. Your opponent strikes back and you _Endure Harm_. You lose position or advantage and suffer -momentum. You face a new or intensified danger. A companion or ally is put in harm's way. Your weapon is dropped or broken. Let the outcome flow out of the fiction, or roll on the _Pay the Price_ table to see what happens. 
"""
        case "Clash":
            text = """
When your foe has initiative and attacks, and you choose to fight back, make this move.

First, envision your action and the fiction of the exchange. Is this a focused, dramatic moment where you each seek an opening? Or is it a flurry of attacks and parries, advances and retreats? The outcome of the _Clash_ determines if your foe presses their advantage, or if you take control of the fight.

On a strong hit, you inflict your harm and steal back initiative. On a weak hit, you manage to inflict harm, but your foe retains initiative and you must _Pay the Price_. The price might be that you _Endure Harm_ as your foe counters. Or, you may face some other dramatic outcome as appropriate to the current situation and your foe's intent.

On a miss, you fail to inflict harm and must _Pay the Price_. This fight is turning against you.

As with the _Strike_ move, each point of harm you inflict is marked on your foe's progress track, as appropriate to their rank (page 134).

If you aren't actively fighting back—you're just trying to avoid the attack or seeking cover—you should _Face Danger_ instead of _Clash_. Using that move gives you more flexibility to bring a favored stat into play, and you suffer a relatively minor cost on a weak hit. Unfortunately, you also give up the opportunity to inflict harm on your foe. See page 85 for more about using _Face Danger_ in a fight.

If you ever respond to an attack by just taking the hit, that's not a move. The outcome isn't in much doubt. _Pay the Price_.
"""
        case "Turn Tide":
            text = """
This move represents a last ditch effort to recover control of the fight. It is that moment when all seems lost, but the hero somehow rallies. 

_Turn the Tide_ lets you take initiative and make a move. The move can be whatever is appropriate under the circumstance—likely _Strike_ or _Secure an Advantage_. Roll the move (add +1), and act on the results. If you've scored a hit, you may take an additional +1 momentum. Then, play to see what happens. Hopefully this bold action is a turning point for the fight.

Here's the catch: If you score a miss when you make your move, you should add extra severity to the consequences. You might face additional harm. Your weapon is broken. Your companion is grievously wounded. Consider the result of your failure and give it teeth. If in doubt, _Ask the Oracle_.

Narratively, this is a dramatic moment. Focus on it. Envision your character's action. You struggle to your feet and raise your sword, your eyes hardening with determination. You spur your mount into a desperate charge. You grab your opponent's blade in your bare hand. You pull the dagger from your boot and lunge. Or, perhaps you state your name, lament the killing of your father, and tell your foe to prepare for death.
"""

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
            [InlineKeyboardButton("Page +", callback_data="page+")],
            [
                InlineKeyboardButton(
                    "Back",
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
    "enter_fray",
    "strike",
    "clash",
    "turn_tide",
    "end_fight",
    "battle",
    "other_battle_moves",
    "endure_harm",
    "face_death",
    "companion_endure_harm",
    "endure_stress",
    "face_desolation",
    "out_supply",
    "face_setback",
    "back_to_main",
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
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
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
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Relationship moves:", reply_markup=reply_markup)


async def combat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Enter the Fray", callback_data="enter_fray")],
        [InlineKeyboardButton("Strike", callback_data="strike")],
        [InlineKeyboardButton("Clash", callback_data="clash")],
        [InlineKeyboardButton("Turn the Tide", callback_data="turn_tide")],
        [InlineKeyboardButton("End the Fight", callback_data="end_fight")],
        [InlineKeyboardButton("Battle", callback_data="battle")],
        [InlineKeyboardButton("Other moves", callback_data="other_battle_moves")],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Combat moves:", reply_markup=reply_markup)


async def suffer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Endure Harm", callback_data="endure_harm")],
        [InlineKeyboardButton("Face Death", callback_data="face_death")],
        [
            InlineKeyboardButton(
                "Companion Endure Harm", callback_data="companion_endure_harm"
            )
        ],
        [InlineKeyboardButton("Endure Stress", callback_data="endure_stress")],
        [InlineKeyboardButton("Face Desolation", callback_data="face_desolation")],
        [InlineKeyboardButton("Out of Supply", callback_data="out_supply")],
        [InlineKeyboardButton("Face a Setback", callback_data="face_setback")],
        [InlineKeyboardButton("Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Suffer moves:", reply_markup=reply_markup)


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

    logging.info("closing_all")
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


async def back_to_combat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await combat_callback(update, context)


async def back_to_suffer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await suffer_callback(update, context)


async def back_to_quest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await quest_callback(update, context)


async def back_to_fate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fate_callback(update, context)


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
    "back_to_combat": back_to_combat_callback,
    "back_to_suffer": back_to_suffer_callback,
    "back_to_quest": back_to_quest_callback,
    "back_to_fate": back_to_fate_callback,
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
