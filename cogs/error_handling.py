import asyncio
import discord
import sys
from discord.ext import commands

import datetime
import traceback
from difflib import get_close_matches


class ErrorHandling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		# Global error handling
		embed = discord.Embed(title="Vegas Lounge: ERROR", color=0xff0000)

		error = getattr(error, 'original', error)

		if isinstance(error, commands.CommandNotFound):
			print("g")
			lst = ["bal", "balance", "roulette", "crash", "blackjack", "slot", "slots", "crate", "coinflip", "credits", "top", "search", "daily", "rewards", "level", "shop", "transfer", "bank", "donator", "stats"]
		#	embed.description = "Command not found!"
			cmd = ctx.message.content.split()[0][1:]
			try:
				closest = get_close_matches(cmd.lower(), lst)[0]
			except IndexError:
				embed.description = f"`{cmd.lower()}` is not a known command."
			else:
				embed.description = f"`{cmd.lower()}` is not a command, did you mean `{closest}`?"


		elif isinstance(error, commands.MissingRequiredArgument):
			err = str(error.param)
			err = err.replace("_", " ")
			err = str(err.split(":")[0])

			firstChar = err[0]
			if firstChar.lower() in "aeiou" and err != "user":
				a_an = "an"
			else:
				a_an = "a"

			embed.description = f"Please specify {a_an} {err} for this command to work."

		elif isinstance(error, commands.TooManyArguments):
			embed.description = "You have tried using this command with too many arguments."

		elif isinstance(error, commands.CheckFailure):
			embed.description = "You do not have the required permissions to use this command."

		elif isinstance(error, commands.CommandOnCooldown):
			embed.description = "Command is on cooldown"

		elif isinstance(error, commands.BadArgument):
			embed.description = f"{error}"
		else:
			err = str(error)
			err = err.split(':', 2)[-1]
			
			if err == "forbiddenError":
				await ctx.send("Your Discord settings does not allow me to DM you. Please change them and try again.")
				return

			if err == "timeoutError":
				await ctx.send("Did not respond in time; timeout.")
				return


			# embed.description = f"Error: `{err}`. \nDeveloper has been contacted with all related details..."
			# e = discord.Embed(title='Command Error', colour=0xcc3366)
			# command_name = ctx.command.qualified_name
			# #if command_name: 
			# #	e.add_field(name='Name', value=ctx.command.qualified_name)
			# e.add_field(name='Author', value=f'{ctx.author} (ID: {ctx.author.id})')

			# fmt = f'Channel: {ctx.channel} (ID: {ctx.channel.id})'
			# if ctx.guild:
			# 	fmt = f'{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})'

			# e.add_field(name='Location', value=f"{fmt}]\n[Link]({ctx.message.jump_url})", inline=False)

			exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
			# e.description = f'```py\n{exc}\n```'
			# e.timestamp = datetime.datetime.utcnow()
			ch = self.bot.get_channel(648617998063763467)
			if len(exc) > 1999:
				await ch.send(f"{exc[:1999]}")
				await ch.send(f"{exc[1999:]}")
			else:
				await ch.send(f"{exc}")

			# await ch.send(embed=e)
			#await ctx.send(f"{error}  {ctx.command.qualified_name}")

		embed.set_thumbnail(url=ctx.author.avatar_url)
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(ErrorHandling(bot))
