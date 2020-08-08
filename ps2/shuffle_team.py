import requests
import math

#http://census.daybreakgames.com/#service-id


class TeamManager:
    def __init__(self):
        self.pseudos_stats = []
        self.pseudos_names = []
        self.pseudos_names_lower = []
        self.player_not_found = []
        self.teams = []

    def get_stats_query(self):
        str_team_names = ','.join(self.pseudos_names_lower)
        pseudo_id = "character?name.first_lower=" + str_team_names + "&c:limit=" + str(len(str_team_names))
        stat_query = "http://census.daybreakgames.com/s:elmecensusdata/get/ps2/" + pseudo_id + "&c:resolve=online_status&c:join=type:profile%5Eon:profile_id%5Eto:profile_id%5Elist:0%5Eshow:name.en%27image_path%5Einject_at:main_class&c:join=type:characters_stat_history%5Eon:character_id%5Eto:character_id%5Elist:0%5Eshow:stat_name%27all_time%5Elist:1%5Einject_at:stats_history%5Eterms:stat_name=deaths%27stat_name=kills&c:join=type:characters_stat%5Eon:character_id%5Eto:character_id%5Elist:0%5Eshow:stat_name%27value_forever%27profile_id%5Elist:1%5Einject_at:stats%5Eterms:stat_name=score%27stat_name=hit_count%27stat_name=fire_count(profile%5Eon:profile_id%5Eto:profile_type_id%5Eshow:name.en%5Einject_at:class)"
        print(stat_query)
        stat_response = requests.get(stat_query)
        if stat_response.status_code != 200 or len(stat_response.json()['character_list']) == 0:
            print("Error in query")
            return "error"
        return stat_response.json()

    def get_personal_stats(self, stat_pseudo):
        stats = {
            'kd': int(stat_pseudo['stats_history'][1]['all_time']) / int(stat_pseudo['stats_history'][0]['all_time']),
            'kpm': int(stat_pseudo['stats_history'][1]['all_time']) / int(stat_pseudo['times']['minutes_played']),
            'minutes_played': int(stat_pseudo['times']['minutes_played'])}

        fire_count = 0
        hit_count = 0
        for stat in stat_pseudo['stats']:
            if stat['stat_name'] == 'fire_count':
                fire_count = fire_count + int(stat['value_forever'])
            if stat['stat_name'] == 'hit_count':
                hit_count = hit_count + int(stat['value_forever'])
        stats['accuracy'] = (hit_count / fire_count) * 100
        return stats

    def add_player_to_teams(self, pseudos_stats, team, i):
        if i < len(pseudos_stats):
            team.append(pseudos_stats[i]['name'])
        if (i + 1) < len(pseudos_stats):
            team.append(pseudos_stats[i + 1]['name'])
        return team

    def make_teams(self, sorted_pseudos_stats, format_team):
        nbr_teams = math.ceil((len(sorted_pseudos_stats) / 2) / format_team)
        self.teams.append(self.player_not_found)
        #TODO Prendre la valeur au dessus
        i = 1
        i_player = 0
        while i_player != nbr_teams:
            self.teams.append([])
            self.teams.append([])
            self.teams[i].append(sorted_pseudos_stats[i_player]['name'])
            i += 2
            i_player += 1
        i = 1
        odd = 1
        while i_player <= len(sorted_pseudos_stats):
            if (odd % 2) == 0:
                self.teams[i] = self.add_player_to_teams(sorted_pseudos_stats, self.teams[i], i_player)
            else:
                self.teams[i + 1] = self.add_player_to_teams(sorted_pseudos_stats, self.teams[i + 1], i_player)
            if i >= nbr_teams:
                i = 1
                odd = 1 + odd
            else:
                i += 2
            i_player += 2
        return self.teams

    def search(self, players):
        people_not_found = self.pseudos_names_lower
        for player in players:
            if player['name']['first_lower'] in people_not_found:
                people_not_found.remove(player['name']['first_lower'])
        return people_not_found

    def shuffle_teams(self, pseudos_names, format_team):
        self.pseudos_names = pseudos_names
        self.pseudos_names_lower = [x.lower() for x in self.pseudos_names]
        print(self.pseudos_names_lower)
        stat_query = self.get_stats_query()
        if stat_query == "error":
            print("Error in the query")
            return
        self.player_not_found = self.search(stat_query['character_list'])
        for player in stat_query['character_list']:
            stats = self.get_personal_stats(player)
            stats['name'] = player['name']['first']
            stats['score'] = (stats['kpm'] * 10) + (stats['kd'] * 10) + stats['accuracy']
            self.pseudos_stats.append(stats)
        sorted_pseudos_stats = sorted(self.pseudos_stats, key=lambda i: i['score'], reverse=True)
        teams = self.make_teams(sorted_pseudos_stats, format_team)
        self.teams = []
        self.pseudos_stats = []
        return teams
