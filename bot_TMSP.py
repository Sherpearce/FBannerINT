from mytoken import get_token
import discord
from asyncio import run, create_task, sleep

# Pour l'envoi de l'image sans la télécharger
from io import BytesIO
from aiohttp import ClientSession

from datetime import datetime


async def send_message(client, BIO:BytesIO):
    # attend que la connection soit établie
    while not client.is_closed():
        pass
    # envoi un message dans tous les channels enregistrés
    for channel_id in client.load_channels():
        file = discord.File(
            BIO, 
            f"Menu de la semaine du {datetime.today().strftime('%Y-%m-%d')}.jpg", 
            description="Menu de la semaine du {datetime.today().strftime('%Y-%m-%d')} à l'INT"
            )
        BIO.seek(0, whence=0)
        channel = client.get_channel(channel_id) #new des Héros
        await channel.send(file=file)

def load_channels():
    """
    renvoi une liste des channels surlesquels envoyer un message.
    Les channels sont stockés dans le fichier "channels.txt" un par ligne avec des commentaires possibles après un '#'
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


async def main():
    flags = discord.flags.Intents.default()
    client = discord.Client(intents=flags)
    @client.event
    async def on_raw_reaction_add(reaction):
        await client.close()

    discord.utils.setup_logging()
    test_url = "http://24x36.art/affiches/HD_1036.jpg"
    async with ClientSession() as session:
        async with session.get(test_url) as resp:
            if resp.status != 200:
                print(f'Erreur lors du chargement de la page : {resp}')
                return
            print("Image récupérée")
            data = BytesIO(await resp.read())
    print(client.is_closed())
    connect = create_task(client.start(get_token()))
    #sd_message = create_task(send_message(client, data))
    await sleep(1)
    # await sd_message
    await connect
    print("toto")

if __name__ == "__main__":
    run(main())

