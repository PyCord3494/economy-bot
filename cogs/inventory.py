import nextcord
from nextcord.ext import commands, menus, application_checks
from nextcord import Interaction
from nextcord.ui import Select

from random import randint, choice, choices
import datetime
from cooldowns import cooldown, SlashBucket

import config, emojis
from db import DB, allItemNamesList, usableItemNamesList, highestRarity, allItems

class MySource(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=5)

	async def format_page(self, menu, entries):
		embed = nextcord.Embed(color=1768431, title=f"The Casino | Inventory")

		for x in range(0, len(entries)):
									# Item, Quantity, Type, Description
			embed.add_field(name=f"{entries[x][0]} {entries[x][4]}  (Amount: {entries[x][1]})", value=entries[x][3], inline=False)
		
		embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")

		return embed

class Inventory(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

	@nextcord.slash_command(guild_ids=[config.adminServerID])
	@application_checks.is_owner()
	async def giveitem(self, interaction:Interaction, 
		    user: nextcord.Member,
			itemselected: str,
			amnt: int=1):
		
		itemselected = DB.fetchOne("SELECT Name FROM Items WHERE Name LIKE ?;", [itemselected])

		if not itemselected:
			await interaction.send("Item could not be found.")
			return
		
		itemselected = itemselected[0]

		self.addItemToInventory(user.id, amnt, itemselected)
		await interaction.send(f"{amnt} {itemselected} given to {user}")


	@nextcord.slash_command()
	@cooldown(1, 5, bucket=SlashBucket.author)
	async def inventory(self, interaction:Interaction):
		inventory = self.getAllInventory(interaction.user)

		if not inventory:
			embed = nextcord.Embed(color=1768431, title=f"The Casino | Inventory")
			embed.description = "Your inventory is empty."
			await interaction.send(embed=embed)
			return

		pages = menus.ButtonMenuPages(
			source=MySource(inventory),
			clear_buttons_after=True,
			style=nextcord.ButtonStyle.primary
		)

		async def callback(interaction:Interaction):
			values = interaction.data['values']

			newSource = []
			if "Usable" in values:
				newSource.extend(self.getAllInventory(interaction.user, 'Usable'))
			if "Collectible" in values:
				newSource.extend(self.getAllInventory(interaction.user, 'Collectible'))
			if "Tool" in values:
				newSource.extend(self.getAllInventory(interaction.user, 'Tool'))
			if "Usable" not in values and "Collectible" not in values and "Tool" not in values:
				newSource.extend(self.getAllInventory(interaction.user))

			await pages.change_source(MySource(newSource))
			await interaction.response.defer()

		options = [
			nextcord.SelectOption(label="All"), 
			nextcord.SelectOption(label="Usable"), 
			nextcord.SelectOption(label="Collectible"),
			nextcord.SelectOption(label="Tool")
		]

		a = Select(options=options, min_values=1, max_values=2)
		a.callback = callback
		pages.add_item(a)

		await pages.start(interaction=interaction, ephemeral=True)

	@nextcord.slash_command()
	@cooldown(1, 5, bucket=SlashBucket.author)
	async def activebuffs(self, interaction:Interaction):
		buffs = DB.fetchAll("SELECT Item FROM ActiveBuffs WHERE DiscordID = ?;", [interaction.user.id])
		tempBuffs = self.bot.get_cog("TempBuffs").getBuffs(interaction.user.id)


		if not buffs and not tempBuffs:
			await interaction.send("You have no active buffs.")
			return

		msg = ""
		if buffs:
			msg += "**Buffs**\n"
			buffs = set(buffs)
			
			for x in buffs:
				msg += x[0]
				msg += "\n"
		
		if tempBuffs:
			msg += "\n**Temp Buffs**\n"

			for record in tempBuffs:
				msg += f"{record[0]} expires <t:{int(record[1])}:R>"
				msg += "\n"



		await interaction.send(msg)


	@nextcord.slash_command()
	@cooldown(1, 5, bucket=SlashBucket.author)
	async def use(self, interaction:Interaction, 
						itemSelected = nextcord.SlashOption(
								required=True,
								name="item", 
								choices=usableItemNamesList),
						amnt:int=1):
		
		embed = nextcord.Embed(color=1768431)

		if amnt < 1:
			raise Exception("valueError")
		if amnt > 25:
			embed.description = f"You can only use up to 25 of this at a time. {amnt:,} is too much!"
			await interaction.send(embed=embed)
			return


		if itemSelected == "Crate":
			await self.bot.get_cog("Shop").useCrate(interaction, amnt)
			return

		if not self.checkInventoryFor(interaction.user, itemSelected, amnt):
			raise Exception("itemNotFoundInInventory")

		if itemSelected == "Small Blind Chip":
			results = await self.bot.get_cog("TempBuffs").addBuff(interaction.user.id, 'Small Blind Chip', amnt)
			embed.description = results
				

		elif itemSelected in ["Voter Chip", "High Card", "One Pair", "Two Pair", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"]:
			if itemSelected == "Voter Chip":
				multiplier = 1.3
				minutes = 150
			if itemSelected == "High Card":
				multiplier = 1.1
				minutes = 120
			if itemSelected == "One Pair":
				multiplier = 1.1
				minutes = 120
			if itemSelected == "Two Pair":
				multiplier = 1.15
				minutes = 120
			if itemSelected == "Straight":
				multiplier = 1.2
				minutes = 120
			if itemSelected == "Flush":
				multiplier = 1.3
				minutes = 120
			if itemSelected == "Full House":
				multiplier = 1.4
				minutes = 90
			if itemSelected == "Four of a Kind":
				multiplier = 1.5
				minutes = 60
			if itemSelected == "Straight Flush":
				multiplier = 1.6
				minutes = 30
			if itemSelected == "Royal Flush":
				multiplier = 1.75
				minutes = 15

			embed.description = self.bot.get_cog("Multipliers").addMultiplier(interaction.user.id, multiplier, datetime.datetime.now() + datetime.timedelta(minutes=(minutes*amnt)))

		elif itemSelected == "Dealer Chip" or itemSelected == "Ace of Spades" or itemSelected == "Big Blind Chip" or itemSelected == "Deck of Cards" or itemSelected == "Three of a Kind":
			self.addActiveItemToDB(interaction.user, itemSelected, amnt)
			if itemSelected != "Three of a Kind":
				gameName = "Blackjack"
			else:
				gameName = "Roulette"
			embed.description = f"{itemSelected} has been activated! Proceed with your {gameName} game."
		elif itemSelected == "Magic 8 Ball":
			text = ""
			totalAmnt = 0
			for _ in range(amnt):
				amntToGive = randint(5000, 25000)
				text += f"+{amntToGive:,}\n"

				totalAmnt += amntToGive
			logID = await self.bot.get_cog("Economy").addWinnings(interaction.user.id, totalAmnt, giveMultiplier=False, activityName=f"8 Ball", amntBet=0)
			
			text += f"\nAdded {totalAmnt:,}{emojis.coin} to your balance"
			embed.description = text

			embed.set_footer(text=f"Log ID: {logID}")
		

		self.removeItemFromInventory(interaction.user, itemSelected, amnt)

		await interaction.send(embed=embed)

	# returns a list of items in the inventory
	def getAllInventory(self, user: nextcord.user, itemType:str=None):
		if itemType:
			return DB.fetchAll("SELECT Item, Quantity, Type, Description, Emoji \
		     				FROM Inventory LEFT JOIN Items ON Inventory.Item = Items.Name \
		     				WHERE DiscordID = ? AND Type = ? AND Quantity > 0;", [user.id, itemType])
		else:
			return DB.fetchAll("SELECT Item, Quantity, Type, Description, Emoji \
		     				FROM Inventory LEFT JOIN Items ON Inventory.Item = Items.Name \
		     				WHERE DiscordID = ? AND Quantity > 0;", [user.id])

	def getCountForItem(self, user: nextcord.user, item: str):
		amnt = DB.fetchOne("SELECT Quantity FROM Inventory WHERE DiscordID = ? AND Item = ?;", [user.id, item])
		
		if not amnt: 
			return 0
		return amnt[0]


	# returns the amount of crates and keys a user has
	def getInventory(self, user: nextcord.user): # grabs all the crates and keys from database
		crates = DB.fetchOne("SELECT Quantity FROM Inventory WHERE DiscordID = ? AND Item = 'Crate';", [user.id])
		keys = DB.fetchOne("SELECT Quantity FROM Inventory WHERE DiscordID = ? AND Item = 'Key';", [user.id])

		if crates: crates = crates[0]
		else: crates = 0
		if keys: keys = keys[0]
		else: keys = 0

		return crates, keys


	def addActiveItemToDB(self, user: nextcord.user, itemName : str, amnt:int):
		if amnt < 1:
			raise ValueError("valueError")
		for _ in range(amnt):
			DB.insert('INSERT INTO ActiveBuffs(DiscordID, Item) VALUES (?, ?);', [user.id, itemName])
	
	def checkForActiveItem(self, user: nextcord.user, itemName: str):
		isInInventory = DB.fetchOne("SELECT 1 FROM ActiveBuffs WHERE DiscordID = ? AND Item = ?;", [user.id, itemName])

		if isInInventory: return True
		else: return False

	def removeActiveItemFromDB(self, user: nextcord.user, itemName: str, amnt: int=1):
		DB.delete("DELETE FROM ActiveBuffs where ID = (SELECT ID FROM ActiveBuffs WHERE DiscordID = ? AND Item = ? LIMIT 1);", [user.id, itemName])

	# checks if user has an item in their inventory
	def checkInventoryFor(self, user: nextcord.user, itemName: str, amnt: int=1):
		if amnt < 1:
			raise ValueError("valueError")
		isInInventory = DB.fetchOne("SELECT 1 FROM Inventory WHERE DiscordID = ? AND Item = ? AND Quantity >= ?;", [user.id, itemName, amnt])
		
		if isInInventory: return True
		else: return False

	def removeItemFromInventory(self, user: nextcord.user, itemName: str, amnt: int=1):
		if amnt < 1:
			raise ValueError("valueError")
		
		quantity = DB.fetchOne("SELECT Quantity FROM Inventory WHERE DiscordID = ? AND Item = ?", [str(user.id), itemName])[0]
		if quantity == amnt:
			DB.delete("DELETE FROM Inventory WHERE DiscordID = ? AND Item = ?", [user.id, itemName])
		else:
			DB.update("UPDATE Inventory SET Quantity = Quantity - ? WHERE DiscordID = ? AND Item = ?;", [amnt, user.id, itemName])

	# called when people open crates (subtracts them from inv.)
	def subtractInv(self, discordid: int, amnt: int): # called when people open crates (subtracts them from inv.)
		DB.update("UPDATE Inventory SET Quantity = Quantity - ? WHERE DiscordID = ? AND Item = 'Crate';", [amnt, discordid])
		DB.update("UPDATE Inventory SET Quantity = Quantity - ? WHERE DiscordID = ? and Item = 'Key';", [amnt, discordid])
	

	def addItemToInventory(self, discordId: int, amnt: int, itemName: str):
		# if user doesnt have item being added, add it to their inventory
		DB.insert('INSERT OR IGNORE INTO Inventory(DiscordID, Item, Quantity) VALUES (?, ?, 0);', [discordId, itemName])
		# update quantity of item in inventory
		DB.update('UPDATE Inventory SET Quantity = Quantity + ? WHERE DiscordID = ? AND Item = ?;', [amnt, discordId, itemName])

	def getRarity(self, rarity):
		if rarity == 0:
			return 0
		elif rarity == 1:
			return choices(population=[x for x in range(2)], weights=[0.80, 0.20], k=1)[0]
		elif rarity == 2:
			return choices(population=[x for x in range(3)], weights=[0.70, 0.20, 0.10], k=1)[0]
		elif rarity == 3:
			return choices(population=[x for x in range(4)], weights=[0.60, 0.20, 0.15, 0.05], k=1)[0]
		elif rarity == 4:
			return choices(population=[x for x in range(5)], weights=[0.45, 0.25, 0.15, 0.10, 0.05], k=1)[0]
		elif rarity == 5:
			return choices(population=[x for x in range(6)], weights=[0.40, 0.20, 0.15, 0.10, 0.10, 0.05], k=1)[0]
		elif rarity == 6:
			return choices(population=[x for x in range(7)], weights=[0.30, 0.15, 0.15, 0.13, 0.12, 0.10, 0.05], k=1)[0]
		elif rarity == 7:
			return choices(population=[x for x in range(8)], weights=[0.25, 0.12, 0.13, 0.14, 0.11, 0.12, 0.08, 0.05], k=1)[0]
		print(f"ERROR!!! RARITY IS {rarity}")
	
	def getRarityName(self, rarity):
		if rarity == 0: return "Uncommon"
		elif rarity == 1: return "Common"
		elif rarity == 2: return "Unique"
		elif rarity == 3: return "Rare"
		elif rarity == 4: return "Mythic"
		elif rarity == 5: return "Exotic"
		elif rarity == 6: return "Legendary"
		elif rarity == 7: return "Artifact"
		else: "Error. Please report this to PyCord for a reward."

	def getRandomItem(self, rarityToSearch:int=None):
		if rarityToSearch == None:
			rarityChosen = self.getRarity(highestRarity)
		else:
			rarityChosen = self.getRarity(rarityToSearch)

		allItems = DB.fetchAll("SELECT * FROM Items WHERE (Type = 'Usable' or TYPE = 'Collectible') and Rarity = ? and Findable = 1 and (ID < 200 or ID >= 300) ORDER BY Price;", [rarityChosen])
		
		itemName, itemRarity, itemEmoji = self.getItemFromListBasedOnPrice(allItems)

		return itemName, itemRarity, itemEmoji

	def getItemFromListBasedOnPrice(self, items):
		# now that we have our chosen rarity... let's get all items of that rarity

		if len(items) == 1:
			return items[0][1], self.getRarityName(items[0][7]), items[0][8]

		# count how many unique prices there are (think of it as another form of rarity)
		# if type(items[0]) == tuple:
		uniquePrices = list(set([x[4] for x in items]))
		uniquePriceCount = len(uniquePrices)
		priceChosen = uniquePrices[self.getRarity(uniquePriceCount-1)]

		itemsToChooseFromGivenPrice = [x for x in items if x[4] == priceChosen]

		# randomly choose item. all items will have same rarity & same price
		itemChosenInList = choice(itemsToChooseFromGivenPrice)
		
		return itemChosenInList[1], self.getRarityName(itemChosenInList[7]), itemChosenInList[8]

	async def GiveRandomItem(self, interaction:Interaction, userId=None):
		if not userId:
			userId = interaction.user.id
		itemName, itemRarity, itemEmoji = self.getRandomItem()
			
		self.addItemToInventory(userId, 1, itemName)

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Item Found!")
		aan = "an" if itemName[0].lower() in "aeiou" else "a"
		embed.description = f"You found {aan} {itemName} {itemEmoji}"
		embed.set_footer(text=f"This item is {itemRarity}")

		await interaction.send(embed=embed)



def setup(bot):
	bot.add_cog(Inventory(bot))