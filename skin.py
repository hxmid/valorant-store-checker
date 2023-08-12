from typing import Dict, List, Union
import requests
from termcolor import colored
from json import load


# tuple(map(lambda x: x["name"], requests.get("https://api.henrikdev.xyz/valorant/v1/content").json()["equips"]))
EQUIPS = ("Odin", "Ares", "Vandal", "Bulldog", "Phantom", "Judge", "Bucky", "Frenzy", "Classic", "Ghost", "Sheriff", "Shorty", "Operator", "Guardian", "Marshal", "Spectre", "Stinger")

# some colours from termcolor's documentation
COLOURS = ("red", "yellow", "green", "cyan", "blue", "magenta")

# requests.get("https://valorant-api.com/v1/currencies").json()
VP_ID = "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"

SKINS = {x["uuid"]: {k: v for k, v in x.items() if k != "uuid"} for x in requests.get("https://valorant-api.com/v1/weapons/skinlevels").json().get("data", [])}

watchlist: List[str] = load(open("watchlist.json", 'r'))

class skin(object):

    def __init__(self, d: Dict[str, Union[str, int]] = {}, update: bool = False):
        self.name = ""
        self.cost = 0
        self.value = 0.0
        self.colour = "dark_grey"
        self.fromdict(d)

        if update:
            self.update_value()

    def __str__(self) -> str:
        return colored(f"<{self.cost :04d} VP> {self.name}", self.colour, attrs = (["bold", "underline"] if self.is_melee() else None))

    def asdict(self) -> Dict[str, Union[str, int]]:
        return {
            "name": self.name,
            "cost": self.cost
        }

    def fromdict(self, d: Dict[str, Union[str, int]]):
        self.name = str(d.get("name", ""))
        self.cost = int(d.get("cost", 0))
        return self

    def update_info_from_server(self, store_item: dict) -> None:
        self.cost = int(store_item.get("Cost", {}).get(VP_ID, 0))
        self.name: str = SKINS.get(store_item.get("OfferID")).get("displayName", "")
        self.update_value()

    def update_value(self) -> None:
        if self.name in watchlist:
            colour = round( ((watchlist.index(self.name)) / float(len(watchlist))) * float(len(COLOURS) - 1.0) )
            self.colour = COLOURS[colour]
            self.value = float(pow(1.3, len(watchlist) - watchlist.index(self.name)))
            self.value += self.value * float( len(watchlist) - (watchlist.index(self.name) + 1) ) / float(len(watchlist))

    def is_melee(self) -> bool:
        return not self.name.endswith(EQUIPS)

class nm_skin(skin):
    def __init__(self, d: Dict[str, Union[str, int]] = {}, update: bool = False):
        super().__init__(d, update)
        self.discount = 0.0

        if update:
            self.update_value()

    def asdict(self) -> Dict[str, Union[str, int, float]]:
        return {
            **super().asdict(),
            "discount": float(self.discount, 0.0)
        }

    def fromdict(self, d: Dict[str, Union[str, int]]) -> None:
        super().fromdict(d)
        self.discount = float(d.get("discount", 0.0))
        self.update_value()

    def update_info_from_server(self, nm_item: dict) -> None:
        super().update_info_from_server(nm_item["Offer"])
        self.cost = nm_item.get("DiscountCosts", {}).get(VP_ID, 0)
        self.discount = float(nm_item.get("DiscountPercent", 0.0))
        self.update_value()

    def update_value(self) -> None:
        super().update_value()
        self.value *= ( 100.0 + (2.0 * float(self.discount)) ) / 50.0
