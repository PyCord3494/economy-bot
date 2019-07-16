import asyncio
import discord
from discord.ext import commands


class ErrorHandling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	async def on_error(self, event_method):
		print(f"Ignoring exception in {event_method}")

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""
		Catch command errors.
		"""
		if isinstance(error, type(None)):
			await ctx.send("yes")
		elif isinstance(error, commands.errors.NotOwner):
			await ctx.send(f"{error}", delete_after=5)
		elif isinstance(error, discord.errors.Forbidden):
			await ctx.send("I don't have permission to perform the action", delete_after=5)
		elif isinstance(error, commands.errors.CommandNotFound):
			await ctx.send("Command not found.")
		elif isinstance(error.__cause__, discord.errors.NotFound):
			await ctx.send("Error cause not found.")
		elif isinstance(error, commands.errors.NoPrivateMessage):
			await ctx.send("That command can not be run in PMs!",
								   delete_after=5)
			return
		elif isinstance(error, commands.errors.DisabledCommand):
			await ctx.send("Sorry, but that command is currently disabled!",
								   delete_after=5)
		elif isinstance(error, commands.errors.CheckFailure):
			await ctx.send("Check failed. You probably don't have "
								   "permission to do this.", delete_after=5)
		elif isinstance(error, commands.errors.CommandOnCooldown):
			await ctx.send(f"{error}", delete_after=5)
		elif isinstance(error, (commands.errors.BadArgument, commands.errors.MissingRequiredArgument)):
			await ctx.send(f"Bad argument: {' '.join(error.args)}", delete_after=5)
		#else:
		#	await ctx.send(f"An error happened. This has been logged and reported. Error: {error}",
		#						   delete_after=5)


def setup(bot):
	bot.add_cog(ErrorHandling(bot))
