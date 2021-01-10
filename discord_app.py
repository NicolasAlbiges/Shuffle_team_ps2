import discord
import os
from ps2 import shuffle_team
from ps2 import team
from ps2 import pseudos
from ps2 import googleSheets
from database import db
from dotenv import load_dotenv

load_dotenv()
discord_token = os.environ.get("discord")
teamManager = shuffle_team.TeamManager()
client = discord.Client()
pseudo = pseudos.Pseudo()
googleSheets = googleSheets.GoogleSheets()
db_data = db.get_data()
if db_data != "error":
    pseudo.add_outfits(db_data['outfits'])

def shuffle_teams_result(shuffle_team_query, format_team):
    resp = ""
    if len(shuffle_team_query) == 0:
      return "The bot couldnt retreive the players, something went wrong"
    if len(shuffle_team_query[0]) != 0:
      str_lost_names = ', '.join(shuffle_team_query[0])
      resp = "Je n'ai pas réussis à trouver ces perosnnes : " + str_lost_names + "\n"
    googleSheets.write_team(shuffle_team_query)
    resp = resp + "Les teams sont prêtes au format" + str(format_team) + "vs" + str(format_team)
    return resp

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        await message.channel.send("Voici les commandes que support le BOT \n\nUne commande pour equilibrer deux teams à partir d'une liste de pseudos\n```!sort-team Playername_1 PlayerName_2 ...\n Exemple : !sort-team NaikenNC FrenchlifeNC Anulos Barn3tNC```\n\n Une commande pour ajouter a la base de donnée les potentielle pseudo que le BOT va rencontrer pour shuffle les teams\n```!team-members OutfitTAG\n Exemple : !team-members 1rpc```")
        return

    if message.content.startswith('!sort-team'):
        print(message.content.split(' '))
        names = message.content.split(' ')
        names.pop(0)
        names = pseudo.replace_pseudos(names)
        shuffle_team_query = teamManager.shuffle_teams(names, 12, "inf")
        resp = ""
        if len(shuffle_team_query[0]) != 0:
            str_lost_names = ', '.join(shuffle_team_query[0])
            resp = "Je n'ai pas réussis à trouver ces perosnnes : " + str_lost_names + "\n\n"
        str_team_one = ', '.join(shuffle_team_query[1])
        str_team_two = ', '.join(shuffle_team_query[2])
        resp = resp + "Voici la premiere team : " + str_team_one + "\n\nVoici la seconde team : " + str_team_two
        await message.channel.send(resp)

    if message.content.startswith('!team-members'):
        outfit_name = message.content.split(' ')
        outfit_name.pop(0)
        if len(outfit_name) == 0:
            return await message.channel.send("Mettez le tag d'une outfit")
        resp = team.get_outfit_member_id(outfit_name[0])
        if resp == "error":
            return await message.channel.send("Une erreur est survenue dans la requête")
        pseudo.add_outfit(resp)
        await message.channel.send("Les joueurs ont été enregistrés dans la base de données")

    if message.content.startswith('!sheet'):
        options = message.content.split(' ')
        options.pop(0)
        if len(options) == 0:
            return await message.channel.send("Mettez au moins un lien d'un Googlesheet")
        players = googleSheets.get_players(options[0])
        names = []
        for player in players:
            first_name = player.split()
            if len(first_name) > 0 and len(first_name[0]) > 3:
                names.append(first_name[0])
        #names = pseudo.replace_pseudos(players)
        names = list(set(names))
        format_team = 12
        if len(names) < 1:
            return await message.channel.send("You needs to put at least 2 people in the player list")
        if len(options) == 2 and options[1] is int:
            format_team = int(options[1])
        shuffle_team_query = teamManager.shuffle_teams(names, format_team, "inf")
        await message.channel.send(shuffle_teams_result(shuffle_team_query, format_team))

    if message.content.startswith('!air'):
        options = message.content.split(' ')
        options.pop(0)
        if len(options) == 0:
            return await message.channel.send("Mettez au moins un lien d'un Googlesheet")
        players = googleSheets.get_players(options[0])
        names = []
        for player in players:
            first_name = player.split()
            if len(first_name) > 0 and len(first_name[0]) > 3:
                names.append(first_name[0])
        format_team = 12
        if len(names) < 1:
            return await message.channel.send("You needs to put at least 2 people in the player list")
        if len(options) == 2 and options[1] is int:
            format_team = int(options[1])
        shuffle_team_query = teamManager.shuffle_teams(names, format_team, "air")
        await message.channel.send(shuffle_teams_result(shuffle_team_query, format_team))

    if message.content.startswith('!clear-player-names'):
        options = message.content.split(' ')
        if len(options) == 1:
            return await message.channel.send("Il manque l'adresse du GoogleSheet !")
        options.pop(0)
        googleSheets.clear_sheet(options[0])
        await message.channel.send("Google sheet propre !")

    if message.content.startswith('!clear-teams'):
        options = message.content.split(' ')
        if len(options) == 1:
            return await message.channel.send("Il manque l'adresse du GoogleSheet !")
        names.pop(0)
        googleSheets.clear_sheet(options[0])
        await message.channel.send("Google sheet propre !")

    if message.content.startswith('!clear-sheet'):
        options = message.content.split(' ')
        if len(options) == 1:
            return await message.channel.send("Il manque l'adresse du GoogleSheet !")
        options.pop(0)
        googleSheets.clear_sheet(options[0])
        await message.channel.send("Google sheet propre !")

    if message.content.startswith('!add-player'):
        options = message.content.split(' ')
        options.pop(0)
        print(options)
        if len(options) > 1:
            val = googleSheets.add_player(options[0], options[1])
            if val != "error":
                await message.channel.send("Le joueur a bien été ajouté !")
                return
        await message.channel.send("Une erreur s'est produite !")


client.run(discord_token)

