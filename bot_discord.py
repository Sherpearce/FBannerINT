# Partie discord
import discord
from mytoken import get_token

# Faire tourner des fonctions en parallèles (dont discord)
from asyncio import create_task, sleep


# Faire passer des dates
from datetime import datetime

# Pour l'envoi de l'image sans la télécharger
from io import BytesIO
from aiohttp import ClientSession

async def send_message(client, b_io:BytesIO):
    """
    Envoi du document du buffer @b_io dans les channels du ficher "channels.txt" 
    via le bot discord actif @client
    """
    # attend que la connection soit établie
    await client.wait_until_ready()

    while client.is_closed():
        await sleep(0.1)
    # envoi un message dans tous les channels enregistrés
    for channel_id in load_channels():
        file = discord.File(
            b_io,
            f"Menu de la semaine du {datetime.today().strftime('%Y-%m-%d')}.jpg", 
            description=f"Menu de la semaine du {datetime.today().strftime('%Y-%m-%d')} à l'INT"
            )
        b_io.seek(0)
        channel = client.get_channel(channel_id) #new des Héros
        await channel.send(file=file)
    await client.close()

def load_channels():
    """
    renvoi une liste des channels surlesquels envoyer un message.
    Les channels sont stockés dans le fichier "channels.txt" un par ligne 
    avec des commentaires possibles après un '#'
    """
    num_line = 1
    liste_channels = []
    with open("channels.txt", 'r', encoding = 'utf-8') as fch:
        line = fch.readline()
        while line != '':
            coupee = line.split('#')
            try:
                liste_channels.append(int(coupee[0]))
            except ValueError as e:
                print(f"Unnable to read line {num_line} ({coupee})\n{e}")
            except Exception as e:
                raise e
            line = fch.readline()
            num_line += 1

    return liste_channels

async def connection(client):
    """
    Lance le bot discord
    """
    print("Lancement de la connection")
    await client.start(get_token())

async def envoi_image_en_ligne(url):
    """
    Envoi l'image donnée en URL sur les channels répertoriés dans le fichier "channels.txt"
    Initialise un bot discord, récupère un stream de l'image à envoyer puis
    envoi l'image dans les différents salons (channels)
    """
    flags = discord.flags.Intents.default()
    client = discord.Client(intents=flags)

    @client.event
    async def on_raw_reaction_add(reaction):
        await client.close()

    discord.utils.setup_logging()

    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f'Erreur lors du chargement de la page : {resp}')
                return
            data = BytesIO(await resp.read())
    connect = create_task(connection(client))
    await sleep(1)
    sd_message = create_task(send_message(client, data))
    await sd_message
    await connect
    return True

