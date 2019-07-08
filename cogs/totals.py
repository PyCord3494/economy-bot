# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Totals(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, aliases=['profile', 'totals', 'me'])
	async def stats(self, ctx):
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		sql = f"""SELECT Paid, Won, Profit, Games, Slots, Blackjack, Crash, Roulette
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

		await ctx.send(embed=embed)



	async def addTotals(self, ctx, spent, won, game):
		profit = won - spent
		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()

		try:
			if game == 0:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Slots = Slots + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

				cursor.execute(sql)
				db.commit()

			elif game == 1:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Blackjack = Blackjack + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

				cursor.execute(sql)
				db.commit()

			elif game == 2:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Crash = Crash + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

				cursor.execute(sql)
				db.commit()

			elif game == 3:
				sql = f"""UPDATE Totals
						  SET Paid = Paid + {spent}, Won = Won + {won}, Profit = Profit + {profit}, Games = Games + 1, Roulette = Roulette + {profit}
						  WHERE DiscordID = '{ctx.author.id}';"""

				cursor.execute(sql)
				db.commit()

		except Exception as e:
			print(e)


		db.close()











def setup(bot):
	bot.add_cog(Totals(bot))