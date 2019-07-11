# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Coinflip(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['flipcoin', 'flip', 'coin', 'cf'], pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def coinflip(self, ctx, sideBet: str, amntBet: int):
		if await self.bot.get_cog("Economy").subtractBet(ctx, amntBet) != 0:
			coin = "<:coins:585233801320333313>"
			sideBet = sideBet.lower()
			if sideBet == "heads" or sideBet == "tails":
				side = random.choice(['Heads', 'Tails'])
				
				multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)

				embed = discord.Embed(color=0x23f518)
				#embed.set_thumbnail(url="https://png2.kisspng.com/sh/a69196ddd7a980602722dfec7d75a1db/L0KzQYm3VcIyN5Dvh5H0aYP2gLBuTgNqdKdqip9sb3nxPbb0jBpqNZZyhAZyY3BxPbj2jPQuPZM1S6RvMUS1cYHrWMIvPmc9UKk7NUS0RYO9WcM2O2I7Sak7Mz7zfri=/kisspng-silver-coin-emoji-emoticon-gold-5b032f142a0d82.6688725415269353161723.png")
				if sideBet.lower() == side.lower():
					moneyToAdd = int(amntBet * 2)
					profitInt = moneyToAdd - amntBet
					profit = f"**{profitInt}** (**+{int(profitInt * (multiplier - 1))}**)"

					file = discord.File("./images/coinwon.png", filename="image.png")

				else:
					moneyToAdd = 0
					profitInt = moneyToAdd - amntBet
					profit = f"**{profitInt}**"

					file = discord.File("./images/coinlost.png", filename="image.png")
					embed.color = discord.Color(0xff2020)
					
				embed.set_thumbnail(url="attachment://image.png")
				embed.add_field(name=f"Pit Boss' Casino | Coinflip", value=f"The coin landed on {side}\n_ _",inline=False)
				giveZeroIfNeg = max(0, profitInt) # will give 0 if profitInt is negative. 
																				# we don't want it subtracting anything, only adding
				await self.bot.get_cog("Economy").addWinnings(ctx.author.id, moneyToAdd + (giveZeroIfNeg * (multiplier - 1)))
				balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
				embed.add_field(name="Profit", value=f"{profit}{coin}", inline=True)
				embed.add_field(name="Credits", value=f"**{balance}**{coin}", inline=True)

				await self.bot.get_cog("Totals").addTotals(ctx, amntBet, moneyToAdd, 4)
				xp = random.randint(45, 475)
				embed.set_footer(text=f"Earned {xp} XP!")
				await self.bot.get_cog("XP").addXP(ctx, xp)
				await ctx.send(file=file, embed=embed)

	@coinflip.error
	async def coinflip_handler(self, ctx, error):
		embed = discord.Embed(color=0xff2020, title="Pit Boss Help Menu")
		embed.add_field(name = "`Syntax: /coin <choice> <bet>`", value = "_ _", inline=False)
		embed.add_field(name = "__Bet either heads or tails on a quick game of coinflip__", value = "_ _", inline=False)
		await ctx.send(embed=embed)
		print(error)

def setup(bot):
	bot.add_cog(Coinflip(bot))