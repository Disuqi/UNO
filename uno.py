import discord
from discord import *
import random

class UNO:
    mainDeck = []
    playedCards = []
    players = []
    won = []
    decks = []
    turn = 0
    playingUno = False
    unoEmb = None
    blocked = False
    rainbow = False
    stacking = False
    stackingCards = []
    def __init__(self):
        self.makeMainDeck()
        self.unoEmb = Embed(title = 'UNO', description = 'Players: \n' + self.getPlayerNames(), colour = discord.Colour.red())
        self.unoEmb.add_field(name='Rules:', value= '✋ to join the game \n▶️ to start the game \n🚪 to leave before starting the game \n🛑 to stop a game \n➕ during the game to draw a card\nUse + to stack cards with the same number\nE.g. 🟥3️⃣+🟩3️⃣+🟨3️⃣')
        
    def refreshPlayers(self):
        self.unoEmb.description = 'Players: \n' + self.getPlayerNames()
        return self.unoEmb

    def getPlayerNames(self):
        playersName = []
        for player in self.players:
            playersName.append(player.display_name)
        listOfPlayers = '\n'.join(playersName)
        return listOfPlayers
    
    def makeMainDeck(self):
        colors = ['🟥', '🟩', '🟨', '🟦']
        signs = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣' ,'7️⃣', '8️⃣', '9️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣' ,'7️⃣', '8️⃣', '9️⃣','🔁', '🚫', '➕','🔁', '🚫', '➕']
        for color in colors:
            for number in signs:
                self.mainDeck.append(color + number)
        for i in range(4):
            self.mainDeck.append('⬛' + '🌈')
            self.mainDeck.append('⬛'+ '☠️')
    
    def startGame(self):
        self.playingUno = True        
        firstCard = random.choice(self.mainDeck)
        while firstCard.__contains__('⬛'):   
            firstCard = random.choice(self.mainDeck)
        self.mainDeck.remove(firstCard)
        self.playedCards.append(firstCard)
        self.unoEmb = Embed(title = 'UNO', description = firstCard, colour = discord.Colour.red())
        self.unoEmb.clear_fields()
        self.unoEmb.set_footer(text = 'It\'s ' + self.players[self.turn].display_name + '\'s turn')
        return self.unoEmb

    def makeDecks(self):
        for player in self.players:
            deck = []
            for i in range(7):
                card = random.choice(self.mainDeck)
                deck.append(card)
                self.mainDeck.remove(card)
            self.decks.append(deck)
        playersDecks = dict(zip(self.players, self.decks))
        return playersDecks
    
    def checkTurn(self, user):
        if user == self.players[self.turn]:
            return True
        else:
            return False
    def addSpecificCards(self, cards):
        for card in cards:
            self.decks[self.nextTurn()].append(card)

    def addCards(self, number):
        cards = []
        for i in range(number):
            card = random.choice(self.mainDeck)
            cards.append(card)
            self.mainDeck.remove(card)
            self.checkMainDeck()
            self.playedCards.append(card)
            if self.stacking == False:
                self.decks[self.nextTurn()].append(card)
        if len(self.stackingCards) > 0:
            for cardino in self.stackingCards:
                self.decks[self.nextTurn()].append(cardino)
        return cards

    def plusOne(self):
        card = random.choice(self.mainDeck)
        self.mainDeck.remove(card)
        self.checkMainDeck()
        self.playedCards.append(card)
        self.decks[self.turn].append(card)
        return card
        
    def endTurn(self):
        self.turn += 1
        if self.turn >= len(self.players):
            self.turn = 0
        if self.blocked == True:
            self.turn += 1 
            if self.turn >= len(self.players):
                self.turn = 0 
    
        self.blocked = False 
        self.unoEmb.set_footer(text = 'It\'s ' + self.players[self.turn].display_name + '\'s turn')
        return self.unoEmb

    def playCard(self, card):
        if card.__contains__('+'):
            cards  = card.split('+')
            addedcards = []           
            checker = self.checkStacking()
            for cardino in cards:
                self.decks[self.turn].remove(cardino)
                self.unoEmb.description = cardino
                self.playedCards.append(cardino)            
                if cardino.endswith('➕'):
                    self.stacking = checker
                    if self.stacking == False:
                        self.blocked = True
                    addedcards += self.addCards(2)
                elif cardino.endswith('🚫'):
                    self.blocked = True
                elif cardino.endswith('🔁'):
                    self.players.reverse()
                    self.decks.reverse()
            if len(addedcards) > 0:
                return addedcards
        else:         
            self.decks[self.turn].remove(card)
            self.unoEmb.description = card
            self.playedCards.append(card)
            if card == '⬛☠️':
                self.rainbow = True
                return self.addCards(4)
            elif card == '⬛🌈':
                self.rainbow = True
            elif card.endswith('➕'):
                self.stacking = self.checkStacking()
                if self.stacking == False:
                    self.blocked = True
                return self.addCards(2)
            elif card.endswith('🚫'):
                self.blocked = True
            elif card.endswith('🔁'):
                self.players.reverse()
                self.decks.reverse()


    def nextPlayer(self):
        nextPlayer = self.players[self.nextTurn()]
        return nextPlayer

    def nextTurn(self):
        nextTurn = self.turn + 1
        if nextTurn >= len(self.players):
            nextTurn = 0
        return nextTurn

    def checkWin(self):
        deck = self.decks[self.turn]
        if len(deck) == 0:
            winner = self.players[self.turn].display_name
            self.players.pop(self.turn)
            self.decks.pop(self.turn)
            self.won.append(winner)
            return winner

    def checkEnd(self):
        if len(self.players) <= 1:
            self.won.append(self.players[0].display_name)
            self.reset
            return self.won
        else:
            return None
    def checkCard(self, card):
        result = False
        if card.__contains__('+'):
            cards = card.split('+')
            cardNumber = cards[0][1]
            for  card in cards:
                if card in self.decks[self.turn]:
                    result = True
                else:
                    result = False
                    break
                if card[1] == cardNumber:
                    result = True
                else:
                    result = False
            if result == True:
                if cards[0][0] == self.unoEmb.description[0] or cards[0][1] == self.unoEmb.description[1]:
                    return result
                else:
                    result = False
                    return result
            else:
                return result
        else:
            if card in self.decks[self.turn]:
                if card.startswith('⬛'):
                    return True
                elif card[0] == self.unoEmb.description[0] or card[1] == self.unoEmb.description[1]:
                    return True

    def checkStacking(self):
        for card in self.decks[self.nextTurn()]:
            if card.endswith('➕'):
                return True
        return False
    def checkMainDeck(self):
        if len(self.mainDeck) <= 4:
            self.mainDeck += self.playedCards

    def reset(self):
        self.mainDeck = []
        self.playedCards = []
        self.players = []
        self.decks = []
        self.turn = 0
        self.playingUno = False
        self.rainbow = False
        self.blocked = False
        self.stacking = False
        self.stackingCards = []
        self.unoEmb = Embed(title = 'UNO', description = 'Players: \n' + self.getPlayerNames(), colour = discord.Colour.red())
        self.unoEmb.add_field(name='Rules:', value= '✋ to join the game \n▶️ to start the game \n🚪 to leave before starting the game \n🛑 to stop a game \n➕ during the game to draw a card\nUse + to stack cards with the same number\nE.g. 🟥3️⃣+🟩3️⃣+🟨3️⃣')
        self.makeMainDeck()
