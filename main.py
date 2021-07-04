import discord
from discord import *
from uno import *
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents = intents)
uno = UNO()   
admins = []
textChannels = []
newRoles = []
unoEmbeds = []
unoMsg = None

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    msg = message.content.lower()
    card = message.content
    player = message.author
    if msg.startswith('!uno') and uno.playingUno == False and player not in uno.players:
        uno.players.append(player)
        global unoMsg
        unoMsg = await message.channel.send(embed = uno.refreshPlayers())
        await unoMsg.add_reaction('✋')
        await unoMsg.add_reaction('▶️')
        await unoMsg.add_reaction('🚪')
    elif uno.playingUno == True and message.author in uno.players:
        await message.delete()
        if uno.stacking == True and not card.endswith('➕'):
            uno.decks[uno.turn] += uno.stackingCards
            await sendCards(uno.players[uno.turn], uno.stackingCards)
            uno.stackingCards.clear()
            uno.stacking = False
            await reloadUnoEmbeds()
        if uno.checkTurn(player) and uno.rainbow == False:
            if uno.checkCard(card):
                if uno.stacking == True:
                    if card.endswith('➕'):
                        playingResult = uno.playCard(card)
                        uno.stackingCards += playingResult
                        winner = uno.checkWin()
                        if winner != None:
                            await generalChannel.send(winner + ' WON!')
                        if uno.stacking == True:
                            await deleteCard(player, card)       
                            await reloadUnoEmbeds()
                        else:
                            uno.addSpecificCards(uno.stackingCards)
                            await sendCards(uno.nextPlayer(), uno.stackingCards)
                            uno.stackingCards.clear()
                            await deleteCard(player, card)       
                            await reloadUnoEmbeds()
                else:
                    endList = uno.checkEnd()
                    if endList != None:
                        i = 1
                        uno.unoEmb.description = 'Winners: '
                        for player in endList:
                            uno.unoEmb.description += '\n' + str(i) + '. ' + player
                            i += 1
                            uno.unoEmb.set_footer(text='The game finished') 
                        await unoMsg.edit(embed = uno.unoEmb)
                        await endGame()
                    else:
                        playingResult = uno.playCard(card)
                        winner = uno.checkWin()
                        if winner != None:
                            await generalChannel.send(winner + ' WON!')
                        if uno.stacking == True:
                            uno.stackingCards += playingResult
                            await deleteCard(player, card)       
                            await reloadUnoEmbeds()
                        else:                
                            if type(playingResult) is list:
                                playingResult += uno.stackingCards
                                await sendCards(uno.nextPlayer(), playingResult)
                                uno.stackingCards = []
                            await deleteCard(player, card)       
                            await reloadUnoEmbeds()
                            if uno.rainbow == True:
                                uno.unoEmb.add_field(name='Colour', value= player.display_name + ' has to choose a colour')
                                for emb in unoEmbeds:
                                    await emb.edit(embed = uno.unoEmb)
                                    if emb.channel.name.lower() == message.author.display_name.lower():
                                        await emb.add_reaction('🟥')
                                        await emb.add_reaction('🟩')
                                        await emb.add_reaction('🟨')
                                        await emb.add_reaction('🟦')
                                        global rainbowEmb 
                                        rainbowEmb = emb
            else:
                await message.channel.send('You do not have that card or you can\'t play')

