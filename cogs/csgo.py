# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class csgo(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['case', 'crate', 'csgo'], pass_context=True)
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def open(self, ctx):
		items = ["Bayonet", "Flip Knife", "Gut Knife", "Karambit", "M9 Bayonet", "Huntsman Knife", "Butterfly Knife", 
		"Falchion Knife", "Shadow Daggers", "Bowie Knife", "Ursus Knife", "Navaja Knife", "Stiletto Knife", "Talon Knife", 
		"CZ75-Auto", "Desert Eagle", "Dual Berettas", "Five-SeveN", "Glock-18", "P2000", "P228", "P250", "R8 Revolver", 
		"Tec-9", "USP-S", "M3", "MAG-7", "Nova", "Sawed-Off", "XM1014", "MAC-10", "MP5", "MP5-SD", "MP7", "MP9", "P90", 
		"PP-Bizon", "TMP", "UMP-45", "AK-47", "AUG", "FAMAS", "Galil", "M4A1", "M4A1-S", "M4A4", "SG 552", "SG 553", "AWP", 
		"G3SG1", "SCAR-20", "Scout", "SG 550", "SSG 08"]

		#items = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]
		embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Case Opening", type="rich")
		embed.add_field(name=":white_large_square::white_large_square::white_large_square::small_red_triangle_down::white_large_square::white_large_square::white_large_square:", value="_ _", inline=False)
		botMsg = await ctx.send(embed=embed)
		i = 0
		limit = 0
		random.shuffle(items)
		for index in range(len(items) - 1):
			if limit > 4:
				break
			if i == 0:
				embed.add_field(name=f"{str(items[index])}", value="_ _", inline=False)
				await botMsg.edit(embed=embed)
				i += 1
			elif i == 1:
				embed.set_field_at(1, name=f"{str(items[index])}\t\t\t\t\t{str(items[index - 1])}", value="_ _", inline=False)
				await botMsg.edit(embed=embed)
				i += 1
			elif i == 2:
				embed.set_field_at(1, name=f"{items[index]}\t\t\t\t\t{items[index - 1]}\t\t\t\t\t{str(items[index - 2])}", value="_ _", inline=False)
				await botMsg.edit(embed=embed)
				i += 1
			elif i > 2:
				embed.set_field_at(1, name=f"{items[index + 1]}\t\t\t\t\t{items[index]}\t\t\t\t\t{str(items[index - 1])}", value="_ _", inline=False)
				await botMsg.edit(embed=embed)
			await asyncio.sleep(0.5)
			limit += 1
		await ctx.send(f"Yay, you won {items[index - 1]}")

def setup(bot):
	bot.add_cog(csgo(bot))