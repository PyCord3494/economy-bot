import nextcord
from nextcord.ext import commands, tasks, application_checks
from nextcord import Interaction

import cooldowns, json, math, asyncio, random, sqlite3

import config, emojis
from db import DB
from cogs.util import PrintProgress, IsDonatorCheck

from datetime import datetime, date, timedelta, time


class DailyQuests(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.questList = None
		self.AssignDailyQuests.start()

	def cog_unload(self):
		self.AssignDailyQuests.cancel()
	
	async def GameEndCheckDailyQuests(self, interaction:Interaction, gameResult: dict):
		quest_updates = [("Play games", 1)]

		gameName = gameResult["Name"]
		amntBet = gameResult["AmntBet"]
		amntWon = gameResult["AmntWon"]

		profit = amntWon - amntBet

		if amntBet == 0: # playing roulette without betting; don't add quest progress for
			return

		# Generic
		quest_updates.append((f"Play games", 1))
		quest_updates.append((f"Bet in games", amntBet))

		if amntBet > 5000:
			quest_updates.append(("Bet over 5000 in a game", 1))

		# Specific game-based
		quest_updates.append((f"Play games in {gameName}", 1))
		quest_updates.append((f"Bet in games of {gameName}", amntBet))

		if profit > 0:
			# Generic
			quest_updates.append(("Profit in games", profit))
			quest_updates.append(("Win games", 1))

			# Specific game-based
			quest_updates.append((f"Profit in {gameName}", profit))
			quest_updates.append((f"Win games in {gameName}", 1))

		# Update the quests for the user
		await self.UpdateUserQuestProgress(interaction, quest_updates)

	@tasks.loop(time=time(hour=5, minute=0))
	async def AssignDailyQuests(self):
		batch_size = 1000  # Adjust the batch size based on your system's capability

		try:
			with sqlite3.connect(config.db) as conn:
				cursor = conn.cursor()
				
				# Delete all previous quests
				cursor.execute("DELETE FROM DailyQuestsUserProgress")
				conn.commit()

				# Fetch all quests once and store them in self.quests
				cursor.execute("SELECT QuestID FROM DailyQuests")
				self.questList = [row[0] for row in cursor.fetchall()]
				
				# Fetch the total number of users
				cursor.execute("SELECT COUNT(DiscordID) FROM Economy")
				total_users = cursor.fetchone()[0]
				num_batches = math.ceil(total_users / batch_size)

				for batch in range(num_batches):
					offset = batch * batch_size
					cursor.execute("SELECT DISTINCT DiscordID FROM Economy LIMIT ? OFFSET ?", (batch_size, offset))
					users = cursor.fetchall()
					
					for user in users:
						discordID = user[0]
						self.AssignQuestsToUser(discordID, cursor=cursor)
					
					conn.commit()
					# Optional: add a delay to avoid hitting rate limits or overwhelming the database
					await asyncio.sleep(0.01)  # Adjust the sleep time based on your system's needs
		except Exception as e:
			print(f"An error occurred: {e}")
		
	def AssignQuestsToUser(self, discordID, cursor=None):
		if self.questList is None:
			print("No Daily Quests have been created... none will be assigned.")
			return  # Ensure quests are loaded before attempting to assign them
		if IsDonatorCheck(discordID):
			chosen_quest_ids = random.sample(self.questList, 5)
		else:
			chosen_quest_ids = random.sample(self.questList, 3)

		# if cursor:
		quest_progress_entries = [(discordID, quest_id, 0) for quest_id in chosen_quest_ids]

		# Perform the bulk insert
		if cursor:
			cursor.executemany(
				"""INSERT INTO DailyQuestsUserProgress (DiscordID, QuestID, Progress) 
				VALUES (?, ?, ?)""",
				quest_progress_entries
			)
		else:
			# Otherwise, create a new connection and cursor
			with sqlite3.connect(config.db) as conn:
				cursor = conn.cursor()
				quest_progress_entries = [(discordID, quest_id, 0) for quest_id in chosen_quest_ids]

				# Perform the bulk insert
				cursor.executemany(
					"""INSERT INTO DailyQuestsUserProgress (DiscordID, QuestID, Progress) 
					VALUES (?, ?, ?)""",
					quest_progress_entries
				)
				conn.commit()

	@nextcord.slash_command(name='dailyquests')
	async def DailyQuests(self, interaction: Interaction):
		discordID = str(interaction.user.id)
		with sqlite3.connect(config.db) as conn:
			cursor = conn.cursor()
			cursor.execute(
				"""
				SELECT dq.QuestName, dq.QuestGoal, dqup.Progress 
				FROM DailyQuestsUserProgress dqup 
				JOIN DailyQuests dq ON dqup.QuestID = dq.QuestID 
				WHERE dqup.DiscordID = ?
				""",
				(discordID,)
			)
			quests = cursor.fetchall()
			if not quests:
				await interaction.send("No quests assigned.")
				return

			# Create an embed object
			embed = nextcord.Embed(
				title="Daily Quests",
				color=0x00ff00  # You can choose a different color if you like
			)

			# Add each quest to the embed
			for quest in quests:
				quest_name, quest_goal, progress = quest
				embed.add_field(
					name=quest_name,
					value=f"{await PrintProgress(progress/quest_goal, True)} {progress}/{quest_goal}",
					inline=False
				)
			
			# Set footer
			if not IsDonatorCheck(discordID):
				embed.set_footer(text="/donate to receive 5 quests!")

		# Send the embed message
		await interaction.send(embed=embed)

	async def UpdateUserQuestProgress(self, interaction:Interaction, quest_progress_list):
		discordID = interaction.user.id
		completed = False
		completedQuests = list()
		with sqlite3.connect(config.db) as conn:
			cursor = conn.cursor()

			# Fetch all quest names the user currently has
			cursor.execute(
				"""
				SELECT dq.QuestName
				FROM DailyQuestsUserProgress dqup
				JOIN DailyQuests dq ON dqup.QuestID = dq.QuestID
				WHERE dq.QuestGoal != dqup.Progress AND dqup.DiscordID = ? 
				""",
				(discordID,)
			)
			# Convert to a set for fast lookup
			user_quests = {row[0] for row in cursor.fetchall()} 

			# Filter the quest_progress_list to only include quests the user has
			filtered_quest_progress_list = [
				(quest_name, progress_increment)
				for quest_name, progress_increment in quest_progress_list
				if quest_name in user_quests
			]

			# iterate through and progress the user's quests
			for quest_name, progress_increment in filtered_quest_progress_list:
				# get the quest to compare progress + progress_increment to goal
				cursor.execute(
					"""
					SELECT dq.QuestGoal, dq.Reward, dqup.Progress
					FROM DailyQuestsUserProgress dqup
					JOIN DailyQuests dq ON dqup.QuestID = dq.QuestID
					WHERE dqup.DiscordID = ? AND dq.QuestName = ?
					""",
					(discordID, quest_name)
				)
				result = cursor.fetchone()
				# this should never occur
				if not result:
					continue

				quest_goal, reward, current_progress = result
				new_progress = current_progress + progress_increment

				if new_progress >= quest_goal:
					# Quest is completed
					cursor.execute(
						"""
						UPDATE DailyQuestsUserProgress
						SET Progress = ?
						WHERE DiscordID = ? AND QuestID = (
							SELECT QuestID FROM DailyQuests WHERE QuestName = ?
						)
						""",
						(quest_goal, discordID, quest_name)
					)
					completed = True
					completedQuests.append((quest_name, reward))
					# await self.reward_user(discordID, reward)  # Make sure reward_user is an async function
				else:
					# Quest is not yet completed
					cursor.execute(
						"""
						UPDATE DailyQuestsUserProgress
						SET Progress = ?
						WHERE DiscordID = ? AND QuestID = (
							SELECT QuestID FROM DailyQuests WHERE QuestName = ?
						)
						""",
						(new_progress, discordID, quest_name)
					)
			conn.commit()

		if completed:
			questsCompletedMsg = ""
			totalReward = 0
			for quest in completedQuests:
				questsCompletedMsg += quest[0] + "\n"
				totalReward += quest[1]

			logID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, totalReward, giveMultiplier=True, activityName="Daily Quest", amntBet=0)
			
			# Create an embed object
			embed = nextcord.Embed(
				title="Daily Quest Completed",
				color=0x00ff00  # You can choose a different color if you like
			)
			embed.description = questsCompletedMsg
			embed.set_footer(text=f"Log ID: {logID}")
			
			embed, file = await DB.addProfitAndBalFields(self, interaction, totalReward, embed, calculateRankedCP=False)
			
			await interaction.send(embed=embed, file=file)
			file.close()



	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def forcereloaddailyquests(self, interaction:Interaction):
		await self.AssignDailyQuests()
		await interaction.send("Reloaded!", ephemeral=True)
		

def setup(bot):
	bot.add_cog(DailyQuests(bot))
