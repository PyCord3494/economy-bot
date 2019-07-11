# Stock market crash game

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


	async def do_loop(self, ctx, botMsg, embed): # keeps the number going and edits the message, until it "crashes"
		await asyncio.sleep(2)
		while True: # will keep going until crash
			self.multiplier += 0.2
			self.multiplier = round(self.multiplier, 1)
			#await self.bot.wait_for('message', check=is_stop, timeout=2)
			embed.set_field_at(0, name = f"Multiplier", value = f"{str(self.multiplier)}x", inline=True)
			embed.set_field_at(1, name = "Profit", value = f"{str(round(self.multiplier * self.amntBet - self.amntBet))}{self.coin}", inline=True)
			await botMsg.edit(embed=embed)
			if self.multiplier == self.crashNum: # if the current multiplier number is the number to crash on 
				self.crash = True
				break
			await asyncio.sleep(2)	
		self.task.cancel() # ends the task


	@commands.command(pass_context=True)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def crash(self, ctx, bet: int): # actual command
		if await self.bot.get_cog("Economy").subtractBet(ctx, bet) != 0: # checks to see if they have {bet} amount
			self.amntBet = round(bet)
			self.userId = ctx.author.id
			#self.crashNum = round(random.uniform(1.2, 2.0), 1)
			if int(self.crashNum * 10) % 2 == 1: # if crash num is odd (ex: 1.3), make it even (ex: 1.4)
				self.crashNum = round(self.crashNum + 0.1, 1)
			await ctx.send(self.crashNum) # DEBUG LINE 

			embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Crash")
			embed.set_footer(text="Use $stop to stop")
			embed.add_field(name = "Multiplier:", value = f"{str(self.multiplier)}x", inline=True)
			embed.add_field(name = "Profit", value = f"{str(round(self.multiplier * self.amntBet - self.amntBet))}{self.coin}", inline=True)
			botMsg = await ctx.send(embed=embed)

			self.task = self.bot.loop.create_task(self.do_loop(ctx, botMsg, embed)) # creates loop for the crash game
			try:
				await self.task # performs the loop
			except:
				# all of this will occur once the game is over

				embed = discord.Embed(color=0x23f518, title="Pit Boss' Casino | Crash")
				multi = self.bot.get_cog("Economy").getMultiplier(ctx)
				
				if self.crash == False: # if they $stop it before it crashes 
					profitInt = int(self.amntBet * self.multiplier - self.amntBet) 
					moneyToAdd = int(self.amntBet + profitInt)
					profit = f"**{profitInt}** (+**{int(profitInt * (multi - 1))}**)"

					await self.bot.get_cog("Economy").addWinnings(ctx.author.id, (moneyToAdd + (profitInt * (multi - 1))))

				else: # if game crashes without them $stop'ing it in time
					moneyToAdd = 0
					profit = f"**-{self.amntBet}**"
					embed.color = discord.Color(0xff2020)

				await self.bot.get_cog("Totals").addTotals(ctx, self.amntBet, moneyToAdd, 2)
				balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
				xp = random.randint(50, 500)
				await self.bot.get_cog("XP").addXP(ctx, xp)
				embed.set_footer(text=f"Earned {xp} XP!")
				embed.add_field(name = f"Crashed at", value = f"{str(self.multiplier)}x", inline=True)
				embed.add_field(name = "Profit", value = f"{profit}", inline=True)
				embed.add_field(name = "Credits",
									value = f"You have {balance} credits", inline=False)
				await botMsg.edit(embed=embed)

			finally:
				# resets all the variables 
				self.task = None
				self.multiplier = 1.0
				self.crashNum = 1.6
				self.crash = False
				self.amntBet = 0


	@commands.command(pass_context=True)
	async def stop(self, ctx): # the command to stop the game before it "crashes"
		if self.task is not None and self.multiplier != self.crashNum and ctx.author.id == self.userId:
			self.task.cancel() # cancel task if there is a current task, and current multiplier number isn't the crashing number
							   # and user issuing command is user who started the ga,e
			print('cancelling')

def setup(bot):
	bot.add_cog(Crash(bot))