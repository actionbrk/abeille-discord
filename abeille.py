import os
import discord
import gspread
import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
import json

client = discord.Client()

class Server:
    def __init__(self, id):
        self.id = id
        self.data = {
            "messages" : 0,
            "messagessupp" : 0,
            "reactions" : 0,
            "reactionssupp" : 0,
            "joins" : 0,
            "leaves" : 0,
            "majavatar" : 0,
            "majpseudo" : 0,
            "status_online" : 0,
            "status_offline" : 0,
            "status_idle" : 0,
            "status_dnd" : 0,
            "messagesbot" : 0,
            "vocal_join" : 0,
            "vocal_leave" : 0,
        }
        self.nbdonnees = 0

# Récupération des informations
discordtoken = os.environ.get('DISCORDTOKEN')
channellog_tmp = os.environ.get('CHANNELLOG')
channellog = discord.Object(id=channellog_tmp)
serverid = os.environ.get('SERVERID')
serverid1 = os.environ.get('SERVER1')
serverid2 = os.environ.get('SERVER2')
clientsecret = str(os.environ.get('CLIENTSECRET'))

servers = []
server1 = Server(serverid1)
servers.append(server1)
server2 = Server(serverid2)
servers.append(server2)

# Connexion G
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

with open("client_secret.json", "r") as jsonFile:
    data = json.load(jsonFile)

tmp = data["private_key"]
data["private_key"] = clientsecret

with open("client_secret.json", "w") as jsonFile:
    json.dump(data, jsonFile)

creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
clientg = gspread.authorize(creds)

# Ouverture des spreadsheets
for server in servers:
    server.ss = clientg.open(server.id)
    server.sh_heures = server.ss.worksheet("heures")

# Variables stockage heure
i = datetime.datetime.now()+timedelta(hours=1)
currenttime = ("%s-%s-%s %s:00:00" % (i.year, str(i.month).zfill(2), str(i.day).zfill(2), str(i.hour).zfill(2)))
debuttime = ("%s-%s-%s %s:00:00" % (i.year, str(i.month).zfill(2), str(i.day).zfill(2), str(i.hour).zfill(2)))

@client.event
async def on_ready():
    print("Ready")
    await client.send_message(channellog, "Ready")
    await client.send_message(channellog, str(debuttime))

@client.event
async def on_resumed():
    print("Resume")
    await client.send_message(channellog, "Resume")
    await client.send_message(channellog, str(debuttime))

@client.event
async def on_error(event, *args, **kwargs):
    print("Error")
    await client.send_message(channellog, "Error")
    await client.send_message(channellog, str(event))

@client.event
async def on_message(message):
    global clientg, servers

    if message.author != client.user:
        # Commandes
        if (message.content == "_stop") and (message.channel.id == channellog.id):
            await client.send_message(message.channel, "...")
            exit(0)
        if message.content == '_servers':
            em = discord.Embed(colour=0xb39ddb)
            em.set_footer(text="Abeille", icon_url="https://raw.githubusercontent.com/actionbrk/Abeille/master/docs/logo.png")
            for server in servers:
                em.add_field(name=server.id, value=str(server.nbdonnees), inline=False)
            await client.send_message(message.channel, embed=em)
        if message.server.me in message.mentions:
            print("Mention");
        if message.server.id is None:
            print("Protection MP")
        else:
            server = await get_server(message.server.id)
            if server is not None:
                await incrementer(datetime.datetime.now())
                server.data["messages"]+=1
                if message.author.bot == True:
                    server.data["messagesbot"]+=1
                    server.nbdonnees+=1
                server.nbdonnees+=1

@client.event
async def on_message_delete(message):
    global servers
    server = await get_server(message.server.id)
    if server is not None:
        await incrementer(datetime.datetime.now())
        server.data["messagessupp"]+=1
        server.nbdonnees+=1

@client.event
async def on_reaction_add(reaction, user):
    global servers
    server = await get_server(reaction.message.server.id)
    if server is not None:
        await incrementer(datetime.datetime.now())
        server.data["reactions"]+=1
        server.nbdonnees+=1

