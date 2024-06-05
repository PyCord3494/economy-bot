import nextcord
from nextcord.ext import commands, tasks
from nextcord import Interaction

from random import choice
import datetime
import cooldowns, emojis, config
from db import DB

class Codes(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.currCode = None
		self.reward = 10000

		self.codes = ["lazy", "flower", "explode", "celebrate", "decorate", "fire", 
				"party", "computer", "home", "garden", "menu", "background", 
				"secular", "message", "fur", "vote", "safety", "environment", 
				"worm", "butt", "primary", "structure", "statement", "look", "memory", 
				"mess", "noise", "track", "tasty", "salon", "favor", "particle", 
				"transparent", "reception", "other", "blind", "cabin", "wings", 
				"premature", "freedom", "language", "bomb", "defend", "hill", "nuclear", 
				"clique", "master", "clean", "growth", "cinema", "beautiful", "steel", "wine", 
				"bishop", "justice", "build", "normal", "temperature", "visit", "rush", "essay", 
				"beef", "chicken", "pork", "trick", "shock", "lean", "glance", "distance", "nature", 
				"patch", "season", "record", "polish", "lounge", "club", "bar", "point", "fair", 
				"frozen", "can", "van", "new", "obey", "object", "theme", "social", "network", "theory", "love", "birthday"]

		self.embed = nextcord.Embed(color=1768431, title=f"New Code")
	
	@commands.Cog.listener()
	async def on_ready(self):
		if not self.GetNewCode.is_running():
			await self.GetNewCode()
			self.GetNewCode.start()
	
	@tasks.loop(time=datetime.time(hour=12, minute=45))
	# @tasks.loop(seconds=30)
	async def GetNewCode(self):
		DB.delete("DELETE FROM Codes;")
		word = choice(self.codes).lower().strip()
		self.currCode = word
		chnl = self.bot.get_channel(config.channelIDForCodes)
		self.embed.description = f"Code is **{word}**"
		await chnl.send(embed=self.embed) 


	@nextcord.slash_command(description="Use a code for extra credits! Codes sent daily in support server")
	@cooldowns.cooldown(1, 2, bucket=cooldowns.SlashBucket.author, cooldown_id='code')
	async def code(self, interaction:Interaction, code:str):
		await interaction.response.defer(with_message=True)
		msg = await interaction.original_message()

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Codes")

		data = DB.fetchOne("SELECT * FROM Codes WHERE DiscordID = ?;", [interaction.user.id])

		if data:
			embed.description = "You have already claimed your reward for this code!"
		
		elif self.currCode is None:
			embed.description = "Code has expired! Please check later for new code"

		elif code.lower() != self.currCode:
			embed.description = "That code is invalid."
		
		else:
			DB.insert("INSERT INTO Codes VALUES(?)", [interaction.user.id])
			logID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, self.reward, activityName=f"Code {code}", amntBet=0)
			embed.description = f"Code redeemed! {self.reward:,}{emojis.coin} added."
			embed.set_footer(text=f"LogID: {logID}")

			
		await msg.edit(embed=embed)


def setup(bot):
	bot.add_cog(Codes(bot))