# from riotwatcher import LolWatcher, ApiError

import cassiopeia as cass
import csv


class Gatherer:
    def __init__(self, api_key):
        super().__init__()
        self._api = cass
        self._api.set_riot_api_key(api_key)
        self._api.set_default_region(self._api.Region.north_america)
        self.queue = self._api.Queue.ranked_solo_fives
        self.mode = self._api.GameMode.classic
        self.game_type = self._api.GameType.matched
        self._data = []

    def by_summoner_name(self, summoner_name, n_matches=50):

        summoner = self._api.get_summoner(name=summoner_name)
        match_history = self._api.get_match_history(summoner, end_index=n_matches)
        # champ_mastery = self._api.get_champion_masteries(summoner)

        matches = self._filter_matches(match_history, n_matches)

        self.gather_match_info(matches)

    def by_elo(self, elo, n_matches=50):
        self._elo = elo
        league = []
        if self._elo == "chal":
            league = self._api.get_challenger_league(queue=self.queue)
        elif self._elo == "gm":
            league = self._api.get_grandmaster_league(queue=self.queue)
        elif self._elo == "mast":
            league = self._api.get_master_league(queue=self.queue)
        else:
            # Get from plat or diamond
            league = self._api.get_challenger_league(queue=self.queue)

        for entry in league.entries:
            self.by_summoner_name(entry.summoner.name)

    def gather_match_info(self, matches):
        for m in matches:
            m_info = []
            m_info.append(m.duration.seconds)
            m_info.append(0 if m.blue_team.first_dragon else 1)
            m_info.append(0 if m.blue_team.first_baron else 1)
            m_info.append(0 if m.blue_team.first_inhibitor else 1)
            m_info.append(0 if m.blue_team.first_rift_herald else 1)
            m_info.append(0 if m.blue_team.first_blood else 1)
            # Per team stats
            m_info.append(m.blue_team.baron_kills)
            m_info.append(m.blue_team.dragon_kills)
            m_info.append(m.blue_team.inhibitor_kills)
            m_info.append(m.blue_team.rift_herald_kills)
            m_info.append(m.blue_team.tower_kills)
            m_info.append(m.red_team.baron_kills)
            m_info.append(m.red_team.dragon_kills)
            m_info.append(m.red_team.inhibitor_kills)
            m_info.append(m.red_team.rift_herald_kills)
            m_info.append(m.red_team.tower_kills)

            # Output column
            m_info.append(0 if m.blue_team.win else 1)

            self._data.append(m_info)

    def _filter_matches(self, match_history, n_matches):
        matches = []
        for match in match_history:
            try:
                if len(matches) >= n_matches:
                    break
                if not match.exists:
                    continue
                if (
                    match.mode == self.mode
                    and match.queue == self.queue
                    and not match.is_remake
                    and match.type == self.game_type
                ):
                    # Filter out matches that are not:
                    #   1. Classic mode
                    #   2. Ranked solo queue
                    #   3. Full length (not a remake)
                    #   4. Matchmade (not custom or tournament)
                    matches.append(match)
            except self._api.datastores.riotapi.common.APIError as err:
                print(err)
                continue

        return matches

    def export_csv(self):
        with open(f"data/{self._elo}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self._data)


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
                        summoner_name = args[0]

                        gatherer.by_summoner_name(summoner_name)
            except Exception as e:
                print(f"Exception: {e}")
        elif sys.argv[1] == "e":
            elo = sys.argv[2]

            gatherer.by_elo(elo)
        else:
            # Just a one time request
            summoner_name = sys.argv[1]

            gatherer.by_summoner_name(summoner_name)

        gatherer.export_csv()

