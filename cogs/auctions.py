import nextcord
from nextcord.ext import commands, menus
from nextcord import Interaction, SelectOption
from nextcord.ui import Select, Button

import asyncio
from datetime import datetime, timedelta
import heapq

from db import DB
import emojis, cooldowns

from cogs.util import SendConfirmButton

# class ListItemModal(nextcord.ui.Modal):
#     def __init__(self):
#         super().__init__(timeout=60, title="List an Item")

#     async def interact(self, interaction: nextcord.Interaction):
#         await interaction.response.send_message("Please select a number:", ephemeral=True, view=ListItemView())
#         await super().interact(interaction)

#     async def on_timeout(self):
#         await self.message.edit(content="You didn't select a number in time.", view=None)

# class DaysForListing(nextcord.ui.TextInput):
# 	def __init__(self):
# 		super().__init__(label="Number of Days", placeholder="7", min_length=1, max_length=1)



class ListItemView(nextcord.ui.View):
	def __init__(self, bot):
		super().__init__(timeout=60)
		self.bot = bot

		self.itemName = None
		self.startingBid = None
		self.dayExpiration = None

		listableItems = ["Key", "Fishing Pole", "Crate", "Dice", "Big Blind Chip", "Small Blind Chip", 
				   "Dealer Chip", "Deck of Cards", "Ace of Spades", "Pickaxe", "Shovel", "High Card",
					"One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", 
					"Straight Flush", "Royal Flush", "Magic 8 Ball"]

		
		itemName = Select(placeholder="What item would you like to list?",
			options=[SelectOption(label=x, value=x) for x in listableItems],
			custom_id="item_name")
		itemName.callback = self.itemCallback
		self.add_item(itemName)

		# self.add_item(TextInput(label="Starting Bid", placeholder=5000))

		startingBid = Select(placeholder="What's the starting bid?",
			options=[SelectOption(label=x, value=x) for x in [500, 1000, 2000, 3000, 4000, 
													 		  5000, 6000, 7000, 8000, 9000, 
															  10000, 11000, 12000, 13000, 14000, 
															  15000, 20000, 25000, 30000, 35000, 
															  40000, 45000, 50000]],
			custom_id="starting_bid")
		startingBid.callback = self.itemCallback
		self.add_item(startingBid)

		daysForListing = Select(placeholder="How many days would you like the bidding to last?",
			options=[SelectOption(label=x+1, value=x+1) for x in range(7)],
			custom_id="day_expiration")
		daysForListing.callback = self.itemCallback
		self.add_item(daysForListing)

		listButton = Button(label="List Item", style=nextcord.ButtonStyle.green, custom_id='list_item')
		listButton.callback = self.itemCallback
		self.add_item(listButton)
	
	async def itemCallback(self, interaction:Interaction):
		if interaction.data['custom_id'] == "item_name":
			self.itemName = interaction.data['values'][0]
		elif interaction.data['custom_id'] == "starting_bid":
			self.startingBid = interaction.data['values'][0]
		elif interaction.data['custom_id'] == "day_expiration":
			self.dayExpiration = interaction.data['values'][0]
		elif interaction.data['custom_id'] == "list_item":
			if not self.itemName or not self.startingBid or not self.dayExpiration:
				await interaction.send("Must select option for each before submitting listing", ephemeral=True)
				return
			if not self.bot.get_cog("Inventory").checkInventoryFor(interaction.user, self.itemName):
				await interaction.send(f"You do not have item {self.itemName} in your inventory", ephemeral=True)
				return
			await interaction.send("Adding listing!", ephemeral=True)
			self.stop()
			return


		await interaction.response.defer()


	
class DisplayAuctionList(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=5)
		

	async def format_page(self, menu, entries):
		embed = nextcord.Embed(color=1768431, title=f"The Casino | Auctions")

		# SellerID, Item, CurrentBid, CurrentBidderID 
		for x in range(0, len(entries)):
			name = f"ID#{entries[x][0]} | {entries[x][2]} - {entries[x][3]:,}{emojis.coin} - {entries[x][5]} bids"

			value = f"*ends <t:{int(entries[x][6])}:R>*"

			embed.add_field(name=name, value=value, inline=False)
		
		embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
		return embed

