from json import dumps
from io import BytesIO
from discord import SyncWebhook, File, HTTPException
from requests import Session
from load_url import fetch_url
from asyncio import run
from datetime import date

def load_webhooks():
    with open("webhooks.txt", 'r', encoding = 'utf-8') as fch:
        return [line.split("#")[0] for line in fch.readlines()]


def send_file_to_webhooks(url:str):
    webhooks = load_webhooks()
    retour = True
    with Session() as s:
        for link in webhooks:
            try:
                wh = SyncWebhook.from_url(link, session=s)
            except ValueError:
                retour = False
                print(f"link: {link} is no more valid")
            fichier = File(run(fetch_url(url)), 
                filename=f"Menu_de_la_semaine_du_{date.today().isoformat()}.jpg")
            try:
                wh.send(file=fichier)
            except HTTPException as e:
                retour = False
            except TypeError as e:
                retour = False
            except:
                retour = False
    return retour

