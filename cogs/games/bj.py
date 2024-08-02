####################################################################
# BLACKJACK! YAY!
# 
# Comment definitions:
# short-version: actual-version
# p: player
# d: dealer

# dealer first turn
# player's turns
# dealer turn
# end game


# with dealer chip:
# dealer first turn
# dealer turn
# player turn
# end game



import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

# import cooldowns
from random import randint, shuffle
import asyncio, cooldowns

import io
from PIL import Image, ImageFont
from pilmoji import Pilmoji

import emojis
from cogs.settings import GetUserSetting
from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck

class CreditsToBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label="Amount of credits", placeholder="Max amount is your bet", min_length=1)

class Insurance(nextcord.ui.Modal):
	def __init__(self, view, bot):
		super().__init__(title="Insurance")
		self.add_item(CreditsToBet())
		self.view = view
		self.bot:commands.bot.Bot = bot

	async def callback(self, interaction: Interaction):
		if interaction.user.id != self.view.ownerId:
			await interaction.send("This is not your game!", ephemeral=True)
			return
		if not self.children[0].value.isdigit():
			await interaction.send("Please enter a valid number!", ephemeral=True)
			return
		self.view.insuranceBet = int(self.children[0].value)
		if self.view.insuranceBet > self.view.amntbet:
			await interaction.send(f"You can't bet more than your original bet of {self.view.amntbet}!", ephemeral=True)
			return
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, self.view.insuranceBet):
			await interaction.send("You don't have enough credits for that bet", ephemeral=True)
			return
		
		await interaction.response.defer()

		self.stop() 

class Button(nextcord.ui.Button['Blackjack']):
	def __init__(self, bot, label, style, row=0, disabled=False):
		self.bot:commands.bot.Bot = bot
		super().__init__(label=label, style=style, row=row, disabled=disabled)
		self.modal = None

	async def callback(self, interaction: Interaction):
		assert self.view is not None
		view: Blackjack = self.view

		if view.ownerId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return

		if view.usedDealerChip:
			if self.label == "Hit":
				await view.hit()
			elif self.label == "Stand":
				await view.EndGame()
		else:
			if self.label == "Insurance":
				self.modal = Insurance(view, view.bot)
				await interaction.response.send_modal(self.modal)
				await self.modal.wait()

				await view.msg.edit(content=f"{interaction.user.mention}\nChecking for blackjack")
				await asyncio.sleep(0.6)
				await view.msg.edit(content=f"{interaction.user.mention}\nChecking for blackjack.")
				await asyncio.sleep(0.6)
				await view.msg.edit(content=f"{interaction.user.mention}\nChecking for blackjack..")
				await asyncio.sleep(0.6)
				await view.msg.edit(content=f"{interaction.user.mention}\nChecking for blackjack...")
				await asyncio.sleep(0.6)
				if view.dealerNum[1] == 10: # checks if dealer's second card is a 10
					await view.msg.edit(content=f"{interaction.user.mention}\nChecking for blackjack... Protected by insurance!")
					await view.displayWinner(999)
					return
				else:
					await view.msg.edit(content=f"{interaction.user.mention}\nDealer does not have blackjack... game will continue")
			if self.label == "Double Down":
				if not await self.bot.get_cog("Economy").subtractBet(interaction.user, view.amntbet):
					await interaction.send("You don't have enough credits for that bet", ephemeral=True)
					return
				self.view.amntbet *= 2
				await view.hit(True)
				return
			if self.label == "Hit":
				if await view.hit():
					return
			elif self.label == "Stand":
				await view.stand()
				return

			if not view.insurance.disabled:
				view.insurance.disabled = True
			if not view.doubleDown.disabled:
				view.doubleDown.disabled = True

		try:
			await interaction.response.defer()
		except:
			pass
		with io.BytesIO() as image_binary:
			if not GetUserSetting(view.ownerId, "ShowBlackjackImg"):
				img = view.PlaceCardsImage()
				img.save(image_binary, 'PNG')
				image_binary.seek(0)
				await view.msg.edit(embed=view.embed, view=view, files=[nextcord.File(fp=image_binary, filename='people.png'), nextcord.File("images/bj.png", filename="thumbnail.png")])
				img.close()
			else:
				await view.msg.edit(embed=view.embed, view=view, file=nextcord.File("images/bj.png", filename="thumbnail.png"))


