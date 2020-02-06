import discord
from discord.ext import commands

import datetime

import asyncio
import json

class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def getUserSettings(self, user):
		with open("settings.json", encoding="utf-8") as f:
			userSettings = json.load(f)

		found = None
		for current_user in userSettings: # for every existing user
			if str(user.id) == current_user: # if user is found
				found = True
				break

		if not found: # if user not in list
			userSettings[str(user.id)] = {
				"blackjack": {
					"emojis": "❌",
					"pass": "✅"
				},
				"roulette": {
					"simple": "❌",
					"default": "N/A"
				},
				"fight": {
					"Dms": "❌",
					"autoConfirm": "❌"
				}
			}

			with open("settings.json","w+") as f:
				json.dump(userSettings, f, indent=4)
		
		return userSettings

	@commands.group(invoke_without_command=True, pass_context=True)
	async def settings(self, ctx, game: str):
		# check if settings page exist
		# if not, input new user to data with default options

		author = ctx.author
		game = game.lower()

		async def msgUser(ctx, msgString):
			try:
				#if not isinstance(ctx.channel, discord.DMChannel):
				#	await ctx.send("Sending DM...")
				return await author.send(f"{msgString}")
			except discord.Forbidden:
				# await ctx.send("Your Discord settings do not allow me to DM you. Please change them and try again.")
				raise Exception("forbiddenError")



		def is_me_reaction(reaction, user):
			return user == author

		async def get_reaction(msg):
			await msg.add_reaction("1⃣") 
			await msg.add_reaction("2⃣")
			try:
				reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
				return reaction, user
			except asyncio.TimeoutError:
				raise Exception("timeoutError")

		async def switchEmojis(currSetting):
			if currSetting == "\u2705": # check mark
				return "\u274c", "\u274c"
			else: return "\u2705", "\u2705"
		
		userSettings = self.getUserSettings(ctx.author)

		if game == "blackjack":
			emojis = userSettings[str(author.id)]["blackjack"]["emojis"]
			placeholder = userSettings[str(author.id)]["blackjack"]["pass"]
			msg = await msgUser(ctx, f"Choose an option:\n1) Use emojis instead of commands -- {emojis}\n2) placeholder -- {placeholder}")

			reaction, user = await get_reaction(msg)

			await msg.delete()

			if str(reaction) == "1⃣": emojis, userSettings[str(author.id)]["blackjack"]["emojis"] = await switchEmojis(emojis)
			elif str(reaction) == "2⃣": placeholder, userSettings[str(author.id)]["blackjack"]["pass"] = await switchEmojis(placeholder)

			msg = await msgUser(ctx, f"New settings:\n1) Use emojis instead of commands  {emojis}\n2) placeholder -- {placeholder}")




		elif game == "roulette":
			simple = userSettings[str(author.id)]["roulette"]["simple"]
			default = userSettings[str(author.id)]["roulette"]["default"]
			msg = await msgUser(ctx, f"Choose an option:\n1) Simple Roulette (play each game with only using one command!) -- {simple}\n2) Set default bet: {default}")

			reaction, user = await get_reaction(msg)

			await msg.delete()

			if str(reaction) == "1⃣": simple, userSettings[str(author.id)]["roulette"]["simple"] = await switchEmojis(simple)
			elif str(reaction) == "2⃣": await ctx.send("Enter what to change the default bet to...")

			msg = await msgUser(ctx, f"New settings:\n1) Simple Roulette (play each game with only using one command!) -- {simple}\n2) Set default bet: {default}")




		elif game == "fight":
			Dms = userSettings[str(author.id)]["fight"]["Dms"]
			autoConfirm = userSettings[str(author.id)]["fight"]["autoConfirm"]
			msg = await msgUser(ctx, f"Choose an option:\n1) Send me DMs for the whole fighting log -- {Dms}\n2) Confirm fight request automatically -- {autoConfirm}")

			reaction, user = await get_reaction(msg)

			await msg.delete()

			if str(reaction) == "1⃣": 
				Dms, userSettings[str(author.id)]["fight"]["Dms"] = await switchEmojis(Dms)
			elif str(reaction) == "2⃣": 
				autoConfirm, userSettings[str(author.id)]["fight"]["autoConfirm"] = await switchEmojis(autoConfirm)


			msg = await msgUser(ctx, f"New settings:\n1) Send me DMs for the whole fighting log -- {Dms}\n2) Confirm fight request automatically -- {autoConfirm}")

		else:
			raise Exception

		with open("settings.json","w+") as f:
			json.dump(userSettings, f, indent=4)


def setup(bot):
	bot.add_cog(Settings(bot))