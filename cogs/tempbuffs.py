import nextcord
from nextcord.ext import commands
from nextcord.ui import Select

from datetime import datetime, timedelta

import asyncio, heapq
from db import DB


class TempBuffs(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.bot.Bot = bot

		self.heap = []
		self._loop = asyncio.get_event_loop()
		self._sleep_task = None

		self.hasExtendedTime = []
		
		self.length = dict()
		self.length['Small Blind Chip'] = 15

	@commands.Cog.listener()
	async def on_ready(self):
		await self.Start()

	async def Start(self):
		await self.load_tempbuffs()

	async def load_tempbuffs(self):
		currentTimestamp = datetime.now().timestamp()
		DB.delete("DELETE FROM TempBuffs WHERE ID IN (SELECT ID FROM TempBuffs WHERE Expires < ?);", [currentTimestamp])

		tempBuffs = DB.fetchAll("SELECT ID, Expires FROM TempBuffs")
		for tempBuff in tempBuffs:
			heapq.heappush(self.heap, (float(tempBuff[1]), tempBuff[0]))
		
		await self._wait_until_next_expiration()

	async def _wait_until_next_expiration(self):
		if not self.heap:
			return  # no temp buffs active
		if self._sleep_task:
			self._sleep_task.cancel()
		next_expiration_time, _ = self.heap[0]
		time_until_next_expiration = (next_expiration_time - datetime.now().timestamp())
		self._sleep_task = asyncio.create_task(asyncio.sleep(time_until_next_expiration))
		try:
			await self._sleep_task
		except asyncio.CancelledError:
			return
		_, buffID = heapq.heappop(self.heap)
		if buffID in self.hasExtendedTime:
			self.hasExtendedTime.remove(buffID)
		else:
			DB.delete("DELETE FROM TempBuffs WHERE ID = ?;", [buffID])
		
		await self._wait_until_next_expiration()


	def userHasBuff(self, userId, buffName):
		data = DB.fetchOne('SELECT Expires FROM TempBuffs WHERE Item = ? AND DiscordID = ?;', [buffName, userId])

		if not data:
			return False
		elif data[0] < datetime.now().timestamp():
			DB.delete('DELETE FROM TempBuffs WHERE Item = ? and DiscordID = ?;', [buffName, userId])
			return False
		else:
			return True

	async def addBuff(self, userId, buffName, amnt):
		length = self.length[buffName] * amnt
		expireTime = (datetime.now() + timedelta(seconds=length)).timestamp()

		if self.userHasBuff(userId, buffName):
			expiresIn = DB.fetchOne('SELECT Expires FROM TempBuffs WHERE Item = ? and DiscordID = ?;', [buffName, userId])[0]
			millisecondsLeft = expiresIn - datetime.now().timestamp()

			expireTime += millisecondsLeft
			# add current time remaining to new one
			DB.update("""Update TempBuffs SET Expires = ? 
							WHERE Item = ? and DiscordID = ?;""", 
							[expireTime, buffName, userId])

			msg = f'Added time! Buff will now expire <t:{int(expireTime)}:R>'

			buffID = DB.fetchOne("SELECT ID FROM TempBuffs WHERE Item = ? and DiscordID = ?;""", [buffName, userId])[0]
			self.hasExtendedTime.append(buffID)
		else:
			DB.insert('INSERT INTO TempBuffs(DiscordID, Item, Expires) VALUES(?, ?, ?)', [userId, buffName, expireTime])
			buffID = DB.fetchOne("SELECT ID FROM TempBuffs WHERE Item = ? and DiscordID = ?;""", [buffName, userId])[0]
			msg = f'Added buff. Will expire <t:{int(expireTime)}:R>'

		heapq.heappush(self.heap, (expireTime, buffID))
		asyncio.create_task(self._wait_until_next_expiration())

		return msg



	def getBuffs(self, userId):
		data = DB.fetchAll('SELECT Item, Expires FROM TempBuffs WHERE DiscordID = ?;', [userId])

		return data




def setup(bot):
	bot.add_cog(TempBuffs(bot))