class AuctionScheduler(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot
		self.heap = []
		self._loop = asyncio.get_event_loop()
		self._sleep_task = None

	@commands.Cog.listener()
	async def on_ready(self):
		await self.Start()


	def GetItem(self, listingID):
		item = DB.fetchOne("SELECT SellerID, Item, CurrentBid, CurrentBidderID FROM AuctionListings WHERE AuctionID = ?", [listingID])

		if not item:
			return None, None, None, None
		
		return item[0], item[1], item[2], item[3]
	
	async def add_auction(self, discordID, item:str, startingBid:int, expires:float):
		DB.insert("INSERT INTO AuctionListings(SellerID, Item, CurrentBid, Expires) VALUES(?, ?, ?, ?)", (discordID, item, startingBid, expires))
		auction_id = DB.fetchOne("SELECT AuctionID FROM AuctionListings WHERE SellerID = ? AND Expires = ?", [discordID, expires])[0]
		heapq.heappush(self.heap, (expires, auction_id))
		await self._wait_until_next_auction()

	async def remove_auction(self, auction_id):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Auction")
		sellerID, itemName, currentBid, currentBidderID = self.GetItem(auction_id)

		try:
			sellerUser = await self.bot.fetch_user(sellerID)
		except:
			sellerUser = await self.bot.fetch_user(547475078082985990)

		# if user bid
		if currentBidderID != "0":
			try:
				buyerUser = await self.bot.fetch_user(currentBidderID)
			except:
				buyerUser = await self.bot.fetch_user(547475078082985990)

			# add item to bidder's inventory
			self.bot.get_cog("Inventory").addItemToInventory(currentBidderID, 1, itemName)
			# add funds to seller
			await self.bot.get_cog("Economy").addWinnings(sellerID, int(round(currentBid*0.975)))

			embed.description = f"Congratulations! Your item {itemName} sold for {currentBid:,} (-2.5% seller fee) {emojis.coin}. Your funds have been added."
			try:
				await sellerUser.send(embed=embed)
			except:
				pass

			embed.description = f"Congratulations! You have won Auction #{auction_id} for item {itemName} ({currentBid:,}{emojis.coin}). Item has been added to your inventory"
			try:
				await buyerUser.send(embed=embed)
			except:
				pass
		# no user bids
		else:
			# add item back to seller's inventory
			self.bot.get_cog("Inventory").addItemToInventory(sellerID, 1, itemName)

			embed.description = f"Your item {itemName} did not sell and has been returned back to your inventory"
			try:
				await sellerUser.send(embed=embed)
			except:
				pass
		
		DB.delete("DELETE FROM AuctionListings WHERE AuctionID = ?;", [auction_id])




	async def load_auctions(self):
		currentTimestamp = datetime.now().timestamp()
		expiredListingIDs = DB.fetchAll("SELECT AuctionID FROM AuctionListings WHERE Expires < ?", [currentTimestamp])
		
		for listingID in expiredListingIDs:
			await self.remove_auction(listingID[0])

		auctionListings = DB.fetchAll("SELECT AuctionID, Expires FROM AuctionListings")
		for auctionListing in auctionListings:
			heapq.heappush(self.heap, (float(auctionListing[1]), auctionListing[0]))
		
		await self._wait_until_next_auction()

	async def Start(self):
		await self.load_auctions()

	async def _wait_until_next_auction(self):
		if not self.heap:
			return  # no auctions scheduled
		if self._sleep_task:
			self._sleep_task.cancel()
		next_expiration_time, _ = self.heap[0]
		time_until_next_auction = (next_expiration_time - datetime.now().timestamp())
		self._sleep_task = asyncio.create_task(asyncio.sleep(time_until_next_auction))
		try:
			await self._sleep_task
		except asyncio.CancelledError:
			return
		_, auction_id = heapq.heappop(self.heap)
		await self.remove_auction(auction_id)
		
		await self._wait_until_next_auction()
	

	@nextcord.slash_command()
	async def auction(self, interaction:Interaction):
		pass

	@auction.subcommand()
	async def list(self, interaction:Interaction):
		data = DB.fetchAll("SELECT * FROM AuctionListings;")
		
		if not data:
			await interaction.send("There are no active listings...", ephemeral=True)
			return
		
		pages = menus.ButtonMenuPages(
			source=DisplayAuctionList(data),
			clear_buttons_after=True,
			style=nextcord.ButtonStyle.primary,
		)
		await pages.start(interaction=interaction, ephemeral=True)

	@auction.subcommand()
	@cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author, cooldown_id='bid')
	async def bid(self, interaction:Interaction, id:int, amnt:int):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Auction | Bid")
		
		sellerID, itemName, currentBid, currentBidderID = self.GetItem(id)

		if not sellerID:
			embed.description = "Auction listing not found..."
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		if sellerID == interaction.user.id:
			embed.description = "You cannot bid on your own item"
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		if currentBidderID == interaction.user.id:
			embed.description = "You are already the highest bidder for this item"
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		if amnt > 100000:
			embed.description = f"Bid must be less than 100,000{emojis.coin}"
			await interaction.send(embed=embed, ephemeral=True)
			return

		if amnt <= currentBid + 100:
			embed.description = f"Current bid is {currentBid}. Your bid must be at least 100{emojis.coin} higher"
			await interaction.send(embed=embed, ephemeral=True)
			return



		if not await SendConfirmButton(interaction, f"You're about to bid on {itemName} for {amnt:,}{emojis.coin}. Proceed?"):
			embed.description = "You have cancelled this transaction."
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		if not await self.bot.get_cog("Economy").subtractBet(interaction.user, amnt):
			embed.description = f"You do not have enough credits for that bid"
			await interaction.send(embed=embed, ephemeral=True)
			return
		
		# refund previous bidder
		if currentBidderID != "0":
			try:
				previousHighestBidder = await self.bot.fetch_user(currentBidderID)
				if previousHighestBidder:
					await self.bot.get_cog("Economy").addWinnings(currentBidderID, currentBid)
					embed.add_field(name="OUTBID!", value=f"You have been outbid for Auction ID#{id} with item {itemName}. Highest bid is now {amnt:,}{emojis.coin}")
					await previousHighestBidder.send(embed=embed)
			except:
				pass
		
		DB.update("UPDATE AuctionListings SET CurrentBid = ?, CurrentBidderID = ?, BidCount = BidCount + 1 WHERE AuctionID = ?", [amnt, interaction.user.id, id])

		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Auction | Bid")
		embed.description = f"You have placed a bid on {itemName} for {amnt:,}{emojis.coin}"
		await interaction.send(embed=embed)

	@auction.subcommand()
	async def sell(self, interaction:Interaction):
		embed = nextcord.Embed(color=1768431, title=f"{self.bot.user.name} | Auction | Sell")

		view = ListItemView(self.bot)
		msg = await interaction.send(view=view, ephemeral=True)
		
		if await view.wait():
			await msg.edit("Timed out.", view=None)
			return

		self.bot.get_cog("Inventory").removeItemFromInventory(interaction.user, view.itemName)
		endTime = (datetime.now() + timedelta(days=int(view.dayExpiration))).timestamp()
		# endTime = (datetime.now() + timedelta(seconds=10)).timestamp()
		asyncio.create_task(
			self.add_auction(
				interaction.user.id, 
				view.itemName, 
				view.startingBid, 
				endTime
			)
		)

		embed.description = f"Successfully listed {view.itemName}, with starting bid of {view.startingBid}{emojis.coin}. Auction ends <t:{int(endTime)}:R>"
		await interaction.send(embed=embed)

def setup(bot):
	bot.add_cog(AuctionScheduler(bot))
# # Example usage:
# scheduler = AuctionScheduler()
# for auction_id in range(100):
# 	asyncio.create_task(scheduler.add_auction(auction_id))

# asyncio.run(scheduler.run())