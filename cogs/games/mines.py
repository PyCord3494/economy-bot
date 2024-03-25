import nextcord
from nextcord.ext import commands
from nextcord import Interaction

import random, cooldowns

from db import DB
from cogs.util import GetMaxBet, IsDonatorCheck


class MinesButton(nextcord.ui.Button['MinesView']):
	def __init__(self, bot, x: int, y: int, value: int):
		super().__init__(style=nextcord.ButtonStyle.secondary, label='\u200b', row=y)
		self.bot:commands.bot.Bot = bot
		self.x = x
		self.y = y
		self.myvalue = value

	# This function is called whenever this particular button is pressed
	# This is part of the "meat" of the game logic
	async def callback(self, interaction: nextcord.Interaction):
		assert self.view is not None
		view: MinesView = self.view

		if view.gameover:
			return

		if self.view.ownerId != interaction.user.id:
			await interaction.send("This is not your game!", ephemeral=True)
			return
		# clicked already-revealed checkmark (to cashout)
		if self.emoji:
			currTimesAmnt = round(view.profit[view.spacesClicked-1], 2)
			currProfit = int(view.amntbet * currTimesAmnt)
			embed = nextcord.Embed(color=1768431, title=f"The Casino | Roobet Mines")
			# embed.description = f"Game finished.\nAmount won: {currProfit:,} ({currTimesAmnt:,}x)"
			await view.Gameover(interaction, embed, currProfit)
			return

		view.spacesClicked += 1
		currTimesAmnt = round(view.profit[view.spacesClicked-1], 2)
		currProfit = int(view.amntbet * currTimesAmnt)

		embed = nextcord.Embed(color=1768431, title=f"The Casino | Roobet Mines")
		msg = None
		# clicked bomb
		if self.myvalue == -1:
			embed.description = "Game finished."
			await view.Gameover(interaction, embed, 0)
			return
		else:
			self.emoji = '✅'
			self.style = nextcord.ButtonStyle.success

			# if revealed all good spaces, they win!
			if view.spacesClicked == view.totalChecks:
				# embed.description = f"Game finished.\nAmount won: {currProfit:,} ({currTimesAmnt:,}x)"
				await view.Gameover(interaction, embed, currProfit)
				return


		if not msg:
			nextTimesAmnt = round(view.profit[view.spacesClicked], 2)
			nextProfit = int(view.amntbet * nextTimesAmnt)
			msg = f"Current Profit to Withdraw: {(currProfit-view.amntbet):,} ({currTimesAmnt:,}x)\nNext Profit: {nextProfit-view.amntbet:,} ({nextTimesAmnt:,}x)"
			embed.set_footer(text="Click one of the checkmarks to withdraw your winnings")

		embed.description = msg
		# await interaction.response.edit_message(embed=embed, view=view)
		await view.msg.edit(embed=embed, view=view)


# This is our actual board View
class MinesView(nextcord.ui.View):
	def __init__(self, bot, msg:nextcord.Message, ownerId:int, mineCount:int, profit, amntbet, priorbal):
		super().__init__(timeout=None)
		# self.current_player = self.X
		self.board = [
			[0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0],
		]

		self.bot:commands.bot.Bot = bot
		
		self.msg = msg
		self.ownerId = ownerId
		self.mineCount = mineCount
		self.profit = profit
		self.amntbet = amntbet
		self.priorBal = priorbal
		self.totalChecks = len(self.board) * len(self.board[0]) - self.mineCount 
		self.spacesClicked = 0
		# prevent somehow calling gameover after game ended
		self.gameover = False

		while mineCount > 0:
			y = random.randint(0, len(self.board)-1) 
			x = random.randint(0, len(self.board[0])-1)
			if self.board[y][x] == 0:
				self.board[y][x] = -1
				mineCount-= 1

		for x in range(len(self.board)):
			for y in range(len(self.board[0])):
				self.add_item(MinesButton(self.bot, x, y, self.board[y][x]))

	# This method checks for the board winner -- it is used by the TicTacToeButton
	async def Gameover(self, interaction:Interaction, embed, moneyToAdd):
		self.gameover = True
		for child in self.children:
			child.disabled = True
			if child.myvalue == -1:
				child.emoji = "💣"
				child.style = nextcord.ButtonStyle.danger
			else:
				child.emoji = '✅'
				child.style = nextcord.ButtonStyle.success
		self.stop()

		gameID = await self.bot.get_cog("Economy").addWinnings(self.ownerId, moneyToAdd, giveMultiplier=True, activityName="Mines", amntBet=self.amntbet)
		
		embed, _ = await DB.addProfitAndBalFields(self, interaction, moneyToAdd-self.amntbet, embed)
		embed = await DB.calculateXP(self, interaction, self.priorBal, self.amntbet, embed, gameID)
		
		# await interaction.response.edit_message(embed=embed, view=self, file=file)
		await self.msg.edit(embed=embed, view=self)

		self.bot.get_cog("Totals").addTotals(interaction, self.amntbet, moneyToAdd, "Mines")

