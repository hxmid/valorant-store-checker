from typing import List
import requests
from termcolor import colored
from json import load


EQUIPS = tuple(map(lambda x: x["name"], requests.get("https://api.henrikdev.xyz/valorant/v1/content").json()["equips"]))
# VP_INFO = requests.get("https://valorant-api.com/v1/currencies").json()["data"][0]
colours = ["red", "yellow", "light_green", "green", "cyan", "blue", "magenta"]

watchlist: List[List[str]] = load(open("watchlist.json", 'r'))

class skin(object):

    def __init__(self, store_item: dict):
        try:
            self.cost = int(store_item["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"])
        except:
            self.cost = 0

        item_id = store_item["OfferID"]

        skin_resp = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{item_id}")
        if skin_resp.status_code != 200:
            print(f"error [{skin_resp.status_code}]: could not get skin")
            raise RuntimeError

        self.name: str = skin_resp.json()["data"]["displayName"]

        for i, loadout in enumerate(watchlist):
            if self.name in loadout:
                self.colour = colours[i]
                self.value = pow(2, len(watchlist) - i)
                self.value += self.value * (len(loadout) - (loadout.index(self.name) + 1)) / len(loadout)
                self.contrib_cost = self.cost
                break
        else:
            self.contrib_cost = 0
            if not self.name.endswith(EQUIPS):
                self.colour = "light_grey"
                self.value = 1.0
            else:
                self.colour = "dark_grey"
                self.value = 0.0

    def __str__(self) -> str:
        return colored(f"<{self.cost : >4} VP> {self.name}", self.colour)
