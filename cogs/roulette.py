# economy-related stuff like betting and gambling, etc.

import discord
from discord.ext import commands
import pymysql
import asyncio
import random

class Roulette(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.previousNums = [""]
		self.coin = "<:coins:585233801320333313>"


	@commands.command(description="Play Roulette!", aliases=['russianroulette', 'r', 'rr', 'roulete', 'roullette', 'roullete'], pass_context=True)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def roulette(self, ctx):
		msg = ctx.message
		channel = msg.channel
		author = msg.author
		mention = author.mention

		numberBet = ""
		rangeBet = ""
		colorBet = ""
		parityBet = ""
		amntNumberBet = 0
		amntRangeBet = 0
		amntColorBet = 0
		amntParityBet = 0
		refund = 0
		displayNumberBet = ""
		displayRangeBet = ""
		displayColorBet = ""
		displayParityBet = ""
		moneyToAdd = 0
		amntLost = 0
		end = 0
		result = ""


		nums = ""
		numCount = 0
		for x in self.previousNums:
			if numCount == 0:
				nums += f"{x}"
			elif numCount % 2 == 1:
				nums += f" , {x}\n"
			elif numCount % 2 == 0:
				nums += f"{x}"

			numCount += 1	

		emojiNum = await self.getNumEmoji(ctx, numberBet)
		embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Roulette")
		embed.add_field(name = "Welcome to roulette, choose an option to bet on or choose start", value = "_ _", inline=True)
		embed.add_field(name = "Current picks:", value = f"Number bet: \nHigh/low bet: \nColor bet: \nParity bet: ", inline=True)
		embed.add_field(name = "Previous Numbers:", value = f"{nums}_ _", inline=True)
		#embed.add_field(name = "", value = "", inline=False)
		msg = await ctx.send(file=discord.File('images/roulette.png'), embed=embed)

		#await ctx.send(f"```Welcome to roulette, choose an option to bet on or choose start```\n\tCurrent picks:\n\t\t\tNumber bet: {str(numberBet)}\n\t\t\tHigh/low bet: {rangeBet}\n\t\t\tColor bet: {colorBet}\n\t\t\tParity bet: {parityBet}\n_ _")

		embedSelection = discord.Embed(color=1768431)

		while True:
			await self.addReactions(msg)

			def is_me(m):
				return m.author.id == author.id

			def is_me_reaction(reaction, user):
				return user == author

			try:
				reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
			except:
				embedError = await self.onTimeout(ctx, msg, amntNumberBet, amntRangeBet, amntColorBet, amntParityBet)
				await msg.edit(embed=embedError)
				await msg.clear_reactions()
				break
			else:
				await msg.clear_reactions()
				if str(reaction) == "🔢":
					embedSelection.clear_fields()
					embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value = f"Insert the number you'd like to bet on (0 - 36) and the amount of {self.coin} you're betting: \n*ex: typing 30 50\nwill bet 50{self.coin} on number 30*")
					await msg.edit(embed=embedSelection)
					try:
						numberBetMsg = await self.bot.wait_for('message', check=is_me, timeout=15)
					except asyncio.TimeoutError:
						await msg.edit(embed=embedError)
						await msg.clear_reactions()
						break
					else:
						numberBets = numberBetMsg.content.split()
						numberBet = int(numberBets[0])
						amntNumberBet = int(numberBets[1])
						if await self.bot.get_cog("Economy").subtractBet(ctx, amntNumberBet) != 0:
							await asyncio.sleep(0.5)
							await numberBetMsg.delete()
							emojiNum = await self.getNumEmoji(ctx, numberBet)
							displayNumberBet = f"{emojiNum}  {amntNumberBet}{self.coin}"
							if not(isinstance(numberBet, int)) or not(numberBet >= 0) or not(numberBet <= 36):
								embedSelection.clear_fields()
								embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value ="Incorrect number.")
								await msg.edit(embed=embedSelection)
								numberBet = ""
								amntNumberBet = 0
								await asyncio.sleep(2)

				if str(reaction) == "🔃":
					embedSelection.clear_fields()
					embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value ="Which would you like to bet on: high or low?")
					await msg.edit(embed=embedSelection)
					await self.addRangeReactions(msg)
					try:
						reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
					except asyncio.TimeoutError:
						await msg.edit(embed=embedError)
						await msg.clear_reactions()
						break
					else:
						if str(reaction) != "↩":
							await msg.clear_reactions()
							embedSelection.clear_fields()
							embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value = f"Insert how much you'd like to bet on {reaction}: ")
							await msg.edit(embed=embedSelection)
							try:
								amntRangeBetMsg = await self.bot.wait_for('message', check=is_me, timeout=15)
							except asyncio.TimeoutError:
								await msg.edit(embed=embedError)
								await msg.clear_reactions()
								break
							else:
								amntRangeBet = int(amntRangeBetMsg.content)
								if await self.bot.get_cog("Economy").subtractBet(ctx, amntRangeBet) != 0:
									await asyncio.sleep(0.5)
									await amntRangeBetMsg.delete()
									rangeBet = reaction
									displayRangeBet = f"{reaction}  {amntRangeBet}{self.coin}"
						else:
							rangeBet = ""
							await msg.clear_reactions()
				

				elif str(reaction) == "🏳️‍🌈":
					embedSelection.clear_fields()
					embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value ="Which would you like to bet on: black, red, or green?")
					await msg.edit(embed=embedSelection)
					await self.addColorReactions(msg)

					try:
						reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
					except asyncio.TimeoutError:
						await msg.edit(embed=embedError)
						await msg.clear_reactions()
						break
					else:
						if str(reaction) != "↩":
							await msg.clear_reactions()
							embedSelection.clear_fields()
							embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value = f"Insert how much you'd like to bet on {reaction}: ")
							await msg.edit(embed=embedSelection)
							try:
								amntColorBetMsg = await self.bot.wait_for('message', check=is_me, timeout=15)
							except asyncio.TimeoutError:
								await msg.edit(embed=embedError)
								await msg.clear_reactions()
								break
							else:
								amntColorBet = int(amntColorBetMsg.content)
								if await self.bot.get_cog("Economy").subtractBet(ctx, amntColorBet) != 0:
									await asyncio.sleep(0.5)
									await amntColorBetMsg.delete()
									colorBet = reaction
									displayColorBet = f"{reaction}  {amntColorBet}{self.coin}"
						else:
							colorBet = ""
							await msg.clear_reactions()
				

				elif str(reaction) == "➗":
					embedSelection.clear_fields()
					embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value ="Which would you like to bet on odd or even?")
					await msg.edit(embed=embedSelection)
					await self.addParityReactions(ctx, msg)
					
					try:
						reaction, user = await self.bot.wait_for('reaction_add', check=is_me_reaction, timeout=15)
					except asyncio.TimeoutError:
						await msg.edit(embed=embedError)
						await msg.clear_reactions()
						break
					else:
						if str(reaction) != "↩":
							await msg.clear_reactions()
							embedSelection.clear_fields()
							embedSelection.add_field(name = "Pit Boss' Casino | Roulette", value = f"Insert how much you'd like to bet on {reaction}: ")
							await msg.edit(embed=embedSelection)
							try:
								amntParityBetMsg = await self.bot.wait_for('message', check=is_me, timeout=15)
							except asyncio.TimeoutError:
								await msg.edit(embed=embedError)
								await msg.clear_reactions()
								break
							else:
								amntParityBet = int(amntParityBetMsg.content)
								if await self.bot.get_cog("Economy").subtractBet(ctx, amntParityBet) != 0:
									await asyncio.sleep(0.5)
									await amntParityBetMsg.delete()
									parityBet = reaction
									displayParityBet = f"{reaction}  {amntParityBet}{self.coin}"
						else:
							parityBet = ""
							await msg.clear_reactions()
				

				elif str(reaction) == "🏁":
