import discord
from discord.ext import commands

import datetime

import json

class Warn(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True, pass_context=True)
	async def settings(self, ctx, game: str):
		with open("settings.json", encoding="utf-8") as f:
			userSettings = json.load(f)

		found = None
		for current_user in userSettings: # for every existing user that has been warned
			if str(user.id) == current_user: # if warned user is current user in list
				keys = list(userSettings[current_user].keys())
				ID = str(len(keys) + 1)
				userSettings[current_user][ID] = {
					"reason": reason,
					"time": x
				}
				found = True
				break

		if not found: # if user hasn't been warned before
			userSettings[str(user.id)] = {
				"1": {
					"reason": reason,
					"time": x
				}
			}