@client.event
async def on_reaction_add(reaction, user):
    guild = reaction.message.guild
    colours = ['🟥' , '🟩' , '🟨', '🟦']
    if user != client.user:
        await reaction.remove(user)
        if reaction.emoji == '✋' and user not in uno.players:
            uno.players.append(user)
            await unoMsg.edit(embed = uno.refreshPlayers())

        elif reaction.emoji == '🚪' and user in uno.players:
            uno.players.remove(user)
            await unoMsg.edit(embed = uno.refreshPlayers())

        elif reaction.emoji == '▶️' and len(uno.players) > 1:
            await unoMsg.clear_reactions()
            global generalChannel
            generalChannel = reaction.message.channel
            await removeAdminRole()
            await makeChannels(guild)
            uno.unoEmb.set_footer(text='Sending your cards please wait! 🔄')
            await unoMsg.edit(embed = uno.unoEmb)
            global allDecks
            allDecks = uno.makeDecks()
            for player in allDecks:
                await sendCards(player, allDecks.get(player))
            unoEmb = uno.startGame()
            generalEmb = discord.Embed(title = 'UNO', description = 'Players: \n' + uno.getPlayerNames() + '\nThese users are now playing UNO!', colour = discord.Colour.red())
            await unoMsg.edit(embed = generalEmb)
            for channel in textChannels:
                channelMsg = await channel.send(embed = unoEmb)
                await channelMsg.add_reaction('➕')
                await channelMsg.add_reaction('🛑')
                unoEmbeds.append(channelMsg)
        elif reaction.emoji == '🛑' and user in uno.players:
            await endGame()
            newEmb = discord.Embed(title = 'UNO', description = 'The game was stopped by ' + user.display_name + '\nYou will now have to start a new game!', colour = discord.Colour.red())
            await unoMsg.edit(embed = newEmb)
        
        elif reaction.emoji == '➕' and user in uno.players and uno.stacking == False:
            if uno.checkTurn(user):
                card = uno.plusOne()
                cards = []
                cards.append(card)
                await sendCards(user, cards)
                await reloadUnoEmbeds()
        elif reaction.emoji in colours and uno.rainbow == True:
            uno.unoEmb.clear_fields()
            await rainbowEmb.clear_reactions()
            await rainbowEmb.add_reaction('➕')
            await rainbowEmb.add_reaction('🛑')
            uno.unoEmb.description = uno.unoEmb.description.replace('⬛', reaction.emoji)
            uno.rainbow = False
            for emb in unoEmbeds:
                await emb.edit(embed = uno.unoEmb)


  
async def deleteCard(player, card):
    for channel in textChannels:
        if channel.name.lower() == player.display_name.lower():
            cards = []
            if card.__contains__('+'):
                cards = card.split('+')
            else:
                cards.append(card)
            async for message in channel.history():
                for cardino in cards:
                    if message.content == cardino:
                        try:
                            await message.delete()
                            cards.remove(cardino)
                        except:
                            pass

 
async def sendCards(player, cards):
    for channel in textChannels:
        if channel.name.lower() == player.display_name.lower():
            for card in cards:
                await channel.send(card)


async def removeAdminRole():
    for player in uno.players:
        for role in player.roles:
            if role.name.lower() == 'admin':
                global adminRole
                adminRole = role
                admins.append(player)
                await player.remove_roles(role)
    
async def returnAdminRole():
    for player in admins:
        await player.add_roles(adminRole)

async def makeChannels(guild):
    for player in uno.players:
        role = await guild.create_role(name = player.display_name)
        newRoles.append(role)
        await player.add_roles(role)
        overW={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel(name = player.display_name, overwrites= overW)
        textChannels.append(channel)

async def deleteChannels():
    for channel in textChannels:
        await channel.delete()
    for role in newRoles:
        await role.delete()

async def reloadUnoEmbeds():
    endEmb = uno.endTurn()                   
    for unoEmb in unoEmbeds:
        await unoEmb.delete()

    unoEmbeds.clear()
    for channel in textChannels:
        unoEmb = await channel.send(embed = endEmb)
        await unoEmb.add_reaction('➕')
        await unoEmb.add_reaction('🛑')
        unoEmbeds.append(unoEmb)

def resetFields():
    global admins
    global textChannels
    global newRoles
    global unoEmbeds
    global stackingCards
    admins = []
    textChannels = []
    newRoles = []
    unoEmbeds = []

async def endGame():
    await returnAdminRole()
    await deleteChannels()
    resetFields()
    uno.reset()

token = os.getenv('TOKEN')
client.run(token)

