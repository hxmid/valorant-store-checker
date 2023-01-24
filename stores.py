from riot_auth import RiotAuth
import asyncio
import requests
from termcolor import colored

watchlist_tiers = {
    "s": {
        "colour": "red",
        "skins": [
            "Xenohunter Knife",
            "Protocol 781-A Sheriff",
            "VALORANT GO! Vol. 1 Knife",
        ],
        "value": 6
    },
    "a": {
        "colour": "yellow",
        "skins": [
            "Protocol 781-A Phantom",
            "Sovereign Sword",
            "RGX 11z Pro Vandal",
            "Sentinels of Light Sheriff",
        ],
        "value": 5
    },
    "b": {
        "colour": "green",
        "skins": [
            "Forsaken Vandal",
            "Glitchpop Vandal",
            "Gaia's Vengeance Vandal",
            "Sentinels of Light Vandal"
        ],
        "value": 4
    },
    "c": {
        "colour": "cyan",
        "skins": [
            "Ruination Phantom",
            "Araxys Vandal",
            "Catrina",
            "Magepunk Sheriff",
            "Singularity Phantom",
        ],
        "value": 3
    },
    "d": {
        "colour": "blue",
        "skins": [
            "Oni Phantom",
            "Blade of Chaos",
            "Araxys Bio Harvester",
        ],
        "value": 2
    },
    "e": {
        "colour": "magenta",
        "skins": [
            "Oni Claw",
        ],
        "value": 1
    }
}


class skin:
    VP_INFO = requests.get("https://valorant-api.com/v1/currencies").json()["data"][0]

    def __init__(self, store_item: dict):
        self.cost = store_item["Cost"][skin.VP_INFO["uuid"]]

        item_id = store_item["OfferID"]

        skin_resp = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{item_id}")
        if skin_resp.status_code != 200:
            print(f"error [{skin_resp.status_code}]: could not get skin")
            exit()

        self.name = skin_resp.json()["data"]["displayName"]

        for tier in watchlist_tiers:
            if self.name in watchlist_tiers[tier]["skins"]:
                self.colour = watchlist_tiers[tier]["colour"]
                self.value = watchlist_tiers[tier]["value"]
                break
        else:
            self.colour = "grey"
            self.value = 0

    def __str__(self):
        return colored(f"<{self.cost} VP> {self.name}", self.colour)

class account:
    def __init__(self, credentials: str):
        (self.region, self.u, self.p) = credentials.split(":", maxsplit=2)
        self.name: str = ""
        self.tag:str = ""
        self.store: list(skin) = []
        self.score = -4

    def set_name(self, acct_key: dict):
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def add_skin(self, s: skin):
        self.store.append(s)
        self.score += pow(2, s.value)

    def __str__(self):
        if self.name == None:
            self.name = ""
        if self.tag == None:
            self.tag = ""
        return  f"{self.u + ':' : <25} {self.name : >16} #{self.tag : <5} ({self.score : 2d}) -> " + "[ " + ", ".join([str(x) for x in self.store]) + " ]"

    def print(self, i):
        return f"{i + 1 :2d}. {self}"

    def write(self, i):
        return self.print(i) + "\n"

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
        acc.add_skin(skin(item))

    return acc


def main():
    while True:
        response = input("[g]enerate new or [d]ump previous ? ")

        if response == "g":
            generate()
            return

        elif response == "d":
            dump()
            return

        print(f"'{response}' wasn't an option. try again")

def dump():
    print(open("dump.txt", 'r', encoding= "utf-8").read())

def generate():
    client_version = {requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]}
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"
    auth = RiotAuth()

    with open("accounts.txt", 'r') as f:
        with open("dump.txt", 'w', encoding = "utf-8") as d:
            accs = []

            for i, details in enumerate(f.read().splitlines()):
                if details == "---":
                    break

                accs.append(get_store(auth, account(details)))

                print(f"  parsed {i + 1} account{'s' if i != 0 else ''}... please wait :)", end = '\r')

            accs.sort(key = lambda x: x.score, reverse = True)

            for i, acc in enumerate(accs):
                print(acc.print(i))
                d.write(acc.write(i))



if __name__ == "__main__":
    main()
