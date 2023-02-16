import asyncio
import requests
from riot_auth import RiotAuth
from typing import List

from skin import skin, VP_ID

class account(object):
    def __init__(self, credentials: str):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name: str = ""
        self.tag: str = ""
        self.store: List[skin] = []
        self.nightmarket: List[skin] = []
        self.score = 0

    def set_name(self, acct_key: dict) -> None:
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def add_skin(self, s: skin) -> None:
        self.store.append(s)
        self.score += s.value

    def add_nightmarket_skin(self, d: dict) -> None:
        s = skin(d["Offer"])
        s.cost = d["DiscountCosts"][VP_ID]
        s.value *= (100.0+float(d["DiscountPercent"]))/100.0
        self.nightmarket.append(s)
        self.score += s.value

    def __str__(self) -> str:
        if self.name == None:
            self.name = ""

        if self.tag == None:
            self.tag = ""

        return f"{self.u + ':' : <25} {self.name : >16} #{self.tag : <5} ({self.score : >6.2f}) -> " + f"({sum(x.cost for x in self.store + self.nightmarket if x.contrib_cost): >5} VP) [ " + ", ".join([str(x) for x in self.store]) + " ]" + (("\n       nm -> [ " + ", ".join([str(x) for x in self.nightmarket]) + " ]\n") if self.nightmarket else "")

    def print(self, i) -> str:
        return f"{i + 1 : >3d}. {self}"

    def write(self, i) -> str:
        return self.print(i) + "\n"

    def get_store(self) -> None:
        asyncio.set_event_loop(asyncio.new_event_loop())
        auth = RiotAuth()
        asyncio.run(auth.authorize(self.u, self.p))

        userinfo = requests.get("https://auth.riotgames.com/userinfo", headers={"Authorization": f"{auth.token_type} {auth.access_token}"})
        if userinfo.status_code != 200:
            print(f"error [{userinfo.status_code}]: could not get userinfo")
            raise RuntimeError

        self.set_name(userinfo.json()["acct"])

        store_resp = requests.get(f"https://pd.{self.region}.a.pvp.net/store/v2/storefront/{auth.user_id}", headers={"X-Riot-Entitlements-JWT": f"{auth.entitlements_token}", "Authorization": f"{auth.token_type} {auth.access_token}"})

        if store_resp.status_code != 200:
            print(f"error [{store_resp.status_code}]: could not get store")
            raise RuntimeError

        store = store_resp.json()

        for item in store["SkinsPanelLayout"]["SingleItemStoreOffers"]:
            self.add_skin(skin(item))

        for item in store.get("BonusStore", {}).get("BonusStoreOffers", []):
            self.add_nightmarket_skin(item)