#					if ready == 1:
					n = random.randrange(0, 36)
					#n = 0

					if n > 18: rangeResult = "⬆"
					else: rangeResult = "⬇"

					if n == 0: colorResult = "💚" #green
					elif n == 1 or n == 3 or n == 5 or n == 7 or n == 9 or n == 12 or n == 14 or n == 16 or n == 18 or n == 19 or n == 21 or n == 23 or n == 25 or n == 27 or n == 30 or n == 32 or n == 34 or n == 36:
						colorResult = "❤" # red
					else: colorResult = "🖤" #black

					if n % 2 == 0: parityResult = "2⃣"
					else: parityResult = "1⃣"

					emojiNum = await self.getNumEmoji(ctx, n)
					winnings = ""

					if numberBet == n:
						winnings += "\nYou guessed the number! You won 35x your bet!"
						await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntNumberBet*35)
						moneyToAdd += amntNumberBet*35

					if str(rangeBet) == rangeResult:
						winnings += "\nYou guessed the range! You won 2x your bet!"
						await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntRangeBet*2)
						moneyToAdd += amntRangeBet*2

					if str(colorBet) == colorResult and str(colorBet) != "💚":
						winnings += "\nYou guessed the color! You won 2x your bet!"
						await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntColorBet*2)
						moneyToAdd += amntColorBet*2
					elif str(colorBet) == colorResult and str(colorBet) == "💚":
						winnings += "\nYou guessed the color green! You won 35x your bet!"
						await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntColorBet*35)
						moneyToAdd += amntColorBet*35

					if str(parityBet) == parityResult:
						winnings += "\nYou guessed the parity! You won 2x your bet!"
						await self.bot.get_cog("Economy").addWinnings(ctx.author.id, amntParityBet*2)
						moneyToAdd += amntParityBet*2

					amntLost = amntNumberBet + amntRangeBet + amntColorBet + amntParityBet


					if moneyToAdd > amntLost:
						multiplier = await self.bot.get_cog("Economy").getMultiplier(ctx)
						result = f"You won a grand total of {moneyToAdd} (+{moneyToAdd * multiplier}){self.coin} after betting {amntLost}{self.coin}"
					elif moneyToAdd < amntLost:
						if moneyToAdd > 0:
							result = f"You won {moneyToAdd} (+0){self.coin} after betting {amntLost}{self.coin}"
						else:
							result = f"You lost {amntLost}{self.coin}"
					else:
						result = "You didn't lose or win anything!"

					balance = await self.bot.get_cog("Economy").getBalance(ctx)
					await self.bot.get_cog("Totals").addTotals(ctx, amntLost, moneyToAdd, 3)
					xp = random.randint(50, 500)
					embed.set_footer(text=f"Earned {xp} XP!")
					await self.bot.get_cog("XP").addXP(ctx, xp)

					embed.remove_field(0)
					embed.set_field_at(1, name="Outcome:", value=f"{msg.content}Number bet: {emojiNum}\nHigh/low bet: {rangeResult}\nColor bet: {colorResult}\nParity bet: {parityResult}")
					embed.add_field(name = "-----------------------------------------------------------------", 
									value = f"{winnings}\n{result}\n**Credits:** {balance}{self.coin}", inline=False)
					await msg.edit(embed=embed)
					if(len(self.previousNums) == 6): # display only 6 previous numbers
						self.previousNums.pop()
					self.previousNums.insert(0, f"{colorResult} {str(n)}") # insert the resulting color and number
					if self.previousNums[1] == "":
						self.previousNums.pop(1) # if there was no previous numbers
						
