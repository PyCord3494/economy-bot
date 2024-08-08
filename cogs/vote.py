import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

from PIL import Image
import cooldowns, json, io

import emojis


class Vote(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

	@nextcord.slash_command(description="Vote")
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, use_external_emojis=True, add_reactions=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='vote')
	async def vote(self, interaction:Interaction):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Vote")

		with open(r"votes.json", 'r') as f:
			votes = json.load(f)

		try:
			numOfVotes = votes[f"{interaction.user.id}"]
		except:
			embed.add_field(name="Links", value="1. [top.gg](https://top.gg/bot/585235000459264005/vote/)\n" + 
				"2. [discordbotlist](https://discordbotlist.com/bots/casino-bot/upvote)\n")
			embed.set_footer(text="Use the /vote command again\nafter voting to receive your perks!")
			await interaction.send("You have not voted yet.", embed=embed)
			return

		if numOfVotes == 1: 
			times = "Time"
			voteMsg = "Vote"
			chip = "Chip"
		else: 
			times = "Times"
			voteMsg = "Votes"
			chip = "Chips"
		
		del votes[f"{interaction.user.id}"]
		with open(r"votes.json", 'w') as f:
			json.dump(votes, f, indent=4)

		moneyToAdd = 8500 * numOfVotes
		logID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName=f"{numOfVotes} {voteMsg}", amntBet=0)
		self.bot.get_cog("Inventory").addItemToInventory(interaction.user.id, numOfVotes, 'Voter Chip')
				
		embed.add_field(name=f"Thanks for Voting {numOfVotes} {times}!", value=f"{moneyToAdd:,}{emojis.coin} has been added to your account and you received {numOfVotes} Voter {chip}!")
		embed.set_footer(text=f"/use to use your Voter Chip\nLog ID {logID}")

		img = nextcord.File("./images/wumpus/thanks.png", filename="vote.png")
		embed.set_thumbnail(url="attachment://vote.png")
		msg = await interaction.send(embed=embed, file=img)
		msg = await msg.fetch()
		await msg.add_reaction("❤️")

		await self.bot.get_cog("DailyQuests").UpdateUserQuestProgress(interaction, [("Vote for the bot", 1)])

def setup(bot):
	bot.add_cog(Vote(bot))