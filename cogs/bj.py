####################################################################
# BLACKJACK! YAY!
# 
# Comment definitions:
# short-version: actual-version
# p: player
# d: dealer


import discord
from discord.ext import commands
import asyncio
from random import randrange
from random import randint

class bj(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.cards = ["♣ 1","♣ 2","♣ 3","♣ 4","♣ 5","♣ 6","♣ 7","♣ 8","♣ 9","♣ 10","♣ Jack","♣ Queen","♣ King",
					  "♦ 1","♦ 2","♦ 3","♦ 4","♦ 5","♦ 6","♦ 7","♦ 8","♦ 9","♦ 10","♦ Jack","♦ Queen","♦ King",
					  "♥ 1","♥ 2","♥ 3","♥ 4","♥ 5","♥ 6","♥ 7","♥ 8","♥ 9","♥ 10","♥ Jack","♥ Queen","♥ King",
					  "♠ 1","♠ 2","♠ 3","♠ 4","♠ 5","♠ 6","♠ 7","♠ 8","♠ 9","♠ 10","♠ Jack","♠ Queen","♠ King"]
		#self.cards = ["♣ 1","♦ 1","♥ 1","♠ 1","♣ 2","♣ 2","♥ 2","♠ 2","♣ 3","♦ 3","♥ 3","♠ 3","♣ 4","♦ 4","♥ 4"]
		self.embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Blackjack")
		self.botMsg = ""

	@commands.command(description="Play BlackJack!", aliases=['blackjack'], pass_context=True)
	@commands.cooldown(1, 5, commands.BucketType.user)	
	async def bj(self, ctx, amntBet: int):
		if await self.bot.get_cog("Economy").subtractBet(ctx, amntBet) != 0:
			# generate the starting cards
			dFirstHand, dFirstNum = await self.dealer_first_turn(ctx)
			
			# collect player input for player's hand
			player_hand, player_num = await self.player_turn(dFirstHand, dFirstNum, ctx)
			# generate dealer's hand
			dealer_hand, dealer_num = await self.dealer_turn(dFirstHand, dFirstNum, ctx)
			
			winner = await self.compare_between(player_num, dealer_num, ctx)
			
			await self.displayWinner(winner, player_hand, player_num, dealer_hand, dealer_num, amntBet, ctx) 



	async def player_turn(self, dCard, dCardNum, ctx):
		pCARD = []
		pCardSuit = []
		pCardNum = []

		pDrawnCard = await self.take_card()

		pCARD.append(pDrawnCard)

		pDrawnCard = pDrawnCard.split()

		# assigns number value
		if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
			pDrawnCard[1] = "10"
		pCardNum.append(int(pDrawnCard[1]))


		self.botMsg = await ctx.send(f"{ctx.message.author.mention}")
		ans = "hit"
		while (ans.lower() == "h") or (ans.lower() == "hit"):
			
			# player draws a card 
			pDrawnCard = await self.take_card()
			pCARD.append((pDrawnCard))

			# splits the number and the suit 
			pDrawnCard = pDrawnCard.split()

			# converts to number
			if pDrawnCard[1] == "Jack" or pDrawnCard[1] == "Queen" or pDrawnCard[1] == "King":
				pDrawnCard[1] = "10"

			# adds the card to the player's hand
			pCardNum.append(int(pDrawnCard[1]))

			pCardNum = await self.eval_ace(pCardNum)

			# used to make display for all p cards
			pTotal = ""
			for x in pCARD:
				pTotal += f"{x} "

			# used to make display for all d cards
			dTotal = ""
			for x in dCard:
				dTotal += f"{x} "

			# if game just started, it will add all the fields; if player "hit", it will update the embed for player's cards
			try:
				self.embed.set_field_at(0, name = f"{ctx.message.author.name}'s CARD:", value = f"{pTotal}\n**Score**: {sum(pCardNum)}", inline=True)
			except:
				self.embed.add_field(name = f"{ctx.message.author.name}'s CARD:", value = f"{pTotal}\n**Score**: {sum(pCardNum)}", inline=True)
				self.embed.add_field(name = "Pit Boss' CARD", value = f"{dCard[0]}\n**Score**: {dCardNum[0]}\n", inline=True)
				self.embed.add_field(name = "_ _", value = "**Options:** hit or stay", inline=False)

			self.embed.set_footer(text=f"Cards in Deck: {len(self.cards)}")

			# ends game if player busted or has 21
			if (await self.is_bust(pCardNum) or await self.is_blackjack(pCardNum)):
				break
			await self.botMsg.edit(content=f"{ctx.message.author.mention}", embed=self.embed)

			def is_me(m):
				return (m.author.id == ctx.author.id) and (m.content.lower() in ["hit", "stay", "h", "s"])
			try:
				# waits for user action; while loop repeated
				ans = await self.bot.wait_for('message', check=is_me, timeout=45)
				ans = ans.content
			except asyncio.TimeoutError:
				await self.botMsg.edit(content="Request timed out.")
				break

		return pCARD, pCardNum


	async def take_card(self):
		# get arbitrary card from 2 to 11.
		drawnCard = self.cards.pop(randint(0, len(self.cards) - 1))

		# if all 52 cards have been used, reset the deck
		if len(self.cards) == 0:
			self.cards = ["♣ 1","♣ 2","♣ 3","♣ 4","♣ 5","♣ 6","♣ 7","♣ 8","♣ 9","♣ 10","♣ Jack","♣ Queen","♣ King",
						  "♦ 1","♦ 2","♦ 3","♦ 4","♦ 5","♦ 6","♦ 7","♦ 8","♦ 9","♦ 10","♦ Jack","♦ Queen","♦ King",
						  "♥ 1","♥ 2","♥ 3","♥ 4","♥ 5","♥ 6","♥ 7","♥ 8","♥ 9","♥ 10","♥ Jack","♥ Queen","♥ King",
						  "♠ 1","♠ 2","♠ 3","♠ 4","♠ 5","♠ 6","♠ 7","♠ 8","♠ 9","♠ 10","♠ Jack","♠ Queen","♠ King"]
		return drawnCard


	async def eval_ace(self, cardNum):
		# Determine Ace = 1 or 11, relying on total cardNum. 
		total = sum(cardNum)
		for ace in cardNum:
			if ace == 11 and total > 21:
				# at position, where Ace == 11, replace by Ace == 1.
				position_ace = cardNum.index(11)
				cardNum[position_ace] = 1
		return cardNum


	async def is_bust(self, cardNum):
		# Condition True: if the cardNum of player (or dealer) > 21.
		total = sum(cardNum)
		if total > 21:
			return True
		return None


	async def is_blackjack(self, cardNum):
		# Condition True: if the cardNum of player (or dealer) == 21.
		total = sum(cardNum)
		if total == 21:
			return True
		return None

	async def dealer_first_turn(self, ctx):
		dCARD = []
		dCardNum = []

		dDrawnCard = await self.take_card()
		dCARD.append(dDrawnCard)

		dDrawnCard = dDrawnCard.split()

		if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
			dDrawnCard[1] = "10"

		dCardNum.append(int(dDrawnCard[1]))

		dCardNum = await self.eval_ace(dCardNum)
		
		return dCARD, dCardNum

	async def dealer_turn(self, dCARD, dCardNum, ctx):
		# d will keep drawing until card values sum > 16
		while sum(dCardNum) <= 16:
			# grabs a card
			dDrawnCard = await self.take_card()
			# adds it to his hand
			dCARD.append(dDrawnCard)

			# splits suit and number
			dDrawnCard = dDrawnCard.split()

			if dDrawnCard[1] == "Jack" or dDrawnCard[1] == "Queen" or dDrawnCard[1] == "King":
				dDrawnCard[1] = "10"

			dCardNum.append(int(dDrawnCard[1]))

			dCardNum = await self.eval_ace(dCardNum)
		return dCARD, dCardNum


	async def compare_between(self, player_hand, dealer_hand, ctx):
		total_player = sum(player_hand)
		total_dealer = sum(dealer_hand)
		player_bust = await self.is_bust(player_hand)
		dealer_bust = await self.is_bust(dealer_hand)
		player_blackjack = await self.is_blackjack(player_hand)
		dearler_blackjack = await self.is_blackjack(dealer_hand)

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
		else:
			await ctx.send(f"Error. Please help Daddy <@547475078082985990>.\ntotal_dealer: {total_dealer}\n total_player: {total_player}")

	async def displayWinner(self, winner, player_hand, player_num, dealer_hand, dealer_num, amntBet, ctx):
		pTotal = ""
		for x in player_hand:
			pTotal += f"{x} "

		dTotal = ""
		for x in dealer_hand:
			dTotal += f"{x} "


		#self.embed.add_field(name = f"{ctx.message.author.name}'s' CARD:", value = f"{pTotal}\n**Score**: {sum(player_num)}", inline=True)

		coin = "<:coins:585233801320333313>"
		xp = randint(50, 500)

		self.embed.set_field_at(1, name = "Pit Boss' CARD", value = f"{dTotal}\n**Score**: {sum(dealer_num)}", inline=True)
		self.embed.set_footer(text=f"Earned {xp} XP!")
		self.embed.color = discord.Color(0xff2020)
		result = ""


		# MONEY WINNINGS EXPLAINED:
		# If you win, you get 2x your money
		# (amntBet * 2)
		# 
		# But profit is only how much you won subtracted with how much you bet
		# Meaning profit = amntBet
		# 
		# 
		#########################

		if winner == 1:
			profitInt = amntBet
			moneyToAdd = amntBet * 2
			result = "YOU WON"
			multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
			profit = f"**{profitInt}** (+**{int(profitInt * (multiplier - 1))}**)"
			self.embed.color = discord.Color(0x23f518)
			await self.bot.get_cog("Totals").addTotals(ctx, amntBet, moneyToAdd, 1)
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, (moneyToAdd + (profitInt * (multiplier - 1))))

		elif winner == -1:
			moneyToAdd = -amntBet
			await self.bot.get_cog("Totals").addTotals(ctx, amntBet, 0, 1)
			result = "YOU LOST"
			profit = f"**{moneyToAdd}**"
		
		elif winner == 0:
			moneyToAdd = 0
			await self.bot.get_cog("Totals").addTotals(ctx, amntBet, amntBet, 1)
			result = "PUSHED"
			profit = f"**{moneyToAdd}**"
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntBet)


		self.embed.add_field(name="Profit", value=f"{profit}{coin}", inline=True)
		self.embed.set_field_at(2, name = "_ _", value = f"**--- {result} ---**", inline=False)

		balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
		self.embed.add_field(name="Credits", value=f"**{balance}**{coin}", inline=True)
		await self.botMsg.edit(content=f"{ctx.message.author.mention}", embed=self.embed)
		await self.bot.get_cog("XP").addXP(ctx, xp)

		self.embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Blackjack")	
		

	@bj.error
	async def bj_handler(self, ctx, error):
		embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
		embed.add_field(name = "`Syntax: $blackjack <bet>`", value = "_ _", inline=False)
		embed.add_field(name="__Play a game of blackjack and try to get to 21 first.__", value = "_ _", inline=False)
		await ctx.send(embed=embed)
		self.embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Blackjack")
		print(error)



def setup(bot):
	bot.add_cog(bj(bot))