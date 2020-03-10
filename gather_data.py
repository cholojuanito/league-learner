# from riotwatcher import LolWatcher, ApiError

import cassiopeia as cass


class Gatherer:
    def __init__(self, api_key):
        super().__init__()
        self._api = cass
        # self._api = LolWatcher(api_key)
        self._api.set_riot_api_key(api_key)
        self._data = []

    def main(self, region, summoner_name, n_matches):
        self._api.set_default_region(region)
        sum_resp = self._api.get_summoner(name=summoner_name)
        print(sum_resp)

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
                        n_matches = args[2]

                        gatherer.main(region, summoner_name, n_matches)
            except Exception as e:
                print(f"Exception: {e}")

        else:
            # Just a one time request
            region = sys.argv[1]
            summoner_name = sys.argv[2]
            n_matches = sys.argv[3]

            gatherer.main(region, summoner_name, n_matches)

        gatherer.export_csv()

