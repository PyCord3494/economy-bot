# economy-related stuff like betting and gambling, etc.

import nextcord
from nextcord.ext import commands
from nextcord import Interaction

import cooldowns, random, math

import emojis
from db import DB
from cogs.totals import log
# from cogs.util import IsDonatorCheck
from cogs.util import IsDonatorCheck

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot


	@nextcord.slash_command()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author)
	async def start(self, interaction:Interaction):
		await self.StartPlaying(interaction, interaction.user)

	async def StartPlaying(self, interaction:Interaction, user:nextcord.Member=None):
		if not user:
			user = interaction.user 
		embed = nextcord.Embed(color=1768431, title=self.bot.user.name)
		embed.set_thumbnail(url=user.avatar)
		embed.set_footer(text=user)
		if await self.accCheck(user):
			embed.description = "You are already registered, silly"
			await interaction.send(embed=embed)
			return
		DB.insert('INSERT INTO Economy(DiscordID) VALUES (?);', [user.id])
		DB.insert('INSERT INTO Totals(DiscordID) VALUES (?);', [user.id])
		log(interaction.user.id, 0, 0, "Registered", 2500)

		self.bot.get_cog("DailyQuests").AssignQuestsToUser(user.id)

		embed.description = f"You are now successfully registered. Enjoy {self.bot.user.name}."

		# if interaction.application_command.qualified_name == 'start'
		# 	await interaction.send(embed=embed)
		# else

		img = nextcord.File("./images/logo.png", filename="logo.png")
		embed.set_thumbnail(url="attachment://logo.png")
		try:
			await interaction.send(embed=embed, file=img)
		except:
			try:
				await interaction.followup.send(embed=embed, file=img)
			except:
				pass

	async def GetBetAmount(self, interaction:Interaction, amntbet):
		if isinstance(amntbet, int):
			return amntbet
		if amntbet.isdigit():
			try:
				amnt = int(amntbet)
				return amnt
			except:
				pass
		if amntbet == "all" or amntbet == "allin" or amntbet == "everything":
			return await self.getBalance(interaction.user)
		if amntbet == "half":
			return math.floor(await self.getBalance(interaction.user) / 2)
		if amntbet == "third":
			return math.floor(await self.getBalance(interaction.user) / 3)
		if amntbet == "fourth":
			return math.floor(await self.getBalance(interaction.user) / 4)
		if "%" == amntbet[-1]:
			return math.floor(await self.getBalance(interaction.user) * (int(amntbet.replace('%','')) / 100))
		if "." in amntbet and amntbet[0] == "0":
			return math.floor(await self.getBalance(interaction.user) * float(amntbet))
		if "/" in amntbet:
			pos = amntbet.find("/")
			try:
				amnt = math.floor(await self.getBalance(interaction.user) * float(int(amntbet[:pos]) / int(amntbet[pos+1:])))
				return amnt
			except:
				pass
		raise commands.BadArgument(f'You entered {amntbet} for the amount you want to bet. Please enter a number instead.')

	@nextcord.slash_command()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='rewards')
	async def rewards(self, interaction:Interaction):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		dailyReward = await self.bot.get_cog("Daily").getDailyReward(interaction)
		multiplier, expiration = self.bot.get_cog("Multipliers").getMultiplierAndExpiration(interaction.user.id)

		embed = nextcord.Embed(color=1768431, title=self.bot.user.name)
		embed.add_field(name = "Daily", value = f"{dailyReward}{emojis.coin}", inline=True)
		embed.add_field(name = "Weekly", value = f"12,500{emojis.coin}", inline=True)
		embed.add_field(name = "Monthly", value = f"36,000{emojis.coin}", inline=True)
		embed.add_field(name = "Multiplier", value = f"{multiplier}x", inline=True)
		if expiration:
			embed.add_field(name = "Expires In", value=f"{expiration}", inline=True)


		# embed.add_field(name = "Weekly", value = f"12500{emojis.coin}", inline=False)
		# embed.add_field(name = "Monthly", value = f"36000{emojis.coin}", inline=True)

		if IsDonatorCheck(interaction.user.id):
			embed.add_field(name = "_ _\nDonator Reward", value = f"{self.getDonatorReward(interaction.user.id)}{emojis.coin}", inline=False)
		else:
			embed.add_field(name = "_ _\nDonator Reward", value = f"You are not a donator", inline=False)

		embed.set_footer(text="Don't forget to /work /vote /beg and /crime for extra credits")
		await deferMsg.edit(embed=embed)


	@nextcord.slash_command()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='balance')
	async def balance(self, interaction:Interaction, user:nextcord.Member=None):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431)
		if not user:
			user = interaction.user
			pronouns = "You"
		else:
			pronouns = "They"
			if not await self.accCheck(user):
				embed.description = "User has not registered yet. They need to use any command or type `/start` to register."
				await deferMsg.edit(embed=embed)
				return

		balance = await self.getBalance(user)
		cryptoBalances = DB.fetchAll(f"SELECT Name, Quantity FROM Crypto WHERE DiscordID = ?;", [user.id])
		# crates, keys = self.bot.get_cog("Inventory").getInventory(user)

		embed.add_field(name = "Credits", value = f"{pronouns} have **{balance:,}**{emojis.coin}", inline=False)

		if not cryptoBalances:
			embed.add_field(name="Crypto", value="You have no crypto.")
		else:
			for crypto in cryptoBalances:
				if crypto[0] == "Bitcoin":
					emoji = emojis.bitcoinEmoji
				elif crypto[0] == "Litecoin":
					emoji = emojis.litecoinEmoji
				elif crypto[0] == "Ethereum":
					emoji = emojis.ethereumEmoji
				
				embed.add_field(name=f"{crypto[0]} {emoji}", value=round(crypto[1], 2))

		# embed.add_field(name = "_ _\nCrates", value = f"{pronouns} have **{crates}** crates", inline=True)
		# embed.add_field(name = "_ _\nKeys", value = f"{pronouns} have **{keys}** keys", inline=True)
		embed.set_footer(text="Want easy money? Don't forget to check out your /rewards")
		
		await deferMsg.edit(embed=embed)
		
	@nextcord.slash_command()
	@cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author, cooldown_id='search')
	async def search(self, interaction:Interaction):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431)
		if await self.getBalance(interaction.user) < 300:
			amnt = random.randint(50, 250)
			await self.addWinnings(interaction.user.id, amnt)
			balance = await self.getBalance(interaction.user)
			
			embed.add_field(name = f"You found {amnt:,}{emojis.coin}", value = f"You have {balance:,}{emojis.coin}", inline=False)
		else:
			embed.add_field(name = f"Error", value = f"{interaction.user.mention}, you can only use this if you have less than 300{emojis.coin}.", inline=False)

		await deferMsg.edit(embed=embed)
		
	@nextcord.slash_command()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='freemoney')
	async def freemoney(self, interaction:Interaction):
		embed = nextcord.Embed(color=1768431, title=self.bot.user.name)
		embed.add_field(name="Free Money Commands", value="`/vote`\n`/search`\n`/daily`\n`/weekly`\n`/monthly`\n`/work`\n`/crime`\n`/beg`")
		await interaction.send(embed=embed)
	
	@nextcord.slash_command()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='donate')
	async def donate(self, interaction:Interaction):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Donate")
		embed.description = "[Perks & Information for Donating](https://docs.justingrah.am/thecasino/donator) \
			\n\nThere are multiple ways to donate. Please click your preferred one below: \
			\n[PayPal](https://www.paypal.com/paypalme/thecasinobot) | [Venmo](https://venmo.com/justinis235) | [CashApp](https://cash.app/$JNGraham)"
		embed.set_footer(text="You will need to join support server to receive perks if you donate!")
		await deferMsg.edit(embed=embed)


	@nextcord.slash_command()
	@cooldowns.cooldown(1, 86400, bucket=cooldowns.SlashBucket.author, cooldown_id='donator')
	async def donator(self, interaction:Interaction):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Donator")
		if not IsDonatorCheck(interaction.user.id):
			embed.description = "You must donate to gain access to this command!\nPlease read Donator Perks for more info\
\n[Donator Perks](https://docs.justingrah.am/thecasino/donator)\n[Donate Now](https://www.paypal.com/paypalme/thecasinobot)"
			embed.set_footer(text="You will need to join support server to receive perks if you donate!")
			await deferMsg.edit(embed=embed)
			return

		donatorReward = self.getDonatorReward(interaction.user.id)
		multiplier = self.bot.get_cog("Multipliers").getMultiplier(interaction.user.id)
		extraMoney = int(donatorReward * (multiplier - 1))
		logID = await self.addWinnings(interaction.user.id, donatorReward, giveMultiplier=True, activityName="Donator Reward", amntBet=0)

		balance = await self.getBalance(interaction.user)
		embed.add_field(name = f"You got {donatorReward:,} {emojis.coin}", 
						value = f"You have {balance:,} credits\nMultiplier: {multiplier}x\nExtra Money: {extraMoney:,}", inline=False)
		embed.set_footer(text=f"Log ID: {logID}")
		await deferMsg.edit(embed=embed)

	def getDonatorReward(self, discordid):
		donatorReward = DB.fetchOne("SELECT DonatorReward FROM Donators WHERE DiscordID = ?;", [discordid])
		if donatorReward:
			return donatorReward[0]
		return None


	async def subtractBet(self, user, amntbet): # subtracts the bet users place when they play games
		if not await self.accCheck(user):
			return False
		balance = await self.getBalance(user)
		if amntbet <= balance and amntbet > 0:
			DB.update("UPDATE Economy SET Credits = Credits - ? WHERE DiscordID = ?;", [amntbet, user.id])
			
			# add xp
			return True # return 1 if user has enough $$$ to bet their amount entered
		else:
			return False # return 0 if user trying to bet more $$$ than they have


	async def addWinnings(self, discordid, winnings, giveMultiplier=False, activityName=None, amntBet=None): # add the amount won 
		if winnings > 0 and giveMultiplier:
			multiplier = self.bot.get_cog("Multipliers").getMultiplier(discordid)
			if multiplier > 1:
				if amntBet > winnings: profitAmnt = amntBet - winnings
				else: profitAmnt = winnings - amntBet
				extraMoney = int(profitAmnt * (multiplier - 1))
				winnings += extraMoney
		if winnings != 0:
			DB.update("UPDATE Economy SET Credits = Credits + ? WHERE DiscordID = ?;", [round(winnings), discordid])

		gameID = None
		balance = DB.fetchOne("SELECT Credits FROM Economy WHERE DiscordID = ?;", [discordid])[0]
		if activityName and "Bought" in activityName: # if using shop
			gameID = log(discordid, winnings, 0, activityName, balance)
		elif activityName and amntBet != None:
			gameID = log(discordid, amntBet, winnings, activityName, balance)
			
		return gameID




	async def getBalance(self, user: nextcord.User):
		balance = DB.fetchOne("SELECT Credits FROM Economy WHERE DiscordID = ?;", [user.id])[0]
		return balance


	@nextcord.slash_command()
	async def leaderboard(self, interaction:Interaction, 
			   option = nextcord.SlashOption( required=False,name="option", choices=("Balance", "Level", "Profit", "Balance+Bank")), 
			   local = nextcord.SlashOption(required=False,name="local", choices=("local", "global"))):
		await self.top(interaction, option, local)

	@nextcord.slash_command()
	@cooldowns.cooldown(1, 15, bucket=cooldowns.SlashBucket.author, cooldown_id='top')
	async def top(self, interaction:Interaction, 
			   option = nextcord.SlashOption(
					required=False,
					name="option", 
					choices=("Balance", "Level", "Profit", "Balance+Bank")), 
				local = nextcord.SlashOption(
					required=False,
					name="local", 
					choices=("local", "global"))):
		await interaction.response.defer()
		deferMsg = await interaction.original_message()
		
		if not self.bot.get_cog("XP").IsHighEnoughLevel(interaction.user.id, 2):
			raise Exception("lowLevel 2")

		if option and option != "Balance":
			if option == "Level":
				sql = f"SELECT DiscordID, Level FROM Economy"
				orderBy = "Level"
			elif option == "Profit":
				sql = f"SELECT DiscordID, Profit FROM Totals"
				orderBy = "Profit"
			elif option == "Balance+Bank":
				sql = f"SELECT DiscordID, Credits+Bank as Balance FROM Economy"
				orderBy = "Balance"
		else:
			option = "Balance"
			sql = f"SELECT DiscordID, Credits FROM Economy"
			orderBy = "Credits"
		
		topUsers = ""
		count = 1
		if local == "global":
			sql += f" ORDER BY {orderBy} DESC LIMIT 10;"
			data = DB.fetchAll(sql)

		else:
			local = "local"
			data = DB.fetchAll(f"{sql} WHERE DiscordID IN (SELECT DiscordID FROM Guilds WHERE GuildID = '{interaction.guild.id}') ORDER BY {orderBy} DESC LIMIT 10;")


		for x in data: 
			user = await self.bot.fetch_user(x[0]) # grab the user from the current record
			topUsers += f"{count}. < {user.name} > - " + "{:,}".format(x[1]) + "\n"

			count += 1 # number the users from 1 - 10
		
		msg = ""
		if local == "local":
			msg = f"```MD\n{local.title()} Leaderboards Top 10 for {option}\n======\n{topUsers}```Use `/opt in` to add yourself to the local leaderboard"
		else:
			msg = f"```MD\n{local.title()} Leaderboards Top 10 for {option}\n======\n{topUsers}```"
		await deferMsg.edit(msg) # the list with the top 10


	@nextcord.slash_command()
	@cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author, cooldown_id='position')
	async def position(self, interaction:Interaction, usr: nextcord.Member=None, option = nextcord.SlashOption(
																required=False,
																name="option", 
																choices=("Balance", "Level", "Profit"))):
		await interaction.response.defer()
		deferMsg = await interaction.original_message()
		if not usr:
			usr = interaction.user

		if not self.bot.get_cog("XP").IsHighEnoughLevel(interaction.user.id, 2):
			raise Exception("lowLevel 2")

		if await self.getBalance(usr) < 5000:
			await deferMsg.edit("You need at least 5,000 credits to use this command.")
			return


		if option and option != "Balance":
			if option == "Level":
				sql = f"""SELECT Position from (SELECT ROW_NUMBER () OVER ( 
								ORDER BY Level DESC
							) Position, DiscordID
						  FROM Economy) WHERE DiscordID = ?;"""
			elif option == "Profit":
				sql = f"""SELECT Position from (SELECT ROW_NUMBER () OVER ( 
								ORDER BY Profit DESC
							) Position, DiscordID
						  FROM Totals) WHERE DiscordID = ?;"""
		else:
			sql = f"""SELECT Position from (SELECT ROW_NUMBER () OVER ( 
								ORDER BY Credits DESC
							) Position, DiscordID
						  FROM Economy) WHERE DiscordID = ?;"""
		
		position = DB.fetchOne(sql, [usr.id])[0]

		await deferMsg.edit(f"You are in position #{position}") # list with the top 10


	async def accCheck(self, user):
		# checks if they already have a wallet in database
		userAcc = DB.fetchOne("SELECT 1 FROM Economy WHERE DiscordID = ?;", [user.id])
		if userAcc: # getRow will not be None if account is found, therefor return True
			return True
		
		return False

	async def notEnoughMoney(self, interaction:Interaction):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | {str(interaction.application_command.qualified_name).title()}")
		embed.set_thumbnail(url=interaction.user.avatar)
		embed.add_field(name="ERROR", value="You do not have enough credits to do that or you are trying to bet an amount less than 1.")

		embed.set_footer(text=interaction.user)

		await interaction.send(embed=embed)


def setup(bot):
	bot.add_cog(Economy(bot))