import discord
from discord.ext import commands
import utils

class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# immediately stop the bot
	@commands.command(hidden = True)
	async def end(self, ctx):
		if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
			await self.bot.logout()

	@commands.command(hidden = True, aliases=['free', 'hmu', 'add', 'givemoney', 'give'])
	async def addmoney(self, ctx, user: str, amnt: int):
		if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
			await self.bot.get_cog("Economy").addWinnings(user, amnt)

	@commands.command(hidden = True)
	async def copy(self, ctx, *, words):
		if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
			await ctx.message.delete() # delete the original message
			await ctx.send(words) # send the message


def setup(bot):
	bot.add_cog(Admin(bot))
