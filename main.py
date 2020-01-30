import discord
from discord.ext import commands
import random
import asyncio
from discord.ext.commands import has_permissions
import time

import ztoken

bot = commands.Bot(command_prefix = "$")
bot.remove_command('help')
extensions = ["cogs.admin", "cogs.economy", "cogs.roulette", "cogs.coinflip", "cogs.slots", "cogs.ttt", "cogs.rps", "cogs.rewards", 
			  "cogs.bj", "cogs.crash", "cogs.xp", "cogs.totals", "cogs.error_handling", "cogs.shop", "cogs.fight", "cogs.user_settings"] # list of cogs to call
# took out "cogs.minesweeper"

# async def background_loop():
#     await bot.wait_until_ready()
#     while not bot.is_closed():
#         channels = [585234678106030083, 585234706568708106]
#         amnts = [10, 15, 20, 25, 30, 35, 50, 75, 100]
#         #time = [60, 120, 150, 180]
#         time = 10
#         channel = bot.get_channel(random.choice(channels))
#         amnt = random.choice(amnts)
#         coin = "<:coins:585233801320333313>"
#         await channel.send(f"A random treasure chest appears with {amnt}{coin}\nType $claim to grab it!", file=discord.File('crate.gif'))
#         def is_me(m):
#             return m.content == "claim" and m.channel == channel
#         crateClaim = await bot.wait_for('message', check=is_me, timeout=40)
#         await bot.get_cog("Economy").addWinnings(crateClaim.author.id, amnt)
#         balance = bot.get_cog("Economy").getBalance(crateClaim.author.id)
#         await channel.send(f"Congrats {crateClaim.author.mention}, you won {amnt}{coin}!\n**Credits:** {balance}{coin}")
#         # Type !claim to random.choice(messages))
#         await asyncio.sleep(100000)


@bot.event
async def on_ready():
	global LogFile

	LogFile = open("Logs.txt", "a")

	print(f"{bot.user.name} - {bot.user.id}")
	print(discord.__version__)
	print("Ready...")

# COMMAND LOGGER

#@bot.event 
#async def on_message(message):
#	if message.author.id != "585227426615787540" and message.content.startswith("$"):
#		localTime = time.asctime(time.localtime(time.time()))
#		LogFile.write(f"\n{message.author}:{message.guild}:{localTime}:{message.content}")
#		LogFile.flush()

@bot.command(pass_context=True)
async def help(ctx):
	embed = discord.Embed(color=1768431, title="Thanks for taking an interest in me!", footer="And that's all for now folks!")
	embed.add_field(name = ":game_die: Game commands", 
					 value="`roulette`, `crash`, `blackjack`, `slot`," 
						 + "`crate`, `coinflip`")

	embed.add_field(name = ":gear: Other commands",
				   value = "`credits`, `top`, `search`, `daily`, `rewards`, "
						 + "`level`, `shop`, `transfer`, `bank`, `donator`, `stats`")

	embed.add_field(name = "_ _",
					value = "Use **$help <command>**"
						  + "\nIf you want to support gambling bot's development [Donate on PayPal](https://www.paypal.me/AutopilotJustin)")
	await ctx.send(embed=embed)


	
# manually load a cog
@bot.command(hidden = True)
@has_permissions(administrator=True)
async def load(ctx, extension):
	try:
		bot.load_extension(extension)
		print(f"Loaded {extension}.\n")
	except Exception as error:
		print(f"{extension} could not be loaded. [{error}]")


# manually unload a cog
@bot.command(hidden = True)
@has_permissions(administrator=True)
async def unload(ctx, extension):
	try:
		bot.unload_extension(extension)
		print(f"Unloaded {extension}.\n")
	except Exception as error:
		print(f"{extension} could not be unloaded. [{error}]")


# manually reload a cog
@bot.command(hidden = True)
@has_permissions(administrator=True)
async def reload(ctx, extension):
	try:
		bot.reload_extension(extension)
		print(f"Reloaded {extension}.\n")
	except Exception as error:
		print(f"{extension} could not be reloaded. [{error}]")

if __name__ == '__main__':
	for extension in extensions:
		try:
			bot.load_extension(extension)
			print(f"Loaded cog: {extension}")
		except Exception as error:
			print(f"{extension} could not be loaded. [{error}]")
	# bot.loop.create_task(background_loop())
	bot.run(ztoken.token)
