import discord
from discord.ext import commands
import utils
import pymysql
from discord.ext.commands import has_permissions, CheckFailure

class Warnings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	@has_permissions(administrator=True)
	async def warn(self, ctx, warn_user, *, reason):
		user = ctx.message.mentions[0];

		db = pymysql.connect(host="twister.hostingspark.net",port=3306, user="hostings_autop",passwd="pwqA!Pp9!1",db="hostings_botdatabase",autocommit=True)
		cursor = db.cursor()
		sql = f"""INSERT INTO Warnings(DiscordID, Reason)
				  VALUES ('{user.id}', '{reason}');"""
		cursor.execute(sql)
		db.commit()

		sql = f"""SELECT DiscordID, Reason
				  FROM Warnings
				  WHERE DiscordID = '{user.id}';"""
		cursor.execute(sql)
		db.commit()
		records = cursor.fetchall()
		db.close()

		num = len(records)

		#await ctx.send(user.mention + f", you've been warned for the following reason: {reason}" +
		#							   f"\nYou now have {num} warnings.")

		embed = discord.Embed(color=1768431, title=f"You've been warned!")
		embed.set_thumbnail(url=user.avatar_url)
		embed.add_field(name = "Reason:", value = f"**1)** {reason}", inline=False)
		if num > 1:
			prevWarnings = ""
			count = 2
			for x in records:
				prevWarnings += f"**{count})** {x[1]}\n"
				count += 1
			embed.add_field(name = "Previous Warnings:", value=f"{prevWarnings}")

		await ctx.send(content=f"{user.mention}:", embed=embed)




def setup(bot):
	bot.add_cog(Warnings(bot))
