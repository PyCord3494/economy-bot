import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import sqlite3, datetime

from math import ceil
from random import randint

import config, emojis

# conn = sqlite3.connect(config.db)
class DB(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

	@staticmethod
	def fetchOne(sql, values: list=None):
		conn = sqlite3.connect(config.db)

		if values:
			cursor = conn.execute(sql, values)
		else:
			cursor = conn.execute(sql)
		data = cursor.fetchone()

		conn.close()

		return data

	@staticmethod
	def fetchAll(sql, values: list=None):
		conn = sqlite3.connect(config.db)

		if values:
			cursor = conn.execute(sql, values)
		else:
			cursor = conn.execute(sql)
		data = cursor.fetchall() 

		conn.close()

		return data

	@staticmethod
	def insert(sql, values: list=None):
		conn = sqlite3.connect(config.db)
		conn.execute(sql, values)
		conn.commit()
		conn.close()


	@staticmethod
	def update(sql, values: list=None):
		conn = sqlite3.connect(config.db)
		if values:
			conn.execute(sql, values)
		else:
			conn.execute(sql)
		conn.commit()
		conn.close()

	@staticmethod
	def delete(sql, values: list=None):
		conn = sqlite3.connect(config.db)
		if values:
			conn.execute(sql, values)
		else:
			conn.execute(sql)
		conn.commit()
		conn.close()
	
	@staticmethod
	def ConvertDatetimeToSQLTime(time:datetime.datetime):
		return time.strftime('%Y-%d-%m %H:%M:%S')

	@staticmethod
	async def calculateXP(self, interaction:Interaction, initBal, amntBet, embed, gameID):
		minBet = initBal * 0.05
		minBet = int(ceil(minBet / 10.0) * 10.0)
		if amntBet >= minBet:
			xp = randint(50, 500)
			embed.set_footer(text=f"Earned {xp:,} XP!\nGameID: {gameID}")
			await self.bot.get_cog("XP").addXP(interaction, xp)
		else:
			embed.set_footer(text=f"You have to bet your minimum to earn xp.\nGameID: {gameID}")
		return embed

	@staticmethod
	async def addProfitAndBalFields(self, interaction:Interaction, profit:int, embed:nextcord.Embed, redEmbed=False, giveMultiplier=True, calculateRankedCP:bool=True):
		balance = await self.bot.get_cog("Economy").getBalance(interaction.user)
		multiplier = self.bot.get_cog("Multipliers").getMultiplier(interaction.user.id)

		if calculateRankedCP:
			await self.bot.get_cog("RankedSystem").AddRankedPoints(interaction, profit > 0)

		name = "Profit"
		if profit > 0 and redEmbed != True:
			embed.color = nextcord.Color(0x23f518)
		else:
			embed.color = nextcord.Color(0xff2020)
		if profit > 0:
			file = emojis.GetWin()
			if giveMultiplier:
				embed.add_field(name=name, value=f"+{profit:,} (+{round(profit * (multiplier - 1))}){emojis.coin}", inline=True)
			else:
				embed.add_field(name=name, value=f"+{profit:,}{emojis.coin}", inline=True)
		else:
			file = emojis.GetLose()
			embed.add_field(name=name, value=f"{profit:,}{emojis.coin}", inline=True)
		
		embed.set_thumbnail(url="attachment://results.png")
		embed.add_field(name="Credits", value=f"{balance:,}{emojis.coin}", inline=True)
		return embed, file


# allItems = DB.fetchAll('SELECT * FROM Items')
# allItemNames = list()
# for x in allItems:
# 	allItemNames.append((x[1],))

# allItemNamesList = [item for sublist in allItemNames for item in sublist]

# buyableItems = DB.fetchAll('SELECT * FROM Items WHERE Buyable = 1;')
# buyableItemNames = list()
# for x in buyableItems:
# 	buyableItemNames.append((x[1],))
# buyableItemNamesList = [item for sublist in buyableItemNames for item in sublist]

# sellableItems = DB.fetchAll("SELECT * FROM Items WHERE SellPrice > 0;")
# sellableItemNames = list()
# for x in sellableItems:
# 	sellableItemNames.append((x[1],))
# sellableItemNamesList = [item for sublist in sellableItemNames for item in sublist]

# usableItemNames = DB.fetchAll("SELECT Name FROM Items WHERE Type = 'Usable';")
# usableItemNamesList = [item[0] for item in usableItemNames]

# collectibleItems = DB.fetchAll("SELECT * FROM Items WHERE Type = 'Collectible';")

# randomItemList = DB.fetchAll("SELECT * FROM Items WHERE Type = 'Usable' or TYPE = 'Collectible';")
# highestRarity = DB.fetchOne("SELECT * FROM Items WHERE Type = 'Usable' or TYPE = 'Collectible' ORDER BY Rarity DESC LIMIT 1;")[7]

# donatorsSQL = DB.fetchAll("SELECT DiscordID FROM Donators;")
# donators = [discordID[0] for discordID in donatorsSQL]




conn = sqlite3.connect(config.db)

cursor = conn.cursor()

allItems = cursor.execute('SELECT * FROM Items').fetchall()
allItemNames = list()
for x in allItems:
	allItemNames.append((x[1],))

allItemNamesList = [item for sublist in allItemNames for item in sublist]


buyableItems = cursor.execute('SELECT * FROM Items WHERE Buyable = 1;').fetchall() 
buyableItemNames = list()
for x in buyableItems:
	buyableItemNames.append((x[1],))
buyableItemNamesList = [item for sublist in buyableItemNames for item in sublist]

sellableItems = cursor.execute("SELECT * FROM Items WHERE SellPrice > 0;").fetchall() 
sellableItemNames = list()
for x in sellableItems:
	sellableItemNames.append((x[1],))
sellableItemNamesList = [item for sublist in sellableItemNames for item in sublist]

usableItemNames = cursor.execute("SELECT Name FROM Items WHERE Type = 'Usable';").fetchall() 
usableItemNamesList = [item[0] for item in usableItemNames]

collectibleItems = cursor.execute("SELECT * FROM Items WHERE Type = 'Collectible';").fetchall() 

data = cursor.execute("SELECT * FROM Items WHERE Type = 'Usable' or TYPE = 'Collectible';").fetchall() 

highestRaritySQL = cursor.execute("SELECT Rarity FROM Items WHERE Type = 'Usable' or TYPE = 'Collectible' ORDER BY Rarity DESC LIMIT 1;").fetchall()
highestRarity = highestRaritySQL[0]

donatorsSQL = cursor.execute("SELECT DiscordID FROM Donators;").fetchall() 
donators = [discordID[0] for discordID in donatorsSQL]

# Fetch all quests once and store them in self.quests
questListSQL = cursor.execute("SELECT QuestID FROM DailyQuests").fetchall()
questList = [row[0] for row in questListSQL]

conn.close()


def setup(bot):
	bot.add_cog(DB(bot))