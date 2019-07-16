# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.coin = "<:coins:585233801320333313>"


	@commands.command(aliases=['begin', 'new'], pass_context=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def start(self, ctx):
		if await self.accCheck(ctx) == False:
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()
			sql = f"""INSERT INTO Economy(DiscordID)
					  VALUES ('{ctx.author.id}');"""
			cursor.execute(sql)
			db.commit()

			sql = f"""INSERT INTO Inventory(DiscordID)
					  VALUES ('{ctx.author.id}');"""
			cursor.execute(sql)
			db.commit()

			sql = f"""INSERT INTO Totals(DiscordID)
					  VALUES ('{ctx.author.id}');"""
			cursor.execute(sql)
			db.commit()

			await ctx.send("You are now successfully registered! Thank you, and have fun.")
		else:
			await ctx.send("You are already registered, silly")
		

	@commands.command(aliases=['bal', 'credits'], pass_context=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def balance(self, ctx):
		""" Show your balance """
		if await self.accCheck(ctx) == True:
			balance = await self.getBalance(ctx)
			crates, keys = await self.getInventory(ctx)
			embed = discord.Embed(color=1768431)
			embed.add_field(name = "Credits", value = f"You have **{balance}** credits", inline=False)
			embed.add_field(name = "_ _\nCrates", value = f"You have **{crates}** crates", inline=True)
			embed.add_field(name = "_ _\nKeys", value = f"You have **{keys}** keys", inline=True)
			await ctx.send(embed=embed)


	def isDonator(self, discordID):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor() # DonatorCheck is either 0 or 1 (0 for not donator, 1 for donator)
		sql = f"""SELECT DonatorCheck 
				  FROM Economy
				  WHERE DiscordID = '{discordID}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		donatorCheck = getRow[0] # assign donatorCheck to grabbed column DonatorCheck for the row that has {discordID}
		db.close()

		return donatorCheck


	def getMultiplier(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT Multiplier
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		multiplier = getRow[0]
		db.close()

		return multiplier


	async def subtractBet(self, ctx, amntBet): # subtracts the bet users place when they play games
		if await self.accCheck(ctx) == True:
			discordId = ctx.author.id
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()
			balance = self.getBalance(ctx.author.id)
			if amntBet <= balance and amntBet > 0:
				sql = f"""UPDATE Economy
						  SET Credits = Credits - {amntBet}
						  WHERE DiscordID = '{discordId}';"""
				cursor.execute(sql)
				db.commit()
				db.close()
				return 1 # return 1 if user has enough $$$ to bet their amount entered
			else:
				await ctx.send(f"Incorrect amount, you have: **{balance}**{self.coin}.")
				db.close()
				return 0 # return 0 if user trying to bet more $$$ than they have



	async def addWinnings(self, discordId, winnings): # add the amount won 
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		
		sql = f"""UPDATE Economy
				  SET Credits = Credits + {winnings}
				  WHERE DiscordID = '{discordId}';"""
		cursor.execute(sql)
		db.commit()
		db.close()


	async def getBalance(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		sql = f"""SELECT Credits
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		db.close()
		balance = getRow[0]
		return balance
	

	async def getInventory(self, ctx): # grabs all the crates and keys from database
		if await self.accCheck(ctx) == True:
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor() 
			# "Keys" is a special word and can't be used in SQL statements for some reason
			sql = f"""SELECT Crates, Keyss
					  FROM Inventory
					  WHERE DiscordID = {ctx.author.id};"""

			cursor.execute(sql)
			db.commit()
			getRow = cursor.fetchone()
			db.close()
			crates = getRow[0]
			keys = getRow[1]
			return crates, keys


	async def subtractInv(self, discordId, amnt): # called when people open crates (subtracts them from inv.)
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""UPDATE Inventory
				  SET Crates = Crates - {amnt}, Keyss = Keyss - {amnt}
				  WHERE DiscordID = '{discordId}';"""
		cursor.execute(sql)
		db.commit()


	@commands.command()
	async def top(self, ctx): # scoreboard to display top 10 richest individuals
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""SELECT DiscordID, Credits
				  FROM Economy
				  Limit 10""" # Limit = 10 to only get 10 people
		cursor.execute(sql) 
		db.commit()
		records = cursor.fetchall() # get all rows (10 total)
		db.close()

		topUsers = ""
		count = 1
		for x in records: 
			user = await self.bot.fetch_user(x[0]) # grab the user from the current record
			topUsers += f"{count}. < {user.name} > - {x[1]}\n"
			count += 1 # number the users from 1 - 10

		await ctx.send(f"```MD\nTop 10\n======\n{topUsers}```") # send the list with the top 10


	async def accCheck(self, ctx):
		# checks if they already have a wallet in database
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		sql = f"""SELECT DiscordID
				  FROM Economy
				  WHERE DiscordID = '{ctx.author.id}';"""

		cursor.execute(sql) 
		db.commit()

		getRow = cursor.fetchone()
		db.close()

		if getRow == None: # getRow will be None if no account is found, therefor return False
			return False
		else: 			   # else if they're in the database, return True
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")



def setup(bot):
	bot.add_cog(Economy(bot))