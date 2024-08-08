import nextcord
from nextcord.ext import commands, application_checks
from nextcord import Interaction

from cooldowns import CallableOnCooldown, reset_bucket

import datetime
import traceback
from difflib import get_close_matches

import config, emojis


class ErrorHandling(commands.Cog):
	def __init__(self, bot:commands.bot.Bot):
		self.bot = bot
		bot.event(self.on_application_command_error)
	
	async def SendErrorToDiscordChannel(self, commandName, msg):
		ch = self.bot.get_channel(config.channelIDForErrors)
		for i in range(0, len(msg), 1995):
			await ch.send(msg[i:i + 1995])

		try:
			await ch.send(f"Further info\n{commandName} ")
		except Exception as e:
			await ch.send(f"error with further infooooo: {e}")
		

	# @commands.Cog.listener()
	async def on_application_command_error(self, interaction:Interaction, error):
		commandName = interaction.application_command.qualified_name.title()

		embed = nextcord.Embed(title=f"{self.bot.user.name} | {commandName} | ERROR", color=0xFF0000)
		error = getattr(error, 'original', error)

		if "missing permissions" in str(error).lower() or "send message" in str(error).lower() or "missing access" in str(error).lower():
			return

		elif isinstance(error, commands.CommandOnCooldown) or isinstance(error, CallableOnCooldown):
			if commandName.lower() in ["blackjack", "coinflip", "crash", "dond", "horse", "mines", "poker", "rps", "scratch", "slots"]:
				msg = f"{commandName} is on cooldown. Please retry again <t:{int(error.resets_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>\n[Donate](https://docs.justingrah.am/thecasino/donator) to have NO cooldowns on games!"
			else:
				msg = f"{commandName} is on cooldown. Please retry again <t:{int(error.resets_at.replace(tzinfo=datetime.timezone.utc).timestamp())}:R>"
				
			embed.description = msg
			embed.set_footer(text="See all your cooldowns with /cooldown")

		elif isinstance(error, commands.CheckFailure) or isinstance(error, application_checks.ApplicationNotOwner):
			try:
				await interaction.send(f"{error}")
			except Exception:
				pass
			return

		elif isinstance(error, commands.BadArgument):
			embed.description = f"{error}"
			try:
				reset_bucket(interaction.application_command.callback, interaction)
			except:
				pass

		else:
			err = str(error)
			err = err.split(':', 2)[-1]
			
			if err == "forbiddenError":
				embed.description = "Your Discord settings does not allow me to DM you. Please change them and try again."
				await emojis.SendInteractionWithStop(interaction, embed, True)
				return

			if err == "timeoutError":
				embed.description = f"Did not respond in time; timeout."
				await emojis.SendInteractionWithStop(interaction, embed, True)
				return

			if err == "valueError":
				embed.description = "Did not provide correct option. Please try again"
				await emojis.SendInteractionWithStop(interaction, embed, True)
				try:
					reset_bucket(interaction.application_command.callback, interaction)
				except:
					pass
				return

			if err == "itemNotFoundInInventory":
				embed.description = "You do not have that item in your inventory"
				await emojis.SendInteractionWithStop(interaction, embed, True)
				return

			if err == "tooPoor":
				embed.description = f"You do not have enough {emojis.coin} to do that (or you are trying to use an amount less than 1)"
				await emojis.SendInteractionWithStop(interaction, embed, True)
				try:
					reset_bucket(interaction.application_command.callback, interaction)
				except:
					pass
				return
			
			if err == "onlySupportServer":
				embed.description = f"You can only use that command in the Support Server.\n[Click Here]({config.serverInviteURL}) to join the Support Server"
				await emojis.SendInteractionWithStop(interaction, embed, True)
				try:
					reset_bucket(interaction.application_command.callback, interaction)
				except:
					pass
				return

			if "minBet" in err:
				embed.description = f"Minimum bet is {err[7:]} {emojis.coin}" 
				await emojis.SendInteractionWithStop(interaction, embed, True)
				# await interaction.send(embed=embed, ephemeral=True)
				try:
					reset_bucket(interaction.application_command.callback, interaction)
				except:
					pass
				return
			
			if "maxBet" in err:
				embed.description = f"Maximum bet is {int(err[7:]):,} {emojis.coin}" 
				await emojis.SendInteractionWithStop(interaction, embed, True)
				try:
					reset_bucket(interaction.application_command.callback, interaction)
				except:
					pass
				return

			if "lowLevel" in err:
				embed.description = f"You must be level {err[9:]} or higher to use this command!" 
				embed.set_footer(text="Check your progress in /level")
				await emojis.SendInteractionWithStop(interaction, embed, True)
				return

			exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
			try:
				exc = exc.split("kwargs)", 1)[1]
			except:
				pass

			await self.SendErrorToDiscordChannel(commandName, exc)


			embed.set_thumbnail(url=interaction.user.avatar)
			embed.set_footer(text=interaction.user)

			
			if "MySQL server" in exc:
				embed.description = "We're having difficulties connecting to the database... Apologies for the inconvenience... Please try again later!"
			else:
				embed.description = "An error has occured. The developers have been notified. Please try again later."


		try:
			await emojis.SendInteractionWithError(interaction, embed, True) 
		except Exception as e:
			pass

def setup(bot):
	bot.add_cog(ErrorHandling(bot))
