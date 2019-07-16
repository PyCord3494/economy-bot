import discord
from discord.ext import commands
import asyncio
import channels
import users
from discord.ext.commands import has_permissions, CheckFailure


class Roles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	# assign roles based on adding a reaction
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if user.id == users.users_dict["Bot"]: # don't assign roles for BotName
			return
		if reaction.message.channel.id == channels.channel["roles"]: # check for right channel
			if reaction.emoji == "💸":
				add_role = discord.utils.get(user.guild.roles, name = "Buyer&Seller")
				await user.add_roles(add_role)
				await user.send("Buyer&Seller role added.")
			elif(str(reaction.emoji) == "🛍"):
				add_role = discord.utils.get(user.guild.roles, name = "Seller")
				await user.add_roles(add_role)
				await user.send("Seller role added.")
			elif(str(reaction.emoji) == "💰"):
				add_role = discord.utils.get(user.guild.roles, name = "Buyer")
				await user.add_roles(add_role)
				await user.send("Buyer role added.")
			elif(str(reaction.emoji) == "💼"):
				add_role = discord.utils.get(user.guild.roles, name = "Trader")
				await user.add_roles(add_role)
				await user.send("Trader role added.")
			elif(str(reaction.emoji) == "🚨"):
				add_role = discord.utils.get(user.guild.roles, name = "I<3Updates!")
				await user.add_roles(add_role)
				await user.send("I<3Updates! role added.")
			elif(str(reaction.emoji) == "🆓"):
				add_role = discord.utils.get(user.guild.roles, name = "I<3FreeStuff!")
				await user.add_roles(add_role)
				await user.send("I<3FreeStuff role added.")


	# remove roles based on removing a reaction
	@commands.Cog.listener()
	async def on_reaction_remove(self, reaction, user):
		if reaction.message.channel.id == channels.channel_dict["roles"]: # check for right channel
			if str(reaction.emoji) == "💸":
				remove_role = discord.utils.get(user.guild.roles, name = "Buyer&Seller")
				await user.remove_roles(remove_role)
				await user.send("Buyer&Seller role removed.")
			elif(str(reaction.emoji) == "🛍"):
				remove_role = discord.utils.get(user.guild.roles, name = "Seller")
				await user.remove_roles(remove_role)
				await user.send("Seller role removed.")
			elif(str(reaction.emoji) == "💰"):
				remove_role = discord.utils.get(user.guild.roles, name = "Buyer")
				await user.remove_roles(remove_role)
				await user.send("Buyer role removed.")
			elif(str(reaction.emoji) == "💼"):
				remove_role = discord.utils.get(user.guild.roles, name = "Trader")
				await user.remove_roles(remove_role)
				await user.send("Trader role removed.")
			elif(str(reaction.emoji) == "🚨"):
				remove_role = discord.utils.get(user.guild.roles, name = "I<3Updates!")
				await user.remove_roles(remove_role)
				await user.send("I<3Updates! role removed.")
			elif(str(reaction.emoji) == "🆓"):
				remove_role = discord.utils.get(user.guild.roles, name = "I<3FreeStuff!")
				await user.remove_roles(remove_role)
				await user.send("I<3FreeStuff! role removed.")


	@commands.command(pass_context = True)
	@has_permissions(administrator=True)
	async def update_roles(self, ctx):
		# delete existing messages
		channel = self.bot.get_channel(channels.channel["roles"]) # get the channel to clear the messages from
		i = 0
		async for message in channel.history():
			if i < (1):
				i += 1
				await message.delete()
		print("Roles channel cleared\n")

		# update the roles channel for autoroles
		embed1 = discord.Embed(title=f"Self-Assignable Role Menu", description=f"React to give yourself a role", color=1768431) # set up embed
		embed1.add_field(name = f"\u200b", value = f"""
			💸 : `Buyer & Seller`\n
			🛍 : `Seller`\n
			💰 : `Buyer`\n
			💼 : `Trader`\n
			🚨 : `Recieve Notifications / Updates`\n
			🆓 : `Access to Free Stuff Channel`""", inline=False)
		channel_roles = await channel.send(embed=embed1)
		# add the emojis to react with
		await channel_roles.add_reaction("💸")
		await channel_roles.add_reaction("🛍")
		await channel_roles.add_reaction("💰")
		await channel_roles.add_reaction("💼")
		await channel_roles.add_reaction("🚨")
		await channel_roles.add_reaction("🆓")

		# ❗ : `Access to Information Channels`\n


def setup(bot):
	bot.add_cog(Roles(bot))
