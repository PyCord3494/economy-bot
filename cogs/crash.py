# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Crash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.userId = ""
		self.task = None
		self.multiplier = 1.0
		self.crashNum = 1.6
		self.coin = "<:coins:585233801320333313>"
		self.crash = False
		self.amntBet = 0


	async def do_loop(self, ctx, botMsg, embed):
		print("begin loop")
		await asyncio.sleep(2)
		while True:
			self.multiplier += 0.2
			self.multiplier = round(self.multiplier, 1)
			#await self.bot.wait_for('message', check=is_stop, timeout=2)
			embed.set_field_at(0, name = f"Multiplier", value = f"{str(self.multiplier)}x", inline=True)
			embed.set_field_at(1, name = "Profit", value = f"{str(round(self.multiplier * self.amntBet - self.amntBet))}{self.coin}", inline=True)
			await botMsg.edit(embed=embed)
			if self.multiplier == self.crashNum:
				self.crash = True
				break
			print("in loop")
			await asyncio.sleep(2)
		print("outside loop")	
		self.task.cancel()


	@commands.command(pass_context=True)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def crash(self, ctx, bet: int):
		if await self.bot.get_cog("Economy").subtractBet(ctx, bet) != 0:
			self.amntBet = round(bet)
			self.userId = ctx.author.id
			#self.crashNum = round(random.uniform(1.2, 2.0), 1)
			if int(self.crashNum * 10) % 2 == 1:
				self.crashNum = round(self.crashNum + 0.1, 1)
			await ctx.send(self.crashNum)
			embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Crash")
			embed.set_footer(text="Use $stop to stop")
			embed.add_field(name = "Multiplier:", value = f"{str(self.multiplier)}x", inline=True)
			embed.add_field(name = "Profit", value = f"{str(round(self.multiplier * self.amntBet - self.amntBet))}{self.coin}", inline=True)
			botMsg = await ctx.send(embed=embed)
			self.task = self.bot.loop.create_task(self.do_loop(ctx, botMsg, embed))
			try:
				await self.task
			except:
				xp = random.randint(50, 500)
				multi = self.bot.get_cog("Economy").getMultiplier(ctx)
				if self.crash == False:
					profit = round(self.amntBet * self.multiplier - self.amntBet)
					await self.bot.get_cog("Economy").addWinnings(ctx.author.id, self.amntBet*self.multiplier)
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)

					embed = discord.Embed(color=0x23f518, title="Pit Boss' Casino | Crash")
					embed.set_footer(text=f"Earned {xp} XP!")
					embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=True)
					embed.add_field(name = "Profit", value = f"{str(profit)} (+{profit * multi}){self.coin}", inline=True)
					embed.add_field(name = "Credits", 
									value = f"You now have {balance}{self.coin}", inline=False)
					await botMsg.edit(embed=embed)
					await self.bot.get_cog("XP").addXP(ctx, xp)
					await self.bot.get_cog("Totals").addTotals(ctx, self.amntBet, self.amntBet * self.multiplier, 2)

				elif self.crash == True:
					balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					embed = discord.Embed(color=0xff2020, title="Pit Boss' Casino | Crash")
					embed.set_footer(text=f"Earned {xp} XP!")
					embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=True)
					embed.add_field(name = "Profit", value = f"-{str(round(self.amntBet))}{self.coin}", inline=True)
					embed.add_field(name = "Credits",
									value = f"You have {balance} credits", inline=False)
					await botMsg.edit(embed=embed)
					await self.bot.get_cog("XP").addXP(ctx, xp)
					await self.bot.get_cog("Totals").addTotals(ctx, self.amntBet, 0, 2)
			finally:
				self.task = None
				self.multiplier = 1.0
				self.crashNum = 1.6
				self.crash = False
				self.amntBet = 0


	@commands.command(pass_context=True)
	async def stop(self, ctx):
		if self.task is not None and self.multiplier != self.crashNum and ctx.author.id == self.userId:
			self.task.cancel()
			print('cancelling')
		#	await message.channel.send(f"self.stop is {self.stop} and author id is {self.userId}")

	# @commands.command(pass_context=True)
	# @commands.cooldown(1, 1, commands.BucketType.user)
	# async def crash(self, ctx, self.amntBet: int):
	# 		self.coin = "<:coins:585233801320333313>"
	# 		if self.amntBet >= 10 and self.amntBet <= 250:
	# 			if await self.bot.get_cog("Economy").subtractBet(ctx, self.amntBet) != 0:
	# 				self.userId = ctx.author.id
	# 				self.multiplier = 1.0
	# 				self.crashNum = round(random.uniform(1.0, 2.0), 1)
	# 				if int(self.crashNum * 10) % 2 == 1:
	# 					self.crashNum = round(self.crashNum + 0.1, 1)
	# 				await ctx.send(self.crashNum)
	# 				embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Crash")
	# 				embed.set_footer(text="Use $stop to stop")
	# 				embed.add_field(name = f"Multiplier:", value = f"{str(self.multiplier)}x", inline=True)
	# 				embed.add_field(name = "Profit", value = f"{str((self.multiplier * self.amntBet) - self.amntBet)}{self.coin}", inline=True)
	# 				botMsg = await ctx.send(embed=embed)
	# 				crash = False
	# 				self.inLoop = True

					# await asyncio.sleep(1)
					# while self.stop:
					# 	self.multiplier += 0.2
					# 	self.multiplier = round(self.multiplier, 1)
					# 	#await self.bot.wait_for('message', check=is_stop, timeout=2)
					# 	embed.set_field_at(0, name = f"Multiplier", value = f"{str(self.multiplier)}x", inline=True)
					# 	embed.set_field_at(1, name = "Profit", value = f"{str((self.multiplier * self.amntBet) - self.amntBet)}{self.coin}", inline=True)
					# 	await botMsg.edit(embed=embed)
					# 	print(self.stop)
					# 	if self.multiplier == self.crashNum:
					# 		crash = True
					# 		break
					# 	if self.stop not True:
					# 		await asyncio.sleep(2)

					# self.inLoop = False
					# if crash == False and self.stop == True:
					# 	await self.bot.get_cog("Economy").addWinnings(ctx.author.id, self.amntBet*2)
					# 	balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					# 	embed = discord.Embed(color=0x23f518, title="Pit Boss' Casino | Crash")
					# 	embed.set_footer(text=f"Earned {round(self.amntBet / 2 * 10)} XP!")
					# 	embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=True)
					# 	embed.add_field(name = "Profit", value = f"-{str(self.amntBet)}{self.coin}", inline=True)
					# 	embed.add_field(name = "Credits", 
					# 					value = f"You now have {balance}{self.coin}", inline=False)
					# 	await botMsg.edit(embed=embed)
					# elif crash == True and self.stop == False:
					# 	balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
					# 	embed = discord.Embed(color=0xff2020, title="Pit Boss' Casino | Crash")
					# 	embed.set_footer(text=f"Earned {self.amntBet / 4 * 10} XP!")
					# 	embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=True)
					# 	embed.add_field(name = "Profit", value = f"-{str(self.amntBet)}{self.coin}", inline=True)
					# 	embed.add_field(name = "Credits",
					# 					value = f"You have {balance} credits", inline=False)
					# 	await botMsg.edit(embed=embed)
					# else:
					# 	await ctx.send(f"ERROR.")

					# self.stop = False


def setup(bot):
	bot.add_cog(Crash(bot))