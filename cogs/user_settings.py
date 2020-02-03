import discord
from discord.ext import commands

import datetime

import asyncio
import json

class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True, pass_context=True)
	async def settings(self, ctx, game: str):
		# check if settings page exist
		# if not, input new user to data with default options

		author = ctx.author
		game = game.lower()

		async def msgUser(ctx, msgString):
			try:
				if not isinstance(ctx.channel, discord.DMChannel):
					await ctx.send("Sending DM...")
				return await author.send(f"{msgString}")
			except discord.Forbidden:
				# await ctx.send("Your Discord settings do not allow me to DM you. Please change them and try again.")
				raise Exception("forbiddenError")

		def is_me_reaction(reaction, user):
			return user == author

		async def get_reaction(msg):
			try:
				await msg.add_reaction("1⃣") 
				await msg.add_reaction("2⃣")
				reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
				return reaction, user
			except asyncio.TimeoutError:
				raise Exception("timeoutError")

		with open("settings.json", encoding="utf-8") as f:
			userSettings = json.load(f)

		found = None
		for current_user in userSettings: # for every existing user
			if str(author.id) == current_user: # if user is found
				found = True
				break

		if not found: # if user not in list
			userSettings[str(author.id)] = {
				"blackjack": {
					"emojis": "❌",
					"pass": "✅"
				},
				"roulette": {
					"simple": "❌",
					"default": "N/A"
				},
				"fight": {
					"Dms:": "✅",
					"autoConfirm": "❌"
				}
			}

		with open("settings.json","w+") as f:
			json.dump(userSettings, f, indent=4)

		if game == "blackjack":
			# grab settings for blackjack
			with open("settings.json", encoding="utf-8") as f:
				userSettings = json.load(f)

			emojis = userSettings[str(author.id)]["blackjack"]["emojis"]
			placeholder = userSettings[str(author.id)]["blackjack"]["pass"]
			msgString = f"Choose an option:\n1) Use emojis instead of commands -- {emojis}\n2) placeholder -- {placeholder}"
			msg = await msgUser(ctx, msgString)

			reaction, user = await get_reaction(msg)

			await msg.delete()

			with open("settings.json", encoding="utf-8") as f:
				userSettings = json.load(f)

			if str(reaction) == "1⃣":
				if userSettings[str(author.id)]["blackjack"]["emojis"] == "\u274c": # check mark
					userSettings[str(author.id)]["blackjack"]["emojis"] = "\u2705"
					await author.send(f"New settings:\n1) Use emojis instead of commands -- ✅\n2) placeholder -- {placeholder}")
				else:
					userSettings[str(author.id)]["blackjack"]["emojis"] = "\u274c"
					await author.send(f"New settings:\n1) Use emojis instead of commands  ❌\n2) placeholder -- {placeholder}")


			elif str(reaction) == "2⃣":
				if userSettings[str(author.id)]["blackjack"]["pass"] == "\u274c": # check mark
					userSettings[str(author.id)]["blackjack"]["pass"] = "\u2705"
					await author.send(f"New settings:\n1) Use emojis instead of commands -- {emojis}\n2) placeholder -- ✅")
				else:
					userSettings[str(author.id)]["blackjack"]["pass"] = "\u274c"
					await author.send(f"New settings:\n1) Use emojis instead of commands  {emojis}\n2) placeholder -- ❌")

			with open("settings.json","w+") as f:
				json.dump(userSettings, f, indent=4)

			# react with emojis instead of entering numbers






		elif game == "roulette":
			simple = userSettings[str(author.id)]["roulette"]["simple"]
			default = userSettings[str(author.id)]["roulette"]["default"]
			msgString = f"Choose an option:\n1) Simple Roulette (play each game with only using one command!) -- {simple}\n2) Set default bet: {default}"
			msg = await msgUser(ctx, msgString)

			reaction, user = await get_reaction(msg)

			await msg.delete()

			with open("settings.json", encoding="utf-8") as f:
				userSettings = json.load(f)

			if str(reaction) == "1⃣":
				if userSettings[str(author.id)]["roulette"]["simple"] == "\u274c": # check mark
					userSettings[str(author.id)]["roulette"]["simple"] = "\u2705"
					await author.send(f"New settings:\n1) Use emojis instead of commands -- ✅\n2) placeholder -- {default}")
				else:
					userSettings[str(author.id)]["roulette"]["simple"] = "\u274c"
					await author.send(f"New settings:\n1) Use emojis instead of commands  ❌\n2) placeholder -- {default}")


			elif str(reaction) == "2⃣":
				if userSettings[str(author.id)]["roulette"]["default"] == "\u274c": # check mark
					userSettings[str(author.id)]["roulette"]["default"] = "\u2705"
					await author.send(f"New settings:\n1) Use emojis instead of commands -- {simple}\n2) placeholder -- ✅")
				else:
					userSettings[str(author.id)]["roulette"]["default"] = "\u274c"
					await author.send(f"New settings:\n1) Use emojis instead of commands  {simple}\n2) placeholder -- ❌")

			with open("settings.json","w+") as f:
				json.dump(userSettings, f, indent=4)












		elif game == "fight":
			with open("settings.json", encoding="utf-8") as f:
				userSettings = json.load(f)

			Dms = userSettings[str(author.id)]["fight"]["Dms"]
			autoConfirm = userSettings[str(author.id)]["fight"]["autoConfirm"]
			msgString = f"Choose an option:\n1) Send me DMs for the whole fighting log -- {Dms}\n2) Confirm fight request automatically -- {autoConfirm}"
			msg = await msgUser(ctx, msgString)

			reaction, user = await get_reaction(msg)

			await msg.delete()

			with open("settings.json", encoding="utf-8") as f:
				userSettings = json.load(f)

			if str(reaction) == "1⃣":
				if userSettings[str(author.id)]["fight"]["Dms"] == "\u274c": # check mark
					userSettings[str(author.id)]["fight"]["Dms"] = "\u2705"
					await author.send(f"New settings:\n1) Send me DMs for the whole fighting log -- ✅\n2) Confirm fight request automatically -- {autoConfirm}")
				else:
					userSettings[str(author.id)]["fight"]["Dms"] = "\u274c"
					await author.send(f"New settings:\n1) Send me DMs for the whole fighting log -- ❌\n2) Confirm fight request automatically -- {autoConfirm}")


			elif str(reaction) == "2⃣":
				if userSettings[str(author.id)]["fight"]["autoConfirm"] == "\u274c": # check mark
					userSettings[str(author.id)]["fight"]["autoConfirm"] = "\u2705"
					await author.send(f"New settings:\n1) Send me DMs for the whole fighting log -- {Dms}\n2) Confirm fight request automatically -- ✅")
				else:
					userSettings[str(author.id)]["fight"]["autoConfirm"] = "\u274c"
					await author.send(f"New settings:\n1) Send me DMs for the whole fighting log -- {Dms}\n2) Confirm fight request automatically -- ❌")

			with open("settings.json","w+") as f:
				json.dump(userSettings, f, indent=4)





		else:
			raise Exception


def setup(bot):
	bot.add_cog(Settings(bot))