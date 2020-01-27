import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# immediately stop the bot
	@commands.command(hidden = True)
	@has_permissions(administrator=True)
	async def end(self, ctx):
		await self.bot.logout()

	@commands.command(hidden = True)
	@has_permissions(administrator=True)
	async def copy(self, ctx, *, words):
		await ctx.message.delete() # delete the original message
		await ctx.send(words) # send the message

	@commands.command(hidden = True, aliases=['free', 'hmu', 'add', 'givemoney', 'give'])
	@has_permissions(administrator=True)
	async def addmoney(self, user: str, amnt: int):
		await self.bot.get_cog("Economy").addWinnings(user, amnt)

	@commands.command(pass_context=True)
	@has_permissions(administrator=True)
	async def givexp(self, discordId: str, xp: int):
		db = pymysql.connect(host=config.host, port=3306, user=config.user, passwd=config.passwd, db=config.db, autocommit=True)
		cursor = db.cursor()
		sql = f"""Update Economy
				  SET XP = XP + {xp}, TotalXP = TotalXP + {xp}
				  WHERE DiscordID = '{discordId}';"""
		cursor.execute(sql)
		db.commit()
		await self.bot.get_cog("XP").levelUp(ctx, db, discordId) # checks if they lvl up
		db.close()

	@commands.command(hidden = True)
	@has_permissions(administrator=True)
	async def givedonator(self, ctx, *, member: discord.Member): # grabs member from input
		await ctx.send(f"Thanks for donating {member.mention}! Giving you perks now.")
		donatorRole = discord.utils.get(ctx.guild.roles, name = "Donator")
		await member.add_roles(donatorRole)
		await ctx.send(f"Donator role added.")
		await self.bot.get_cog("Economy").addWinnings(member.id, 5000)
		await ctx.send(f"5000 credits added.")



def setup(bot):
	bot.add_cog(Admin(bot))