class Blackjack(nextcord.ui.View):
	def __init__(self, bot, id, cards, amntbet, currCount):
		super().__init__(timeout=120)
		self.bot:commands.bot.Bot = bot

		self.cards = cards
		self.pCARD = list()
		self.pCardSuit = list()
		self.pCardNum = list()

		self.currCardCount = currCount

		self.interaction = None
		self.ownerId = id

		self.dealersTurn = False
		self.dealerNum = list()
		self.dealerHand = list()
		self.embed = None
		self.msg = None

		self.amntbet = amntbet

		self.usedDealerChip = False # forces dealer to go first
		self.usedAceofSpades = False # forces player's first card to be an Ace
		self.showCardCount = False # big blind chip
		self.usedDeckOfCards = False # player cannot bust

		self.doubleDown = Button(bot, label="Double Down", style=nextcord.ButtonStyle.blurple, row=1)
		self.add_item(self.doubleDown)
		self.insurance = Button(bot, label="Insurance", style=nextcord.ButtonStyle.blurple, row=1, disabled=True)
		self.add_item(self.insurance)

		self.insuranceBet = None

		self.file = nextcord.File("images/bj.png", filename="thumbnail.png")
	
	async def on_timeout(self):
		self.clear_items()
		await self.msg.edit(embed=None, view=self, 
					       content=f"{self.interaction.user.mention}\nYou took too long to respond, staying with your current hand")
		await self.stand()
	

	def PlaceCardsImage(self):
		def GetFileNameForCard(card):
			card = card.split()
			if card[1] == "10":
				fileName = "T"
			elif card[1] == "Jack":
				fileName = "J"
			elif card[1] == "Queen":
				fileName = "Q"
			elif card[1] == "King":
				fileName = "K"
			else:
				fileName = card[1]

			if card[0] == "♣": fileName += "C"
			elif card[0] == "♦": fileName += "D"
			elif card[0] == "♥": fileName += "H"
			elif card[0] == "♠": fileName += "S"

			return fileName

		imgForeground = Image.open('images/cards/background.png')
		dealer = Image.open('images/wumpus/blackjackwumpus.png')
		dealer = dealer.resize((200, 200))


		img = Image.new("RGBA", (imgForeground.width, imgForeground.height+400), color=(0, 0, 0, 0))
		img.paste(dealer, box=(int(img.width/2)-int(dealer.width/2), 10))
		# img.paste(dealer.rotate(180), box=(int(img.width/2)-int(dealer.width/2), img.height-dealer.height))
		img.paste(imgForeground, box=(0, int((img.height - imgForeground.height)/2)))

		font_type = ImageFont.truetype('arial.ttf',40)

		startYPos = 200

		def PasteText(player:bool, xPos, yPos):
			if player:
				cards = self.pCARD
				num = self.pCardNum
			else:
				if self.dealersTurn:
					cards = self.dealerHand
					num = self.dealerNum
				else:
					cards = [self.dealerHand[0]]
					num = [self.dealerNum[0]]

			cardsUnicode = list()
			for card in cards:
				fileName = GetFileNameForCard(card)

				cardImg = Image.open(f'images/cards/{fileName}.png')
				cardImg = cardImg.resize((75, 114))
				img.paste(cardImg, (xPos, yPos), mask=cardImg)

				xPos += 85

				cardsUnicode.append(card[0] + " " + fileName[0])

			count = 0
			with Pilmoji(img) as pilmoji:
				for card in cardsUnicode:
					if count == 4:
						xPos += 80
						if player: yPos = 200 + startYPos
						else: yPos = 20 + startYPos
					if card[0] == "♥" or card[0] == "♦":
						color = (153, 0, 0)
					else:
						color = "black"
					pilmoji.text((xPos+20,yPos-20), card, color, font_type)
					yPos += 40
					count += 1
				if player:
					pilmoji.text((100, 310+startYPos), f"Score: {sum(num)}", "black", font_type)
					name_font = ImageFont.truetype('arial.ttf',50)
					pilmoji.text((100, 380+startYPos), f"{self.interaction.user.display_name}", (88, 101, 242), name_font)
				else:
					pilmoji.text((100, 130+startYPos), f"Score: {sum(num)}", "black", font_type)

		PasteText(False, 20, 20+startYPos)
		PasteText(True, 20, 200+startYPos)


		return img



	async def Start(self, interaction: Interaction):
		await interaction.response.defer(with_message=True)
		self.interaction = interaction
		self.msg = await self.interaction.original_message()
		self.usedAceofSpades = False
		self.usedDealerChip = False
		self.showCardCount = False
		self.usedDeckOfCards = False

		# generate the starting cards
		if self.bot.get_cog("Inventory").checkForActiveItem(interaction.user, "Dealer Chip"):
			self.bot.get_cog("Inventory").removeActiveItemFromDB(interaction.user, "Dealer Chip")
			self.usedDealerChip = True
		elif self.bot.get_cog("Inventory").checkForActiveItem(interaction.user, "Big Blind Chip"):
			self.bot.get_cog("Inventory").removeActiveItemFromDB(interaction.user, "Big Blind Chip")
			self.showCardCount = True
		elif self.bot.get_cog("Inventory").checkForActiveItem(interaction.user, "Ace of Spades"):
			self.bot.get_cog("Inventory").removeActiveItemFromDB(interaction.user, "Ace of Spades")
			self.usedAceofSpades = True
		elif self.bot.get_cog("Inventory").checkForActiveItem(interaction.user, "Deck of Cards"):
			self.bot.get_cog("Inventory").removeActiveItemFromDB(interaction.user, "Deck of Cards")
			self.usedDeckOfCards = True


		self.embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Blackjack")
		self.embed.set_thumbnail(url="attachment://thumbnail.png")


		self.dealer_first_turn()

		if self.usedDealerChip:
			self.remove_item(self.doubleDown)
			self.remove_item(self.insurance)

			dTotal = ""
			for x in self.dealerHand:
				dTotal += f"{x} "

			self.embed.add_field(name = f"{self.interaction.user.name}'s cards:", value = f"Waiting...", inline=True)
			self.embed.add_field(name = f"{self.bot.user.name}'s cards", value = f"{dTotal}\n**Score**: {sum(self.dealerNum)}\n", inline=True)
			self.embed.add_field(name = "_ _", value = "**Options:** hit or stay", inline=False)
			# if not self.showCardCount:
			# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}")
			# else:
			# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}\nCount is {self.currCardCount[0]}")
			
			if self.showCardCount:
				self.embed.set_footer(text=f"Count is {self.currCardCount[0]}")


			with io.BytesIO() as image_binary:
				if not GetUserSetting(self.ownerId, "ShowBlackjackImg"):
					img = self.PlaceCardsImage()
					img.save(image_binary, 'PNG')
					image_binary.seek(0)
					await self.msg.edit(content=f"{self.interaction.user.mention}", view=self, 
											files=[nextcord.File(fp=image_binary, filename='people.png'), self.file], embed=self.embed)
					img.close()
				else:
					await self.msg.edit(content=f"{self.interaction.user.mention}", view=self, file=self.file, embed=self.embed)

			await self.dealer_turn()

		elif self.usedDeckOfCards:
			self.remove_item(self.doubleDown)
			self.remove_item(self.insurance)
			self.add_item(Button(self.bot, label="Hit", style=nextcord.ButtonStyle.green))
			self.add_item(Button(self.bot, label="Stand", style=nextcord.ButtonStyle.red))

		else:
			self.add_item(Button(self.bot, label="Hit", style=nextcord.ButtonStyle.green))
			self.add_item(Button(self.bot, label="Stand", style=nextcord.ButtonStyle.red))

		await self.player_first_turn()

	async def player_first_turn(self):
		for x in range(0,2):
			# player draws a card
			# if x == 0:
			# 	pDrawnCard = "♦ 2"
			# else:
			# 	pDrawnCard = "♠ A"
			if self.usedAceofSpades and x == 0:
				pDrawnCard = "♠ A"
			else:
				pDrawnCard = self.take_card()
			self.pCARD.append(pDrawnCard)

			# splits the number and the suit 
			pDrawnCard = pDrawnCard.split()

			# converts to number
			if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
				pDrawnCard[1] = "10"
			elif pDrawnCard[1] == "A":
				pDrawnCard[1] = "11"

			# adds the card to the player's hand
			self.pCardNum.append(int(pDrawnCard[1]))

			# checks if player has an ace
			self.pCardNum = self.eval_ace(self.pCardNum)

		# used to make display for all p cards
		pTotal = ""
		for x in self.pCARD:
			pTotal += f"{x} "

		# used to make display for all d cards
		dTotal = ""
		for x in self.dealerHand:
			dTotal += f"{x} "
		
		await self.player_turn(pTotal)
	
	async def player_turn(self, pTotal):
		if self.usedDealerChip:
			self.embed.set_field_at(0, name = f"{self.interaction.user.name}'s cards:", value = f"{pTotal}\n**Score**: {sum(self.pCardNum)}", inline=True)
			await self.msg.edit(embed=self.embed)
		else:	
			self.embed.add_field(name = f"{self.interaction.user.name}'s cards:", value = f"{pTotal}\n**Score**: {sum(self.pCardNum)}", inline=True)
			self.embed.add_field(name = f"{self.bot.user.name}'s cards", value = f"{self.dealerHand[0]}\n**Score**: {self.dealerNum[0]}\n", inline=True)
			self.embed.add_field(name = "_ _", value = "**Options:** hit or stay", inline=False)
			
			# if not self.showCardCount:
			# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}")
			# else:
			# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}\nCount is {self.currCardCount[0]}")
			
			if self.showCardCount:
				self.embed.set_footer(text=f"Count is {self.currCardCount[0]}")

			with io.BytesIO() as image_binary:
				if not GetUserSetting(self.ownerId, "ShowBlackjackImg"):
					img = self.PlaceCardsImage()
					img.save(image_binary, 'PNG')
					image_binary.seek(0)
					await self.msg.edit(content=f"{self.interaction.user.mention}", view=self, 
											files=[nextcord.File(fp=image_binary, filename='people.png'), self.file], embed=self.embed)
					img.close()
				else:
					await self.msg.edit(content=f"{self.interaction.user.mention}", view=self, file=self.file, embed=self.embed)

			if (self.is_blackjack(self.pCardNum)): # if player has blackjack
				if self.dealerHand[0].split()[1] == "A": # if dealer has Ace showing and player used dealer chip
					self.remove_item(self.doubleDown) # remove double down button
					for child in self.children:
						if child.label == "Hit": # remove Hit button 
							self.remove_item(child)
					# will be left with Stand and Insurance
					await self.msg.edit(embed=self.embed, view=self, content=f"{self.interaction.user.mention}\nYou got a blackjack! Dealer has an ace, would you like to take insurance or stand?")
				else:
					# player dealt blackjack
					if(len(self.pCARD) == 2):
						await self.EndGame() # end game because instant win
					else: # player has blackjack, but not first 2 cards
						await self.stand()


	async def hit(self, isDoubleDown=False):
		pDrawnCard = self.take_card()

		# splits the number and the suit 
		splitpDrawnCard = pDrawnCard.split()

		# converts to number
		if splitpDrawnCard[1] == "Jack" or splitpDrawnCard[1] == "Queen" or splitpDrawnCard[1] == "King":
			splitpDrawnCard[1] = "10"
		elif splitpDrawnCard[1] == "A":
			splitpDrawnCard[1] = "11"

		if self.usedDeckOfCards:
			if sum(self.pCardNum) + int(splitpDrawnCard[1]) > 21:
				await self.interaction.send(f"This would bust you at {sum(self.pCardNum) + int(splitpDrawnCard[1])}", ephemeral=True)
				self.cards.append(pDrawnCard)
				return

		# adds card to player hand
		self.pCARD.append(pDrawnCard)
		# adds the card num to the player's hand
		self.pCardNum.append(int(splitpDrawnCard[1]))
	
		# checks if player has an ace
		self.pCardNum = self.eval_ace(self.pCardNum)

		# used to make display for all p cards
		pTotal = ""
		for x in self.pCARD:
			pTotal += f"{x} "

		# used to make display for all d cards
		dTotal = ""
		for x in self.dealerHand:
			dTotal += f"{x} "

		self.embed.set_field_at(0, 
			name = f"{self.interaction.user.name}'s cards:", 
			value = f"{pTotal}\n**Score**: {sum(self.pCardNum)}", 
			inline=True)

		# if not self.showCardCount:
		# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}")
		# else:
		# 	self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}\nCount is {self.currCardCount[0]}")
		
		if self.showCardCount:
			self.embed.set_footer(text=f"Count is {self.currCardCount[0]}")

		# ends game if player busted or has 21
		if (self.is_bust(self.pCardNum) or self.is_blackjack(self.pCardNum)):
			if self.is_blackjack(self.pCardNum):
				await self.stand()
			else:
				await self.EndGame()
			return True
		if isDoubleDown:
			await self.stand()


	async def stand(self):
		self.clear_items()
		self.stop()
		await self.msg.edit(view=self)
		# generate dealer's hand
		await self.dealer_turn()
		await self.EndGame()


	async def EndGame(self):
		self.dealersTurn = True
		self.CalculateCardCount(self.dealerNum[1])
		winner = self.compare_between()
		await self.displayWinner(winner) 


	def CalculateCardCount(self, card):
		try:
			card = int(card)
			if card <= 6:
				self.currCardCount[0] += 1
			elif card >= 10:
				self.currCardCount[0] -= 1
		except:
			self.currCardCount[0] -= 1

	def take_card(self, calculateCount:bool=True):
		# if all 52 cards have been used, reset the deck
		if len(self.cards) == 0:
			self.cards = ["♣ A", "♣ 2", "♣ 3", "♣ 4", "♣ 5", "♣ 6", "♣ 7", "♣ 8", "♣ 9", "♣ 10", "♣ Jack", "♣ Queen", "♣ King",
						  "♦ A", "♦ 2", "♦ 3", "♦ 4", "♦ 5", "♦ 6", "♦ 7", "♦ 8", "♦ 9", "♦ 10", "♦ Jack", "♦ Queen", "♦ King",
						  "♥ A", "♥ 2", "♥ 3", "♥ 4", "♥ 5", "♥ 6", "♥ 7", "♥ 8", "♥ 9", "♥ 10", "♥ Jack", "♥ Queen", "♥ King",
						  "♠ A", "♠ 2", "♠ 3", "♠ 4", "♠ 5", "♠ 6", "♠ 7", "♠ 8", "♠ 9", "♠ 10", "♠ Jack", "♠ Queen", "♠ King"]
			shuffle(self.cards)

		drawnCard = self.cards.pop()

		if calculateCount:
			num = drawnCard.split(' ')[1]
			self.CalculateCardCount(num)

		return drawnCard
		# return "♠ 4"


	def eval_ace(self, cardNum):
		# Determine Ace = 1 or 11, relying on total cardNum. 
		total = sum(cardNum)
		for ace in cardNum:
			if ace == 11 and total > 21:
				# at position, where Ace == 11, replace by Ace == 1.
				position_ace = cardNum.index(11)
				cardNum[position_ace] = 1
		return cardNum


	def is_bust(self, cardNum):
		# Condition True: if the cardNum of player (or dealer) > 21.
		total = sum(cardNum)
		if total > 21:
			return True
		return None


	def is_blackjack(self, cardNum):
		# Condition True: if the cardNum of player (or dealer) == 21.
		total = sum(cardNum)
		if total == 21:
			return True
		return None

	def dealer_first_turn(self):
		# dDrawnCard = "♦ A"
		for x in range(0, 2):
			# if x == 0:
			# 	dDrawnCard = "♦ A"
			# else:
			# 	dDrawnCard = "♦ 10"
			# else:
			calculateCards = True
			if x == 1:
				calculateCards = False

			dDrawnCard = self.take_card(calculateCount=calculateCards)
			self.dealerHand.append(dDrawnCard)

			dDrawnCard = dDrawnCard.split()

			if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
				dDrawnCard[1] = "10"
			elif dDrawnCard[1] == "A":
				dDrawnCard[1] = "11"
				if x == 0:
					self.insurance.disabled = False # if dealer's FIRST card is Ace, ask player if they want to buy insurance


			self.dealerNum.append(int(dDrawnCard[1]))

			self.dealerNum = self.eval_ace(self.dealerNum)
	
	async def refresh_dealer_hand(self):
		dTotal = ""
		for x in self.dealerHand:
			dTotal += f"{x} "

		self.embed.set_field_at(1, name = f"{self.bot.user.name}'s cards", value = f"{dTotal}\n**Score**: {sum(self.dealerNum)}", inline=True)

		await self.msg.edit(view=self, embed=self.embed)
		await asyncio.sleep(0.6)


	async def dealer_turn(self):
		await self.refresh_dealer_hand()
		# d will keep drawing until card values sum > 16
		while sum(self.dealerNum) <= 16:
			# grabs a card
			dDrawnCard = self.take_card()
			# adds it to his hand
			self.dealerHand.append(dDrawnCard)

			# splits suit and number
			dDrawnCard = dDrawnCard.split()

			if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
				dDrawnCard[1] = "10"
			elif dDrawnCard[1] == "A":
				dDrawnCard[1] = "11"

			self.dealerNum.append(int(dDrawnCard[1]))

			self.dealerNum = self.eval_ace(self.dealerNum)

			# if not self.usedDealerChip:

			# if self.usedDealerChip:
			await self.refresh_dealer_hand()
		
		if self.usedDealerChip:
			self.add_item(Button(self.bot, label="Hit", style=nextcord.ButtonStyle.green))
			self.add_item(Button(self.bot, label="Stand", style=nextcord.ButtonStyle.red))
			await self.msg.edit(view=self, embed=self.embed)




	def compare_between(self):
		total_player = sum(self.pCardNum)
		total_dealer = sum(self.dealerNum)
		player_bust = self.is_bust(self.pCardNum)
		dealer_bust = self.is_bust(self.dealerNum)
		player_blackjack = self.is_blackjack(self.pCardNum)
		dearler_blackjack = self.is_blackjack(self.dealerNum)

		# when p bust.
		if player_bust:
			return -1
		# when d bust
		elif dealer_bust:
			return 1
		# when both 21
		elif player_blackjack and dearler_blackjack:
			return 0
		# when p 21
		elif player_blackjack:
			return 1
		# when d 21
		elif dearler_blackjack:
			return -1
		# when total CARD of player (dealer) < 21.
		elif total_player < 21 and total_dealer < 21:
			if total_player > total_dealer:
				return 1
			elif total_dealer > total_player:
				return -1
			else:
				return 0

	async def displayWinner(self, winner):
		self.clear_items()
		self.stop()
		await self.msg.edit(view=self)

		user = self.interaction.user
		pTotal = ""
		for x in self.pCARD:
			pTotal += f"{x} "

		dTotal = ""
		for x in self.dealerHand:
			dTotal += f"{x} "


		#self.embed.add_field(name = f"{author.name}'s' CARD:", value = f"{pTotal}\n**Score**: {sum(player_num)}", inline=True)

		self.embed.set_field_at(1, name = f"{self.bot.user.name}'s cards", value = f"{dTotal}\n**Score**: {sum(self.dealerNum)}", inline=True)
		self.embed.color = nextcord.Color(0xff2020)
		result = ""


		# file = None

		moneyToAdd = 0
		if winner == 999: # won by insurance
			moneyToAdd = self.insuranceBet * 3
			# if bought insurance and has blackjack
			if self.is_blackjack(self.pCardNum):
				profitInt = moneyToAdd - self.insuranceBet
			else:
				profitInt = moneyToAdd - self.amntbet - self.insuranceBet
				
			result = "DEALER 21 ON HAND, BUT WON INSURANCE"

			self.embed.color = nextcord.Color(0x23f518)
			file = nextcord.File("./images/insurance.png", filename="thumbnail.png")
			
		elif winner == 1:
			moneyToAdd = self.amntbet * 2 
			profitInt = moneyToAdd - self.amntbet
			result = "YOU WON"
			
			self.embed.color = nextcord.Color(0x23f518)
			if sum(self.pCardNum) == 21:
				file = nextcord.File("./images/21.png", filename="thumbnail.png")
			else:
				file = nextcord.File("./images/bjwon.png", filename="thumbnail.png")

		elif winner == -1:
			moneyToAdd = 0 # nothing to add since loss
			profitInt = -self.amntbet # profit = amntWon - amntbet; amntWon = 0 in this case
			result = "YOU LOST"
			file = nextcord.File("./images/bjlost.png", filename="thumbnail.png")


		elif winner == 0:
			moneyToAdd = self.amntbet # add back their bet they placed since it was pushed (tied)
			profitInt = 0 # they get refunded their money (so they don't make or lose money)
			result = "PUSHED"
			file = nextcord.File("./images/bjpushed.png", filename="thumbnail.png")

		gameID = await self.bot.get_cog("Economy").addWinnings(self.interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="BJ", amntBet=self.amntbet)
		self.embed.set_field_at(2, name = f"**--- {result} ---**", value = "_ _", inline=False)

		self.embed, _ = await DB.addProfitAndBalFields(self, self.interaction, profitInt, self.embed)

		balance = await self.bot.get_cog("Economy").getBalance(user)
		self.embed = await DB.calculateXP(self, self.interaction, balance - profitInt, self.amntbet, self.embed, gameID)

		# if winner == 999:
		# await self.interaction.send(content=f"{user.mention}", file=file, embed=self.embed)

		# await interaction.send(content=f"{interaction.user.mention}", file=file, embed=self.embed)
		self.embed.set_thumbnail(url="attachment://thumbnail.png")
		with io.BytesIO() as image_binary:
			if not GetUserSetting(self.ownerId, "ShowBlackjackImg"):
				img = self.PlaceCardsImage()
				img.save(image_binary, 'PNG')
				image_binary.seek(0)
				await self.msg.edit(embed=self.embed, view=None, files=[nextcord.File(fp=image_binary, filename='people.png'), file])
				img.close()
			else:
				await self.msg.edit(embed=self.embed, view=None, file=file)
		file.close()

		await self.bot.get_cog("Totals").addTotals(self.interaction, self.amntbet, moneyToAdd, "Blackjack")	
		await self.bot.get_cog("Quests").AddQuestProgress(self.interaction, user, "BJ", profitInt)
		# if player won by blackjack:
		# 		has blackjack (21 with first 2 cards) and did not win by insurance
		await self.bot.get_cog("Achievements").AddAchievementProgress(self.interaction, 
				 "Blackjack", 
				 [self.amntbet, moneyToAdd > self.amntbet, sum(self.pCardNum) == 21 and len(self.pCARD) == 2 and winner == 1], 
				 self.ownerId)
		
		gameResult = {
			"Name": "Blackjack", 
			"AmntBet": self.amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(self.interaction, gameResult)


class bj(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.cards = ["♣ A", "♣ 2", "♣ 3", "♣ 4", "♣ 5", "♣ 6", "♣ 7", "♣ 8", "♣ 9", "♣ 10", "♣ Jack", "♣ Queen", "♣ King",
					  "♦ A", "♦ 2", "♦ 3", "♦ 4", "♦ 5", "♦ 6", "♦ 7", "♦ 8", "♦ 9", "♦ 10", "♦ Jack", "♦ Queen", "♦ King",
					  "♥ A", "♥ 2", "♥ 3", "♥ 4", "♥ 5", "♥ 6", "♥ 7", "♥ 8", "♥ 9", "♥ 10", "♥ Jack", "♥ Queen", "♥ King",
					  "♠ A", "♠ 2", "♠ 3", "♠ 4", "♠ 5", "♠ 6", "♠ 7", "♠ 8", "♠ 9", "♠ 10", "♠ Jack", "♠ Queen", "♠ King"]
		shuffle(self.cards)
		self.count = [0]

	@nextcord.slash_command(description="Play BlackJack!")
	@commands.bot_has_guild_permissions(send_messages=True, manage_messages=True, embed_links=True, use_external_emojis=True, attach_files=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='blackjack', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def blackjack(self, interaction:Interaction, amntbet):
		amntbet = await self.bot.get_cog("Economy").GetBetAmount(interaction, amntbet)

		if amntbet < 100:
			raise Exception("minBet 100")
		
		if amntbet > GetMaxBet(interaction.user.id, "Blackjack"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Blackjack')}")
		
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")
		
		view = Blackjack(self.bot, interaction.user.id, self.cards, amntbet, self.count)
		await view.Start(interaction)


def setup(bot):
	bot.add_cog(bj(bot))