# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random
import time
import datetime
from PIL import Image, ImageDraw, ImageFont

actualGame = ["Slt", "BJ", "Crsh", "RLTTE", "CF", "RPS"]

def log(discordID, creditsSpent, creditsWon, gameNumber): # Logs what credits have been spent where, by who, to who, why and the time which this has happened
	#localtime = time.asctime(time.localtime(time.time()))
	x = datetime.datetime.now()
						#  MON DAY HOUR:MIN:SEC
	localtime = x.strftime("%b %d %H:%M:%S")
	logs = open("logs.txt", "a")
	logs.write(f"{localtime} : {discordID} : {creditsSpent} : {creditsWon} : {actualGame[gameNumber]}\n")
	logs.flush()
	logs.close()

class Totals(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def profile(self, ctx):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
			try:
				db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
				cursor = db.cursor()

				sql = f"""SELECT Profit, Games
						  FROM Totals
						  WHERE DiscordID = '{ctx.author.id}';"""
				cursor.execute(sql)
				db.commit()
				getRow = cursor.fetchone()

				profit = getRow[0]
				games = getRow[1]

				db.close()

				db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
				cursor = db.cursor()

				sql = f"""SELECT Credits, Level, XP
						  FROM Economy
						  WHERE DiscordID = '{ctx.author.id}';"""
				cursor.execute(sql)
				db.commit()
				getRow = cursor.fetchone()
				db.close()
				balance = getRow[0]
				level = getRow[1]
				xp = getRow[2]
				XPtoLevelUp = [5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000]
				requiredXP = XPtoLevelUp[level]

				crates, keys = await self.bot.get_cog("Economy").getInventory(ctx)

				embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Profile")
				embed.set_thumbnail(url=ctx.author.avatar_url)
				embed.add_field(name = "User", value = f"{ctx.author.name}", inline=True)
				embed.add_field(name = "Level", value = f"{level}", inline=True)
				embed.add_field(name = "Balance", value = f"{balance}", inline=True)
				embed.add_field(name = "XP / Next Level", value = f"{xp} / {requiredXP}", inline=True)
				embed.add_field(name = "Profit", value = f"{profit}", inline=True)
				embed.add_field(name = "Games Played", value = f"{games}", inline=True)
				embed.add_field(name = "Crates", value = f"{crates}", inline=True)
				embed.add_field(name = "Keys", value = f"{keys}", inline=True)

				img = Image.open("./images/scroll.png")
				font_type = ImageFont.truetype('arial.ttf',30)
				draw = ImageDraw.Draw(img)
				draw.text(xy=(125,100), text=f"{ctx.author.name}",fill=(170,126,0),font=font_type)
				draw.text(xy=(375,100), text=f"Level {level}",fill=(170,126,0),font=font_type)
				img.save("images/profile.png")
				file = discord.File("images/profile.png", filename="image.png")
				embed.set_image(url="attachment://image.png")

				await ctx.send(file=file, embed=embed)
			except Exception as e:
				print(e)
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")



	@commands.command(pass_context=True, aliases=['totals', 'me'])
	async def stats(self, ctx):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
			db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
			cursor = db.cursor()

			sql = f"""SELECT Paid, Won, Profit, Games, Slots, Blackjack, Crash, Roulette, Coinflip, RPS
					  FROM Totals
					  WHERE DiscordID = '{ctx.author.id}';"""
			cursor.execute(sql)
			db.commit()
			getRow = cursor.fetchone()

			creditsSpent = getRow[0]
			creditsWon = getRow[1]
			profit = getRow[2]
			games = getRow[3]
			slots = getRow[4]
			blackjack = getRow[5]
			crash = getRow[6]
			roulette = getRow[7]
			coinflip = getRow[8]
			rps = getRow[9]

			db.close()

			embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Stats")
			embed.add_field(name = "Total Spent", value = f"{creditsSpent}", inline=True)
			embed.add_field(name = "Total Won", value = f"{creditsWon}", inline=True)
			embed.add_field(name = "Profit", value = f"{profit}", inline=True)
			embed.add_field(name = "Games Played", value = f"{games}", inline=True)
			embed.add_field(name = "Slots", value = f"{slots}", inline=True)
			embed.add_field(name = "Blackjack", value = f"{blackjack}", inline=True)
			embed.add_field(name = "Crash", value = f"{crash}", inline=True)
			embed.add_field(name = "Roulette", value = f"{roulette}", inline=True)
			embed.add_field(name = "Coinflip", value = f"{coinflip}", inline=True)
			embed.add_field(name = "Rock-Paper-Scissors", value = f"{rps}", inline=True)

			await ctx.send(embed=embed)
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")



	async def addTotals(self, ctx, spent, won, game):
		discordID = ctx.author.id
		profit = won - spent
		db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
		cursor = db.cursor()

		try:
			if game == 0:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Slots = Slots + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""
						  
			elif game == 1:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Blackjack = Blackjack + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""


			elif game == 2:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Crash = Crash + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

			elif game == 3:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Roulette = Roulette + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

			elif game == 4:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Coinflip = Coinflip + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""


			elif game == 5:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, RPS = RPS + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""


			cursor.execute(sql)
			db.commit()

		except Exception as e:
			print(e)

		log(discordID, spent, won, game)

		db.close()

def setup(bot):
	bot.add_cog(Totals(bot))