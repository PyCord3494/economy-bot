# economy-related stuff like betting and gambling, etc.
# profit = moneyToAdd - amntBet
# money to add = moneyToAdd + amntBet (if u win)

import discord
from discord.ext import commands
import sqlite3
import asyncio
import random

from db import DB

class Slots(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.coin = "<:coins:585233801320333313>"

	@commands.command(pass_context=True)
	async def memes(self, ctx, stuff: int):
		await ctx.send(f"{max(0, stuff)}")

	@commands.command(description="Pay to play the slots!", aliases=['slotmachine', 'slot', 'gamble'], pass_context=True)
	@commands.cooldown(1, 9, commands.BucketType.user)
	@commands.bot_has_guild_permissions(send_messages=True, use_external_emojis=True)
	async def slots(self, ctx, amntBet):
		coin = "<:coins:585233801320333313>"
		
		if not await self.bot.get_cog("Economy").accCheck(ctx.author):
			await ctx.invoke(self.bot.get_command('start'))

		amntBet = await self.bot.get_cog("Economy").GetBetAmount(ctx, amntBet)

		if not await self.bot.get_cog("Economy").subtractBet(ctx.author, amntBet):
			embed = discord.Embed(color=1768431, title=f"{self.bot.user.name} | Slots")
			embed.set_thumbnail(url=ctx.author.avatar_url)
			embed.add_field(name="ERROR", value="You do not have enough to do that.")

			embed.set_footer(text=ctx.author)

			await ctx.send(embed=embed)
			return

		emojis = "🍎🍋🍇🍓🍒🍊"

		a = random.choice(emojis)
		b = random.choice(emojis)
		c = random.choice(emojis)

		embed = discord.Embed(color=1768431, title=f"{self.bot.user.name}' Casino | Slots", type="rich")

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
		multiplier = self.bot.get_cog("Economy").getMultiplier(ctx.author)
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
		embed.add_field(name=f"**--- {result} ---**", value="_ _", inline=False)
		embed = await DB.addProfitAndBalFields(self, ctx, profit, embed)

		balance = await self.bot.get_cog("Economy").getBalance(ctx.author)
		priorBal = balance - profitInt + (giveZeroIfNeg * (multiplier - 1))
		embed = await DB.calculateXP(self, ctx, priorBal, amntBet, embed)

		await botMsg.edit(embed=embed)
		await self.bot.get_cog("Totals").addTotals(ctx, amntBet, moneyToAdd, 0)

		await self.bot.get_cog("Quests").AddQuestProgress(ctx, ctx.author, "Slts", profitInt)


def setup(bot):
	bot.add_cog(Slots(bot))