# from riotwatcher import LolWatcher, ApiError

import cassiopeia as cass


class Gatherer:
    def __init__(self, api_key):
        super().__init__()
        self._api = cass
        # self._api = LolWatcher(api_key)
        self._api.set_riot_api_key(api_key)
        self._data = []

    def main(self, region, summoner_name, n_matches=20):
        matches = []

        self._api.set_default_region(region)
        summoner = self._api.get_summoner(name=summoner_name)
        match_history = self._api.get_match_history(summoner, end_index=n_matches)
        print(match_history)
        for match in match_history:
            print(f"Mode: {match.mode} and remake {match.is_remake}")
            if len(matches) >= n_matches:
                break
            if match.mode == self._api.GameMode.classic and not match.is_remake:
                matches.append(match)

        for m in matches:
            pass

    def export_csv(self):
        pass


if __name__ == "__main__":
    import sys
    import os

    api_key = os.environ["RIOT_API_KEY"]
    gatherer = Gatherer(api_key)

    if len(sys.argv) > 1:
        if sys.argv[1] == "f":
            # Read a file
            file_name = sys.argv[2]
            try:
                with open(file_name, "r") as f:
                    for line in f:
                        args = line.split(" ")
                        region = args[0]
                        summoner_name = args[1]

                        gatherer.main(region, summoner_name)
            except Exception as e:
                print(f"Exception: {e}")

        else:
            # Just a one time request
            region = sys.argv[1]
            summoner_name = sys.argv[2]

            gatherer.main(region, summoner_name)

        gatherer.export_csv()

