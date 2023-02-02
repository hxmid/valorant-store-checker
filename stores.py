from riot_auth import RiotAuth
from riot_auth.auth_exceptions import RiotAuthenticationError
import asyncio
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


class skin:
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


class account:
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


def get_store(acc: account) -> account:
    client_version: str = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"
    asyncio.set_event_loop(asyncio.new_event_loop())
    auth = RiotAuth()
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


def main() -> None:
    while True:
        response = input("[g]enerate new or [d]ump previous ? ")

        if response == "g":
            generate()
            return

        elif response == "d":
            dump()
            return

        print(f"'{response}' wasn't an option. try again")


def dump() -> None:
    print(open("dump.txt", 'r', encoding = "utf-8").read())


def generate() -> None:


    with open("accounts.txt", 'r') as f:
        with open("dump.txt", 'w', encoding = "utf-8") as d:
            accs = []

            for i, details in enumerate(f.read().splitlines()):
                if details == "---":
                    break
                acc = account(details)
                try:
                    accs.append(get_store(acc))
                except RiotAuthenticationError:
                    print(f"error: invalid user/pass for account \'{acc.u}\'")
                    continue

                print(f"  parsed {i + 1} account{'s' if i != 0 else ''}... please wait :)", end = '\r')

            accs.sort(key = lambda x: x.score, reverse = True)

            for i, acc in enumerate(accs):
                print(acc.print(i))
                d.write(acc.write(i))


if __name__ == "__main__":
    main()
