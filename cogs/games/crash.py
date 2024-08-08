# Stock market crash game

import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns, asyncio, random

import emojis
from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck

class Button(nextcord.ui.Button):
	def __init__(self, label, style):
		super().__init__(label=label, style=style)
	
	async def callback(self, interaction: Interaction):
		assert self.view is not None
		view: View = self.view

		if view.task is not None and view.multiplier != view.crashNum and interaction.user.id == view.userId:
			view.task.cancel() # cancel task if there is a current task, and current multiplier number isn't the crashing number
							# and user issuing command is user who started the game
			await view.finished(interaction)

class View(nextcord.ui.View):
	def __init__(self, bot, userId, amntbet):
		super().__init__()
		self.bot:commands.bot.Bot = bot
		self.userId = userId
		self.task = None
		self.multiplier = 1.0
		self.crashNum = 1.2
		self.crash = False
		self.amntbet = amntbet
		self.embed = None
		self.cashoutButton = Button("Cashout", nextcord.ButtonStyle.green)
		self.botMsg = None

	async def Start(self, interaction:Interaction):
		self.add_item(self.cashoutButton)
		
		pC = random.randint(1, 10)
		if 1 <= pC <= 3:	self.crashNum = 1.2 								# 30%
		elif 4 <= pC <= 5:	self.crashNum = 1.4									# 20% 
		elif 6 <= pC <= 8:	self.crashNum = random.choice([1.6, 1.8])			# 30%
		elif pC == 9:		self.crashNum = random.choice([1.8, 2.0, 2.2, 2.4])	# 10%
		elif pC == 10:	 	
			self.crashNum = round(random.uniform(2.6, 12.0), 1)					# 10%
			if int(self.crashNum * 10) % 2 == 1: self.crashNum = round(self.crashNum + 0.1, 1)

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Crash")
		embed.add_field(name = "Multiplier:", value = f"{str(self.multiplier)}x", inline=True)
		embed.add_field(name = "Profit", value = f"{str(round(self.multiplier * self.amntbet - self.amntbet))}{emojis.coin}", inline=True)

		self.botMsg = await interaction.send(embed=embed, view=self, ephemeral=True)

		try:
			if self.crashNum == 1.2:
				self.crash = True
				raise Exception
			self.task = self.bot.loop.create_task(self.do_loop(embed)) # creates loop for the crash game
			await self.task # performs the loop
		except:
			if self.crash:
				await self.finished(interaction)
			else:
				await self.botMsg.edit(embed=embed)
		finally:
			# resets all the variables 
			self.task = None
			self.multiplier = 1.0
			self.crashNum = 1.6
			self.crash = False
			self.embed = embed


	async def do_loop(self, embed): # keeps the number going and edits the message, until it "crashes"
		await asyncio.sleep(2)
		while True: # will keep going until crash
			self.multiplier += 0.2
			self.multiplier = round(self.multiplier, 1)
			#await self.bot.wait_for('message', check=is_stop, timeout=2)
			embed.set_field_at(0, name = f"Multiplier", value = f"{str(self.multiplier)}x", inline=True)
			embed.set_field_at(1, name = "Profit", value = f"{round(self.multiplier * self.amntbet - self.amntbet):,}{emojis.coin}", inline=True)
			await self.botMsg.edit(embed=embed)
			if self.multiplier == self.crashNum: # if the current multiplier number is the number to crash on 
				self.crash = True
				break
			await asyncio.sleep(2)	
		self.task.cancel() # ends the task

	async def finished(self, interaction:Interaction):
		self.cashoutButton.disabled = True
		await self.botMsg.edit(view=self)
		embed = nextcord.Embed(color=0x23f518, title=f"{self.bot.user.name} | Crash")
		profitInt = 0
		
		if not self.crash: # if they /done it before it crashes 
			profitInt = int(self.amntbet * self.multiplier - self.amntbet) 
			moneyToAdd = int(self.amntbet + profitInt)

		else: # if game crashes without them doing /done
			profitInt = -self.amntbet
			moneyToAdd = 0
			embed.color = nextcord.Color(0xff2020)

		gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="CRSH", amntBet=self.amntbet)

		embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=False)

		if not self.crash:
			embed.add_field(name = f"Would've crashed at", value=f"{self.crashNum}x", inline=False)
		embed, file = await DB.addProfitAndBalFields(self, interaction, profitInt, embed)

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		embed = await DB.calculateXP(self, interaction, balance - profitInt, self.amntbet, embed, gameID)

		await interaction.send(embed=embed, file=file)
		file.close()

		await self.bot.get_cog("Totals").addTotals(interaction, self.amntbet, moneyToAdd, "Crash")
		await self.bot.get_cog("Quests").AddQuestProgress(interaction, interaction.user, "Crsh", profitInt)

		gameResult = {
			"Name": "Crash", 
			"AmntBet": self.amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)


class Crash(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot


	@nextcord.slash_command()
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, use_external_emojis=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='crash', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def crash(self, interaction:Interaction, amntbet:int=nextcord.SlashOption(description="Enter the amount you want to bet. Minimum is 100")): # actual command
		if amntbet < 100:
			raise Exception("minBet 100")
		
		if amntbet > GetMaxBet(interaction.user.id, "Crash"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Crash')}")

		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")

		view = View(self.bot, interaction.user.id, amntbet)
		await view.Start(interaction)



def setup(bot):
	bot.add_cog(Crash(bot))