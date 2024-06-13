import asyncio
import requests
from riot_auth import RiotAuth
# from custom_auth import RiotAuth
from typing import List

from skin import nm_skin, skin, vp, ml_prices

class account(object):
    CLIENT_VERSION : str = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientVersion"]
    def __init__(self, credentials: str = ":::"):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name : str = ""
        self.tag : str = ""
        self.store: List[skin] = []
        self.nm: List[nm_skin] = []

    def set_name(self, acct_key: dict) -> None:
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def get_vp_price(self) -> int:
        return sum([x.cost for x in self.store + self.nm if x.value()])

    def get_cost(self) -> float:
        total_cost = 0
        vp_price = self.get_vp_price()
        for i in range(len(ml_prices)):
            while (vp_price >= ml_prices[i].points):
                vp_price -= ml_prices[i].points
                total_cost += ml_prices[i].price
        return total_cost

    def __str__(self) -> str:

        s = ""

        if self.name == None:
            self.name = ""

        if self.tag == None:
            self.tag = ""

        s += f"{self.u + ':' : <25}" + " " + f"{self.name : >16} #{self.tag : <5}"
        s += " => "
        s += f"({self.score() : >.2e})"
        s += " < "
        s += f"{self.get_vp_price() :05d} VP"
        s += " -> "
        s += f"${self.get_cost() :>3.2f}"
        s += " > "

        s += ( " [ " + ", ".join( [ str(x) for x in self.store ] ) + " ]" )

        if self.nm:
            s += "\n\t\tnm -> [ "
            s +=    ", ".join( [ str(x) for x in self.nm ] )
            s += " ]"

        return s


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

        store_resp = requests.get(f"https://pd.{self.region}.a.pvp.net/store/v2/storefront/{auth.user_id}",
                                  headers={
                                      "X-Riot-Entitlements-JWT": f"{auth.entitlements_token}",
                                      "Authorization": f"{auth.token_type} {auth.access_token}",
                                      "X-Riot-ClientPlatform": "ewogICAgInBsYXRmb3JtVHlwZSI6ICJQQyIsCiAgICAicGxhdGZvcm1PUyI6ICJXaW5kb3dzIiwKICAgICJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwKICAgICJwbGF0Zm9ybUNoaXBzZXQiOiAiVW5rbm93biIKfQ==",
                                      "X-Riot-ClientVersion": "release-08.09-shipping-57-2521387"
                                  })

        if store_resp.status_code != 200:
            print(f"error [{store_resp.status_code}]: could not get store for account '{self.u}'")
            print(f"  reason: {store_resp.reason}")
            raise RuntimeError

        store: dict = store_resp.json()
        for item in store.get("SkinsPanelLayout", {}).get("SingleItemStoreOffers", []):
            s = skin()
            s.update_info_from_server(item)
            self.store.append(s)

        for item in store.get("BonusStore", {}).get("BonusStoreOffers", []):
            s = nm_skin()
            s.update_info_from_server(item)
            self.nm.append(s)

        if self.region != "ap":
            ap_store = account(f"ap:{self.u}:{self.p}")
            ap_store.get_store()
            self.store.extend(ap_store.store)
            self.nm.extend(ap_store.nm)

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
        self.store  = [skin(x) for x in d.get("store", [])]
        self.nm     = [nm_skin(x) for x in d.get("nm", [])]
        return self

    def score(self) -> float:
        return float(sum([x.value() for x in self.store + self.nm]))
        # return float(sum([x.value() for x in self.nm]))