@client.event
async def on_reaction_remove(reaction, user):
    global servers
    server = await get_server(reaction.message.server.id)
    if server is not None:
        await incrementer(datetime.datetime.now())
        server.data["reactionssupp"]+=1
        server.nbdonnees+=1

@client.event
async def on_member_join(member):
    global servers
    server = await get_server(member.server.id)
    if server is not None:
        await incrementer(datetime.datetime.now())
        server.data["joins"]+=1
        server.nbdonnees+=1

@client.event
async def on_member_remove(member):
    global servers
    server = await get_server(member.server.id)
    if server is not None:
        await incrementer(datetime.datetime.now())
        server.data["leaves"]+=1
        server.nbdonnees+=1

@client.event
async def on_member_update(before, after):
    global servers
    server = await get_server(after.server.id)
    if server is not None:
        if before.avatar != after.avatar:
            await incrementer(datetime.datetime.now())
            server.data["majavatar"]+=1
            server.nbdonnees+=1
        if before.nick != after.nick:
            await incrementer(datetime.datetime.now())
            server.data["majpseudo"]+=1
            server.nbdonnees+=1
        if before.status != after.status:
            await incrementer(datetime.datetime.now())
            if(after.status == discord.Status.online):
                server.data["status_online"]+=1
            elif(after.status == discord.Status.offline):
                server.data["status_offline"]+=1
            elif(after.status == discord.Status.idle):
                server.data["status_idle"]+=1
            elif(after.status == discord.Status.dnd):
                server.data["status_dnd"]+=1
            server.nbdonnees+=1

@client.event
async def on_voice_state_update(before, after):
    global servers
    server = await get_server(after.server.id)
    if server is not None:
        if (before.voice.voice_channel != after.voice.voice_channel) and (after.bot == False):
            if before.voice.voice_channel is None:
                server.data["vocal_join"]+=1
                server.nbdonnees+=1
            elif after.voice.voice_channel is None:
                server.data["vocal_leave"]+=1
                server.nbdonnees+=1


# Connexion G et actualisation données
async def login_update():
    global clientg
    # Actualisation compteur données
    try:
        clientg.login()
    except:
        print("Exception login_update")
        await client.send_message(channellog, "Exception login_update")
        exit(0)

# Incrementer valeurs dans messagesheure
async def incrementer(timestamp):
    global servers, currenttime

    timestampfr = timestamp + timedelta(hours=1)
    timestampfr = ("%s-%s-%s %s:00:00" % (str(timestampfr.year), str(timestampfr.month).zfill(2), str(timestampfr.day).zfill(2), str(timestampfr.hour).zfill(2)))

    # Si on est passé à l'heure suivante
    if timestampfr != currenttime:
        tmp_currenttime = currenttime
        currenttime = timestampfr
        # Première ligne
        if tmp_currenttime == debuttime:
            print("Première ligne G")
            try:
                await login_update()
                for server in servers:
                    server.sh_heures.append_row([tmp_currenttime,'','','','','','','',''],'USER_ENTERED')
            except:
                await client.send_message(channellog, "Exception incrementer premier")
                exit(0)
        # Nouvelle ligne
        else:
            for server in servers:
                print("Nouvelle ligne G")
                values = list(map(str,server.data.values()))
                values.insert(0,tmp_currenttime)
                tours=0
                while True:
                    await login_update()
                    tours+=1
                    try:
                        server.sh_heures.append_row(values,'USER_ENTERED')
                        break
                    except:
                        await client.send_message(channellog, f"Erreur écriture {server.id} (essai {tours}). Nouvelle tentative...")
                        print(f"Erreur écriture {server.id} (essai {tours}). Nouvelle tentative...")
                        if tours==5:
                            await client.send_message(channellog, f"Exception incrementer {server.id}")
                            print(f"Exception incrementer {server.id}")
                            exit(0)
        # Reset des compteurs
        for server in servers:
            server.data = dict.fromkeys(server.data, 0)
            server.nbdonnees = 0

async def get_server(id):
    for server in servers:
        if server.id == id:
            return server
    return None

client.run(discordtoken)
print("Fin")
