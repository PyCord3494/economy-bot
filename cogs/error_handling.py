import discord
from discord.ext import commands
import math

class ErrorHandling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):

		# if command has local error handler, return
		if hasattr(ctx.command, "on_error"):
			print(0)
			return

		# get the original exception
		error = getattr(error, "original", error)


		ignored = (commands.CheckFailure, commands.DisabledCommand)
		if isinstance(error, ignored):
			print(f"Error occurred: {error}")
			return

		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(f"MissingRequiredArgument: {error}")

		elif isinstance(error, commands.TooManyArguments):
			await ctx.send(f"TooManyArguments: {error}")

		elif isinstance(error, commands.CommandNotFound):
			await ctx.send(f"Command not found: `{ctx.invoked_with}`")

		#elif isinstance(error, commands.TypeError):
		#	await ctx.send("Command not found.")

		elif isinstance(error, commands.CommandOnCooldown):
			# rounds to #.##
			await ctx.send("This command is on cooldown, retry in **{:0.2f}s**.".format(error.retry_after))
			return

		elif isinstance(error, commands.BadArgument):
			await ctx.send("Bad argument")

		elif isinstance(error, commands.UserInputError):
			await ctx.send(f"Input error: {error}")
			ctx.command.reset_cooldown(ctx)
			return

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send("This command cannot be used in direct messages.")
			except discord.Forbidden:
				pass
			return

def setup(bot):
	bot.add_cog(ErrorHandling(bot))