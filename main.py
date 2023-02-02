from riot_auth import RiotAuth
from riot_auth.auth_exceptions import RiotAuthenticationError
import requests
from termcolor import colored

from account import account
from skin import skin


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
    client_version: str = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{client_version} %s (Windows;10;;Professional, x64)"

    with open("accounts.txt", 'r') as f:
        with open("dump.txt", 'w', encoding = "utf-8") as d:
            accs = []

            for i, details in enumerate(f.read().splitlines()):
                if details == "---":
                    break
                acc = account(details)
                try:
                    acc.get_store()
                except RiotAuthenticationError:
                    print(f"error: invalid user/pass for account \'{acc.u}\'")
                    continue

                accs.append(acc)
                print(f"  parsed {i + 1} account{'s' if i != 0 else ''}... please wait :)", end = '\r')

            accs.sort(key = lambda x: x.score, reverse = True)

            for i, acc in enumerate(accs):
                print(acc.print(i))
                d.write(acc.write(i))


if __name__ == "__main__":
    main()
