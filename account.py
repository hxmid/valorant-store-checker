import asyncio
import requests
from riot_auth import RiotAuth
from typing import List

from skin import nm_skin, skin

class account(object):
    def __init__(self, credentials: str = ":::"):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name: str = ""
        self.tag: str = ""
        self.store: List[skin] = []
        self.nm: List[nm_skin] = []
        self.score = 0.0

    def set_name(self, acct_key: dict) -> None:
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def add_skin(self, s: skin) -> None:
        self.store.append(s)
        self.score += s.value

    def add_nm_skin(self, n: nm_skin) -> None:
        self.nm.append(n)
        self.score += n.value

    def __str__(self) -> str:
        if self.name == None:
            self.name = ""

        if self.tag == None:
            self.tag = ""

        return f"{self.u + ':' : <25} {self.name : >16} #{self.tag : <5} -> ({sum([x.cost for x in self.store + self.nm if x.value]) : >5} VP) [ " + ", ".join([str(x) for x in self.store]) + " ]" + (("\n\tnm -> [ " + ", ".join([str(x) for x in self.nm]) + " ]\n") if self.nm else "")

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

        store: dict = store_resp.json()
        for item in store.get("SkinsPanelLayout", {}).get("SingleItemStoreOffers", []):
            s = skin()
            s.update_info_from_server(item)
            self.add_skin(s)

        for item in store.get("BonusStore", {}).get("BonusStoreOffers", []):
            s = nm_skin()
            s.update_info_from_server(item)
            self.add_nm_skin(s)

    def asdict(self):
        return {
            "username": self.u,
            "name": self.name,
            "tag": self.tag,
            "store": [x.asdict() for x in self.store],
            "nm": [x.asdict() for x in self.nm]
        }

    def fromdict(self, d: dict):
        self.u      = str(d.get("username", ""))
        self.name   = str(d.get("name", ""))
        self.tag    = str(d.get("tag", ""))
        self.store  = [skin(x, True) for x in d.get("store", [])]
        self.nm     = [nm_skin(x, True) for x in d.get("nm", [])]

    def calc_score(self) -> int:
        self.score = float(sum([x.value for x in self.store + self.nm]))
