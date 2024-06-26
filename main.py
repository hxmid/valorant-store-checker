#!/usr/env/bin python

import json
from time import sleep
from typing import Dict, List
from aiohttp import ClientOSError, ServerDisconnectedError
from custom_auth import RiotAuth as CustomAuth
from riot_auth import RiotAuth
from riot_auth.auth_exceptions import RiotAuthenticationError, RiotRatelimitError
import requests
import argparse
from aiohttp.client_exceptions import ClientResponseError, ClientConnectorError

from account import account

def main(d: bool) -> None:
    if d:
        dump()
    else:
        generate()


def dump() -> None:
    data: List[Dict] = json.load(open("stores.json", "r"))
    stores: List[account] = []

    for x in data:
        a = account().fromdict(x)
        if a.score() >= 0:
            stores.append(a)

    stores.sort(key = lambda x: x.score(), reverse = True)

    for i, s in enumerate(stores):
        print(s.print(i))

    with open("new_stores.json", "w") as f:
        json.dump([acc.asdict() for acc in stores], f, indent = 2)


def generate() -> None:
    client_version: str = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"

    with open("accounts.txt", "r") as f:
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

                except RiotAuthenticationError as e:
                    print(f"error: invalid user/pass for account '{acc.u}'. skipping ...")
                    break

                except ClientResponseError or RiotRatelimitError:
                    print(f"debug: rate limited, waiting 15 seconds before retrying (try switching vpn location)")
                    sleep(15)
                    continue

                except requests.exceptions.ConnectionError or ServerDisconnectedError or ClientOSError or ClientConnectorError or ConnectionRefusedError:
                    print(f"debug: unreachable, switching ...")
                    continue

                except Exception as e:
                    if CustomAuth.is_proxy_exception(e):
                        print(f"debug: {str(e).lower()}, switching ...")
                    elif isinstance(e, RuntimeError):
                        print(f"error: failed to get store for account, retrying ...")
                        sleep(15)
                    else:
                        raise e

                else:
                    break

            if acc.score() >= 0:
                accs.append(acc)

            print(f"\tparsed {i + 1} account{'s' if i else ' '}  ...")
            #sleep(60)

        with open("new_accounts.txt", "w") as f:
            for acc in accs:
                if acc.score() >= 0:
                    f.write(f"{acc.region}:{acc.u}:{acc.p}\n")

        accs.sort(key = lambda x: x.score(), reverse = True)

        for i, acc in enumerate(accs):
            print(acc.print(i))

        with open("stores.json", "w") as f:
            json.dump([acc.asdict() for acc in accs], f, indent = 2)



if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-d", "--dump",
        action = "store_true",
        dest = "dump",
        help = "dump previous instead of regenerating"
    )
    main(argparser.parse_args().dump)
