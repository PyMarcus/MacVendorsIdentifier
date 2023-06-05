import argparse
import json
import os
import sys
from configparser import ConfigParser
from nss import NSSProxy
from termcolor import colored


profile_path = "~/.mozilla/firefox-esr"
DEFAULT_ENCODING = "utf-8"
password_list = list[dict[str, str]]


class Firefox:
    def __init__(self, basepath: str = ''):
        self.profile = None
        self.basepath = basepath
        self.proxy = NSSProxy()

        if not self.basepath:
            self._get_args()

    def _get_args(self) -> str:
        parser = argparse.ArgumentParser(description='Browser Over')
        parser.add_argument('-p', '--path', dest='firefox_path', type=str, help='Firefox dir path', required=True)
        args = parser.parse_args()
        self.basepath = os.path.expanduser(args.firefox_path)

    def load_profile(self, profile):
        self.profile = profile
        self.proxy.initialize(self.profile)

    def unload_profile(self):
        self.proxy.shutdown()

    def getCredentialsJson(self):
        db = os.path.join(self.basepath, self.profile, "logins.json")

        if not os.path.isfile(db):
            print(colored('\nUser has no saved passwords: logins.json', 'red'))
            return

        with open(db) as fh:
            data = json.load(fh)
            logins = data["logins"]
            for i in logins:
                yield (i["hostname"], i["encryptedUsername"],
                       i["encryptedPassword"], i["encType"])

    def decrypt_passwords(self) -> password_list:
        credentials = self.getCredentialsJson()

        outputs: list[dict[str, str]] = []

        for url, user, passw, enctype in credentials:
            if enctype:
                try:
                    user = self.proxy.decrypt(user)
                    passw = self.proxy.decrypt(passw)
                except (TypeError, ValueError) as e:
                    continue

            output = {"url": url, "user": user, "password": passw}
            outputs.append(output)
        return outputs

    def decrypt_passwords_2(self, username):
        with open('./.venv/pass.json') as fh:
            data = json.load(fh)
            for user, info in data.items():
                if user == username:
                    credentials = []
                    for item in info:
                        url = item.get("url", "")
                        user = item.get("user", "")
                        password = item.get("password", "")
                        output = {"url": url, "user": user, "password": password}
                        credentials.append(output)
                    return credentials

    def printOutput_2(self, list):
        if len(list) == 0:
            print(colored('\nUser has no saved passwords: logins.json', 'red'))
            return

        for d in list:
            record: str = (
                f"\nWebsite:  '{d['url']}'\n"
                f"Username: '{d['user']}'\n"
                f"Password: '{d['password']}'"
            )
            print(record)

    def printOutput(self, pwstore: password_list):
        for output in pwstore:
            if output['url'] == 'chrome://FirefoxAccounts':
                continue
            record: str = (
                f"\nWebsite:  '{output['url']}'\n"
                f"Username: '{output['user']}'\n"
                f"Password: '{output['password']}'"
            )
            print(record)

    def get_sections(self, profiles):
        sections = {}
        for i, section in enumerate(profiles.sections(), start=1):
            if section.startswith("Profile"):
                profile_path = profiles.get(section, "Path")
                sections[str(i)] = profile_path
        return sections

    def read_profiles(self, basepath):
        profile_ini = os.path.join(basepath, "profiles.ini")

        if not os.path.isfile(profile_ini):
            print("File not found: profiles.ini", file=sys.stderr)
            sys.exit(1)

        profiles = ConfigParser()
        profiles.read(profile_ini, encoding=DEFAULT_ENCODING)
        return profiles

    def get_available_profiles(self):
        profiles: ConfigParser = self.read_profiles(self.basepath)
        return self.get_sections(profiles)

    def get_profile(self, profiles_list: dict):
        section = profiles_list["1"]
        print("Using profile: ", section)

        section = section
        profile = os.path.join(self.basepath, section)
        return profile

    def exit(self):
        print(colored('\n\nExiting...', 'red'))
        self.unload_profile()
        sys.exit(0)

    def process_profiles(self, selected_profiles: dict or str):
        if isinstance(selected_profiles, dict):
            print(colored('Processing all profiles', 'yellow'))
            for profile in selected_profiles.values():
                username = profile.split(".")[-1]
                print(colored(f'\n[*] Processing profile: {username}', 'yellow'))
                self.load_profile(profile)
                outputs = self.decrypt_passwords_2(username)
                self.printOutput_2(outputs)
                self.unload_profile()
        else:
            username = selected_profiles.split(".")[-1]
            print(colored(f'\n[*] Processing profile: {username}', 'yellow'))
            self.load_profile(selected_profiles)
            outputs = self.decrypt_passwords_2(username)
            self.printOutput_2(outputs)
            self.unload_profile()

    def select_profile(self, profiles_list: dict):
        while True:
            try:
                print(colored('\n==============================', 'yellow'))
                print(colored('Select a profile:', 'yellow'))
                for key, value in profiles_list.items():
                    print(colored(f'[{key}]', 'yellow'), colored(f'{value.split(".")[-1]}', 'white'))
                print(colored('\n[*]', 'yellow'), colored('All profiles', 'white'))
                print(colored('[q]', 'yellow'), colored('Quit\n', 'white'))

                choice = input(colored('=> ', 'yellow'))
                if choice in profiles_list.keys():
                    self.process_profiles(profiles_list[choice])
                elif choice == '*':
                    self.process_profiles(profiles_list)
                elif choice == 'q':
                    self.exit()
                else:
                    print(colored('Invalid choice', 'red'))
            except Exception as e:
                print(colored(f'Error: {e}', 'red'))
            except KeyboardInterrupt:
                self.exit()

    def run(self):
        profiles_list = self.get_available_profiles()
        while True:
            self.select_profile(profiles_list)


firefox = Firefox()
firefox.run()

# python3 firefox.py -p "~/.mozilla/firefox-esr"