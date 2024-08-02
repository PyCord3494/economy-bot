import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns, asyncio, random

import emojis
from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck


class DealNoDealButton(nextcord.ui.Button):
	def __init__(self, label, style):
		super().__init__(label=label, style=style)
	async def callback(self, interaction: nextcord.Interaction):
		assert self.view is not None
		offerView: OfferView = self.view
		view: View = offerView.view
		
		if view.ownerId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return
		if self.label == "Deal":
			await view.EndGame(interaction, offerView.offer)
		elif self.label == "No Deal":
			await view.NoDeal()
		try:
			await interaction.response.defer()
		except:
			pass

class Button(nextcord.ui.Button):
	def __init__(self, label, value, style, row):
		super().__init__(label=label, style=style, row=row)
		self.value = value
		self.opened = False
	async def callback(self, interaction: nextcord.Interaction):
		assert self.view is not None
		view: View = self.view

		if view.ownerId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return

		if self.opened:
			return

		if not view.myCase:
			view.myCase = self
			self.disabled = True
			self.style = nextcord.ButtonStyle.gray

			view.embed.description = f"{view.getPrefixMsg()}"

			view.remove_item(self)

			children = view.children.copy()

			view.clear_items()

			if self.row >= 1:
				children[4].row = 1
			if self.row >= 2:
				children[9].row = 2
			if self.row >= 3:
				children[14].row = 3

			self.row = 0
			view.add_item(self)
			for child in children:
				view.add_item(child)

			await view.msg.edit(view=view, embed=view.embed)
			return
		
		if view.finalTurn:
			await view.EndGame(interaction, self.value)
			return

		self.label = f"{self.value}x"
		self.opened = True
		if self.value < 1:
			self.style = nextcord.ButtonStyle.green
		elif self.value == 1:
			self.style = nextcord.ButtonStyle.gray
		else:
			self.style = nextcord.ButtonStyle.red
		
		self.disabled = True

		await view.msg.edit(view=view)

		await view.caseOpened(self)

		try:
			await interaction.response.defer()
		except:
			pass

class OfferView(nextcord.ui.View):
	def __init__(self, bot, view):
		super().__init__(timeout=60)
		self.bot:commands.bot.Bot = bot
		self.view = view

		self.add_item(DealNoDealButton(label="Deal", style=nextcord.ButtonStyle.green))
		self.add_item(DealNoDealButton(label="No Deal", style=nextcord.ButtonStyle.red))
		self.offer = None
	
	async def Offer(self):
		view = self.view
		multipliersRemaining = []
		for child in view.children:
			if not child.opened:
				multipliersRemaining.append(child.value)
		self.offer = round(sum(multipliersRemaining) / len(multipliersRemaining), 2)

		view.embed.description = f"{view.getMultiplierList()}\n\n\n**Offer: {self.offer}x**\n\n\n**Deal or No Deal?**"

		await view.msg.edit(embed=view.embed, view=self)


