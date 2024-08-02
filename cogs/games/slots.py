import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns, asyncio, random, emojis

from cogs.settings import GetUserSetting
from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck

class StartGame(nextcord.ui.Button):
	def __init__(self, bot):
		super().__init__(label="Start", style=nextcord.ButtonStyle.green)
		self.bot = bot
	
	async def callback(self, interaction:Interaction):
		assert self.view is not None
		view:SlotsView = self.view

		if interaction.user.id != view.owner.id:
			await interaction.send(f"This is not your button", ephemeral=True)
			return
		view.stop()
		await interaction.response.defer()

class SlotsView(nextcord.ui.View):
	def __init__(self, bot, owner:nextcord.Member):
		super().__init__(timeout=120)
		self.owner = owner

		self.startButton = StartGame(bot)
		self.add_item(self.startButton)


class Slots(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.bigWinAmnt = 25000
	

	@nextcord.slash_command(description="Pay to play the slots!")
	@cooldowns.cooldown(1, 9, bucket=cooldowns.SlashBucket.author, cooldown_id='slots', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	@commands.bot_has_guild_permissions(send_messages=True, use_external_emojis=True)
	async def slots(self, interaction:Interaction, amntbet):
		amntbet = await self.bot.get_cog("Economy").GetBetAmount(interaction, amntbet)

		if amntbet < 100:
			raise Exception("minBet 100")
		
		if amntbet > GetMaxBet(interaction.user.id, "Slots"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Slots')}")

		priorBal = await self.bot.get_cog("Economy").getBalance(interaction.user)

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Slots")

		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")

		msgPrefix = "**=== [  <a:pepeslots:1155199556506636410> SLOTS <a:pepeslots:1155199556506636410>  ] ===**\n"
		bigWinMsg = f"----------------------------\n\n**=== [ BIG WIN ] ===**\n{self.bigWinAmnt:,}{emojis.coin}\n"
		embed.description = f"{msgPrefix}\n----------------------------\n| 🎰  [  ]  [  ]  [  ]  🎰 |\n{bigWinMsg}"
		embed.set_footer(text=f"You must bet at least {int(self.bigWinAmnt*0.10):,} to qualify for the big win")
		# embed.add_field(name="----------------------------\n| 🎰  [  ]  [  ]  [  ]  🎰 |\n----------------------------", value="_ _")
		# botMsg = await interaction.send(embed=embed)
		botMsg = None
		if not GetUserSetting(interaction.user.id, "HideSlotsStartButton"):
			view = SlotsView(self.bot, interaction.user)
			botMsg = await interaction.send(view=view, embed=embed)
			await view.wait()


		slotEmojis = "🍎🍋🍇🍓🍒"
		# slotEmojis = "🍎"

		a = random.choice(slotEmojis)
		b = random.choice(slotEmojis)
		c = random.choice(slotEmojis)

		embed.description = f"{msgPrefix}\n----------------------------\n| 🎰  {a}  [  ]  [  ]  🎰 |\n{bigWinMsg}"
		# embed.set_field_at(0, name=f"------------------------------\n| 🎰  {a}  [  ]  [  ]  🎰 |\n------------------------------", value="_ _")
		# await botMsg.edit(embed=embed)
		embed.set_footer(text=None)
		if botMsg:
			await botMsg.edit(view=None, embed=embed)
		else:
			botMsg = await interaction.send(embed=embed)
		await asyncio.sleep(1.5)

		embed.description = f"{msgPrefix}\n----------------------------\n| 🎰  {a}  {b}  [  ]  🎰 |\n{bigWinMsg}"
		# embed.set_field_at(0, name=f"-------------------------------\n| 🎰  {a}  {b}  [  ]  🎰 |\n-------------------------------", value="_ _")
		# await botMsg.edit(embed=embed)
		await botMsg.edit(embed=embed)
		await asyncio.sleep(1.5)

		embed.description = f"{msgPrefix}\n----------------------------\n| 🎰  {a}  {b} {c}  🎰 |\n{bigWinMsg}"
		# embed.set_field_at(0, name=f"--------------------------------\n| 🎰  {a}  {b}  {c}  🎰 |\n--------------------------------", value="_ _")
		# await botMsg.edit(embed=embed)
		await botMsg.edit(embed=embed)

		#slotmachine = f"**[ {a} {b} {c} ]\n{interaction.user.name}**,"
		embed = nextcord.Embed(color=0x23f518, title=f"{self.bot.user.name} | Slots")

		if (a == b == c) or ((a == b) or (a == c) or (b == c)):
			result = "YOU WON"
			if (a == b == c): # if all match
				# must bet at least 10% of big win amount to participate
				if amntbet >= int(self.bigWinAmnt*.10):
					moneyToAdd = self.bigWinAmnt + int(amntbet * 3)
					self.bigWinAmnt = 25000
					result = "YOU WON 3x AND THE BIG WIN!"
				else:
					moneyToAdd = int(amntbet*3)

			elif (a == b) or (a == c) or (b == c): # if two match
				moneyToAdd = int(amntbet * 1.5) # you win 150% your bet
				if amntbet >= int(self.bigWinAmnt*.10):
					self.bigWinAmnt += 1000

		else: # if no match
			moneyToAdd = 0
			result = "YOU LOST"

			embed.color = nextcord.Color(0xff2020)

			if amntbet >= int(self.bigWinAmnt*.10):
				self.bigWinAmnt += 5000

		gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="Slots", amntBet=amntbet)

		profitInt = moneyToAdd - amntbet

		embed.add_field(name=f"{msgPrefix}\n----------------------------\n| 🎰  {a}  {b} {c}  🎰 |\n----------------------------\n\n**--- {result} ---**", value="_ _", inline=False)

		embed, file = await DB.addProfitAndBalFields(self, interaction, profitInt, embed)
		embed = await DB.calculateXP(self, interaction, priorBal, amntbet, embed, gameID)

		await botMsg.edit(content=None, embed=embed, file=file)
		file.close()

		await self.bot.get_cog("Totals").addTotals(interaction, amntbet, moneyToAdd, "Slots")
		await self.bot.get_cog("Quests").AddQuestProgress(interaction, interaction.user, "Slt", profitInt)

		gameResult = {
			"Name": "Slots", 
			"AmntBet": amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)


def setup(bot):
	bot.add_cog(Slots(bot))