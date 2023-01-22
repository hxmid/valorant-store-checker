from riot_auth import RiotAuth
import asyncio
import requests
from termcolor import colored
import json

watchlist = [
    "Xenohunter Knife",
    "VALORANT GO! Vol. 1 Knife",
    "Gaia's Vengeance Vandal",
    "Oni Phantom",
    "Protocol 781-A Phantom",
    "Protocol 781-A Sheriff",
    "Catrina",
    "Blade of Chaos",
    "Sovereign Sword",
    "Forsaken Vandal",
    "Glitchpop Vandal",
    "Araxys Vandal",
    "Araxys Bio Harvester",
    "RGX 11z Pro Vandal",
    "Sentinels of Light Sheriff",
    "Oni Claw",
]

weapons = [
    "Classic",
    "Shorty",
    "Frenzy",
    "Ghost",
    "Sheriff",
    "Stinger",
    "Spectre",
    "Bucky",
    "Judge",
    "Vandal",
    "Phantom",
    "Marshal",
    "Operator",
    "Odin",
    "Ares",
    "Bulldog",
    "Guardian",
]

VP_INFO = requests.get("https://valorant-api.com/v1/currencies").json()["data"][0]

class account:
    def __init__(self, credentials: str):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name: str = ""
        self.tag:str = ""
        self.store: list(skin) = []

    def set_name(self, acct_key: dict):
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def __str__(self):
        if self.name == None:
            self.name = ""
        if self.tag == None:
            self.tag = ""
        return  f"{self.u + ':' : <25} {self.name : >16} #{self.tag : <5} ({self.region}) -> " + "[ " + ", ".join([str(x) for x in self.store]) + " ]"

class skin:
    WATCH = 'red'
    KNIFE = 'yellow'
    DEFAULT = 'grey'

    def __init__(self, store_item: dict):
        self.cost = store_item["Cost"][VP_INFO["uuid"]]

        item_id = store_item["OfferID"]
        skin_resp = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{item_id}")
        if skin_resp.status_code != 200:
            print(f"error [{skin_resp.status_code}]: could not get skin")
            exit()

        self.name = skin_resp.json()["data"]["displayName"]

    def is_knife(self):
        if self.name.split()[-1] not in weapons:
            return True
        return False

    def is_watched(self):
        if self.name in watchlist:
            return True
        return False

    def __str__(self):
        return colored(f"<{self.cost} VP> {self.name}", skin.WATCH if self.is_watched() else skin.KNIFE if self.is_knife() else skin.DEFAULT)


def get_store(auth: RiotAuth, acc: account) -> account:
    asyncio.run(auth.authorize(acc.u, acc.p))

    userinfo = requests.get("https://auth.riotgames.com/userinfo", headers={"Authorization": f"{auth.token_type} {auth.access_token}"})
    if userinfo.status_code != 200:
        print(f"error [{userinfo.status_code}]: could not get userinfo")
        exit()

    acc.set_name(userinfo.json()["acct"])

    store_resp = requests.get(f"https://pd.{acc.region}.a.pvp.net/store/v2/storefront/{auth.user_id}", headers={"X-Riot-Entitlements-JWT": f"{auth.entitlements_token}", "Authorization": f"{auth.token_type} {auth.access_token}"})
    if store_resp.status_code != 200:
        print(f"error [{store_resp.status_code}]: could not get store")
        exit()

    store = store_resp.json()["SkinsPanelLayout"]["SingleItemStoreOffers"]

    for item in store:
        acc.store.append(skin(item))

    return acc


def main():
    client_version = {requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]}
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"
    auth = RiotAuth()

    print(open("dump.txt", 'r', encoding= "utf-8").read())

    with open("accounts.txt", 'r') as f:
        with open("dump.txt", 'w', encoding = "utf-8") as d:
            for i, details in enumerate(f.read().splitlines()):
                if details == "---":
                    break

                acc = get_store(auth, account(details))

                s = f"{i + 1 :2d}. {acc}"

                print(s)

                d.write(s + "\n")


if __name__ == "__main__":
    main()
