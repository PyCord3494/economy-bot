import discord
from discord.ext import commands
import utils
import pymysql
import asyncio
import config

class Shop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.items = [1000, 5000, 50000, 100000, 150000, 250000, 35000]


	@commands.group(invoke_without_command=True, pass_context=True)
	async def shop(self, ctx):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
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
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")
			return 0

	@shop.command()
	async def buy(self, ctx, ID: int, amnt: int):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
			discordId = ctx.author.id
			cost = self.items[ID - 1] * amnt
			balance = await self.bot.get_cog("Economy").getBalance(ctx)
			if balance >= cost:
				if ID <= 7 and ID > 0:
					await self.bot.get_cog("Economy").addWinnings(discordId, -(cost))
					db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
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


					db.close()
				else:
					await ctx.send("Invalid item ID.")
			else:
				await ctx.send(f"That will cost you {cost} credits, but you only have {balance} credits")
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")


	@shop.command()
	async def sell(ctx, ID: int, amnt: int):
		await ctx.send("sold")

	@commands.group(pass_context=True)
	async def crate(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("$crate open *amnt*")


	@crate.command()
	async def open(self, ctx, amnt=1):
		if await self.bot.get_cog("Economy").accCheck(ctx) == True:
			crates, keys = await self.bot.get_cog("Economy").getInventory(ctx)
			if crates >= amnt and keys >= amnt and amnt > 0:
				await self.bot.get_cog("Economy").subtractInv(ctx.author.id, amnt)
				crates = crates - amnt
				keys = keys - amnt
				balance = await self.bot.get_cog("Economy").getBalance(ctx)
				await ctx.send(f"You got **0** credits\nYou got **0** crates\nYou got **0** keys\n\nYou now have **{balance}** credits, **{rCrates}** crates, and **{rKeys}** keys")
			elif crates != False:
				await ctx.send(f"\n{ctx.author.mention}, you have {crates} crates and {keys} keys.\nType $crate to learn how to obtain more.")
		else:
			await ctx.send("Hello! Please type $start to create your wallet. :smiley:")
		





def setup(bot):
	bot.add_cog(Shop(bot))