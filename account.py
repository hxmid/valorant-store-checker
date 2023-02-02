import asyncio
import requests
from riot_auth import RiotAuth

from skin import skin

class account(object):
    def __init__(self, credentials: str):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name: str = ""
        self.tag: str = ""
        self.store: list(skin) = []
        self.score = 0

    def set_name(self, acct_key: dict):
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def add_skin(self, s: skin):
        self.store.append(s)
        self.score += s.value

    def __str__(self):
        if self.name == None:
            self.name = ""

        if self.tag == None:
            self.tag = ""

        return  f"{self.u + ':' : <25} {self.name : >16} #{self.tag : <5} ({self.score : >2}) -> " + "[ " + ", ".join([str(x) for x in self.store]) + " ]"

    def print(self, i):
        return f"{i + 1 :2d}. {self}"

    def write(self, i):
        return self.print(i) + "\n"

    def get_store(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        auth = RiotAuth()
        asyncio.run(auth.authorize(self.u, self.p))

        userinfo = requests.get("https://auth.riotgames.com/userinfo", headers={"Authorization": f"{auth.token_type} {auth.access_token}"})
        if userinfo.status_code != 200:
            print(f"error [{userinfo.status_code}]: could not get userinfo")
            exit()

        self.set_name(userinfo.json()["acct"])

        store_resp = requests.get(f"https://pd.{self.region}.a.pvp.net/store/v2/storefront/{auth.user_id}", headers={"X-Riot-Entitlements-JWT": f"{auth.entitlements_token}", "Authorization": f"{auth.token_type} {auth.access_token}"})
        if store_resp.status_code != 200:
            print(f"error [{store_resp.status_code}]: could not get store")
            exit()

        store = store_resp.json()["SkinsPanelLayout"]["SingleItemStoreOffers"]

        for item in store:
            self.add_skin(skin(item))
