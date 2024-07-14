"""Module running discord webhook to forward Campus TMSP events weekly timetable from FB"""
#!/usr/bin/env python3
# Faire tourner des fonctions en parallèles (dont discord)
from asyncio import run

# Faire passer des dates
from datetime import datetime, date, time
from time import sleep

from load_url import load_menu_url, urls_differentes
from bot_discord import envoi_image_en_ligne

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
        new_url = run(load_menu_url())
        reussite = False
        if urls_differentes(new_url):
            reussite = run(envoi_image_en_ligne(new_url))
        sleep(calcul_temps_d_attente(reussite=reussite))

if __name__ == "__main__":
    #link = "
    # https://upload.wikimedia.org/wikipedia/commons/
    # thumb/7/73/Orange_trademark.svg/64px-Orange_trademark.svg.png"
    #run(envoi_image_en_ligne(link))
    print(calcul_temps_d_attente(False))
    main()