class View(nextcord.ui.View):
	def __init__(self, bot, ownerId):
		super().__init__(timeout=60)
		self.bot:commands.bot.Bot = bot
		self.amntBet = None

		# self.multiplier = []
		self.msg = None
		self.embed = None

		self.totalCasesLeft = 0
		self.casesLeftTillOffer = 3

		self.finalTurn = False
		self.endGame = False

		self.myCase = None

		self.offerView = OfferView(bot, self)

		self.ownerId = ownerId
	
	def getPrefixMsg(self):
		msg = f"{self.getMultiplierList()}\nYour case: {self.myCase.label}\n\n\n"

		if self.casesLeftTillOffer == 1: 
			plural = "case"
		else: plural = "cases"
		msg += f"**Choose {self.casesLeftTillOffer} more {plural}**"

		return msg
	
	def getMultiplierList(self):
		leftSide = []
		rightSide = []
		count = 0
		temp = self.children.copy()
		temp.sort(key=lambda x: x.value, reverse=False)
		for case in temp:
			if case.opened:
				value = f"~~{case.value}x~~"
			else:
				value = f"{case.value}x"
			if count // (len(temp)/2) > 0:
				rightSide.append(f"{value}")
			else:
				leftSide.append(f"{value}")
			count += 1

		msg = ""

		for count in range(len(leftSide)):
			msg += f"{leftSide[count]}"
			if count < len(rightSide):
				if len(leftSide[count]) > 5:
					msg += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{rightSide[count]}\n"
				elif len(leftSide[count]) == 5:
					msg += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{rightSide[count]}\n"
				elif len(leftSide[count]) == 4:
					msg += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{rightSide[count]}\n"
				elif len(leftSide[count]) == 3:
					msg += f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{rightSide[count]}\n"
				
		return msg


	async def Start(self, interaction:Interaction, casecount, multiplier, amntBet):
		self.ownerId = interaction.user.id
		self.amntBet = amntBet
		self.totalCasesLeft = casecount
		random.shuffle(multiplier)
		# self.multiplier = multiplier
		for x in range(casecount):
			row = x//5
			case = Button(label=f"{x+1}", value=multiplier[x], style=nextcord.ButtonStyle.blurple, row=row)
			self.add_item(case)
		
		self.embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Deal or No Deal")
		self.embed.description = f"{self.getMultiplierList()}\n\n\n**Choose YOUR case**"
		self.msg = await interaction.send(embed=self.embed, view=self)
		# self.msg = await msg.fetch()
	
	async def caseOpened(self, case:Button):
		self.totalCasesLeft -= 1
		self.casesLeftTillOffer -= 1
		self.embed.description = f"{self.getPrefixMsg()}"
		await self.msg.edit(embed=self.embed, view=self)
		# if self.casesOpened == len(self.multiplier):

		await self.ProcessCases()
	
	async def CheckForFinalTurn(self):
		if self.totalCasesLeft == 2:
			self.finalTurn = True
			
			unopenedCase = None
			for case in self.children:
				if not case.opened:
					if case.value != self.myCase.value: 
						unopenedCase = case
						break
			
			self.clear_items()

			self.add_item(self.myCase)
			self.add_item(unopenedCase)

			self.myCase.disabled = False

			self.embed.description = f"{self.getMultiplierList()}\nYour case: {self.myCase.label}\n\n\n**Final turn.** Click your case or the other case to open"
			await self.msg.edit(embed=self.embed, view=self)

			return True
	
	async def ProcessCases(self):
		# cases left till offer is 0, send player offer
		if self.casesLeftTillOffer == 0:
			await self.offerView.Offer()
			return
		else:
			await self.CheckForFinalTurn()

	
	async def NoDeal(self):
		if await self.CheckForFinalTurn():
			return

		if self.totalCasesLeft >= 4 and self.totalCasesLeft <= 5:
			self.casesLeftTillOffer = self.totalCasesLeft - 2
		else:
			self.casesLeftTillOffer = 3
		self.embed.description = f"{self.getPrefixMsg()}"
		await self.msg.edit(embed=self.embed, view=self)

	async def EndGame(self, interaction:Interaction, multiplier):
		self.endGame = True
		self.embed.description = f"**Game Over**\nYou won **{multiplier}x** your bet!"

		moneyToAdd = int(round(self.amntBet * multiplier))
		profitInt = moneyToAdd - self.amntBet

		if multiplier >= 1:
			gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="DOND", amntBet=self.amntBet)
			self.embed, file = await DB.addProfitAndBalFields(self, interaction, profitInt, self.embed)
		else:
			gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=False, activityName="DOND", amntBet=self.amntBet)
			self.embed, file = await DB.addProfitAndBalFields(self, interaction, profitInt, self.embed, True)

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		self.embed = await DB.calculateXP(self, interaction, balance - moneyToAdd, self.amntBet, self.embed, gameID)

		await self.msg.edit(embed=self.embed, view=None, file=file)
		file.close()

		await self.bot.get_cog("Totals").addTotals(interaction, self.amntBet, moneyToAdd, "DOND")

		gameResult = {
			"Name": "DOND", 
			"AmntBet": self.amntBet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)


class Dond(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.multipliers = {
			5: [0.01, 0.5, 1.0, 1.4, 2.0],
			10: [0.01, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0],
		}

	@nextcord.slash_command()
	@cooldowns.cooldown(1, 10, bucket=cooldowns.SlashBucket.author, cooldown_id='dond', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def dond(self, interaction:Interaction, amntbet:int=nextcord.SlashOption(description="Enter the amount you want to bet. Minimum is 1000"), 
				casecount:int = nextcord.SlashOption(choices=[5, 10])):
		if amntbet < 1000:
			raise Exception("minBet 1000")
		
		if amntbet > GetMaxBet(interaction.user.id, "DOND"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'DOND')}")

		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")

		multiplier = self.multipliers[casecount]
		view = View(self.bot, interaction.user.id)
		await view.Start(interaction, casecount, multiplier, amntbet)

def setup(bot):
	bot.add_cog(Dond(bot))