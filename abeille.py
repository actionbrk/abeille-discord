import discord
import gspread
import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials
from lxml import etree

client = discord.Client()

data = {
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
}

# Connexion G
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
clientg = gspread.authorize(creds)
ss = clientg.open("Abeille")

# Initialisation variables
sheet_general = ss.worksheet("general")
sheet_messagesheure = ss.worksheet("messagesheure")
nb_donnees = int(sheet_general.acell('A2').value) # 'Données' dans general

# Variables stockage heure
i = datetime.datetime.now()+timedelta(hours=1)
currenttime = ("%s-%s-%s %s:00:00" % (i.year, str(i.month).zfill(2), str(i.day).zfill(2), str(i.hour).zfill(2)))
debuttime = ("%s-%s-%s %s:00:00" % (i.year, str(i.month).zfill(2), str(i.day).zfill(2), str(i.hour).zfill(2)))

# Récupération des informations abeille.config
tree = etree.parse("abeille.config")
discordtoken = tree.xpath("/config/discordtoken")[0].text
channellog_tmp = tree.xpath("/config/channellog")[0].text
channellog = discord.Object(id=channellog_tmp)
serverid = tree.xpath("/config/serverid")[0].text

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
    global clientg, general_donnees, sheet_general, sheet_messagesheure, data, nb_donnees

    if message.author != client.user:
        # Commandes
        if (message.content == "_stop") and (message.channel.id == channellog.id):
            await client.send_message(message.channel, "...")
            exit(0)
        if message.content == "_info":
            em = discord.Embed(colour=0xb39ddb)
            em.set_author(name='AppartData', icon_url="https://actionbrk.github.io/img/appartdata.png", url="https://actionbrk.github.io/aek/appartdata.html")
            em.set_footer(text="Données récoltées par Abeille", icon_url="https://raw.githubusercontent.com/actionbrk/Abeille/master/docs/logo.png")
            em.add_field(name="Messages postés", value=str(data["messages"]), inline=True)
            em.add_field(name="Messages supprimés", value=str(data["messagessupp"]), inline=True)
            em.add_field(name="Réactions ajoutées", value=str(data["reactions"]), inline=True)
            em.add_field(name="Réactions supprimées", value=str(data["reactionssupp"]), inline=True)
            em.add_field(name="Passages en ligne", value=str(data["status_online"]), inline=True)
            em.add_field(name="Passages hors-ligne", value=str(data["status_offline"]), inline=True)
            em.add_field(name="Passages absent", value=str(data["status_idle"]), inline=True)
            em.add_field(name="Passages occupé", value=str(data["status_dnd"]), inline=True)
            em.add_field(name="Messages bot", value=str(data["messagesbot"]), inline=True)
            await client.send_message(message.channel, embed=em)
        if message.content == 'Bzz bzz serveurs':
            for serv in client.servers:
                await client.send_message(message.channel, serv.name)
        if message.server.me in message.mentions:
            print("Mention");
        if message.content == "_stats":
            em = discord.Embed(colour=0xb39ddb)
            em.set_author(name='AppartData', icon_url="https://actionbrk.github.io/img/appartdata.png", url="https://actionbrk.github.io/aek/appartdata.html")
            em.set_footer(text="Données récoltées par Abeille", icon_url="https://raw.githubusercontent.com/actionbrk/Abeille/master/docs/logo.png")
            em.add_field(name="Télécharger les stats du serveur", value="[CSV](https://docs.google.com/spreadsheets/u/1/d/1Gl27WsswWqur2N8EqBICp4H8JsQZDl0mXAuxNdgG-LQ/export?format=csv&id=1Gl27WsswWqur2N8EqBICp4H8JsQZDl0mXAuxNdgG-LQ&gid=116803434)", inline=False)
            em.add_field(name="Dernière mise à jour", value=currenttime, inline=False)
            await client.send_message(message.channel, embed=em)
        if message.server.id is None:
            print("Protection MP")
        elif message.server.id == serverid:
            print("[Posté] " + "#" + message.channel.name)
            await incrementer(datetime.datetime.now())
            data["messages"]+=1
            if message.author.bot == True:
                data["messagesbot"]+=1
                nb_donnees+=1
            nb_donnees+=1

