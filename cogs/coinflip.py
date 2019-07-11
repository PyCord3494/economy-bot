# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Coinflip(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['flipcoin', 'flip', 'coin'], pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def coinflip(self, ctx, sideBet: str, amntBet: int):
		if await self.bot.get_cog("Economy").subtractBet(ctx, amntBet) != 0:
			coin = "<:coins:585233801320333313>"
			sideBet = sideBet.lower()
			if sideBet == "heads" or sideBet == "tails":
				coinsides = ['Heads', 'Tails']
				side = random.choice(coinsides)
				if sideBet.lower() == side.lower():
					profitInt = amntBet
					moneyToAdd = amntBet * 2
					multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)

					await self.bot.get_cog("Economy").addWinnings(ctx.author.id, (moneyToAdd + (profitInt * (multiplier - 1))))
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					embed = discord.Embed(color=0x23f518, type="rich")
					embed.add_field(name=f"Pit Boss' Casino | Coinflip", value=f"The coin landed on {side}\n**--- YOU WON ---**",inline=False)
					embed.add_field(name="Profit", value=f"**{moneyToAdd}** (+**{moneyToAdd * multiplier}**){coin}", inline=True)
					embed.add_field(name="Credits", value=f"**{balance}**{coin}", inline=True)
					await ctx.send(embed=embed)

				else:
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					embed = discord.Embed(color=0xff2020, type="rich")
					embed.add_field(name=f"Pit Boss' Casino | Coinflip", value=f"The coin landed on {side}",inline=False)
					embed.add_field(name="-----------------------------------------------------------------", 
						value = f"Sorry, you didn't win anything.\n**Credits**: {balance}{coin}", inline=False)
					await ctx.send(embed=embed)

	@coinflip.error
	async def coinflip_handler(self, ctx, error):
		embed = discord.Embed(color=0xff2020, title="Pit Boss Help Menu")
		embed.add_field(name = "`Syntax: /coin <choice> <bet>`", value = "_ _", inline=False)
		embed.add_field(name = "__Bet either heads or tails on a quick game of coinflip__", value = "_ _", inline=False)
		await ctx.send(embed=embed)
		print(error)

def setup(bot):
	bot.add_cog(Coinflip(bot))