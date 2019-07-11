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

	@commands.command(description="Check your balance!", aliases=['bal', 'credits'], pass_context=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def balance(self, ctx):
		""" Show your balance """
		balance = self.getBalance(ctx.author.id)
		embed = discord.Embed(color=1768431)
		embed.add_field(name = f"Credits", value = f"You have **{balance}** credits", inline=False)
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

	
	#@balance.error
	#async def balance_handler(self, ctx, error):
	#	embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
	#	embed.add_field(name = f"{error}", value="_ _")
	#	print(error)



	# async def createWallet(self, ctx):
	# 	db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
	# 	cursor = db.cursor()
	# 	discordId = ctx.author.id

	# 	sql_check = f"""SELECT *
 #                    FROM Economy
 #                    WHERE DiscordID = '{discordId}';"""
	# 	cursor.execute(sql_check)
	# 	db.commit()

	# 	records = cursor.fetchall()

	# 	num_of_rows = 0
	# 	for row in records:
	# 		num_of_rows += 1

	# 	if num_of_rows < 1:
	# 		botMsg = await ctx.send("Creating your wallet... Please wait.")

	# 		add_walletId = self.createID(db, cursor)

	# 		sql_insert = f"""INSERT INTO Economy(WalletID, DiscordID, Credits)
	# 							VALUES ('{add_walletId}', '{discordId}', 100);"""
	# 		cursor.execute(sql_insert)
	# 		db.commit()

	# 		balance = self.getBalance(ctx.author.id)
	# 		newMsg = f"Wallet created. Your balance is: **${balance}**\nYou may now use your money. :wink:"
			
	# 		MODERATION_CHANNEL = self.bot.get_channel(ctx.channel.id)
	# 		editMsg = await MODERATION_CHANNEL.fetch_message(botMsg.id)
	# 		await editMsg.edit(content=newMsg)
	# 		db.close()
	# 		return 0
	# 	else:
	# 		db.close()
	# 		return 1


	async def subtractBet(self, ctx, amntBet): # subtracts the bet users place when they play games
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


	def getBalance(self, discordId):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		sql = f"""SELECT DiscordId, Credits
				  FROM Economy
				  WHERE DiscordID = '{discordId}';"""
		cursor.execute(sql)
		db.commit()
		getRow = cursor.fetchone()
		balance = getRow[1]
		db.close()

		return balance

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



def setup(bot):
	bot.add_cog(Economy(bot))