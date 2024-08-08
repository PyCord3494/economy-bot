from typing import Any, Coroutine
import nextcord
from nextcord.ext import commands 
from nextcord import Interaction, Color

from random import randrange, choices, choice
from PIL import Image
import cooldowns, asyncio, io

import emojis
from db import DB
from cogs.util import IsDonatorCheck, BetAgainView


class GetAmountToBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label="Amount of credits to bet", min_length=1, max_length=6, required=True, placeholder="1000")
class GetNumberBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label = "Number to bet on", min_length = 1, max_length = 2, required=False, placeholder = "0 - 36")
class GetColorBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label = "Color to bet on", min_length = 3, max_length = 5, required=False, placeholder = "Red, Black, or Green")
class GetParityBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label = "Bet on the Parity", min_length = 3, max_length = 4, required=False, placeholder = "ODD or EVEN")
class GetHighLowBet(nextcord.ui.TextInput):
	def __init__(self):
		super().__init__(label = "Bet on high or low", min_length = 3, max_length = 4, required=False, placeholder = "HIGH or LOW")


class Button(nextcord.ui.Button):
	def __init__(self, bot, label, style, row, acceptableResponses=None):
		super().__init__(label=label, style=style, row=row)

		self.bot:commands.bot.Bot = bot
		self.acceptableResponses = acceptableResponses
		self.option = None
		self.bet = None
		
	async def callback(self, interaction: Interaction):
		assert self.view is not None
		view: View = self.view
		if view.ownerId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return
		if self.label == "Spin":
			try:
				await interaction.response.defer()
			except:
				pass
			view.stop()
			return
		
		modal = Modal(self.label)
		await interaction.response.send_modal(modal=modal)

		await modal.wait()

		value = modal.children[0].value
		bet = modal.children[1].value

		if not value or not bet:
			return
		
		value = value.lower()
		if value not in self.acceptableResponses:
			await interaction.send("Did not provide correct choice. Please try again", ephemeral=True)
			return

		if value.isdigit(): # for number betting
			value = int(value) # convert to number

			if value > 36 or value < 0:
				await interaction.send("Number must be between 0 and 36. Please try again", ephemeral=True)
				return

		if not bet.isdigit():
			await interaction.send("Did not provide number for bet. Please try again", ephemeral=True)
			return
		bet = int(bet)
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, bet):
			await interaction.send("You don't have enough credits for that bet", ephemeral=True)
			return
		
		self.option = value
		self.bet = bet

		self.disabled = True
		view.ProcessBets()

		view.embed.set_field_at(0, name="Picks", value=view.getFullBetsDisplay(), inline=True)

		await interaction.edit_original_message(embed=view.embed, view=view)


class Modal(nextcord.ui.Modal):
	def __init__(self, modalType):
		super().__init__(title="Place your bet", timeout=60)
		if modalType == "Number":
			self.add_item(GetNumberBet())
		elif modalType == "Color":
			self.add_item(GetColorBet())
		elif modalType == "Parity":
			self.add_item(GetParityBet())
		elif modalType == "High or Low":
			self.add_item(GetHighLowBet())
		self.amntbet = GetAmountToBet()
		
		self.add_item(self.amntbet)

	async def callback(self, interaction: nextcord.Interaction):
		try:
			await interaction.response.defer()
		except:
			pass
		self.stop()
		# await interaction.send(f"{self.number.value} {self.color.value} {self.parity.value} {self.highlow.value} {self.amntbet.value} ")