class Mines(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.profits = [
			[3311.01, 1.04, 1.08, 1.13, 1.20, 1.23, 1.37, 1.33, 1.38, 1.47, 1.60, 1.72, 1.83, 2.00, 2.25, 2.53, 2.80, 3.22, 3.70, 4.30, 6.00, 8.21, 12.33, 24.73],
			[1.03, 1.10, 1.20, 1.32, 1.43, 1.62, 1.82, 2.13, 2.44, 2.81, 3.23, 3.80, 4.50, 5.4, 6.6, 8.25, 10.61, 14.14, 19.80, 29.70, 49.50, 99, 297],
			[1.06, 1.25, 1.46, 1.71, 2.00, 2.35, 2.79, 3.35, 4.07, 5.00, 6.25, 7.96, 10.35, 13.80, 18.97, 27.11, 40.66, 65.06, 113.85, 227.70, 569.25, 2277],
			[1.10, 1.40, 1.70, 2.09, 2.58, 3.23, 4.09, 5.26, 6.88, 9.17, 12.51, 17.52, 25.30, 37.95, 59.64, 99.39, 178.91, 357.81, 834.90, 2504, 12523],
			[1.20, 1.55, 2.00, 2.58, 3.39, 4.52, 6.14, 8.50, 12.04, 17.52, 26.77, 40.87, 66.41, 113.85, 208.72, 417.45, 939.26, 2504, 8766, 52598],
			[1.26, 1.70, 2.34, 3.23, 4.52, 6.46, 9.44, 14.17, 21.89, 35.03, 58.38, 102.17, 189.75, 379.5, 834.9, 2087, 6261, 25047, 175329],
			[1.35, 1.90, 2.77, 4.09, 6.14, 9.44, 14.95, 24.47, 41.60, 73.95, 138.66, 277.33, 600.87, 1442, 3965, 13219, 59486, 475893],
			[1.40, 2.15, 3.34, 5.26, 8.50, 14.17, 24.47, 44.05, 83.20, 166.40, 356.56, 831.98, 2163, 6489, 23794, 118973, 1070759],
			[1.46, 2.44, 4.05, 6.88, 12.04, 21.89, 41.60, 83.20, 176.80, 404.10, 1010, 2828, 9193, 36773, 202254, 2022545],
			[1.56, 2.80, 5.00, 9.17, 17.52, 35.03, 73.95, 166.40, 404.10, 1077, 3232, 11414, 49031, 294188, 3236072],
			[1.62, 3.23, 6.24, 12.51, 26.27, 58.38, 138.66, 356.56, 1010, 3232, 12123, 56574, 367735, 4412826],
			[1.71, 3.78, 7.94, 17.652, 40.87, 102.17, 277.33, 813.98, 2828, 11314, 56574, 396022, 5146297],
			[1.86, 4.48, 10.34, 25.30, 66.41, 189.75, 600.87, 2163, 9193, 49031, 367735, 5148297],
			[2.00, 5.37, 13.80, 37.95, 113.85, 379.50, 1442, 6489, 36773, 294188, 4412826],
			[2.50, 6.57, 18.97, 59.64, 208.72, 834.90, 3965, 23794, 202254, 3236072],
			[2.75, 8.23, 27.11, 99.39, 417.45, 2087, 13219, 118973, 2022545],
			[3.09, 10.61, 40.66, 178.91, 939.26, 6281, 59486, 1070759],
			[3.54, 14.14, 65.06, 357.81, 2504, 25047, 475893],
			[4.12, 19.80, 113.85, 834.90, 8766, 175329],
			[4.95, 29.70, 222.70, 2504, 52598],
			[6.19, 49.50, 569.25, 12523],
			[8.25, 99, 2277],
			[12.38, 297],
			[24.75]
		]

	@nextcord.slash_command()
	async def mines(self, interaction:Interaction):
		pass

	@mines.subcommand()
	@cooldowns.cooldown(1, 9, bucket=cooldowns.SlashBucket.author, cooldown_id='mines', check=lambda *args, **kwargs: not IsDonatorCheck(args[1].user.id))
	async def start(self, interaction:Interaction, amntbet:int=nextcord.SlashOption(description="Enter the amount you want to bet. Minimum is 1000"), 
						  minecount:int = nextcord.SlashOption(required=True,name="minecount", choices=[x+1 for x in range(24)])):
		await interaction.response.defer()
		msgSent = await interaction.original_message()
		if amntbet < 1000:
			await msgSent.edit("Minimum bet is 1000")
			return
		
		if amntbet > GetMaxBet(interaction.user.id, "Mines"):
			raise Exception(f"maxBet {GetMaxBet(interaction.user.id, 'Mines')}")

		priorbal = await self.bot.get_cog("Economy").getBalance(interaction.user)
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amntbet):
			raise Exception("tooPoor")
		
		profit = self.profits[minecount-1]

		nextProfit = int(amntbet * profit[0])

		msg = f"Roobet Mines\nCurrent Profit to Withdraw: 0 (1.00x)\nNext Profit: {(nextProfit-amntbet):,} ({profit[0]:,}x)"
		embed = nextcord.Embed(color=1768431, title=f"The Casino | Roobet Mines", description=msg)
		await msgSent.edit(embed=embed, view=MinesView(self.bot, msgSent, interaction.user.id, minecount, profit, amntbet, priorbal))

	@mines.subcommand()
	async def profits(self, interaction: Interaction, minecount:int = nextcord.SlashOption(required=True,name="minecount", choices=[x+1 for x in range(24)])):
		profit = self.profits[minecount-1]
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Roobet Mines", description=f"Profit Table for {minecount} Mines")
		for i in range(len(profit)):
			embed.add_field(name=f"{i+1} Click", value=f"{profit[i]:,}x", inline=True)
		await interaction.send(embed=embed)


def setup(bot):
	bot.add_cog(Mines(bot))
