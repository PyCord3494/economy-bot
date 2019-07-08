import discord
from discord.ext import commands
import utils
import pymysql
import asyncio

class Shop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.items = [1000, 5000, 50000, 100000, 150000, 35000, 250000]


	@commands.group(invoke_without_command=True)
	async def shop(self, ctx):
		if ctx.invoked_subcommand is None:
			if utils.check_roles(["Donator"], [y.name for y in ctx.message.author.roles]):
				await ctx.send("```ML\nID            ITEMS                COST\n"
									+ "----------------------------------------\n"
									+ "1            1 crate               1,000\n"
									+ "2             1 key                5,000\n"
									+ "3        +1,000 to daily          50,000\n"
									+ "4       +500 to lvl reward       100,000\n"
									+ "5      +5,000 to vote reward     150,000\n"
									+ "6   +1.5x Profit on Future Games 300,000\n"
									+ "7     +2,500 to donator reward    35,000\n"
									+ "----------------------------------------\n"
									+ "Use +shop buy <id> <amount>\n```")

			else:
				await ctx.send("```ML\nID            ITEMS                COST\n"
									+ "----------------------------------------\n"
									+ "1           +1 crate               1,000\n"
									+ "2            +1 key                5,000\n"
									+ "3        +1,000 to daily          50,000\n"
									+ "4       +500 to lvl reward       100,000\n"
									+ "5      +5,000 to vote reward     150,000\n"
									+ "6   +1.5x Profit on Future Games 300,000\n"
									+ "----------------------------------------\n"
									+ "Use +shop buy <id> <amount>\n```")

	@shop.command()
	async def buy(ctx, ID: int, amnt: int):
		discordId = ctx.author.id
		cost = self.items[ID] * amnt
		balance = self.bot.get_cog("Economy").getBalance(ctx.author.id) > price
		if balance > price:
			await self.bot.get_cog("Economy").addWinnings(discordId, -(cost))
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()
			
			if ID == 1:
				pass

			elif ID == 2:
				pass

			elif ID == 3:
				sql = f"""UPDATE Economy
					  SET DailyReward = DailyReward + 1000
					  WHERE DiscordID = '{discordId}';"""
				cursor.execute(sql)
				db.commit()	

			elif ID == 4:
				sql = f"""UPDATE Economy
					  SET Multiplier = Multiplier + 2
					  WHERE DiscordID = '{discordId}';"""
				cursor.execute(sql)
				db.commit()	

			elif ID == 5:
				pass

			elif ID == 6:
				sql = f"""UPDATE Economy
					  SET Multiplier = Multiplier + 2
					  WHERE DiscordID = '{discordId}';"""
				cursor.execute(sql)
				db.commit()	

			elif ID == 7:
				sql = f"""UPDATE Economy
					  SET Multiplier = Multiplier + 2
					  WHERE DiscordID = '{discordId}';"""
				cursor.execute(sql)
				db.commit()				

			db.close()
		else:
			ctx.send(f"That will cost you {cost} credits, but you only have {balance} credits")


	@shop.command()
	async def sell(ctx, ID: int, amnt: int):
		await ctx.send("sold")



def setup(bot):
	bot.add_cog(Shop(bot))