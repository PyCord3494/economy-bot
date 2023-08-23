import nextcord
from nextcord.ext import commands 
from nextcord import Interaction

import cooldowns
import json


class Vote(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.coin = "<:coins:585233801320333313>"

	@nextcord.slash_command(description="Vote")
	@commands.bot_has_guild_permissions(send_messages=True, embed_links=True, use_external_emojis=True)
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='vote')
	async def vote(self, interaction:Interaction):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Vote")
		embed.set_thumbnail(url=interaction.user.avatar)

		with open(r"votes.json", 'r') as f:
			votes = json.load(f)

		try:
			numOfVotes = votes[f"{interaction.user.id}"]
		except:
			embed.add_field(name="Links", value="1. [top.gg](https://top.gg/bot/585235000459264005/vote/)\n" + 
				"2. [discordbotlist](https://discordbotlist.com/bots/casino-bot/upvote)\n")
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

		moneyToAdd = 8500 * numOfVotes
		logID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, moneyToAdd, giveMultiplier=True, activityName=f"{numOfVotes} {voteMsg}", amntBet=0)
		self.bot.get_cog("Inventory").addItemToInventory(interaction.user.id, numOfVotes, 'Voter Chip')
				
		embed.add_field(name=f"Thanks for Voting {numOfVotes} {times}!", value=f"{moneyToAdd:,}{self.coin} has been added to your account and you received {numOfVotes} Voter {chip}!")
		embed.set_footer(text=f"/use to use your Voter Chip\nLog ID {logID}")
		msg = await interaction.send(embed=embed)
		msg = await msg.fetch()
		await msg.add_reaction("❤️")

		del votes[f"{interaction.user.id}"]
		with open(r"votes.json", 'w') as f:
			json.dump(votes, f, indent=4)

def setup(bot):
	bot.add_cog(Vote(bot))