## Planetside 2 Shuffle team

A Discord bot for Planetside 2 **under construction**.
 
Shuffle team via command line or with a GoogleSheet link using a discord bot.

Made with python 3 and Census Planetside 2, Google and Discord API's.

For running the project you :

```bash
python discord_app.py
```

You can add the bot via this invitational link :

 [Suffle_team_ps2 Discord Bot](https://discord.com/oauth2/authorize?client_id=735537281980563608&permissions=334912&scope=bot)

And you can copy the spreadsheet form the discord is using :

 [Formated SpreadSheet](https://discord.com/oauth2/authorize?client_id=735537281980563608&permissions=334912&scope=bot)



## Requirements

 * [Python 3](https://www.python.org/downloads/)

 ### API
 
 * [Census Planetside 2](http://census.daybreakgames.com/)
 * [Discord](https://discord.com/developers/docs/intro)
 * [Google SpreadSheets](https://developers.google.com/sheets/api/quickstart/python)

## The commands available


Show all the commands available :

```bash
!help
```

Make teams from a list of players name :

```bash
!sort-team PlayerName1 PlayerName2 PlayerName3 ...
```

Add a player to the spreadsheet :

```bash
!add-player googleLink PLayerName
```

From the players names on the spreadsheet make team depending on the team size :

```bash
!sheet googleLink teamSize
```

From an outfit tag, add all player names to the database :

```bash
!team-members teamTag
```

Clear the player names in a google speardsheet :

```bash
!clear-player-names googleLink
```

Clear the teams in a google speardsheet :

```bash
!clear-teams googleLink
```

Clear the sheet in a google speardsheet :

```bash
!clear-sheet googleLink
```

## Author

* Nicolas Albiges ([LinkedIn](https://www.linkedin.com/in/nicolas-albiges/)/[GitHub](https://github.com/NicolasAlbiges))
* Mail adress : nalbiges22@gmail.com



