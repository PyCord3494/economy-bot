import discord
from discord.ext import commands
import pymysql
import asyncio
import random
import channels
import utils

class Rewards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.levelReward = [550, 1500, 3000, 7500, 13500, 18500, 24000, 29000, 35000, 42000, 50000]

	@commands.command(pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def rewards(self, ctx):
		dailyReward = await self.getDailyReward(ctx)
		level = await self.getLevel(ctx)
		levelReward = self.levelReward[level]
		donatorReward = await self.getDailyReward(ctx)


		embed = discord.Embed(color=1768431)
		embed.set_footer(text=f"Donators can $claimall !")
		embed.add_field(name = "Daily", value = f"**{dailyReward}** credits", inline=True)
		embed.add_field(name = "Level Reward", value = f"**{levelReward}** credits", inline=True)
		embed.add_field(name = "Donator Reward", value = f"**{donatorReward}** credits", inline=True)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True)
	@commands.cooldown(1, 500, commands.BucketType.user)
	async def donator(self, ctx):
		if utils.check_roles(["Donator"], [y.name for y in ctx.message.author.roles]):
			donatorReward = await self.getDonatorReward(ctx)
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, donatorReward)
			balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
			embed = discord.Embed(color=1768431)
			embed.add_field(name = f"You got {donatorReward} credits", 
							value = f"You have {balance} credits", inline=False)
			await ctx.send(embed=embed)
		else:
			embed = discord.Embed(color=0xff2020)
			embed.add_field(name="You must donate 10USD or more to use this command", value="[Click Here](https://www.paypal.me/AutopilotJustin) to donate, then contact <@547475078082985990>")
			await ctx.send(embed=embed)


	@commands.command(pass_context=True)
	@commands.cooldown(1, 500, commands.BucketType.user)
	async def levelreward(self, ctx):
		level = await self.getLevel(ctx)
		levelReward =  self.levelReward[level]

		multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
		extraMoney = int(levelReward * (multiplier - 1))
		await self.bot.get_cog("Economy").addWinnings(ctx.author.id, levelReward + extraMoney)
		balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)

		embed = discord.Embed(color=1768431)
		embed.add_field(name = f"You got {levelReward} (+{extraMoney}) credits",
						value = f"You have {balance} credits\nMultiplier: {multiplier}x\nExtra Money: {extraMoney}", inline=False)
		await ctx.send(embed=embed)


	@commands.command(pass_context=True)
	#@commands.cooldown(1, 500, commands.BucketType.user)
	async def daily(self, ctx):
		if ctx.message.channel.id == channels.channel["dailymoney"]:			
			dailyReward = await self.getDailyReward(ctx)
			multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
			extraMoney = int(dailyReward * (multiplier - 1))
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, dailyReward + extraMoney)
			balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
			embed = discord.Embed(color=1768431)
			embed.add_field(name = f"You got {dailyReward} (+{extraMoney}) credits", 
							value = f"You have {balance} credits\nMultiplier: {multiplier}x\nExtra Money: {extraMoney}", inline=False)
			await ctx.send(embed=embed)
		else:
			ctx.command.reset_cooldown(ctx)
			await ctx.message.delete()
			botMsg = await ctx.send(f"{ctx.author.mention}, that command is only allowed in <#585234694170345501>")
			await asyncio.sleep(6.5)
			await botMsg.delete()

	# @commands.command(pass_context=True)
	# async def claimall(self, ctx):
	# 	db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
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

	# 	multiplier = self.bot.get_cog("Economy").getMultiplier(ctx)
	# 	await self.bot.get_cog("Economy").addWinnings(ctx.author.id, totalMoney)

	# 	balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)

	@commands.command(pass_context=True)
	async def search(self, ctx):
		amnt = random.randint(25, 100)
		if self.bot.get_cog("Economy").getBalance(ctx.author.id) < 100:
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amnt)
			balance = self.bot.get_cog("Economy").getBalance(ctx.author.id)
			embed = discord.Embed(color=1768431)
			embed.add_field(name = f"You found {amnt} credits", value = f"You have {balance} credits", inline=False)
			await ctx.send(embed=embed)
		else:
			await ctx.send(ctx.author.mention + ", you can't use this if you have over 25 credits.")

	async def getDailyReward(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT DailyReward
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		dailyReward = getRow[0]
		db.close()
		return dailyReward

	async def getLevel(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT Level
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		level = getRow[0]
		db.close()
		return level

	async def getDonatorReward(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT DonatorReward
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		dailyReward = getRow[0]
		db.close()
		return dailyReward

	#@daily.error
	#async def daily_handler(self, ctx, error):
	#	embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
	#	embed.add_field(name = "`Syntax: $daily`", value = "_ _", inline=False)
	#	embed.add_field(name = "__Claim your FREE daily money!.__", value="_ _", inline=False)
	#	await ctx.send(embed=embed)
	#	print(error)


def setup(bot):
	bot.add_cog(Rewards(bot))