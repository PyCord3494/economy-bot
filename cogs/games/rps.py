import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns, random

from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck

class rps(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

	@nextcord.slash_command()
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, attach_files=True, add_reactions=True, use_external_emojis=True, manage_messages=True, read_message_history=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='rockpaperscissors', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def rockpaperscissors(self, 
								interaction:Interaction, 
								amntbet,
								userchoice = nextcord.SlashOption(
										required=True,
										name="choice", 
										choices=("rock", "paper", "scissors")
									)
								):

		amntbet = await self.bot.get_cog("Economy").GetBetAmount(interaction, amntbet)

		if amntbet < 100:
			raise Exception("minBet 100")

		if amntbet > GetMaxBet(interaction.user.id, "RPS"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'RPS')}")

		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")
			
		botChoice = random.choice(['rock', 'paper', 'scissors'])

		if userchoice == botChoice:
			winner = 0
			file = nextcord.File("./images/rps/tie.png", filename="image.png")

		elif userchoice == "rock" and botChoice == "scissors":
			winner = 1
			file = nextcord.File("./images/rps/rockwon.png", filename="image.png")

		elif userchoice == "paper" and botChoice == "rock":
			winner = 1
			file = nextcord.File("./images/rps/paperwon.png", filename="image.png")

		elif userchoice == "scissors" and botChoice == "paper":
			winner = 1
			file = nextcord.File("./images/rps/scissorswon.png", filename="image.png")

		elif userchoice == "rock" and botChoice == "paper":	
			winner = -1
			file = nextcord.File("./images/rps/rocklost.png", filename="image.png")

		elif userchoice == "paper" and botChoice == "scissors":
			winner = -1
			file = nextcord.File("./images/rps/paperlost.png", filename="image.png")

		elif userchoice == "scissors" and botChoice == "rock":
			winner = -1
			file = nextcord.File("./images/rps/scissorslost.png", filename="image.png")

		embed = nextcord.Embed(color=0xff2020)
		if winner == 1:
			moneyToAdd = amntbet * 2 
			profitInt = moneyToAdd - amntbet
			result = "YOU WON"

			embed.color = nextcord.Color(0x23f518)

		elif winner == -1:
			moneyToAdd = 0 # nothing to add since loss
			profitInt = -amntbet # profit = amntWon - amntbet; amntWon = 0 in this case
			result = "YOU LOST"


		elif winner == 0:
			moneyToAdd = amntbet # add back their bet they placed since it was pushed (tied)
			profitInt = 0 # they get refunded their money (so they don't make or lose money)
			result = "PUSHED"

		embed.add_field(name=f"{self.bot.user.name}' Casino | RPS", value=f"**{interaction.user.name}** picked **{userchoice}** \n**Pit Boss** picked **{botChoice}**",inline=False)
		gameID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName="RPS", amntBet=amntbet)
		
		embed.add_field(name=f"**--- {result} ---**", value="_ _", inline=False)
		
		embed, _ = await DB.addProfitAndBalFields(self, interaction, profitInt, embed)

		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		embed = await DB.calculateXP(self, interaction, balance - profitInt, amntbet, embed, gameID)

		embed.set_thumbnail(url="attachment://image.png")
		await interaction.send(content=f"{interaction.user.mention}", file=file, embed=embed)
		file.close()
		
		await self.bot.get_cog("Totals").addTotals(interaction, amntbet, moneyToAdd, "RPS")
		await self.bot.get_cog("Quests").AddQuestProgress(interaction, interaction.user, "RPS", profitInt)

		gameResult = {
			"Name": "RPS", 
			"AmntBet": amntbet, 
			"AmntWon": moneyToAdd
		}
		await self.bot.get_cog("DailyQuests").GameEndCheckDailyQuests(interaction, gameResult)


def setup(bot):
	bot.add_cog(rps(bot))