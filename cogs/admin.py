import nextcord
from nextcord.ext import commands, application_checks
from nextcord import Interaction

import math, datetime, cooldowns

import config, emojis
from db import DB, donators

from cogs.util import SendConfirmButton, IsDonatorCheck


def SentMaxAmount(amnt, halfAmnt:bool=False):
	if halfAmnt:
		return int(amnt) >= 200000
	else:
		return int(amnt) >= 450000



class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

	def isOwner(self, theid):
		return theid == config.botOwnerDiscordID
	
	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def select(self, interaction:Interaction, whattoselect,
		  table = nextcord.SlashOption(required=True, name="table", choices=("AchievementProgress", "ActiveBuffs", "Bounties", "Codes", "Crypto", "CryptoMiner", 
																	   "Donators", "Economy", "Guilds", "Inventory", "Items", 
																	   "Logs", "MinerBlocks", "MinerInventory", "Monopoly", 
																	   "MonopolyPeople", "Multipliers", "MultipliersPerm", "Prestige", "Quests", "RankedUsers", 
																	   "Settings", "Totals")),
		  conditions=None):
		if interaction.user.id != config.botOwnerDiscordID:
			await interaction.send("No.")
			return
		if conditions == None:
			sqlStatement = f"SELECT {whattoselect} FROM {table}"
		else:
			sqlStatement = f"SELECT {whattoselect} FROM {table} WHERE {conditions}"

		results = DB.fetchAll(sqlStatement)

		msg = ""
		for x in results:
			msg += f"{x}\n"

		await interaction.send(msg)
	
	@nextcord.slash_command()
	async def pay(self, interaction:Interaction, user: nextcord.Member, amnt):
		await self.send(interaction=interaction, user=user, amnt=amnt)
	
	@nextcord.slash_command()
	async def transfer(self, interaction:Interaction, user: nextcord.Member, amnt):
		await self.send(interaction=interaction, user=user, amnt=amnt)
	

	@nextcord.slash_command()
	@cooldowns.cooldown(1, 600, bucket=cooldowns.SlashBucket.author, cooldown_id='send1', 
					 check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id) and SentMaxAmount(kwargs['amnt']))
	@cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.author, cooldown_id='send2', 
					 check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id) and SentMaxAmount(kwargs['amnt'], True))
	@cooldowns.cooldown(4, 300, bucket=cooldowns.SlashBucket.author, cooldown_id='send3')
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='send4')
	async def send(self, interaction:Interaction, user: nextcord.Member, amnt:int):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Send")
		if interaction.guild_id not in [1207789281037516900, 821015960931794964, config.adminServerID, 1201596618496032930, 1166804572501721230, 1181383297310400572, 825179206958055425, 467084194200289280, 670038316271403021, 751429233049468960, 1057947351542669332, 1057947351542669332]:
			embed.description = "This command can only be used in [Donator](https://docs.justingrah.am/thecasino/donator) servers and the [Support Server](https://discord.gg/ggUksVN)."
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		if not await self.bot.get_cog("Economy").accCheck(user):
			embed.description = f"{user} has not registered. Cannot send money to them."
			await interaction.send(embed=embed, ephemeral=True)
			return
		

		amnt = await self.bot.get_cog("Economy").GetBetAmount(interaction, amnt)

		if amnt < 100:
			await interaction.send("You must send at least 100 coins")
			return
		
		# if donator sending or donator receiving
		if IsDonatorCheck(interaction.user.id) or IsDonatorCheck(user.id):
			if amnt > 5000000:
				embed.description = f"You can only send up to 5,000,000 {emojis.coin}"
				await interaction.send(embed=embed, ephemeral=True)
				cooldowns.reset_bucket(self.send.callback, interaction)
				return
			amntToReceive = math.floor(amnt * .90)
			tax = "10% tax"
		else:
			if amnt > 500000:
				embed.description = f"You can only send up to 500,000 {emojis.coin}"
				embed.set_footer(text=f"Donators can send/receive up to 5,000,000 credits!")
				await interaction.send(embed=embed, ephemeral=True)
				return
			# if support server
			if interaction.guild_id == config.adminServerID:
				amntToReceive = math.floor(amnt * .60)
				tax = "40% tax"
				embed.set_footer(text="Donator servers have 20% tax and donators have 10%!")
			# if donator server
			else:
				amntToReceive = math.floor(amnt * .80)
				tax = "20% tax"
				embed.set_footer(text="Donators have 10% tax, for sending and receiving!")
		if not await SendConfirmButton(interaction, f"They will only receive {amntToReceive:,}{emojis.coin} ({tax}). Proceed?"):
			embed.description = "You have cancelled this transaction."
			await interaction.send(embed=embed, ephemeral=True)
			cooldowns.reset_bucket(self.send.callback, interaction)
			return
		
		
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amnt):
			cooldowns.reset_bucket(self.send.callback, interaction)
			raise Exception("tooPoor")
		
		senderID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, 0, activityName=f"Sent to {user.id}", amntBet=amnt)
		# discordid, winnings, giveMultiplier=False, activityName=None, amntBet=None
		receiverID = await self.bot.get_cog("Economy").addWinnings(user.id, amntToReceive, activityName=f"Recieved from {interaction.user.id}", amntBet=0)

		embed.description = f"{interaction.user.mention} successfully sent {amnt:,}{emojis.coin}to {user.mention}! (Log ID: {senderID}\nAfter {tax}, they received {amntToReceive:,}{emojis.coin} (Log ID: {receiverID})"
		await interaction.send(embed=embed)
	
	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def info(self, interaction:Interaction, user: nextcord.Member):
		pass
	
	@info.subcommand()
	@application_checks.is_owner()
	async def view(self, interaction:Interaction, user: nextcord.Member):
		await interaction.response.defer(with_message=True)
		deferMsg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | User Info")

		registered = DB.fetchOne("SELECT DateTime FROM Logs WHERE Activity = 'Registered' AND DiscordID = ?;", [user.id])
		if registered:
			embed.add_field(name="Registered On", value=registered[0])
		
		top5 = DB.fetchAll("SELECT Activity, COUNT(*) as Amnt FROM Logs WHERE DiscordID = ? GROUP BY Activity order by Amnt DESC LIMIT 5;", [user.id])
		top5Msg = ""
		for data in top5:
			top5Msg += f"{data[0]} | {data[1]:,}\n"
		embed.add_field(name="Top 5 Activities", value=top5Msg)

		economyData = DB.fetchOne("SELECT Credits, Bank, TotalXP, Level FROM Economy WHERE DiscordID = ?;", [user.id])
		embed.add_field(name="Balance", value=f"{economyData[0]:,} | {economyData[1]:,}")
		embed.add_field(name="XP/Level", value=f"{economyData[2]:,} | {economyData[3]:,}")
	
		await deferMsg.edit(embed=embed)
	
	@info.subcommand()
	@application_checks.is_owner()
	async def activity(self, interaction:Interaction, user: nextcord.Member, amnt:int=10):
		topActivity = DB.fetchAll("SELECT Activity, COUNT(*) as Amnt FROM Logs WHERE DiscordID = ? GROUP BY Activity order by Amnt DESC LIMIT ?;", [user.id, amnt])

		topActivityMsg = ""
		for data in topActivity:
			topActivityMsg += f"{data[0]} | {data[1]:,}\n"
		await interaction.send(topActivityMsg)

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def delete(self, interaction:Interaction, user: nextcord.Member):
		if not await self.bot.get_cog("Economy").accCheck(user):
			await interaction.send("User not registered in system...")
			return

		DB.delete("DELETE FROM Inventory WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Totals WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM ActiveBuffs WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Crypto WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM CryptoMiner WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Economy WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM MinerInventory WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Monopoly WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM MonopolyPeople WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Multipliers WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Quests WHERE DiscordID = ?;", [user.id])
		DB.delete("DELETE FROM Guilds WHERE DiscordID = ?;", [user.id])

		await interaction.send("Deleted user.")

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def resetmultipliers(self, interaction:Interaction):
		DB.delete(f"DELETE FROM Multipliers;")
		await interaction.send(f"All multipliers have been reset.\nUpdated all rows.")


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def addmultiplier(self, interaction:Interaction, user:nextcord.Member, multiplier:float, duration:int):
		msg = self.bot.get_cog("Multipliers").addMultiplier(user.id, multiplier, datetime.datetime.now() + datetime.timedelta(seconds=duration))
		await interaction.send(msg)

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def getmultipliers(self, interaction:Interaction):
		multipliers = DB.fetchAll("SELECT DiscordID, Multiplier, Expires FROM Multipliers;", None)

		msg = "Multipliers are below:\n"
		for multiplier in multipliers:
			expireDate = datetime.datetime.strptime(multiplier[2], '%Y-%d-%m %H:%M:%S')
			multiplierValue = multiplier[1]
			if expireDate > datetime.datetime.now():
				seconds = (expireDate - datetime.datetime.now()).total_seconds()
				
				timeLeft = ""
				if seconds > 86400: # days
					timeLeft += f"{math.floor(seconds / 86400)} days "
					seconds = seconds % 86400
				if seconds > 3600: # hours
					timeLeft += f"{math.floor(seconds / 3600)} hours "
					seconds = seconds % 3600
				if seconds > 60: # minutes
					timeLeft += f"{math.floor(seconds / 60)} minutes "
					seconds = seconds % 60
				# seconds will now be the left over seconds
				seconds = round(seconds)
				timeLeft += f"{seconds} seconds"

				msg += f"ID: {multiplier[0]}'s expires at {expireDate}. {timeLeft} left. {multiplierValue}x multiplier\n"


		await interaction.send(msg)


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def servers(self, interaction:Interaction):
		await interaction.send(f"I am currently in {len(self.bot.guilds)} servers")

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def uses(self, interaction:Interaction):
		await interaction.response.defer(with_message=True)
		msg = await interaction.original_message()
		amnt = DB.fetchAll("select DateTime, Activity from logs;")

		totalUses = len(amnt) + 96934 + 1584255

		todaysUses = 0
		weeksUses = 0
		monthsUses = 0
		sixHourUses = 0
		hourUses = 0

		todayActivities = {}
		weeksActivities = {}

		registered = {}
		registered["day"] = 0
		registered["week"] = 0
		registered["month"] = 0
		
		for record in amnt:
			# print(record)
			dateStr = record[0]
			datetime_object = datetime.datetime.strptime(dateStr, '%b/%d/%y %H:%M:%S')
			
			diff = datetime.datetime.now() - datetime_object
			
			if diff.total_seconds() <= 2592000:
				monthsUses += 1
				if record[1] == "Registered":
					registered["month"] += 1

				if diff.total_seconds() <= 604800:
					weeksUses += 1
					if record[1] in weeksActivities:
						weeksActivities[record[1]] += 1
					else:
						weeksActivities[record[1]] = 1
					if record[1] == "Registered":
						registered["week"] += 1

					if diff.total_seconds() <= 86400:
						todaysUses += 1
						if record[1] in todayActivities:
							todayActivities[record[1]] += 1
						else:
							todayActivities[record[1]] = 1
						if record[1] == "Registered":
							registered["day"] += 1


						if diff.total_seconds() <= 21600:
							sixHourUses += 1
							if diff.total_seconds() <= 3600:
								hourUses += 1


		sortedTodayActivities = dict(sorted(todayActivities.items(), key=lambda item: item[1], reverse=True))
		todayActivitiesMsg = ""
		count = 1
		for key, val in sortedTodayActivities.items():
			todayActivitiesMsg += f"**{count})** {key} (**{val}** times)\n"

			count += 1
			if count == 6:
				break
		
		sortedWeekActivities = dict(sorted(weeksActivities.items(), key=lambda item: item[1], reverse=True))
		weekActivitiesMsg = ""
		count = 1
		for key, val in sortedWeekActivities.items():
			weekActivitiesMsg += f"**{count})** {key} (**{val}** times)\n"

			count += 1
			if count == 6:
				break

		
		text = f"I have been used:\n\t\t**{monthsUses}** times this month. ({registered['month']} new users)\n\
\t\t**{weeksUses}** times this week. ({registered['week']} new users)\n\t\t**{todaysUses}** times today. ({registered['day']} new users)\n\
\t\t**{sixHourUses}** times in the past 6 hours.\n\t\t**{hourUses}** times in the past hour.\n\
And in total, over **{totalUses:,}** times.\n\n\
Today's top uses:\n{todayActivitiesMsg}\n\n\
Week's top uses:\n{weekActivitiesMsg}\n\n"
		await msg.edit(content=text)

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def forcestart(self, interaction:Interaction, member: nextcord.Member):
		await self.bot.get_cog("Economy").StartPlaying(interaction, member)
		await interaction.send("User registered")

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def end(self, interaction:Interaction):
		await interaction.send("Shutting down... Goodbye.")
		await self.bot.close()


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def copy(self, interaction:Interaction, *, words):
		await interaction.channel.send(words) # send the message
		await interaction.response.defer(with_message=False)


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def addmoney(self, interaction:Interaction, user: nextcord.Member, amnt:int):
		await self.bot.get_cog("Economy").addWinnings(user.id, amnt)
		await interaction.send("Money added, Master.")


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def givexp(self, interaction:Interaction, user: nextcord.Member, xp:int):
		DB.update("UPDATE Economy SET XP = XP + ?, TotalXP = TotalXP + ? WHERE DiscordID = ?;", [xp, xp, user.id])
		await self.bot.get_cog("XP").levelUp(interaction, user.id) # checks if they lvl up
		await interaction.send(f"Added {xp} XP to {user.mention}")

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def givelevel(self, interaction:Interaction, user: nextcord.Member, level:int):
		await self.bot.get_cog("XP").addLevel(user.id, level) # checks if they lvl up
		await interaction.send(f"Added {level} levels to {user.mention}")

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def givedonator(self, interaction:Interaction, member: nextcord.Member): # grabs member from input
		if IsDonatorCheck(member.id):
			await interaction.send(f"{member.mention} is already a donator!")
			return

		await interaction.send(f"Thanks for donating {member.mention}! Giving you perks now.")
		donatorRole = nextcord.utils.get(interaction.guild.roles, name = "Donator")
		try:
			await member.add_roles(donatorRole)
		except:
			pass

		creditsGiven = 50000
		donatorReward = 5000
		await self.bot.get_cog("Economy").addWinnings(member.id, creditsGiven)

		DB.insert("INSERT INTO Donators(DiscordID, Level, DonatorReward) VALUES(?, ?, ?)", [member.id, 1, donatorReward])
		donators.append(str(member.id))
		

		await interaction.send(f"**Donator** role added\
\n{creditsGiven:,}{emojis.coin} added.\
\n{donatorReward:,}{emojis.coin} added to your Donator Reward\
\nGame cooldowns **removed**\
\n**Tripled** your daily reward\
\n**Doubled** your weekly reward\
\n**Doubled** your monthly reward\
\nGave you access to **/donator**\
\nSet your fee for **10%** to send/receive coins.\
\nMaximum coins you can send increased to 5,000,000{emojis.coin}\
\nReduced cooldown to send coins\
\nSet maximum bounty you can place to 1,000,000{emojis.coin}\
\n\n**Please provide <@547475078082985990> the server ID you'd like to allow /send to work in**")


	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def showallcommands(self, interaction:Interaction):
		msg = ""
		for cmd in self.bot.commands:
			if not cmd.description:
				msg += f"{cmd.name}\n"
		await interaction.send(msg)

def setup(bot):
	bot.add_cog(Admin(bot))
