import discord
import os

client = discord.Client()
discordtoken = os.environ.get('TOKEN')

@client.event
async def on_message(message):

    if message.author != client.user:
        # Commandes
        if (message.content == "_stop") and (message.channel.id == channellog.id):
            await client.send_message(message.channel, "...")
            exit(0)
        if message.content == "_test":
            await client.send_message(message.channel, "Test")

client.run(discordtoken)
