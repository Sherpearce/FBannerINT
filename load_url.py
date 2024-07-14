# Récupérer et traiter le lien
import xml.etree.cElementTree as cET
from lxml import etree


# Pour l'envoi de l'image sans la télécharger
from io import BytesIO
from aiohttp import ClientSession

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

async def fetch_url(url) -> BytesIO:
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f'Erreur lors du chargement de la page : {resp}')
                return
            data = BytesIO(await resp.read())
    return data