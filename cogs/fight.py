# zipped in order: pTurn, pHealth, pArmor, pCheckArmor, pPotions
# pHealth represents users hp, default 100
# pArmor represents users armor, default 100
# pCheckArmor will see if the user has any armor left or if it's all gone
# pPotions is to heal once; will set to false once used
# pShields is a shield to block 1 attack; will set to false once used


import discord
from discord.ext import commands
import asyncio
from random import randrange
from random import randint

class Fight(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.embed = discord.Embed(color=0x24ecf7, title="Pit Boss' Wrestling | FIGHT!")
		self.p1Health, self.p2Health = 100, 100
		self.p1Armor, self.p2Armor = 100, 100
		self.p1CheckArmor, self.p2CheckArmor = True, True
		self.p1Potions, self.p2Potions = True, True
		self.p1Shields, self.p2Shields = True, True

	@commands.command(pass_context=True)
	async def fight(self, ctx, *, member: discord.Member):
		try:
			p1Lvl = await self.bot.get_cog("XP").getLevel(ctx.author.id)
			p2Lvl = await self.bot.get_cog("XP").getLevel(member.id)

			dmg = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
			p1Dmg = dmg[p1Lvl]
			p2Dmg = dmg[p2Lvl]
		except Exception as e:
			await ctx.send(f"User does not have an account. Error: {e}")


		# listed in order: player health, armor, checkArmor, potion
		try:
			p1 = [self.p1Health, self.p1Armor, self.p1CheckArmor, self.p1Potions]
			p2 = [self.p2Health, self.p2Armor, self.p2CheckArmor, self.p2Potions]

			#firstTurn = self.firstTurn(p1Lvl, p2Lvl)
			turnNum = 0
			while True:
				act = randint(1, 100) # generate what they'll do on their turn
				
				if turnNum % 2 == 0: # player 1's turn
					self.embed.color = discord.Color(0x007efd)
					player = p1
					pText = "Player 1"
					opponent = p2
					oText = "Player 2"

				else:  # player 2's turn
					self.embed.color = discord.Color(0xfd0006)
					player = p2
					pText = "Player 2"
					opponent = p1
					oText = "Player 1"

				if act <= 70: # 70% chance to attack; dmg amount based on generated #
					opponent[0] -= act
					self.embed.add_field(name="DAMAGE", value=f"{pText} damaged {oText} for {act} damage!\nHe has {opponent[0]} health left!")
					await asyncio.sleep(2)
				elif act > 70: # 30% chance to heal; heal amount based on generated #
					player[3] -= 1
					player[0] += act
					self.embed.add_field(name="HEALED", value=f"{pText} healed for {act} health!\nHealth Remaining: {player[0]}\nPotions remaining: {player[0]}")
					await asyncio.sleep(2)
				
				# sends embed and resets it for next turn
				await ctx.send(embed=self.embed)
				self.embed.clear_fields()

				turnNum += 1 # changes whose turn it is

				if self.checkGameOver(p1, p2):
					#print("broke")
					break # will break once player is dead
				await asyncio.sleep(2)

			await ctx.send("Someone died")

		finally: 
			# resets all the variables
			self.embed = discord.Embed(color=0x24ecf7, title="Pit Boss' Wrestling | FIGHT!")
			self.p1Health, self.p2Health = 100, 100
			self.p1Armor, self.p2Armor = 100, 100
			self.p1CheckArmor, self.p2CheckArmor = True, True
			self.p1Potions, self.p2Potions = True, True
			self.p1Shields, self.p2Shields = True, True



	def firstTurn(self, p1Lvl, p2Lvl): # determines who goes first by comparing levels; lower level has priority
		if p1Lvl < p2Lvl:return False
		else:return True

	def checkGameOver(self, p1, p2): # checks if either player is dead
		if p1[0] <= 0 or p2[0] <= 0:
			print(p1[0])
			print(p2[0])
			return True
		else:
			return False



def setup(bot):
	bot.add_cog(Fight(bot))