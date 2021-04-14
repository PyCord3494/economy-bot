import discord
from discord.ext import commands
import pymysql
import asyncio
import random
import channels
import config
import utils

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.levelReward = [550, 1500, 3000, 7500, 13500, 18500, 24000, 29000, 35000, 42000, 50000]

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def rewards(self, ctx):
		# dailyReward = await self.getDailyReward(ctx)
		if not await self.bot.get_cog("Economy").accCheck(ctx.author):
			await ctx.send("Hello! Please type .start to create your wallet. :smiley:")
			return
		level = await self.getLevel(ctx)
		levelReward = self.levelReward[level]
		donatorReward = await self.getDonatorReward(ctx)


		embed = discord.Embed(color=1768431)
		embed.set_footer(text=f"Donators can $claimall !")
		# embed.add_field(name = "Daily", value = f"**{dailyReward}** credits", inline=True)
		embed.add_field(name = "Level Reward", value = f"**{levelReward}** credits", inline=True)
		embed.add_field(name = "Donator Reward", value = f"**{donatorReward}** credits", inline=True)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True)
	@commands.cooldown(1, 500, commands.BucketType.user)
	async def donator(self, ctx):
		if not await self.bot.get_cog("Economy").accCheck(ctx.author):
			await ctx.send("Hello! Please type .start to create your wallet. :smiley:")
			return

		if self.bot.get_cog("Economy").isDonator(ctx.author.id) == 1:
			donatorReward = await self.getDonatorReward(ctx)
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, donatorReward)
			balance = await self.bot.get_cog("Economy").getBalance(ctx.author)
			embed = discord.Embed(color=1768431)
			embed.add_field(name = f"You got {donatorReward} credits", 
							value = f"You have {balance} credits", inline=False)
			await ctx.send(embed=embed)
	else:
		await ctx.send("Hello! Please type .start to create your wallet. :smiley:")


	@commands.command(pass_context=True)
	@commands.cooldown(1, 500, commands.BucketType.user)
	async def levelreward(self, ctx):
		if not await self.bot.get_cog("Economy").accCheck(ctx.author):
			await ctx.send("Hello! Please type .start to create your wallet. :smiley:")
			return
		level = await self.getLevel(ctx)
		levelReward =  self.levelReward[level]

		multiplier = self.bot.get_cog("Economy").getMultiplier(ctx.author)
		extraMoney = int(levelReward * (multiplier - 1))
		await self.bot.get_cog("Economy").addWinnings(ctx.author.id, levelReward + extraMoney)
		balance = await self.bot.get_cog("Economy").getBalance(ctx.author)

		embed = discord.Embed(color=1768431)
		embed.add_field(name = f"You got {levelReward} (+{extraMoney}) credits",
						value = f"You have {balance} credits\nMultiplier: {multiplier}x\nExtra Money: {extraMoney}", inline=False)
		await ctx.send(embed=embed)


	# @commands.command(pass_context=True)
	# @commands.cooldown(1, 500, commands.BucketType.user)
	# async def daily(self, ctx):
	# 	if await self.bot.get_cog("Economy").accCheck(ctx.author) == True:			
	# 		dailyReward = await self.getDailyReward(ctx)
	# 		multiplier = self.bot.get_cog("Economy").getMultiplier(ctx.author)
	# 		extraMoney = int(dailyReward * (multiplier - 1))
	# 		await self.bot.get_cog("Economy").addWinnings(ctx.author.id, dailyReward + extraMoney)
	# 		balance = await self.bot.get_cog("Economy").getBalance(ctx.author)
	# 		embed = discord.Embed(color=1768431)
	# 		embed.add_field(name = f"You got {dailyReward} (+{extraMoney}) credits", 
	# 						value = f"You have {balance} credits\nMultiplier: {multiplier}x\nExtra Money: {extraMoney}", inline=False)
	# 		await ctx.send(embed=embed)
	# 	else:
	# 		await ctx.send("Hello! Please type .start to create your wallet. :smiley:")

	# @commands.command(pass_context=True)
	# async def claimall(self, ctx):
	# 	db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
	# 	cursor = db.cursor()

	# 	sql = f"""SELECT Level
	# 			  FROM Economy
	# 			  WHERE DiscordID = '{ctx.author.id}';"""
	# 	cursor.execute(sql)
	# 	db.commit()
	# 	getRow = cursor.fetchone()


	# 	level = int(getRow[0])

	# 	db.close()

	# 	totalMoney = self.levelReward[level] + 1000

	# 	multiplier = self.bot.get_cog("Economy").getMultiplier(ctx.author)
	# 	await self.bot.get_cog("Economy").addWinnings(ctx.author.id, totalMoney)

	# 	balance = await self.bot.get_cog("Economy").getBalance(ctx.author)

	# @commands.command(pass_context=True)
	# async def search(self, ctx):
	# 	if await self.bot.get_cog("Economy").accCheck(ctx.author) == True:
	# 		if await self.bot.get_cog("Economy").getBalance(ctx.author) < 100:
	# 			amnt = random.randint(50, 250)
	# 			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amnt)
	# 			balance = await self.bot.get_cog("Economy").getBalance(ctx.author)
	# 			embed = discord.Embed(color=1768431)
	# 			embed.add_field(name = f"You found {amnt} credits", value = f"You have {balance} credits", inline=False)
	# 			await ctx.send(embed=embed)
	# 		else:
	# 			await ctx.send(ctx.author.mention + ", you can't use this if you have over 25 credits.")
	# 	else:
	# 		await ctx.send("Hello! Please type .start to create your wallet. :smiley:")

	# async def getDailyReward(self, ctx):
	# 	db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
	# 	cursor = db.cursor()
	# 	sql = f"""SELECT DailyReward
	# 			  FROM Economy
	# 			  WHERE DiscordID = '{ctx.author.id}';"""
	# 	cursor.execute(sql)
	# 	db.commit()
	# 	getRow = cursor.fetchone()
	# 	db.close()
	# 	dailyReward = getRow[0]
	# 	return dailyReward

	async def getLevel(self, ctx):
		db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT Level
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		db.close()
		level = getRow[0]
		return level

	async def getDonatorReward(self, ctx):
		db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
		cursor = db.cursor()

		sql = f"""SELECT DonatorReward
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		db.close()
		donatorReward = getRow[0]

		if donatorReward == None:
			donatorReward = 25000
			
		return donatorReward

	#@daily.error
	#async def daily_handler(self, ctx, error):
	#	embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
	#	embed.add_field(name = "`Syntax: $daily`", value = "_ _", inline=False)
	#	embed.add_field(name = "__Claim your FREE daily money!.__", value="_ _", inline=False)
	#	await ctx.send(embed=embed)
	#	print(error)


def setup(bot):
	bot.add_cog(Rewards(bot))