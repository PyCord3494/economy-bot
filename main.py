import discord
from discord.ext import commands
import random
import utils
import asyncio


bot = commands.Bot(command_prefix = "$")
bot.remove_command('help')
extensions = ["cogs.user_manage", "cogs.roles", "cogs.admin", "cogs.economy", "cogs.roulette", "cogs.coinflip", "cogs.slots", "cogs.ttt",
              "cogs.rps", "cogs.rewards", "cogs.bj", "cogs.csgo", "cogs.crash", "cogs.xp", "cogs.totals", "cogs.shop", "cogs.warnings"] # list of cogs to call
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
    print(f"{bot.user.name} - {bot.user.id}")
    print(discord.__version__)
    print("Ready...")


@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(color=1768431, title="Thanks for taking an interest in me!", footer="And that's all for now folks!")
    embed.add_field(name = ":game_die: Game commands", 
                     value="`roulette`, `crash`, `lower`, `blackjack`, `slot`, `roulette`, " 
                         + "`poker`, `crate`, `connect4`, `coinflip`, `highlow`, `scratch`, "
                         + "`tictactoe`, `horse`, `minesweeper`, `jackpot`, `crypto`, `fight`")

    embed.add_field(name = ":gear: Other commands",
                   value = "`credits`, `top`, `search`, `daily`, `vote`, `rewards`, "
                         + "`level`, `shop`, `transfer`, `bank`, `donator`, `stats`")

    embed.add_field(name = "_ _",
                    value = "Use **+help <command>**"
                          + "\nIf you need help or have questions Join official server"
                          + "\nAdd to your server - Click here"
                          + "\nIf you want to support gambling bot's development [Donate on PayPal](https://www.paypal.me/AutopilotJustin)")
    await ctx.send(embed=embed)


    
# manually load a cog
@bot.command(hidden = True)
async def load(ctx, extension):
    if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
        try:
            bot.load_extension(extension)
            print(f"Loaded {extension}.\n")
        except Exception as error:
            print(f"{extension} could not be loaded. [{error}]")


# manually unload a cog
@bot.command(hidden = True)
async def unload(ctx, extension):
    if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
        try:
            bot.unload_extension(extension)
            print(f"Unloaded {extension}.\n")
        except Exception as error:
            print(f"{extension} could not be unloaded. [{error}]")


# manually reload a cog
@bot.command(hidden = True)
async def reload(ctx, extension):
    if utils.check_roles(["Admins"], [y.name for y in ctx.message.author.roles]): # check the user has the required role
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
    bot.run("NTg1MjI3NDI2NjE1Nzg3NTQw.XPWZpQ.GxYOpdP2MeLwN9BFhsxMo9kbqOs")
