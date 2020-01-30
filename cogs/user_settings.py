import discord
from discord.ext import commands

import datetime

import json

class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True, pass_context=True)
	async def settings(self, ctx, game: str):
		# check if settings page exist
		# if not, input new user to data with default options

		game = game.lower()

		def is_me_reaction(reaction, user):
			return user == author

		def get_reaction(msg):
			try:
				await msg.add_reaction("1⃣") 
				await msg.add_reaction("2⃣")
				return await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
				return

		if game == "blackjack":
			# grab settings for blackjack
			msg = await ctx.send("Choose an option:")

			reaction, user = get_reaction(msg)

			if str(reaction) == "1⃣":
				pass
			elif str(reaction) == "2⃣":
				pass

			# react with emojis instead of entering numbers

		elif game == "roulette":
			# grab settings for roulette
			msg = await ctx.send("Choose an option:\n1) Simple Roulette (play each game with only using one command!)\n2) Set default bet")

			reaction, user = get_reaction(msg)

			if str(reaction) == "1⃣":
				pass
			elif str(reaction) == "2⃣":
				pass

		elif game == "fight":
			# grab settings for fight
			msg = await ctx.send("Choose an option:\n1) Send me DMs for the whole fighting log\n2) Confirm fight request automatically")

			reaction, user = get_reaction(msg)

			if str(reaction) == "1⃣":
				pass
			elif str(reaction) == "2⃣":
				pass

		else:
			raise Exception



	@user_settings.error
	async def user_settings_handler(self, ctx, error):
		embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
		embed.add_field(name = "`Syntax: $settings <game>`", value = "_ _", inline=False)
		embed.add_field(name="__Change the settings for one of the games.__", value = "_ _", inline=False)
		embed.add_field(name="__Possible games are blackjack, roulette, and fight__", value = "_ _", inline=False)
		await ctx.send(embed=embed)
		self.embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Settings")
		print(error)

def setup(bot):
	bot.add_cog(Settings(bot))

	# 	with open("settings.json", encoding="utf-8") as f:
	# 		userSettings = json.load(f)

	# 	found = None
	# 	for current_user in userSettings: # for every existing user that has been warned
	# 		if str(user.id) == current_user: # if warned user is current user in list
	# 			keys = list(userSettings[current_user].keys())
	# 			ID = str(len(keys) + 1)
	# 			userSettings[current_user][ID] = {
	# 				"reason": reason,
	# 				"time": x
	# 			}
	# 			found = True
	# 			break

	# 	if not found: # if user hasn't been warned before
	# 		userSettings[str(user.id)] = {
	# 			"1": {
	# 				"reason": reason,
	# 				"time": x
	# 			}
	# 		}