class View(nextcord.ui.View):
	def __init__(self, bot, previousNums, ownerId):
		super().__init__()
		self.bot:commands.bot.Bot = bot
		self.previousNums = previousNums

		self.ownerId = ownerId

		self.add_item(Button(bot = self.bot, label = "Spin", style = nextcord.ButtonStyle.green, row=0))
		self.number = Button(bot = self.bot, label = "Number", style = nextcord.ButtonStyle.blurple, row=1, acceptableResponses=[str(x) for x in range(0,37)])
		self.highOrLow = Button(bot = self.bot, label = "High or Low", style = nextcord.ButtonStyle.blurple, row=1, acceptableResponses=["high", "low"])
		self.color = Button(bot = self.bot, label = "Color", style = nextcord.ButtonStyle.blurple, row=1, acceptableResponses=["red", "black", "green"])
		self.parity = Button(bot = self.bot, label = "Parity", style = nextcord.ButtonStyle.blurple, row=1, acceptableResponses=["odd", "even"])
		
		self.add_item(self.number)
		self.add_item(self.highOrLow)
		self.add_item(self.color)
		self.add_item(self.parity)

		self.msg = None
		self.embed = None
		self.totalBet = 0

		self.displayNumberBet = ""
		self.displayParityBet = ""
		self.displayColorBet = ""
		self.displayHighLowBet = ""

		# 75% chance to get red
		self.usedThreeOfAKind = False

	def ProcessBets(self):
		self.totalBet = 0
		if self.number.option:
			self.totalBet += self.number.bet
			self.displayNumberBet = self.getNumEmoji(self.number.option)
		if self.parity.option:
			self.totalBet += self.parity.bet
			self.displayParityBet = "1⃣" if self.parity.option == "odd" else "2⃣"
		if self.color.option:
			self.totalBet += self.color.bet
			if self.color.option == "red": self.displayColorBet = ":heart:"
			elif self.color.option == "black": self.displayColorBet = ":black_heart:"
			else: self.displayColorBet = ":green_heart:"
		if self.highOrLow.option:
			self.totalBet += self.highOrLow.bet
			self.displayHighLowBet = "⬆" if self.highOrLow.option == "high" else "⬇"
		
	def getFullBetsDisplay(self):
		numberBet = ""
		highLowBet = ""
		colorBet = ""
		parityBet = ""
		if self.number.option:
			numberBet = f"{self.displayNumberBet} {self.number.bet}{emojis.coin}"
		if self.highOrLow.option:
			highLowBet = f"{self.displayHighLowBet} {self.highOrLow.bet}{emojis.coin}"
		if self.color.option:
			colorBet = f"{self.displayColorBet} {self.color.bet}{emojis.coin}"
		if self.parity.option:
			parityBet = f"{self.displayParityBet} {self.parity.bet}{emojis.coin}"
		return f"Number bet: {numberBet}\n \
			  High/low bet: {highLowBet}\n \
			  Color bet: {colorBet}\n \
			  Parity bet: {parityBet}"


	async def Start(self, interaction:Interaction, playAgain=False):
		try:
			await interaction.response.defer()
			self.msg = await interaction.original_message()
		except:
			pass

		self.usedThreeOfAKind = False
		if self.bot.get_cog("Inventory").checkForActiveItem(interaction.user, "Three of a Kind"):
			self.bot.get_cog("Inventory").removeActiveItemFromDB(interaction.user, "Three of a Kind")
			self.usedThreeOfAKind = True

		self.totalBet = 0
		
		# modal = GetBets()
		# try:
		# 	await interaction.response.send_modal(view=View())
		# except Exception as e:
		# 	return

		nums = ""
		numCount = 0
		for x in self.previousNums:
			if numCount == 0:
				nums += f"{x}"
			elif numCount % 2 == 1:
				nums += f" , {x}\n"
			elif numCount % 2 == 0:
				nums += f"{x}"

			numCount += 1

		self.embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Roulette")
		
		self.embed.add_field(name="Picks",
						value=f"Number bet: \nHigh/low bet: \nColor bet: \nParity bet: ",
						inline=True)
		self.embed.add_field(name="Previous Numbers", value=f"{nums}_ _", inline=True)
		await self.msg.edit(file=nextcord.File('images/roulette/roulette.png'), embed=self.embed, view=self)

		await self.wait()

		for child in self.children:
			if not child.disabled:
				child.disabled = True

		await self.msg.edit(view=self)

		await self.Spin(interaction)

	async def Spin(self, interaction:Interaction):
		toDelete = await interaction.send("The wheel is spinning...", ephemeral=True)
		await asyncio.sleep(1.5)

		red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
		black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

		# 60% chance to pick a red
		if self.usedThreeOfAKind:
			chosenList = choices(population=[red, black], weights=[0.60, 0.50], k=1)[0]
			n = choice(chosenList)
		else:
			n = randrange(0, 37)
		

		roulette = Image.open('images/roulette/roulette.png')
		whiteChip = Image.open('images/roulette/whitechip.png')
		whiteChip = whiteChip.resize((50, 50))
		roulette.paste(whiteChip, self.getPos(n), whiteChip)
		# n = 0

		if n > 18: 
			highLowResult = "⬆"
			roulette.paste(whiteChip, self.getHighLowPos("high"), whiteChip)
		else: 
			highLowResult = "⬇"
			roulette.paste(whiteChip, self.getHighLowPos("low"), whiteChip)

		if n == 0: colorResult = ":green_heart:"  # green
		elif n == 1 or n == 3 or n == 5 or n == 7 or n == 9 or n == 12 or n == 14 or n == 16 or n == 18 or n == 19 or n == 21 or n == 23 or n == 25 or n == 27 or n == 30 or n == 32 or n == 34 or n == 36:
			colorResult = ":heart:"  # red
			roulette.paste(whiteChip, self.getColorPos("red"), whiteChip)
		else: 
			colorResult = ":black_heart:"  # black
			roulette.paste(whiteChip, self.getColorPos("black"), whiteChip)

		if n % 2 == 0: 
			parityResult = "2⃣"
			roulette.paste(whiteChip, self.getParityPos("even"), whiteChip)
		else:
			parityResult = "1⃣"
			roulette.paste(whiteChip, self.getParityPos("odd"), whiteChip)

		# roulette.save("images/roulette/temproulette.png")

		emojiNum = self.getNumEmoji(n)
		winnings = ""

		moneyToAdd = 0
		if self.number.option == n:
			winnings += "\nYou guessed the number! You won 35x your bet!"
			moneyToAdd += self.number.bet * 35

		if self.displayHighLowBet == highLowResult:
			winnings += "\nYou guessed the high/low! You won 2x your bet!"
			moneyToAdd += self.highOrLow.bet * 2

		if self.displayColorBet == colorResult and self.displayColorBet != ":green:":
			winnings += "\nYou guessed the color! You won 2x your bet!"
			moneyToAdd += self.color.bet * 2
		elif self.displayColorBet == colorResult:
			winnings += "\nYou guessed the color green! You won 35x your bet!"
			moneyToAdd += self.color.bet * 35

		if self.displayParityBet == parityResult:
			winnings += "\nYou guessed the parity! You won 2x your bet!"
			moneyToAdd += self.parity.bet * 2
		
		amntSpent = self.totalBet
		if amntSpent != 0:
			gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="RLTTE", amntBet=amntSpent)
		else:
			gameID = None

		if moneyToAdd > amntSpent:
			# \n**Profit:** {moneyToAdd - amntSpent}{emojis.coin}
			result = f"You won a grand total of {moneyToAdd}{emojis.coin} after betting {amntSpent}{emojis.coin}"
		elif moneyToAdd < amntSpent:
			if moneyToAdd > 0:
				result = f"You got back {moneyToAdd:,}{emojis.coin} after betting {amntSpent:,}{emojis.coin}"
			else:
				result = f"You lost {amntSpent:,}{emojis.coin}"
		else:
			result = "You didn't lose or win anything!"

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		if self.number.bet or self.highOrLow.bet or self.color.bet or self.parity.bet:
			priorBal = balance + amntSpent - moneyToAdd
			self.embed = await DB.calculateXP(self, interaction, priorBal, amntSpent, self.embed, gameID)
		else:
			self.embed.set_footer(text="No bets were placed, no XP was earned.")
		self.embed.set_field_at(0, name="Picks", 
			value=self.getFullBetsDisplay())
		self.embed.set_field_at(1, name="Outcome:",
							value=f"Number: {emojiNum}\nHigh/low: {highLowResult}\nColor: {colorResult}\nParity: {parityResult}")
		self.embed.add_field(name="-----------------------------------------------------------------",
						value=f"{winnings}\n{result}", inline=False)
		
		if moneyToAdd > amntSpent:
			self.embed, _ = await DB.addProfitAndBalFields(self, interaction, moneyToAdd - amntSpent, self.embed)
		else:
			self.embed, _ = await DB.addProfitAndBalFields(self, interaction, -amntSpent + moneyToAdd, self.embed)
		with io.BytesIO() as image_binary:
			roulette.save(image_binary, 'PNG')
			image_binary.seek(0)

			betAgainView = BetAgainView()
			await self.msg.edit(embed=self.embed, file=nextcord.File(fp=image_binary, filename='image.png'), view=betAgainView)
			roulette.close()

		await self.bot.get_cog("Totals").addTotals(interaction, amntSpent, moneyToAdd, "Roulette")
		await self.bot.get_cog("Quests").AddQuestProgress(interaction, interaction.user, "Rltte", moneyToAdd - amntSpent)

		gameResult = {
			"Name": "Roulette", 
			"AmntBet": amntSpent, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)

		if len(self.previousNums) == 8:  # display only 8 previous numbers
			self.previousNums.pop()
		self.previousNums.insert(0, f"{colorResult} {str(n)}")  # insert the resulting color and number

		await toDelete.delete()

		if await betAgainView.wait():
			await self.msg.edit(view=None)
			return

		if self.totalBet != 0 and not await self.bot.get_cog("Economy").subtractBet(interaction.user, self.totalBet):
			await interaction.send("You don't have enough credits for that bet", ephemeral=True)
			return
		
		if not IsDonatorCheck(interaction.user.id):
			betAgainEmbed = nextcord.Embed(color=Color.yellow())
			betAgainEmbed.description = "***Resetting roulette table***"
			betAgainEmbed.set_footer(text="Tables are instantly reset for donators")
			toDelete = await interaction.send(embed=betAgainEmbed, ephemeral=True)
			await asyncio.sleep(4)
			await toDelete.delete()

		self.embed.remove_field(2)
		self.embed.remove_field(2)
		self.embed.remove_field(2)
		await self.Spin(interaction)



	def getColorPos(self, color):
		if color == "red":
			return (505, 440)
		else:
			return (680, 440)

	def getHighLowPos(self, highLow):
		if highLow == "high":
			return (1030, 440)
		else:
			return (155, 440)

	def getParityPos(self, parity):
		if parity == "even":
			return (330, 440)
		else:
			return (855, 440)


	def getPos(self, num:int):
		if num == 0: 
			return (30,75)

		x = 0
		y = 0

		if num % 3 == 0:
			y = 75
		elif num % 3 == 2:
			y = 170
		elif num % 3 == 1:
			y = 265

		if num in [1, 2, 3]:			x = 110
		elif num in [4, 5, 6]:			x = 200
		elif num in [7, 8, 9]:			x = 285
		elif num in [10, 11, 12]:		x = 375
		elif num in [13, 14, 15]:		x = 460
		elif num in [16, 17, 18]:		x = 550
		elif num in [19, 20, 21]:		x = 635
		elif num in [22, 23, 24]:		x = 725
		elif num in [25, 26, 27]:		x = 810
		elif num in [28, 29, 30]:		x = 900
		elif num in [31, 32, 33]:		x = 985
		elif num in [34, 35, 36]:		x = 1075
		
		return (x,y)

	def getNumEmoji(self, num):
		num = int(num)
		if num == "":return ""
		elif num == 0:return ":zero:"
		elif num == 1:return ":one:"
		elif num == 2:return ":two:"
		elif num == 3:return ":three:"
		elif num == 4:return ":four:"
		elif num == 5:return ":five:"
		elif num == 6:return ":six:"
		elif num == 7:return ":seven:"
		elif num == 8:return ":eight:"
		elif num == 9:return ":nine:"
		elif num == 10:return ":keycap_ten:"
		elif num == 11:return ":one::one:"
		elif num == 12:return ":one::two:"
		elif num == 13:return ":one::three:"
		elif num == 14:return ":one::four:"
		elif num == 15:return ":one::five:"
		elif num == 16:return ":one::six:"
		elif num == 17:return ":one::seven:"
		elif num == 18:return ":one::eight:"
		elif num == 19:return ":one::nine:"
		elif num == 20:return ":two::zero:"
		elif num == 21:return ":two::one:"
		elif num == 22:return ":two::two:"
		elif num == 23:return ":two::three:"
		elif num == 24:return ":two::four:"
		elif num == 25:return ":two::five:"
		elif num == 26:return ":two::six:"
		elif num == 27:return ":two::seven:"
		elif num == 28:return ":two::eight:"
		elif num == 29:return ":two::nine:"
		elif num == 30:return ":three::zero:"
		elif num == 31:return ":three::one:"
		elif num == 32:return ":three::two:"
		elif num == 33:return ":three::three:"
		elif num == 34:return ":three::four:"
		elif num == 35:return ":three::five:"
		elif num == 36:return ":three::six:"
		else: "error"


class Roulette(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.previousNums = []
		self.totalBet = 0

	@nextcord.slash_command(description="Play Roulette!")
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, attach_files=True, add_reactions=True, use_external_emojis=True, manage_messages=True, read_message_history=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='roulette')
	async def roulette(self, interaction:Interaction):
		view = View(self.bot, self.previousNums, interaction.user.id)
		await view.Start(interaction)

def setup(bot):
	bot.add_cog(Roulette(bot))