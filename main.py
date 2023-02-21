import json
from time import sleep
from typing import Dict, List
from riot_auth import RiotAuth
from riot_auth.auth_exceptions import RiotAuthenticationError, RiotRatelimitError
# from aiohttp.client_exceptions import ClientResponseError
import requests
import argparse
# from threading import Thread
# from time import sleep

from account import account

# THREADS = []

def main(gen: bool) -> None:
    if gen:
        generate()
    else:
        dump()


def dump() -> None:
    data: List[Dict] = json.load(open("stores.json", 'r'))
    stores: List[account] = []

    for x in data:
        a = account()
        a.fromdict(x)
        if a.score > 0:
            stores.append(a)


    stores.sort(key = lambda x: x.score, reverse = True)

    for i, s in enumerate(stores):
        print(s.print(i))

    with open("new_stores.json", 'w') as f:
        json.dump([acc.asdict() for acc in stores], f, indent = 2)


def generate() -> None:
    client_version: str = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"

    with open("accounts.txt", 'r') as f:
        with open("dump.txt", 'w', encoding = "utf-8") as d:
            accs: List[account] = []

            for i, details in enumerate(f.read().splitlines()):

                if not details:
                    continue

                if details.startswith("//"):
                    continue

                if details == "---":
                    break

                acc = account(details)

                while True:
                    try:
                        acc.get_store()

                        # t = Thread(target=acc.get_store)
                        # THREADS.append(t)
                        # sleep(1)
                        # t.start()

                    except RiotAuthenticationError as e:
                        print(f"error: invalid user/pass for account '{acc.u}'")
                        raise e

                    except RiotRatelimitError:
                        print(f"error: rate limited, trying again :)  ", end = "\r")
                        sleep(15)
                        continue

                    else:
                        break

                accs.append(acc)
                print(f"  parsed {i + 1} account{'s' if i else ''}... please wait :)", end = '\r')

            # for t in THREADS:
            #     t.join()

            with open("new_accounts.txt", 'w') as f:
                for acc in accs:
                    if acc.store > 0:
                        f.write(f"{acc.region}:{acc.u}:{acc.p}\n")

            accs.sort(key = lambda x: x.score, reverse = True)

            with open("stores.json", 'w') as f:
                for i, acc in enumerate(accs):
                    print(acc.print(i))
                json.dump([acc.asdict() for acc in accs], f, indent = 2)



if __name__ == "__main__":

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "-g", "--gen",
        action = "store_true",
        dest = "g",
        help = "regenerate instead of dumping previous"
    )

    main(argparser.parse_args().g)
