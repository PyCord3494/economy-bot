import discord
from discord.ext import commands
import utils
import pymysql
import asyncio

class Shop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.items = [1000, 5000, 50000, 100000, 150000, 250000, 35000]


	@commands.group(invoke_without_command=True, pass_context=True)
	async def shop(self, ctx):
		if ctx.invoked_subcommand is None:
			if self.bot.get_cog("Economy").isDonator(ctx.author.id) == 1:
				await ctx.send("```ML\nID            ITEMS                COST\n"
									+ "----------------------------------------\n"
									+ "1            1 crate               1,000\n"
									+ "2             1 key                5,000\n"
									+ "3        +1,000 to daily          50,000\n"
									+ "4       +500 to lvl reward       100,000\n"
									+ "5      ---------------------     150,000\n"
									+ "6   +1.5x Profit on Future Games 250,000\n"
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
									+ "5      ---------------------     150,000\n"
									+ "6   +50% Profit on Future Games 250,000\n"
									+ "----------------------------------------\n"
									+ "Use +shop buy <id> <amount>\n```")

	@shop.command()
	async def buy(ctx, ID: int, amnt: int):
		discordId = ctx.author.id
		cost = self.items[ID] * amnt
		balance = self.bot.get_cog("Economy").getBalance(ctx.author.id) > price
		if balance > price:
			if ID < 8 and ID > 0:
				await self.bot.get_cog("Economy").addWinnings(discordId, -(cost))
				db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
				cursor = db.cursor()
				
				if ID == 1:
					sql = f"""UPDATE Inventory
						  SET Crates = Crates + {amnt}
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()

				elif ID == 2:
					sql = f"""UPDATE Inventory
						  SET Keys = Keys + {amnt}
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()

				elif ID == 3:
					sql = f"""UPDATE Economy
						  SET DailyReward = DailyReward + 1000
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()	

				elif ID == 4:
					sql = f"""UPDATE Economy
						  SET LevelReward = LevelReward + 500
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()	

				elif ID == 5:
					pass

				elif ID == 6:
					sql = f"""UPDATE Economy
						  SET Multiplier = Multiplier + 0.5
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()	

				elif ID == 7 and await self.bot.get_cog("Economy").isDonator(discordId) == 1:
					sql = f"""UPDATE Economy
						  SET Multiplier = DonatorReward + 2500
						  WHERE DiscordID = '{discordId}';"""
					cursor.execute(sql)
					db.commit()	

				else:
					await ctx.send("Invalid choice.")	

			db.close()
		else:
			ctx.send(f"That will cost you {cost} credits, but you only have {balance} credits")


	@shop.command()
	async def sell(ctx, ID: int, amnt: int):
		await ctx.send("sold")

	@commands.group(pass_context=True)
	async def crate(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("$crate open *amnt*")


	@crate.command()
	async def open(self, ctx, amnt=1):
		crates, keys = await self.bot.get_cog("Economy").getInventory(ctx.author.id)
		if crates >= amnt and keys >= amnt:
			await ctx.send(f"Success\nkeys = {keys}\ncrates = {crates}")
		else:
			await ctx.send(f"{ctx.author.mention}, you only have {crates} crates and {keys} keys.\nType $crate to learn how to obtain more.")
		





def setup(bot):
	bot.add_cog(Shop(bot))