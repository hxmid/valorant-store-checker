import requests
from termcolor import colored

watchlist_tiers = {
    "s": {
        "colour": "red",
        "skins": [
            "Xenohunter Knife",
            "VALORANT GO! Vol. 1 Knife",
            "Protocol 781-A Sheriff",
            "Chronovoid Vandal",
        ],
        "value": 5
    },
    "a": {
        "colour": "yellow",
        "skins": [
        ],
        "value": 4
    },
    "b": {
        "colour": "green",
        "skins": [
            "Araxys Vandal",
            "Equilibrium",
        ],
        "value": 3
    },
    "c": {
        "colour": "cyan",
        "skins": [
            "Sovereign Sword",
            "Forsaken Vandal",
            "RGX 11z Pro Vandal",
            "Sovereign Ghost",
            "Chronovoid Sheriff",
            "Protocol 781-A Phantom",
            "Luna's Descent",
        ],
        "value": 2
    },
    "d": {
        "colour": "blue",
        "skins": [
            "Glitchpop Vandal",
            "Gaia's Vengeance Vandal",
            "Sentinels of Light Vandal",
            "Sentinels of Light Sheriff",
            "Ruination Phantom",
        ],
        "value": 1
    },
    "e": {
        "colour": "magenta",
        "skins": [
            "Catrina",
        ],
        "value": 0
    }
}

class skin(object):
    VP_INFO = requests.get("https://valorant-api.com/v1/currencies").json()["data"][0]
    EQUIPS = tuple(map(lambda x: x["name"], requests.get("https://api.henrikdev.xyz/valorant/v1/content").json()["equips"]))

    def __init__(self, store_item: dict):
        self.cost = store_item["Cost"][skin.VP_INFO["uuid"]]

        item_id = store_item["OfferID"]

        skin_resp = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{item_id}")
        if skin_resp.status_code != 200:
            print(f"error [{skin_resp.status_code}]: could not get skin")
            exit()

        self.name: str = skin_resp.json()["data"]["displayName"]

        for tier in watchlist_tiers:
            if self.name in watchlist_tiers[tier]["skins"]:
                self.colour = watchlist_tiers[tier]["colour"]
                self.value = pow(2, watchlist_tiers[tier]["value"])
                break
        else:
            self.colour = "grey" if self.name.endswith(skin.EQUIPS) else "white"
            self.value = 0

    def __str__(self):
        return colored(f"<{self.cost} VP> {self.name}", self.colour)
