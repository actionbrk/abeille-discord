import discord
import gspread
import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
from lxml import etree

client = discord.Client()
discordtoken = os.environ['TOKEN']

@client.event
async def on_message(message):
    global clientg, general_donnees, sheet_general, sheet_messagesheure, data, nb_donnees

    if message.author != client.user:
        # Commandes
        if (message.content == "_stop") and (message.channel.id == channellog.id):
            await client.send_message(message.channel, "...")
            exit(0)
        if message.content == "_test":
            await client.send_message(message.channel, "Test")

client.run(discordtoken)
