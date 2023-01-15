from riot_auth import RiotAuth
import asyncio
import requests

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
        return f"{self.name} #{self.tag} -> [ %s ]" % (", ".join([x.lower() for x in self.store]))


def get_store(acc: account) -> account:
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

    with open("accounts.txt", 'r') as f:
        for details in f.read().splitlines():
            acc = account(details)
            acc = get_store(acc)

            print(acc)


if __name__ == "__main__":
    main()
