from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
teams_placements = [["E4:E20", "F4:F20"], ["H4:H18", "I4:I20"], ["K4:K30", "L4:L30"]]
players_names = "B3:B49"


class GoogleSheets:
    def __init__(self):
        self.sheet = None
        self.connect()
        self.SAMPLE_SPREADSHEET_ID = None
        self.SAMPLE_RANGE_NAME = 'A1:AA1000'

    def get_sheet_ID(self, url):
        url = url.replace("https://docs.google.com/spreadsheets/d/", "")
        self.SAMPLE_SPREADSHEET_ID = url.split("/")[0]

    def connect(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def get_players(self, link):
        self.get_sheet_ID(link)
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                         range=self.SAMPLE_RANGE_NAME, majorDimension='COLUMNS').execute()
        values = result.get('values', [])
        print(values)
        if values:
            return values[1][2:]
        return []

    def place_teams(self, teams, i, i_team_placement):
        if len(teams[i]) > 12:
            i_team_placement = 2
        print("\nTEAM 1 ->", [teams[i] + [''] * (12 - len(teams[i]))])
        resource = {
            "majorDimension": "COLUMNS",
            "values": [teams[i] + [''] * (12 - len(teams[i]))]
        }
        self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                   range=teams_placements[i_team_placement][0], body=resource, valueInputOption="USER_ENTERED").execute()
        print("TEAM 2 ->", [teams[i + 1] + [''] * (11 - len(teams[i + 1]))])
        resource = {
            "majorDimension": "COLUMNS",
            "values": [teams[i + 1] + [''] * (11 - len(teams[i + 1]))]
        }
        self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                   range=teams_placements[i_team_placement][1], body=resource, valueInputOption="USER_ENTERED").execute()

    def write_team(self, teams):
        print(teams)
        if self.SAMPLE_SPREADSHEET_ID is None:
            return
        i = 1
        i_team_placement = 0
        while i != len(teams):
            self.place_teams(teams, i, i_team_placement)
            i += 2
            i_team_placement += 1

    def write_values(self, values, range_sheet):
        resource = {
            "majorDimension": "COLUMNS",
            "values": values
        }
        self.sheet.values().update(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                   range=range_sheet, body=resource, valueInputOption="USER_ENTERED").execute()

    def clear_teams(self, link):
        self.get_sheet_ID(link)
        for i in range(0, 3):
            self.write_values([[''] * 12], teams_placements[i][0])
            self.write_values([[''] * 12], teams_placements[i][1])

    def clear_players_names(self, link):
        self.get_sheet_ID(link)
        self.write_values([[''] * 44], players_names)

    def clear_sheet(self, link):
        self.clear_teams(link)
        self.clear_players_names(link)

    def add_player(self, link, player):
        values = self.get_players(link)
        print(values)
        if len(values) < 44:
            values.append(player)
            self.write_values([values], players_names)
            return values
        return "error"
