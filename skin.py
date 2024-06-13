from typing import Dict, List, Union, Tuple
import requests
from termcolor import colored
from json import load


# tuple(map(lambda x: x["name"], requests.get("https://api.henrikdev.xyz/valorant/v1/content").json()["equips"]))
EQUIPS = ("Odin", "Ares", "Vandal", "Bulldog", "Phantom", "Judge", "Bucky", "Frenzy", "Classic", "Ghost", "Sheriff", "Shorty", "Operator", "Guardian", "Marshal", "Spectre", "Stinger", "Outlaw")

# some colours from termcolor's documentation
COLOURS = ("red", "yellow", "green", "cyan", "blue", "magenta")

# requests.get("https://valorant-api.com/v1/currencies").json()
VP_ID = "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"

SKINS = {x["uuid"]: {k: v for k, v in x.items() if k != "uuid"} for x in requests.get("https://valorant-api.com/v1/weapons/skinlevels").json().get("data", [])}

watchlist: Dict[str, List[str]] = load(open("watchlist.json", "r"))

def get_scores():
    scores = {}
    for tier in watchlist.keys():
        for skin in watchlist[tier]:
            scores.update({skin: (COLOURS[round( ((sorted(list(watchlist.keys()), key=lambda x: float(x), reverse=True).index(tier)) / float(len(watchlist.keys()))) * float(len(COLOURS) - 1.0) )], float(tier))})
    return scores
SCORES: Dict[str, Tuple[str, float]] = get_scores()
del get_scores

# TODO: find a way to figure out how much per skin and then per account
class vp:

    MYR_TO_AUD = 0.323947

    def __init__(self, price, points):
        self.price = price * vp.MYR_TO_AUD
        self.points = points

ml_prices = [
    vp( 199.90, 6750 ),
    vp( 104.90, 3400 ),
    vp(  59.90, 1900 ),
    vp(  39.90, 1250 ),
    vp(  19.90,  600 ),
    vp(  13.90,  375 ),
]

class skin(object):

    def __init__(self, d: Dict[str, Union[str, int]] = {}):
        self.name = ""
        self.cost = 0
        self.fromdict(d)

    def __str__(self) -> str:
        return colored(f"<{self.cost :04d} VP> {self.name}", self.colour(), attrs = (["bold", "underline"] if self.is_melee() else None))

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

        self.name: str = SKINS.get(store_item.get("OfferID")).get("displayName", "").strip().replace("\u00d8", "O")

    def colour(self) -> str:
        return SCORES.get(self.name, ("dark_grey", 0.0))[0]

    def value(self) -> float:
        return SCORES.get(self.name, ("dark_grey", 0.0))[1]

    def is_melee(self) -> bool:
        return not self.name.endswith(EQUIPS)

class nm_skin(skin):
    def __init__(self, d: Dict[str, Union[str, int]] = {}):
        self.discount = 0.0
        super().__init__(d)
        self.fromdict(d)

    def __str__(self) -> str:
        return colored(f"<{self.cost :04d} VP ({int(self.discount)}%)> {self.name}", self.colour(), attrs = (["bold", "underline"] if self.is_melee() else None))

    def asdict(self) -> Dict[str, Union[str, int, float]]:
        return {
            **super().asdict(),
            "discount": float(self.discount)
        }

    def fromdict(self, d: Dict[str, Union[str, int]]) -> None:
        super().fromdict(d)
        self.discount = float(d.get("discount", 0.0))
        return self

    def update_info_from_server(self, nm_item: dict) -> None:
        super().update_info_from_server(nm_item["Offer"])
        self.cost = nm_item.get("DiscountCosts", {}).get(VP_ID, 0)
        self.discount = float(nm_item.get("DiscountPercent", 0.0))

    def value(self) -> float:
        return super().value() * ((100.0 + (self.discount ** 4)) / 100)

    def colour(self) -> str:
        return super().colour()
