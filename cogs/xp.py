# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class XP(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.XPtoLevelUp = [5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000]
		self.levelReward = [550, 1500, 3000, 7500, 13500, 18500, 24000, 29000, 35000, 42000, 50000]



	@commands.command(aliases=['xp'], pass_context=True)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def level(self, ctx):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()

			sql = f"""SELECT LevelReward, XP, TotalXP, Level
					  FROM Economy
					  WHERE DiscordID = '{ctx.author.id}';"""
			cursor.execute(sql)
			db.commit()
			getRow = cursor.fetchone()

			level = getRow[3]
			xp = getRow[1]
			requiredXP = self.XPtoLevelUp[level]
			levelReward = getRow[0]
			progress = round((xp / requiredXP) * 100)
			totalXP = getRow[1]

			db.close()

			embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Level")
			embed.add_field(name = "Level", value = f"You are level **{level}**", inline=True)
			embed.add_field(name = "Level Reward", value = f"**{levelReward}**", inline=True)
			embed.add_field(name = "Total XP", value = f"**{totalXP}**", inline=True)
			embed.add_field(name = "XP / Next Level", value = f"**{xp}** / **{requiredXP}**", inline=True)
			embed.add_field(name = "XP Until Level Up", value = f"**{requiredXP - xp}**", inline=True)
			embed.add_field(name = "Progress", value = f"**{progress}%**", inline=True)
			await ctx.send(embed=embed)
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")


	async def addXP(self, ctx, xp):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		sql = f"""Update Economy
				  SET XP = XP + {xp}
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()

		await self.levelUp(ctx, db, ctx.author.id)

		sql = f"""Update Economy
				  SET totalXP = totalXP + {xp}
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		db.close()


	async def levelUp(self, ctx, db, discordId):
		cursor = db.cursor()
		sql_check = f"""SELECT XP, Level
						FROM Economy
						WHERE DiscordID = '{discordId}';"""
		cursor.execute(sql_check)
		db.commit()
		getRow = cursor.fetchone()
		xp = getRow[0]
		level = getRow[1]

		if xp > self.XPtoLevelUp[level]:
			sql = f"""Update Economy
				  SET LevelReward = {self.levelReward[level + 1]}, XP = XP - {self.XPtoLevelUp[level]}, Level = Level + 1
				  WHERE DiscordID = '{discordId}';"""
			cursor.execute(sql)
			db.commit()
			embed = discord.Embed(color=1768431, title="Level Up!")
			file = discord.File("./images/levelup.png", filename="image.png")
			embed.set_thumbnail(url="attachment://image.png")
			embed.add_field(name = f"{ctx.author.name}, you Leveled Up!", value = "_ _", inline=False)
			embed.add_field(name = f"Level Reward", value = f"**{self.levelReward[level]} ---> {self.levelReward[level + 1]}**:confetti_ball::confetti_ball:", inline=False)
			await ctx.send(file=file, embed=embed)
			#print(level + 1)
			#role = discord.utils.get(ctx.guild.roles, name = f"Level {level + 1}")
			#await ctx.author.add_roles(role)
			#await asyncio.sleep(0.5)
			#role = discord.utils.get(ctx.guild.roles, name = f"Level {level}")
			#await ctx.author.remove_roles(role)

# HERE FOR TESTING PURPOSES FOR IMAGES AND THUMBNAILS
	# @commands.command(pass_context=True)
	# async def test(self, ctx):
	# 	embed = discord.Embed(color=1768431, title="Level Up!")
	# 	file = discord.File("./images/timeout.png", filename="image.png")
	# 	embed.set_thumbnail(url="attachment://image.png")
	# 	embed.add_field(name = f"{ctx.author.name}, you Leveled Up!", value = "_ _", inline=False)
	# 	embed.add_field(name = f"Level Reward", value = f"**550 ---> 1500** :confetti_ball::confetti_ball: ", inline=False)
	# 	await ctx.send(file=file, embed=embed)



		
def setup(bot):
	bot.add_cog(XP(bot))