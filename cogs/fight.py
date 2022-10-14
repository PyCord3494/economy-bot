	# zipped in order: pTurn, pHealth, pArmor, pCheckArmor, pPotions
# pHealth represents users hp, default 100
# pArmor represents users armor, default 100
# pCheckArmor will see if the user has any armor left or if it's all gone
# pPotions is to heal once; will set to false once used
# pShields is a shield to block 1 attack; will set to false once used


import nextcord
from nextcord.ext import commands 
from nextcord import Interaction
from nextcord import FFmpegPCMAudio 
from nextcord import Member 
from nextcord.ext.commands import has_permissions, MissingPermissions

import asyncio
from random import randrange
from random import randint
from PIL import Image, ImageDraw, ImageFont, ImageOps

class Fight(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.embed = nextcord.Embed(color=0x24ecf7, title="Pit Boss' Wrestling | FIGHT!")
		self.p1Health, self.p2Health = 100, 100
		self.p1Armor, self.p2Armor = 100, 100
		self.p1CheckArmor, self.p2CheckArmor = True, True
		self.p1Potions, self.p2Potions = True, True
		self.p1Shields, self.p2Shields = True, True
		self.msg = ""
		self.playerSettings, self.oppoSettings = [None,  None]


	@nextcord.slash_command()
	async def fight(self, interaction:Interaction, *, member: nextcord.Member):

		if interaction.user == member:
			await interaction.response.send_message("Cannot challenge yourself!")
			return

		async def fetchSettings(user):
			userSettings = self.bot.get_cog("Settings").getUserSettings(user)
			return [userSettings[str(user.id)]["fight"]["Dms"], userSettings[str(user.id)]["fight"]["autoConfirm"]]

		author = interaction.user
		self.playerSettings = await fetchSettings(author)
		self.oppoSettings = await fetchSettings(member)

		if self.oppoSettings[1] != "\u2705": # if autoConfirm is not on
			await interaction.response.send_message(f"{member.mention}, you've been challenged by {author.mention}, do you accept? (Yes/No)")
		
			def is_me(m):
					return (m.author.id == member.id) and (m.content.lower() in ["yes", "no"])
			try:
				ans = await self.bot.wait_for('message', check=is_me, timeout=5) # waits for opponent's response
				ans = ans.content.lower() # grab the message object's contents in lowercase
			except asyncio.TimeoutError:
				raise Exception("timeoutError")

			if ans == "no":
				await interaction.response.send_message("Opponent has refused.")
				return

			elif ans == "yes":
				await interaction.response.send_message("Continuing.")

		try:
			p1Lvl = await self.bot.get_cog("XP").getLevel(author.id)
			p2Lvl = await self.bot.get_cog("XP").getLevel(member.id)
		except Exception as e:
			await interaction.response.send_message(f"User does not have an account. Error: {e}")
			return


		# listed in order: player health, armor, checkArmor, potions
		try:
			p1 = [self.p1Health, self.p1Armor, self.p1CheckArmor, self.p1Potions]
			p2 = [self.p2Health, self.p2Armor, self.p2CheckArmor, self.p2Potions]
			file = nextcord.File("images/map.png", filename="image.png")
			self.embed.set_image(url="attachment://image.png")
			await self.fighting(interaction, member, p1, p2)
		finally: 
			# reset all the variables
			self.embed = nextcord.Embed(color=0x24ecf7, title="Pit Boss' Wrestling | FIGHT!")
			self.p1Health, self.p2Health = 100, 100
			self.p1Armor, self.p2Armor = 100, 100
			self.p1CheckArmor, self.p2CheckArmor = True, True
			self.p1Potions, self.p2Potions = True, True
			self.p1Shields, self.p2Shields = True, True



	def firstTurn(self, p1Lvl, p2Lvl): # determines who goes first by comparing levels; lower level has priority
		if p1Lvl < p2Lvl:return False
		else:return True

	async def fighting(self, interaction:Interaction, member, p1, p2):
		turnNum = 0
		author = interaction.user
		while True:
			if turnNum % 2 == 0: # player 1's turn
				self.embed.color = nextcord.Color(0x007efd)
				player = [p1, author.name]
				opponent = [p2, member.name]

			else:  # player 2's turn
				self.embed.color = nextcord.Color(0xfd0006)
				player = [p2, member.name]
				opponent = [p1, author.name]

			act = randrange(100) # generate what they'll do on their turn
			if act <= 70: # 70% chance to attack; dmg amount based on generated num
				if opponent[0][1] > 0: # if armor exists
					opponent[0][1] -= act + 35

					if opponent[0][1] < 0: # if they do more dmg to armor than armor can handle
						self.embed.add_field(name="DAMAGE", value=f"{player[1]} broke {opponent[1]}\'s shield and damaged him for {opponent[0][1] * -1} damage!")
						opponent[0][0] += opponent[0][1] # take out hp for remaining dmg
						opponent[0][1] = 0 # set armor to 0 since armor can't be negative
					else:
						self.embed.add_field(name="DAMAGE", value=f"{player[1]} damaged {opponent[1]}\'s shield for {act + 35} damage!\nHe has {opponent[0][1]} armor left!")

				else:
					opponent[0][0] -= act + 20
					self.embed.add_field(name="DAMAGE", value=f"{player[1]} damaged {opponent[1]} for {act + 20} damage!\nHe has {opponent[0][0]} health left!")
				await asyncio.sleep(3)
			elif act > 70: # 30% chance to heal; heal amount based on generated #
				if player[0][3] > 0:
					player[0][3] -= 1
					player[0][0] += act
					self.embed.add_field(name="HEALED", value=f"{player[1]} healed for {act} health!\nHealth Remaining: {player[0][0]}\nPotions remaining: {player[0][3]}")
				else:
					self.embed.add_field(name="HEALED", value=f"{player[1]} tried to use a health potion, but realized he has none.")
				await asyncio.sleep(3)

			#print(act)
			users = [author, member]
			if turnNum % 2 == 0:
				await self.createImg(player, opponent)
			else:
				await self.createImg(opponent, player)


			if self.playerSettings[0] == "\u2705": # if Dms are on
				file = nextcord.File("images/mapUpdated.png", filename="image.png")
				self.embed.set_image(url="attachment://image.png")
				await author.send(file=file, embed=self.embed)
			if self.oppoSettings[0] == "\u2705": # if Dms are on
				file = nextcord.File("images/mapUpdated.png", filename="image.png")
				self.embed.set_image(url="attachment://image.png")
				await member.send(file=file, embed=self.embed)
			self.embed.clear_fields()

			turnNum += 1 # changes whose turn it is

			dead = self.checkGameOver(player, opponent)
			if dead:
				#print("broke")
				break # will break once player is dead

		await interaction.response.send_message(f"{dead} has been killed!")


	def checkGameOver(self, player, opponent): # checks if either player is dead
		if player[0][0] <= 0:
			return player[1]

		elif opponent[0][0] <= 0:
			return opponent[1]
		else:
			return None

	async def createImg(self, player, oppo):
		img = Image.open("images/map.png")

		leftPlayer = Image.open("images/subzero-left.png")
		img.paste(leftPlayer, (100, 190), leftPlayer)

		rightPlayer = Image.open("images/subzero-left.png")
		rightPlayer = ImageOps.mirror(rightPlayer)
		img.paste(rightPlayer, (475, 190), rightPlayer)

		font_type = ImageFont.truetype('arial.ttf',30)
		draw = ImageDraw.Draw(img)
		draw.text(xy=(125,80), text=f"{player[1]}\nArmor: {player[0][1]}\nHP: {player[0][0]}",fill=(255,255,255),font=font_type)
		draw.text(xy=(549,80), text=f"{oppo[1]}\nArmor: {oppo[0][1]}\nHP: {oppo[0][0]}",fill=(255,255,255),font=font_type)
		img.save("images/mapUpdated.png")



def setup(bot):
	bot.add_cog(Fight(bot))