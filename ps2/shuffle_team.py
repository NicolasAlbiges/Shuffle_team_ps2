import requests
import math
import json
import os
from socket import error as SocketError
import time

#http://census.daybreakgames.com/#service-id

#TODO Remove this bit a of code and get weapons from other files
def get_data():
  if os.path.exists('database/weapons.json'):
    with open('database/weapons.json', "r") as db:
      if db:
        return json.load(db)
      return "error"
  return "error"


def check_division_zero(dividend, divisor):
    if dividend == 0 or divisor == 0:
        return 0
    return dividend / divisor

class TeamManager:
    def __init__(self):
        self.pseudos_stats = []
        self.pseudos_names = []
        self.pseudos_names_lower = []
        self.player_not_found = []
        self.teams = []
        self.weapons = get_data()

    def get_stats_query(self):
        char_list = []
        ct = 0
        while self.pseudos_names_lower:
            players_temp = self.pseudos_names_lower[:6]
            self.pseudos_names_lower = self.pseudos_names_lower[6:]
            lower_pseudos = ','.join(players_temp)
            pseudos_id = "character?name.first_lower=" + lower_pseudos + "&c:limit=" + str(len(lower_pseudos))
            stat_query = "http://census.daybreakgames.com/s:elmecensusdata/get/ps2/" + pseudos_id + "&c:resolve=weapon_stat,weapon_stat_by_faction,stat_history"
            try:
                stat_response = requests.post(url=stat_query, headers={
                    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
                time.sleep(1)
            except SocketError as e:
                print("Error too big request I guess or another problem")
            if stat_response.status_code != 200 or len(stat_response.json()['character_list']) == 0:
                print("Error in query with code : %d"% stat_response.status_code)
            elif len(stat_response.json()['character_list']) != 0:
                char_list = char_list + stat_response.json()['character_list']
            if ct > 20:
                print("Error too big request I guess or another problem")
                return []
        return char_list

    def get_weapon_stats(self, stats):
        inf_weapon_hit_count = 0
        inf_weapon_fire_count = 0
        weapon_play_time = 0
        weapon_score = 0
        deaths_inf = 0
        deaths_air = 0
        if "weapon_stat" not in stats:
            print("Error in data")
            return 1
        for stat in stats["weapon_stat"]:
            if int(stat['item_id']) in self.weapons['weapons_air'] and stat["stat_name"] == "weapon_play_time":
                weapon_play_time = weapon_play_time + int(stat["value"])
            if int(stat["item_id"]) in self.weapons['weapons_air'] and stat["stat_name"] == "weapon_score":
                weapon_score = weapon_score + int(stat["value"])
            if int(stat['item_id']) in self.weapons['weapons'] and stat["stat_name"] == "weapon_hit_count":
                inf_weapon_hit_count = inf_weapon_hit_count + int(stat["value"])
            if int(stat["item_id"]) in self.weapons['weapons'] and stat["stat_name"] == "weapon_fire_count":
                inf_weapon_fire_count = inf_weapon_fire_count + int(stat["value"])
            if int(stat["item_id"]) in self.weapons['weapons_air'] and stat["stat_name"] == "weapon_deaths":
                deaths_air = int(stat["value"]) + deaths_air
            if int(stat["item_id"]) in self.weapons['weapons'] and stat["stat_name"] == "weapon_deaths":
                deaths_inf = int(stat["value"]) + deaths_inf
        acc = check_division_zero(inf_weapon_hit_count, inf_weapon_fire_count) * 100
        return acc, weapon_play_time, weapon_score, deaths_inf, deaths_air

    def get_weapon_stat_faction(self, stats):
        kills_air = 0
        kills_inf = 0
        kills_heads = 0
        weapon_vehicle_kills = 0
        if "weapon_stat_by_faction" not in stats:
            print("Error in data")
            return 1
        for stat in stats["weapon_stat_by_faction"]:
            if int(stat['item_id']) in self.weapons['weapons_air'] and stat["stat_name"] == "weapon_vehicle_kills":
                weapon_vehicle_kills = int(stat["value_vs"]) + int(stat["value_tr"]) + int(stat["value_nc"]) + weapon_vehicle_kills
            if int(stat['item_id']) in self.weapons['weapons_air'] and stat["stat_name"] == "weapon_kills":
                kills_air = int(stat["value_vs"]) + int(stat["value_tr"]) + int(stat["value_nc"]) + kills_air
            if int(stat['item_id']) in self.weapons['weapons'] and stat["stat_name"] == "weapon_kills":
                kills_inf = int(stat["value_vs"]) + int(stat["value_tr"]) + int(stat["value_nc"]) + kills_inf
            if int(stat['item_id']) in self.weapons['weapons'] and stat["stat_name"] == "weapon_headshots":
                kills_heads = int(stat["value_vs"]) + int(stat["value_tr"]) + int(stat["value_nc"]) + kills_heads
        hsr = check_division_zero(kills_heads, kills_inf) * 100
        return hsr, kills_inf, kills_air, weapon_vehicle_kills

    def get_stats_history(self, stats):
        deaths = 1
        kills = 0
        for stat in stats['stats']['stat_history']:
            if stat['stat_name'] == 'deaths':
                deaths = int(stat['all_time'])
            if stat['stat_name'] == 'kills':
                kills = int(stat['all_time'])
        return deaths, kills

    def get_personal_stats(self, stat_pseudo):
        acc, weapon_play_time, weapon_score, deaths_inf, deaths_air = self.get_weapon_stats(stat_pseudo['stats'])
        hsr, kills_inf, kills_air, weapon_vehicle_kills = self.get_weapon_stat_faction(stat_pseudo['stats'])
        #deaths, kills = self.get_stats_history(stat_pseudo)
        stats = {
            'kd_inf': check_division_zero(kills_inf, deaths_inf),
            'kd_air': check_division_zero(kills_air, deaths_air),
            'kpm_inf': check_division_zero(kills_inf, int(stat_pseudo['times']['minutes_played'])),
            'kpm_air': check_division_zero(kills_air / int(stat_pseudo['times']['minutes_played'])),
            'minutes_played': int(stat_pseudo['times']['minutes_played']),
            'acc': acc,
            'hsr': hsr,
            'ivi': acc * hsr
        }
        return stats

    def get_personal_stats_air(self, stat_pseudo):
        acc, weapon_play_time, weapon_score, deaths_inf, deaths_air = self.get_weapon_stats(stat_pseudo['stats'])
        hsr, kills_inf, kills_air, weapon_vehicle_kills = self.get_weapon_stat_faction(stat_pseudo['stats'])
        kd = check_division_zero(kills_air, deaths_air)
        stats = {
            'kd_air': kd,
            'minutes_played': weapon_play_time,
            'kills_air': kills_air,
            'Vkills': weapon_vehicle_kills,
        }
        return stats

    def add_player_to_teams(self, pseudos_stats, team, i):
        if i < len(pseudos_stats):
            team.append(pseudos_stats[i]['name'])
        if (i + 1) < len(pseudos_stats):
            team.append(pseudos_stats[i + 1]['name'])
        return team

    def make_teams(self, sorted_pseudos_stats, format_team):
        #nbr_teams = math.ceil((len(sorted_pseudos_stats) / 2) / format_team)
        #TODO Change by hand for two or one team
        nbr_teams = 1
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

    def make_score(self, kills, vkills, minutes, kd):
        if kd > 10:
            kd = 10
        if kills > 20000:
            kills = 20000
        days = (((minutes / 50) / 60) / 24)
        if days > 30:
            days = 30
        print("MAKING SCORE METHOD : The kills %f    The VKills %f    Days played %f   Vkills/minutes %f  and kd  %f" % ((kills / 1000), (vkills / 1000), days, (check_division_zero(vkills, (minutes / 60)) * 100), kd))
        score = (kills / 1000) + (vkills / 1000) + days + (check_division_zero(vkills, (minutes / 60)) * 100) + kd
        return score

    def shuffle_teams_air(self, player):
        stats = self.get_personal_stats_air(player)
        stats['name'] = player['name']['first']
        stats['score'] = self.make_score(stats['kills_air'], stats['Vkills'], stats['minutes_played'], stats['kd_air'])
        print("The name %s  The score : %d kills_air %f Vkills %f minute_played %f"% (stats['name'], stats['score'], stats['kills_air'] , stats['Vkills'], stats['minutes_played']))
        self.pseudos_stats.append(stats)

    def shuffle_teams_inf(self, player):
        stats = self.get_personal_stats(player)
        stats['name'] = player['name']['first']
        stats['score'] = (stats['kpm_inf'] * 100) + (stats['kd_inf'] * 100) + stats['ivi'] + (
                (stats['minutes_played'] / 60) / 24 / 2)
        print("The name %s  The score : %d kpm_inf %f kd_inf %f ivi %f minute_played %f"% (stats['name'], stats['score'], stats['kpm_inf'] , stats['kd_inf'], stats['ivi'], ((stats['minutes_played'] / 60) / 24 / 2)))
        self.pseudos_stats.append(stats)

    def shuffle_teams(self, pseudos_names, format_team, type_team):
        self.pseudos_names = pseudos_names
        self.pseudos_names_lower = [x.lower() for x in self.pseudos_names]
        print(self.pseudos_names_lower)
        stat_query = self.get_stats_query()
        if stat_query == "error":
            print("Error in the query")
            return []
        self.player_not_found = self.search(stat_query)
        for player in stat_query:
            if "stats" not in player or "weapon_stat_by_faction" not in player['stats'] or "weapon_stat" not in player['stats'] or "stat_history" not in player['stats']:
                print("Player stats not found : ", player)
                self.player_not_found.append(player['name']['first'])
                #TODO Rajouter du debug pour le bot et afficher le gars manquant
            elif type_team == "air":
                self.shuffle_teams_air(player)
            elif type_team == "inf":
                self.shuffle_teams_inf(player)
        sorted_pseudos_stats = sorted(self.pseudos_stats, key=lambda i: i['score'], reverse=True)
        teams = self.make_teams(sorted_pseudos_stats, format_team)
        self.teams = []
        self.pseudos_stats = []
        return teams