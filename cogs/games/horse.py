import nextcord
from nextcord.ext import commands 
from nextcord import Interaction, InteractionMessage

import cooldowns, random, time

from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck


class Button(nextcord.ui.Button):
	def __init__(self, label, style, row=1):
		super().__init__(label=label, style=style, row=row)
	
	async def callback(self, interaction: Interaction):
		assert self.view is not None
		view: View = self.view

		if view.userId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return

		if self.label == "Start":
			if view.horseChosen:
				await view.HorseRace(interaction)
				return
			else:
				await interaction.send("You must first select a horse!")
		else:
			view.horseChosen = self.label
			for child in view.children:
				if child.row != 2:
					child.disabled = True
			await view.msg.edit(view=view)

		try:
			await interaction.response.defer()
		except:
			pass


class View(nextcord.ui.View):
	def __init__(self, bot:commands.bot.Bot, interaction:Interaction, amntbet:int, horse:str):
		super().__init__()
		self.bot = bot
		self.interaction = interaction
		self.userId = interaction.user.id
		self.msg:InteractionMessage = None
		self.amntbet = amntbet
		self.horseChosen = horse
		self.embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Horse")
		self.raceTrack = None

		self.horses = list()

	def GetDisplay(self, horseTrack):
		msg = ""
		for element in horseTrack:
			msg += f"{element}"
		return msg

	def GetFullDisplay(self, horses):
		msg = "-------------------------------------------------"
		x = 0
		for horse in horses:
			if x == 0: indicator = ":red_circle:"
			elif x == 1: indicator = ":blue_circle:"
			elif x == 2: indicator = ":green_circle:"
			elif x == 3: indicator = ":white_circle:"
			else: indicator = ":warning:"
			msg += f"\n{indicator}|"
			msg += self.GetDisplay(horse)
			x += 1
		self.raceTrack = "-------------------------------------------------"
		return msg

	async def Start(self):
		if not self.horseChosen:
			self.add_item(Button("Red", nextcord.ButtonStyle.red))
			self.add_item(Button("Blue", nextcord.ButtonStyle.blurple))
			self.add_item(Button("Green", nextcord.ButtonStyle.green))
			self.add_item(Button("Grey", nextcord.ButtonStyle.grey))

		self.add_item(Button("Start", nextcord.ButtonStyle.green, row=2))

		self.raceTrack = "-------------------------------------------------"

		for x in range(4):
			self.horses.append(list())
		for x in range(4):	
			for char in self.raceTrack:
				self.horses[x].append(char)
			self.horses[x].append(":horse_racing:")
		
		self.raceTrack = self.GetFullDisplay(self.horses)

		msg = await self.interaction.send(content=self.raceTrack, view=self, embed=self.embed)
		self.msg = await msg.fetch()
	
	async def HorseRace(self, interaction:Interaction):
		try:
			await interaction.response.defer()
		except:
			pass
		for child in self.children:
			child.disabled = True
		await self.msg.edit(view=self)

		
		notWon = True
		winner = None
		while notWon:
			for _ in range(20):
				raceToMove = random.randint(0, 4)
				# raceToMove = 0
				if raceToMove == 0:
					self.horses[0] = self.horses[0][1:]
				elif raceToMove == 1:
					self.horses[1] = self.horses[1][1:]
				elif raceToMove == 2:
					self.horses[2] = self.horses[2][1:]
				elif raceToMove == 3:
					self.horses[3] = self.horses[3][1:]
				
				if self.horses[0][0] != "-" or self.horses[1][0] != "-" or self.horses[2][0] != "-" or self.horses[3][0] != "-":
					if self.horses[0][0] != "-":
						winner = "Red"
					elif self.horses[1][0] != "-":
						winner = "Blue"
					elif self.horses[2][0] != "-":
						winner = "Green"
					elif self.horses[3][0] != "-":
						winner = "Grey"
					notWon = False
					break


			await self.msg.edit(content=self.GetFullDisplay(self.horses), view=self, embed=self.embed)

			time.sleep(0.5)
		await self.EndGame(interaction, winner)
	
	
	async def EndGame(self, interaction:Interaction, winner):
		if winner == self.horseChosen:
			# PLAYER WINS
			moneyToAdd = self.amntbet * 4
		else:
			# PLAYER LOSES
			moneyToAdd = 0

		profitInt = moneyToAdd - self.amntbet
		
		gameID = await self.bot.get_cog("Economy").addWinnings(self.userId, moneyToAdd, giveMultiplier=True, activityName="Horse", amntBet=self.amntbet)
		
		self.embed, file = await DB.addProfitAndBalFields(self, self.interaction, profitInt, self.embed)

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		self.embed = await DB.calculateXP(self, interaction, balance - profitInt, self.amntbet, self.embed, gameID)

		await self.msg.edit(content=self.GetFullDisplay(self.horses), view=self, embed=self.embed, file=file)
		file.close()

		await self.bot.get_cog("Totals").addTotals(interaction, self.amntbet, moneyToAdd, "Horse")

		gameResult = {
			"Name": "Horse", 
			"AmntBet": self.amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)


class Horse(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot


	@nextcord.slash_command()
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, use_external_emojis=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='horse', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def horse(self, 
		 interaction:Interaction, 
		 amntbet:int=nextcord.SlashOption(required=True, description="Enter the amount you want to bet. Minimum is 100"),
		 horse:str=nextcord.SlashOption(description="What horse would you like?", required=False, choices=["Red", "Blue", "Green", "Grey"])): # actual command

		if amntbet < 100:
			raise Exception("minBet 100")
		
		if amntbet > GetMaxBet(interaction.user.id, "Horse"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Horse')}")
		
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")
		
		view = View(self.bot, interaction, amntbet, horse)

		await view.Start()



def setup(bot):
	bot.add_cog(Horse(bot))