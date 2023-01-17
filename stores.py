from riot_auth import RiotAuth
import asyncio
import requests
from termcolor import colored

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
    "Sentinels of Light Sheriff"
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
    "Guardian"
]

class account:
    def __init__(self, r_u_p: str):
        (r, u, p) = r_u_p.split(":", maxsplit=2)
        self.u = u
        self.p = p
        self.region = r
        self.name = ""
        self.tag = ""
        self.store = []

    def set_name(self, acct_key: dict):
        self.name = acct_key["game_name"]
        self.tag = acct_key["tag_line"]

    def __str__(self):
        return  "%32s -> %s" % (f"{self.name} #{self.tag} ({self.region})", "[ " + ", ".join([colored(x, 'red' if x in watchlist else 'yellow' if x.split()[-1] not in weapons else 'white') for x in self.store]) + " ]")


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

    store = store_resp.json()["SkinsPanelLayout"]["SingleItemOffers"]

    for item in store:
        skin_resp = requests.get(f"https://valorant-api.com/v1/weapons/skinlevels/{item}")
        if skin_resp.status_code != 200:
            print(f"error [{skin_resp.status_code}]: could not get skin")
            exit()

        acc.store.append(skin_resp.json()["data"]["displayName"])

    return acc


def main():
    client_version = {requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]}
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"
    auth = RiotAuth()

    with open("accounts.txt", 'r') as f:
        for i, details in enumerate(f.read().splitlines()):
            if details == '---':
                break
            acc = account(details)
            acc = get_store(auth, acc)

            print(f"{i + 1 :2d}. {acc}")


if __name__ == "__main__":
    main()
