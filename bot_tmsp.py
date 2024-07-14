# Partie discord
import discord
from mytoken import get_token

# Faire tourner des fonctions en parallèles (dont discord)
from asyncio import run, create_task, sleep

# Pour l'envoi de l'image sans la télécharger
from io import BytesIO
from aiohttp import ClientSession

# Faire passer des dates
from datetime import datetime, date, time

# Récupérer et traiter le lien
import xml.etree.cElementTree as cET
from lxml import etree

async def load_menu_url():

    dnld = "https://www.facebook.com/groups/campusTMSP/"

    parser = etree.XMLParser(recover = True)

    async with ClientSession() as session:
        async with session.get(dnld) as resp:
            if resp.status != 200:
                print(f'Erreur lors du chargement de la page : {resp}')
                return
            data = BytesIO(await resp.read())

    root = cET.parse(data, parser=parser).getroot()
    # ça devrait être la bonne ligne
    # elle fonctionne si on enregistre le fichier mais pas avec les BytesIO)
    img = root.find('./html/head/[@property="og:image"]')
    picture_link = ''
    if img is None:
        # C'est pas ouf de faire comme ça
        # on peut vérifier avec .get("property") == "og:image"
        picture_link = root.getchildren()[0].getchildren()[22].get("content")
    else:
        picture_link = img.attrib["src"]
    return picture_link

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

def urls_differentes(nouvelle_url):
    """
    Teste si l'url @nouvelle_url est différente de l'url enregistrée dans le fichier "lien.txt"
    renvoi un boolean
        - True  si différentes
        - False si identiques
    """
    with open("lien.txt", 'r', encoding = "utf-8") as fch_lien:
        ancienne_url = fch_lien.readline()
        print(ancienne_url)
        print(nouvelle_url)

    return ancienne_url != nouvelle_url

def calcul_temps_d_attente(reussite:bool):
    """
    Renvoi le temps d'attente en secondes avant le prochain horaire de vérification
    Les horaires sont:
        - dimanche 20h
        - dimanche 22h
        - lundi 20h

    si @reussite vaut True, renvoit le temps d'attente avant le prochain "dimanche 20h"
    """
    now = datetime.today()
    now_iso = now.isocalendar()
    wake_up = None

    if reussite:
        week = now_iso.week
        # il faut changer de semaine si on est encore dimanche
        if now_iso.weekday == 7:
            week +=1
        wake_up = datetime.combine(
            date.fromisocalendar(now_iso.year, week, now_iso.weekday),
            time(hour = 20)
        )
    else:
        # dijonction de cas du dimanche
        if now_iso.weekday == 7:
            if now.hour < 20:
                wake_up = datetime.combine(
                    date.fromisocalendar(now_iso.year, now_iso.week, now_iso.weekday),
                    time(hour = 20)
                )
            elif now.hour < 22:
                wake_up = datetime.combine(
                    date.fromisocalendar(now_iso.year, now_iso.week, now_iso.weekday),
                    time(hour = 22)
                )
            else:
                wake_up = datetime.combine(
                    date.fromisocalendar(now_iso.year, now_iso.week +1, 1),
                    time(hour = 20)
                )
        # lundi avant 20h
        elif now_iso.weekday == 1 and now.hour < 20:
            wake_up = datetime.combine(
                    date.fromisocalendar(now_iso.year, now_iso.week , 1),
                    time(hour = 20)
                )
        #cas général
        else:
            wake_up = datetime.combine(
                    date.fromisocalendar(now_iso.year, now_iso.week , 7),
                    time(hour = 20)
                )
    return (wake_up-now).total_seconds()

def main():
    """
    Lancement général du service
    """

    #lancement immédiat
    while True:
        print("Lancement !")
        new_url = load_menu_url()
        reussite = False
        if urls_differentes(new_url):
            reussite = run(envoi_image_en_ligne)
        sleep(calcul_temps_d_attente(reussite=reussite))

if __name__ == "__main__":
    #link = "
    # https://upload.wikimedia.org/wikipedia/commons/
    # thumb/7/73/Orange_trademark.svg/64px-Orange_trademark.svg.png"
    #run(envoi_image_en_ligne(link))
    print(calcul_temps_d_attente(False))