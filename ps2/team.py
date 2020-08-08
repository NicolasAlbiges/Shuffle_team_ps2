import requests


def get_outfit_member_query(team_tag):
    team_tag_lower = "?alias_lower=" + team_tag.lower()
    outfit_member = "http://census.daybreakgames.com/get/ps2/outfit/" + team_tag_lower + "&c:hide=name_lower,alias_lower,time_created,time_created_date,leader_character_id&c:join=outfit_member^inject_at:members^list:1^show:character_id%27rank(character_name^inject_at:name^on:character_id^to:character_id^show:name.first)"
    outfit_member_response = requests.get(outfit_member)
    if outfit_member_response.status_code != 200 or len(outfit_member_response.json()['outfit_list']) == 0:
        print("Error in query")
        return "error"
    return outfit_member_response.json()['outfit_list']


def get_outfit_member_id(team_tag):
    outfit_member_query = get_outfit_member_query(team_tag)
    if outfit_member_query == "error":
        return "error"
    outfit_members = []
    for outfit_member in outfit_member_query[0]['members']:
        outfit_members.append({
            'character_id': outfit_member['character_id'],
            'name': outfit_member['name']['name']['first']
        })
    return {"members": outfit_members, "tag": team_tag.lower()}
