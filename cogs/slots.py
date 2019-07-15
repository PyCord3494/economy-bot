# economy-related stuff like betting and gambling, etc.
# profit = moneyToAdd - amntBet
# money to add = moneyToAdd + amntBet (if u win)

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Slots(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def memes(self, ctx, stuff: int):
		await ctx.send(f"{max(0, stuff)}")

	@commands.command(description="Pay to play the slots!", aliases=['slotmachine', 'slot', 'gamble'], pass_context=True)
	@commands.cooldown(1, 9, commands.BucketType.user)
	async def slots(self, ctx, amntBet: int):
		coin = "<:coins:585233801320333313>"
		
		if await self.bot.get_cog("Economy").subtractBet(ctx, amntBet) != 0:
			#emojis = "🍎🍋🍇🍓🍒"
			emojis = "🍎🍒"

			a = random.choice(emojis)
			b = random.choice(emojis)
			c = random.choice(emojis)

			embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Slots", type="rich")

			embed.add_field(name="----------------------------\n| 🎰  [  ]  [  ]  [  ]  🎰 |\n----------------------------", value="_ _")
			botMsg = await ctx.send(embed=embed)
			await asyncio.sleep(1.5)

			embed.set_field_at(0, name=f"------------------------------\n| 🎰  {a}  [  ]  [  ]  🎰 |\n------------------------------", value="_ _")
			await botMsg.edit(embed=embed)
			await asyncio.sleep(1.5)

			embed.set_field_at(0, name=f"-------------------------------\n| 🎰  {a}  {b}  [  ]  🎰 |\n-------------------------------", value="_ _")
			await botMsg.edit(embed=embed)
			await asyncio.sleep(1.5)

			embed.set_field_at(0, name=f"--------------------------------\n| 🎰  {a}  {b}  {c}  🎰 |\n--------------------------------", value="_ _")
			await botMsg.edit(embed=embed)

			#slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"
			embed.color = discord.Color(0x23f518)
			multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
			if (a == b == c): # if all match
				moneyToAdd = int(amntBet * 2)
				profitInt = moneyToAdd - amntBet
				result = "YOU WON"
				profit = f"**{profitInt}** (**+{int(profitInt * (multiplier - 1))}**)"


			elif (a == b) or (a == c) or (b == c): # if two match
				moneyToAdd = int(amntBet * 1.5) # you win 150% your bet
				profitInt = moneyToAdd - amntBet
				result = "YOU WON"
				profit = f"**{profitInt}** (**+{int(profitInt * (multiplier - 1))}**)"


			else: # if no match
				moneyToAdd = 0
				profitInt = moneyToAdd - amntBet
				result = "YOU LOST"
				profit = f"**{profitInt}**"

				embed.color = discord.Color(0xff2020)

			giveZeroIfNeg = max(0, profitInt) # will give 0 if profitInt is negative. 
																				# we don't want it subtracting anything, only adding
																				
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, moneyToAdd + (giveZeroIfNeg * (multiplier - 1)))
			balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
			embed.add_field(name=f"**--- {result} ---**", value="_ _", inline=False)	
			embed.add_field(name="Profit", value=f"{profit}{coin}", inline=True)
			embed.add_field(name="Credits", value=f"**{balance}**{coin}", inline=True)

			await self.bot.get_cog("Totals").addTotals(ctx, amntBet, moneyToAdd, 0)
			xp = random.randint(45, 475)
			embed.set_footer(text=f"Earned {xp} XP!")
			await self.bot.get_cog("XP").addXP(ctx, xp)
			await botMsg.edit(embed=embed)

	# @slots.error
	# async def slots_handler(self, ctx, error):
	# 	embed = discord.Embed(color=0xff2020, title="Pit Boss Help Menu")
	# 	embed.add_field(name = "`Syntax: /slots <bet>`", value = "_ _", inline=False)
	# 	embed.add_field(name = "__Play slots for a chance to double your money!__", value = "_ _", inline=False)
	# 	await ctx.send(embed=embed)
	# 	print(error)

def setup(bot):
	bot.add_cog(Slots(bot))