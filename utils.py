# file containing all reused methods and functions for the bot

# check if the user has permission to use this command
def check_roles(allowed_role, author_roles):
    return(bool(set(author_roles) & set(allowed_role)))
# if utils.check_roles(["PUT_ROLE_HERE"], [y.name for y in ctx.message.author.roles]): # check the user has the required role


###############################################################################


# checks if the command is in the correct channel
# else:
#     botMsg = await client.send_message(message.channel, person + ", you can only use commands in the <#551089360561504317> channel.")
#     await asyncio.sleep(2)
#     await client.delete_message(message)
#     await asyncio.sleep(10)
#     await client.delete_message(botMsg)
#
#
# # ASK ABOUT
# elif message.content[0:5].lower() == "&edit":
#     await editMessage(message)
# @client.event
# async def editMessage(msg):
#
# 	messageWithoutCommand = msg.content[6:]
# 	messageList = messageWithoutCommand.split(" | ")
#
# 	chnlID = messageList[0]
# 	msgID = messageList[1]
# 	msgContent = messageList[2]
#
# 	MODERATION_CHANNEL = client.get_channel(chnlID)
# 	editMsg = await client.get_message(MODERATION_CHANNEL, msgID)
# 	await client.edit_message(editMsg, msgContent)
#
# 	print("Edited Message\n")


#@commands.command(pass_content=True)
#async def yesorno(ctx):
#	await client.say('Discord, yes or no?')
#	response = client.wait_for_message(author=ctx.message.author, timeout=30)
#	if response.clean_content.lower() == 'yes':
#		await client.say('You said yes.')
#	elif response.clean_content.lower() == 'no':
#		await client.say('You said no.')
#	else:
#		await client.say("That isn't a valid response.")



## message.count(",")
## MAKE SURE IT IS ONLY THREE COMMAS
