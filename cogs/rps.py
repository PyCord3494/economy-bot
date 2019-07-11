import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class rps(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def rps(self, ctx, userChoice: str, amntBet: int):
		coin = "<:coins:585233801320333313>"
		userChoice = userChoice.lower()
		if userChoice == "rock" or userChoice == "paper" or userChoice == "scissors":
			if await self.bot.get_cog("Economy").subtractBet(ctx, amntBet) != 0:
				botChoice = random.choice(['rock', 'paper', 'scissors'])

				if userChoice == botChoice:
					winner = 0

				elif userChoice == "rock" and botChoice == "scissors":
					winner = 1

				elif userChoice == "paper" and botChoice == "rock":
					winner = 1

				elif userChoice == "scissors" and botChoice == "paper":
					winner = 1

				elif userChoice == "rock" and botChoice == "paper":	
					winner = -1

				elif userChoice == "paper" and botChoice == "scissors":
					winner = -1

				elif userChoice == "scissors" and botChoice == "rock":
					winner = -1

				multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
				embed = discord.Embed(color=0xff2020)
				if winner == 1:
					moneyToAdd = amntBet * 2 
					profitInt = moneyToAdd - amntBet
					result = "YOU WON"
					profit = f"**{profitInt}** (**+{int(profitInt * (multiplier - 1))}**)"
					
					embed.color = discord.Color(0x23f518)

				elif winner == -1:
					moneyToAdd = 0 # nothing to add since loss
					profitInt = -amntBet # profit = amntWon - amntBet; amntWon = 0 in this case
					result = "YOU LOST"
					profit = f"**{profitInt}**"

				
				elif winner == 0:
					moneyToAdd = amntBet # add back their bet they placed since it was pushed (tied)
					profitInt = 0 # they get refunded their money (so they don't make or lose money)
					result = "PUSHED"
					profit = f"**{profitInt}**"

				embed.add_field(name=f"Pit Boss' Casino | RPS", value=f"**{ctx.author.name}** picked **{userChoice}** \n**Pit Boss** picked **{botChoice}**",inline=False)
				giveZeroIfNeg = max(0, profitInt) # will give 0 if profit is negative. 
																						# we don't want it subtracting anything, only adding
				await self.bot.get_cog("Economy").addWinnings(ctx.author.id, moneyToAdd + (giveZeroIfNeg * (multiplier - 1)))
				balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
				embed.add_field(name="Profit", value=f"{profit}{coin}", inline=True)
				embed.add_field(name="Credits", value=f"**{balance}**{coin}", inline=True)

				await self.bot.get_cog("Totals").addTotals(ctx, amntBet, moneyToAdd, 5)
				xp = random.randint(50, 500)
				embed.set_footer(text=f"Earned {xp} XP!")
				await self.bot.get_cog("XP").addXP(ctx, xp)
				await ctx.send(content=f"{ctx.message.author.mention}", embed=embed)



		else:
			await ctx.send("Incorrect choice.")

	@rps.error
	async def rps_handler(self, ctx, error):
		embed = discord.Embed(color=0xff2020, title="Pit Boss Help Menu")
		embed.add_field(name = "`Syntax: /rps <choice> <bet>`", value = "_ _", inline=False)
		embed.add_field(name = "__Verse the bot against some rock, paper, scissors__", value="_ _", inline=False)
		await ctx.send(embed=embed)
		print(error)


def setup(bot):
	bot.add_cog(rps(bot))