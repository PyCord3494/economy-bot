import discord
from discord.ext import commands
import pymysql
import asyncio
import random
import channels

class UserManage(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	
	@commands.command()
	async def accept(self, ctx):
		if ctx.message.channel.id == channels.channel["verify"]:
			await asyncio.sleep(0.5)
			role = discord.utils.get(ctx.guild.roles, name = "Level 0")
			await ctx.message.author.add_roles(role) 
			await asyncio.sleep(0.5)
			role = discord.utils.get(ctx.guild.roles, name = "unverified")
			await ctx.message.author.remove_roles(role) 
			await ctx.message.delete()

			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()

			# ADD THEIR WALLET PROFILE
			sql_insert = f"""INSERT INTO Economy(DiscordID)
									VALUES ('{ctx.author.id}');"""
			cursor.execute(sql_insert)
			db.commit()

			# ADD THEIR TOTALS PROFILE
			sql_insert = f"""INSERT INTO Totals(DiscordID)
									VALUES ('{ctx.author.id}');"""
			cursor.execute(sql_insert)
			db.commit()

			db.close()


	@commands.Cog.listener()
	async def on_member_join(self, member):
		role = discord.utils.get(member.guild.roles, name = "unverified")
		await member.add_roles(role)
		new_member = await self.bot.fetch_user(member.id) 
		welcome_channel = self.bot.get_channel(channels.channel["join&leave"]) 
		try:
			await new_member.send(f"Hello and welcome to the Vegas Lounge. Please read the rules to learn how to verify yourself.")
		except: 
			print("User does not allow DMs from people in the server. Failed to send welcome message.")
		await welcome_channel.send(f"<@{new_member.id}>, welcome to the Vegas Lounge!")


	@commands.Cog.listener()
	async def on_member_remove(self, member):
		leaver = await self.bot.fetch_user(member.id) 
		welcome_channel = self.bot.get_channel(channels.channel["join&leave"]) 
		await welcome_channel.send(f"{leaver.name}#{leaver.discriminator} has escaped!")

		try:
			db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
			cursor = db.cursor()

			# REMOVE THEIR WALLET PROFILE
			sql_delete = f"""DELETE FROM Economy
									WHERE DiscordID = '{member.id}';"""
			cursor.execute(sql_delete)
			db.commit()

			# REMOVE THEIR TOTALS PROFILE
			sql_delete = f"""DELETE FROM Totals
									WHERE DiscordID = '{member.id}';"""
			cursor.execute(sql_delete)
			db.commit()

			db.close()
		except Exception as e:
			contactOwner = await self.bot.fetch_user("547475078082985990") 
			await contactOwner.send(e)


def setup(bot):
	bot.add_cog(UserManage(bot))