#				else:
#					await msg.edit(content="Roulette game ended; no bets were placed]")
					break

				await asyncio.sleep(0.5)
				embed = discord.Embed(color=1768431, title="Pit Boss' Casino | Roulette")
				embed.add_field(name = "Welcome to roulette, choose an option to bet on or choose start", value = "_ _", inline=True)
				embed.add_field(name = "Current picks:", value = f"Number bet: {displayNumberBet}\nHigh/low bet: {displayRangeBet}\nColor bet: {displayColorBet}\nParity bet: {displayParityBet}", inline=True)
				embed.add_field(name = "Previous Numbers:", value = f"{nums}_ _", inline=True)
				await msg.edit(embed=embed)

	async def onTimeout(self, ctx, msg, nBet, rBet, cBet, pBet):
		embedError = discord.Embed(color=1768431)
		embedError.add_field(name = "Pit Boss' Casino | Roulette", value = "Request timed out.", inline=False)
		refund = nBet + rBet + cBet + pBet
		if refund > 0:
			await self.bot.get_cog("Economy").addWinnings(ctx.author.id, refund)
			balance = await self.bot.get_cog("Economy").getBalance(ctx)
			embedError.add_field(name = "-----------------------------------------------------------------",
								 value = f"A refund has been issued!\nYou received your {refund}{self.coin}\n**Credits:** {balance}{self.coin}", inline=False)
		else:
			balance = await self.bot.get_cog("Economy").getBalance(ctx)
			embedError.add_field(name = "-----------------------------------------------------------------",
								 value = f"Your balance was not affected.\n**Credits:** {balance}{self.coin}", inline=False)

		return embedError

	async def addReactions(self, msg):
		await msg.add_reaction("🔢") # 2 tr
		await msg.add_reaction("🔃")
		await msg.add_reaction("🏳️‍🌈") # 3 l
		await msg.add_reaction("➗") # 4 mid
		await msg.add_reaction("🏁")

	async def addColorReactions(self, msg):
		await msg.add_reaction("🖤")
		await msg.add_reaction("❤")
		await msg.add_reaction("💚")
		await msg.add_reaction("↩")

	async def addRangeReactions(self, msg):
		await msg.add_reaction("⬆")
		await msg.add_reaction("⬇")
		await msg.add_reaction("↩")

	async def addParityReactions(self, ctx, msg):
		await msg.add_reaction("1⃣") 
		await msg.add_reaction("2⃣")
		await msg.add_reaction("↩") 

	async def getNumEmoji(self, ctx, num):
		if num == "":return ""
		elif num == 0:return "<:0_:585640351683969025>"
		elif num == 1:return "<:1:585592684710723598>"
		elif num == 2:return "<:2:585592684752666624>"
		elif num == 3:return "<:3:585592684740083713>"
		elif num == 4:return "<:4:585592684643745795>"
		elif num == 5:return "<:5:585592684769574931>"
		elif num == 6:return "<:6:585592684714917910>"
		elif num == 7:return "<:7:585592685126221824>"
		elif num == 8:return "<:8:585592684778094635>"
		elif num == 9:return "<:9_:585592878689157120>"
		elif num == 10:return "<:10:585592684761317376>"
		elif num == 11:return "<:11:585565283784065024>"
		elif num == 12:return "<:12:585595231223939082>"
		elif num == 13:return "<:13:585565282865512449>"
		elif num == 14:return "<:14:585565283792453652>"
		elif num == 15:return "<:15:585565283637264392>"
		elif num == 16:return "<:16:585565283679207474>"
		elif num == 17:return "<:17:585565283939385412>"
		elif num == 18:return "<:18:585565283834527874>"
		elif num == 19:return "<:19:585594924884426753>"
		elif num == 20:return "<:20:585565282681094163>"
		elif num == 21:return "<:21:585593632891863084>"
		elif num == 22:return "<:22:585593632858439710>"
		elif num == 23:return "<:23:585593633034600479>"
		elif num == 24:return "<:24:585593632917028865>"
		elif num == 25:return "<:25:585593632845987840>"
		elif num == 26:return "<:26:585594135705157632>"
		elif num == 27:return "<:27:585593633038663762>"
		elif num == 28:return "<:28:585593632892125204>"
		elif num == 29:return "<:29:585593632904577024>"
		elif num == 30:return "<:30:585593632560775169>"
		elif num == 31:return "<:31:585593632636272644>"
		elif num == 32:return "<:32:585593632854376448>"
		elif num == 33:return "<:33:585593632891863089>"
		elif num == 34:return "<:34:585593632850051110>"
		elif num == 35:return "<:35:585593631843549214>"
		elif num == 36:return "<:36:585593631881297939>"
		else: "error"


	# @roulette.error
	# async def roulette_handler(self, ctx, error):
	# 	embed = discord.Embed(color=1768431, title="Pit Boss Help Menu")
	# 	embed.add_field(name = "`Syntax: /roulette`", value = "_ _", inline=False)
	# 	embed.add_field(name = "__Play the Casino version of Roulette__", value = "_ _", inline=False)
	# 	await ctx.send(embed=embed)
	# 	print(error)


def setup(bot):
	bot.add_cog(Roulette(bot))