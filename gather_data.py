# from riotwatcher import LolWatcher, ApiError

import cassiopeia as cass
import csv
import numpy as np


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
        self._match_ids = []

    def by_summoner_name(self, summoner_name, n_matches=30):

        summoner = self._api.get_summoner(name=summoner_name)
        match_history = self._api.get_match_history(summoner, end_index=n_matches)
        # champ_mastery = self._api.get_champion_masteries(summoner)

        matches = self._filter_matches(match_history, n_matches)

        for m in matches:
            self.gather_match_info(m)

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
            self.by_summoner_name(entry.summoner.name, n_matches=n_matches)

    def by_match_ids(self, match_ids):
        for m_id in match_ids:
            self.by_match_id(m_id)

    def by_match_id(self, match_id):
        match = self._api.get_match(match_id)
        self.gather_match_info(match)

    def gather_match_info(self, m):
        m_info = []
        bteam_largest_killing_spree = 0
        bteam_largest_multi_kill = 0
        bteam_highest_champ_lvl = 1
        bteam_best_kda = 0
        rteam_largest_killing_spree = 0
        rteam_largest_multi_kill = 0
        rteam_highest_champ_lvl = 1
        rteam_best_kda = 0

        bteam_totals = []
        rteam_totals = []
        for b_part, r_part in zip(m.blue_team.participants, m.red_team.participants):
            b_stats, r_stats = b_part.stats, r_part.stats
            bteam_totals.append(
                [
                    b_stats.kills,
                    b_stats.assists,
                    b_stats.gold_earned,
                    b_stats.gold_spent,
                    b_stats.vision_score,
                    b_stats.wards_placed,
                    b_stats.wards_killed,
                    b_stats.total_minions_killed,
                    b_stats.total_damage_dealt,
                    b_stats.total_damage_dealt_to_champions,
                    b_stats.total_damage_taken,
                    b_stats.total_heal,
                    b_stats.damage_self_mitigated,
                    b_stats.total_time_crowd_control_dealt,
                ]
            )
            rteam_totals.append(
                [
                    r_stats.kills,
                    r_stats.assists,
                    r_stats.gold_earned,
                    r_stats.gold_spent,
                    r_stats.vision_score,
                    r_stats.wards_placed,
                    r_stats.wards_killed,
                    r_stats.total_minions_killed,
                    r_stats.total_damage_dealt,
                    r_stats.total_damage_dealt_to_champions,
                    r_stats.total_damage_taken,
                    r_stats.total_heal,
                    r_stats.damage_self_mitigated,
                    r_stats.total_time_crowd_control_dealt,
                ]
            )

            if b_stats.largest_killing_spree > bteam_largest_killing_spree:
                bteam_largest_killing_spree = b_stats.largest_killing_spree

            if b_stats.largest_multi_kill > bteam_largest_multi_kill:
                bteam_largest_multi_kill = b_stats.largest_multi_kill

            if b_stats.level > bteam_highest_champ_lvl:
                bteam_highest_champ_lvl = b_stats.level

            if b_stats.kda > bteam_best_kda:
                bteam_best_kda = b_stats.kda

            if r_stats.largest_killing_spree > rteam_largest_killing_spree:
                rteam_largest_killing_spree = r_stats.largest_killing_spree

            if r_stats.largest_multi_kill > rteam_largest_multi_kill:
                rteam_largest_multi_kill = r_stats.largest_multi_kill

            if r_stats.level > rteam_highest_champ_lvl:
                rteam_highest_champ_lvl = r_stats.level

            if r_stats.kda > rteam_best_kda:
                rteam_best_kda = r_stats.kda

        bteam_totals = np.sum(np.asarray(bteam_totals).T, axis=1)
        rteam_totals = np.sum(np.asarray(rteam_totals).T, axis=1)

        m_info.append(m.duration.seconds)
        m_info.append(0 if m.blue_team.first_dragon else 1)
        m_info.append(0 if m.blue_team.first_baron else 1)
        m_info.append(0 if m.blue_team.first_inhibitor else 1)
        m_info.append(0 if m.blue_team.first_rift_herald else 1)
        m_info.append(0 if m.blue_team.first_blood else 1)
        # Blue team stats
        m_info.append(m.blue_team.baron_kills)
        m_info.append(m.blue_team.dragon_kills)
        m_info.append(m.blue_team.inhibitor_kills)
        m_info.append(m.blue_team.rift_herald_kills)
        m_info.append(m.blue_team.tower_kills)
        m_info.append(bteam_largest_killing_spree)
        m_info.append(bteam_largest_multi_kill)
        m_info.append(bteam_highest_champ_lvl)
        m_info.append(bteam_best_kda)
        m_info.extend(bteam_totals.tolist())

        # Red team stats
        m_info.append(m.red_team.baron_kills)
        m_info.append(m.red_team.dragon_kills)
        m_info.append(m.red_team.inhibitor_kills)
        m_info.append(m.red_team.rift_herald_kills)
        m_info.append(m.red_team.tower_kills)
        m_info.append(rteam_largest_killing_spree)
        m_info.append(rteam_largest_multi_kill)
        m_info.append(rteam_highest_champ_lvl)
        m_info.append(rteam_best_kda)
        m_info.extend(rteam_totals.tolist())

        # Output column
        m_info.append(0 if m.blue_team.win else 1)

        self._data.append(m_info)
        self._match_ids.append(m.id)

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
        with open(f"data/match_ids.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer = csv.writer(self._match_ids)


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
