import discord
from discord.ext import commands
import asyncio
from random import randrange
from random import randint

class Champion(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	



def setup(bot):
	bot.add_cog(Champion(bot))