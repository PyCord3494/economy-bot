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
				botChoice = ['rock', 'paper', 'scissors']
				botChoice = random.choice(botChoice)

				winner = 10

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


				if winner == 1:
					await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntBet*2)
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					multiplier = await self.bot.get_cog("Economy").getMultiplier(ctx)
					embed = discord.Embed(color=0x23f518, type="rich")
					embed.add_field(name=f"Pit Boss' Casino | RPS", value=f"**{ctx.author.name}** picked **{userChoice}** \n**Bot** picked **{botChoice}**",inline=False)
					embed.add_field(name="-----------------------------------------------------------------", 
						value = f"Congratulations, you just won {amntBet*2} (+{(amntBet*2) * multiplier}){coin}!\n**Credits**: {balance}{coin}", inline=False)
					await ctx.send(embed=embed)

				elif winner == -1:
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					embed = discord.Embed(color=0xff2020, type="rich")
					embed.add_field(name=f"Pit Boss' Casino | RPS", value=f"**{ctx.author.name}** picked **{userChoice}** \n**Bot** picked **{botChoice}**",inline=False)
					embed.add_field(name="-----------------------------------------------------------------", 
						value = f"Sorry, you didn't win anything.\n**Credits**: {balance}{coin}", inline=False)
					await ctx.send(embed=embed)

				elif winner == 0:
					await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntBet)
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					embed = discord.Embed(color=1768431, type="rich")
					embed.add_field(name=f"Pit Boss' Casino | RPS", value=f"**{ctx.author.name}** picked **{userChoice}** \n**Bot** picked **{botChoice}**",inline=False)
					embed.add_field(name="-----------------------------------------------------------------", 
						value = f"It's a tie. At least you get your {amntBet}{coin} back!\n**Credits**: {balance}{coin}", inline=False)
					await ctx.send(embed=embed)

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