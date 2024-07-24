"""Module de webhook pour envoyer des images"""

from asyncio import run
from datetime import date
from discord import SyncWebhook, File, HTTPException
from requests import Session
from load_url import fetch_url

def load_webhooks():
    """
    Renvoi une liste des webhooks contenus dans le fichier 'webhooks.txt'
    1 par ligne, commentaire possible après un #
    """
    with open("webhooks.txt", 'r', encoding = 'utf-8') as fch:
        return [line.split("#")[0] for line in fch.readlines()]


def send_file_to_webhooks(url:str):
    """
    Envoi le fichier dont le lien est en url à tous les webhook du fichier 'webhooks.txt'
    Le fichier est alors appelé 'Menu_de_la_semaine_du_yyyy-mm-dd.jpg'
    """
    webhooks = load_webhooks()
    retour = True
    fichier = File(
        run(fetch_url(url)),
        filename=f"Menu_de_la_semaine_du_{date.today().isoformat()}.jpg")
    with Session() as s:
        for link in webhooks:
            try:
                wh = SyncWebhook.from_url(link, session=s)
            except ValueError:
                retour = False
                print(f"link: {link} is no more valid")
            try:
                # J'ai commenté la ligne de l'avatar pour 2 raisons:
                # - 1 Je ne suis pas BDE donc j'ai pas la légitimité de le mettre
                # - 2 L'image est en 2048² alors que du 50² suffirait (je suppose) sinon 512² max
                wh.send(
                    content = f"""Salut l'INT !
 Voici le menu du la semaine du {date.today().day}/{date.today().month}""",
                    #avater_url="https://bde-imtbs-tsp.fr/static/vieasso/img/LogoBDE.png",
                    username="Campus TMSP",
                    file=fichier)
            except HTTPException:
                retour = False
            except TypeError:
                retour = False
    return retour

if __name__ == "__main__":
    send_file_to_webhooks("https://fr.wikipedia.org/static/images/icons/wikipedia.png")
