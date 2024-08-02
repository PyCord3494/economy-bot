import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns, asyncio, random

import emojis
from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck


class MultiplayerButton(nextcord.ui.Button):
	def __init__(self, label, style):
		super().__init__(label=label, style=style)
	
	async def callback(self, interaction:Interaction):
		assert self.view is not None
		view: MultiplayerView = self.view
		
		if interaction.user.id != view.opponent.id:
			if interaction.user.id == view.player.id:
				await interaction.send(f"This button must be clicked by {view.opponent.mention}", ephemeral=True)
				return
			else:
				await interaction.send(f"This is not your game", ephemeral=True)
				return

		view.children.clear()

		if self.label == "Deny": 
			view.embed.color = nextcord.Color(0xff2020)
			view.embed.description = "This request has been denied."
			await interaction.edit(embed=view.embed, view=view)
			return
		
		await interaction.edit(view=view)
		
		await view.Play(interaction)
			

class MultiplayerView(nextcord.ui.View):
	def __init__(self, bot:commands.bot.Bot):
		super().__init__()
		self.bot = bot

		self.player = None
		self.opponent = None
		self.sidebet = None
		self.amntbet = None

		self.embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Coinflip")
	
	async def Initiate(self, interaction:Interaction, player:nextcord.Member, opponent:nextcord.Member, sidebet, amntbet):
		self.player=player
		self.opponent=opponent
		self.sidebet = sidebet
		self.amntbet = amntbet

		acceptButton = MultiplayerButton("Accept", nextcord.ButtonStyle.green)
		denyButton = MultiplayerButton("Deny", nextcord.ButtonStyle.red)
		
		self.add_item(acceptButton)
		self.add_item(denyButton)

		self.embed.description = f"{self.opponent} must click Accept to begin... They have 30 seconds"
		
		await interaction.send(embed=self.embed, view=self)
	
	async def Play(self, interaction:Interaction):
		if not await self.bot.get_cog("Economy").subtractBet(self.player, self.amntbet):
			raise Exception("tooPoor")

		if not await self.bot.get_cog("Economy").subtractBet(self.opponent, self.amntbet):
			await self.bot.get_cog("Economy").addWinnings(self.player.id, self.amntbet)
			await interaction.send(f"{self.opponent.mention} does not have enough money for this")
			return
		
		side = random.choice(["heads", "tails"]) # computer picks result

		file = None
		if side == "heads":
			file = nextcord.File("./images/coinheads.png", filename="image.png")
		else:
			file = nextcord.File("./images/cointails.png", filename="image.png")
		if self.sidebet == side: # if author bets on correct side
			winner = self.player
			loser = self.opponent
		else: # else, user bet on correct side
			winner = self.opponent
			loser = self.player
		self.embed.set_thumbnail(url="attachment://image.png")
		self.embed.description = f"The coin landed on {side}\n_ _{winner.mention} wins {self.amntbet*2}{emojis.coin}!"

		winnerLogID = await self.bot.get_cog("Economy").addWinnings(winner.id, self.amntbet*2, giveMultiplier=False, activityName="CF", amntBet=self.amntbet)
		loserLogID = await self.bot.get_cog("Economy").addWinnings(loser.id, 0, giveMultiplier=False, activityName="CF", amntBet=self.amntbet)

		self.embed.set_footer(text=f"{winner}'s GameID: {winnerLogID}\n{loser}'s GameID: {loserLogID}")

		await interaction.edit(file=file, embed=self.embed)
		file.close()




class Coinflip(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot


	@nextcord.slash_command()
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, attach_files=True, use_external_emojis=True, manage_messages=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='coinflip', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def coinflip(self, interaction:Interaction, amntbet, sidebet = nextcord.SlashOption(
																required=True,
																name="side", 
																choices=("heads", "tails")), 
														user: nextcord.Member=None):
		amntbet = await self.bot.get_cog("Economy").GetBetAmount(interaction, amntbet)

		if user:
			if user.id == interaction.user.id:
				await interaction.send(f"You cannot play with yourself", ephemeral=True)

			# if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			# 	raise Exception("tooPoor")

			# if not await self.bot.get_cog("Economy").subtractBet(user, amntbet):
			# 	await interaction.send(f"{user.mention} has either not typed /start yet or does not have enough money for this.", ephemeral=True)
			# 	return
			
			view = MultiplayerView(self.bot)
			await view.Initiate(interaction, interaction.user, user, sidebet, amntbet)			

			return





		###################
		## SINGLE PLAYER ##
		###################
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		if amntbet < 100:
			raise Exception("minBet 100")

		if amntbet > GetMaxBet(interaction.user.id, "Coinflip"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Coinflip')}")

		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")


		side = random.choice(["Heads", "Tails"]).lower()

		embed = nextcord.Embed(color=0x23f518)
		
		if sidebet == side:
			moneyToAdd = int(amntbet * 2)
			file = nextcord.File("./images/coinwon.png", filename="image.png")

		else:
			moneyToAdd = 0
			file = nextcord.File("./images/coinlost.png", filename="image.png")
			embed.color = nextcord.Color(0xff2020)

		profitInt = moneyToAdd - amntbet

		embed.add_field(name=f"{self.bot.user.name} | Coinflip", value=f"The coin landed on {side}\n_ _",inline=False)
		gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="CF", amntBet=amntbet)
		
		
		embed, _ = await DB.addProfitAndBalFields(self, interaction, profitInt, embed)

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		embed = await DB.calculateXP(self, interaction, balance - profitInt, amntbet, embed, gameID)

		embed.set_thumbnail(url="attachment://image.png")
		await interaction.send(file=file, embed=embed)

		await self.bot.get_cog("Totals").addTotals(interaction, amntbet, moneyToAdd, "Coinflip")
		await self.bot.get_cog("Quests").AddQuestProgress(interaction, interaction.user, "CF", profitInt)

		gameResult = {
			"Name": "Coinflip", 
			"AmntBet": amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)

def setup(bot):
	bot.add_cog(Coinflip(bot))