@client.event
async def on_message_delete(message):
    global nb_donnees
    if message.server.id == serverid:
        print("[Supprimé] " + "#" + message.channel.name)
        await incrementer(datetime.datetime.now())
        data["messagessupp"]+=1
        nb_donnees+=1

@client.event
async def on_reaction_add(reaction, user):
    global nb_donnees
    if reaction.message.server.id == serverid:
        print("[Réaction ajoutée]")
        await incrementer(datetime.datetime.now())
        data["reactions"]+=1
        nb_donnees+=1

@client.event
async def on_reaction_remove(reaction, user):
    global nb_donnees
    if reaction.message.server.id == serverid:
        print("[Réaction supprimée]")
        await incrementer(datetime.datetime.now())
        data["reactionssupp"]+=1
        nb_donnees+=1

@client.event
async def on_member_join(member):
    global nb_donnees
    if member.server.id == serverid:
        print("[Join] " + member.name)
        await incrementer(datetime.datetime.now())
        data["joins"]+=1
        nb_donnees+=1

@client.event
async def on_member_remove(member):
    global nb_donnees
    if member.server.id == serverid:
        print("[Leave] " + member.name)
        await incrementer(datetime.datetime.now())
        data["leaves"]+=1
        nb_donnees+=1

@client.event
async def on_member_update(before, after):
    global nb_donnees
    if after.server.id == serverid:
        if before.avatar != after.avatar:
            print("[Avatar update] " + after.name)
            await incrementer(datetime.datetime.now())
            data["majavatar"]+=1
        if before.nick != after.nick:
            print("[Pseudo update] " + after.name)
            await incrementer(datetime.datetime.now())
            data["majpseudo"]+=1
            nb_donnees+=1
        if before.status != after.status:
            print("[Status update] " + after.name)
            await incrementer(datetime.datetime.now())
            if(after.status == discord.Status.online):
                data["status_online"]+=1
            elif(after.status == discord.Status.offline):
                data["status_offline"]+=1
            elif(after.status == discord.Status.idle):
                data["status_idle"]+=1
            elif(after.status == discord.Status.dnd):
                data["status_dnd"]+=1
            nb_donnees+=1

@client.event
async def on_voice_state_update(before, after):
    global nb_donnees
    if after.server.id == serverid:
        if before.voice.voice_channel != after.voice.voice_channel:
            if before.voice.voice_channel is None:
                print("[Vocal+] " + after.name)
            elif after.voice.voice_channel is None:
                print("[Vocal-] " + after.name)


# Connexion G et actualisation données
async def login_update():
    global clientg, general_donnees
    # Actualisation compteur données
    try:
        clientg.login()
    except:
        print("Exception login_update")
        await client.send_message(channellog, "Exception login_update")
        exit(0)

# Incrementer valeurs dans messagesheure
async def incrementer(timestamp):
    global sheet_messagesheure, currenttime, data

    timestampfr = timestamp + timedelta(hours=1)
    timestampfr = ("%s-%s-%s %s:00:00" % (str(timestampfr.year), str(timestampfr.month).zfill(2), str(timestampfr.day).zfill(2), str(timestampfr.hour).zfill(2)))

    # Si on est passé à l'heure suivante
    if timestampfr != currenttime:
        await login_update()
        # Première ligne
        if currenttime == debuttime:
            print("Première ligne G")
            try:
                sheet_messagesheure.append_row([currenttime,'','','','','','','',''],'USER_ENTERED')
            except:
                await client.send_message(channellog, "Exception incrementer premier")
                exit(0)
        # Nouvelle ligne
        else:
            print("Nouvelle ligne G")
            try:
                values = list(map(str,data.values()))
                values.insert(0,currenttime)
                sheet_messagesheure.append_row(values,'USER_ENTERED')
                sheet_general.update_acell('A2', str(nb_donnees))
            except:
                await client.send_message(channellog, "Exception incrementer")
                exit(0)

        currenttime = timestampfr
        data = dict.fromkeys(data, 0)


client.run(discordtoken)
print("Fin")
