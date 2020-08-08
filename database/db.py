import json
import os.path


def get_data():
    if os.path.exists('database/db_outfit.json'):
        with open('database/db_outfit.json', "r") as db:
            if db:
                return json.load(db)
            return "error"
    return "error"


def add_outfit_db(data, outfit):
    for i in range(0, len(data['outfits'])):
        if data['outfits'][i]['tag'] == outfit['tag']:
            data['outfits'][i] = outfit
            return data
    data['outfits'].append(outfit)
    return data


def insert_outfit(outfit):
    if os.path.exists('database/db_outfit.json'):
        data = get_data()
        if data == "error":
            return "error"
        with open('database/db_outfit.json', "w") as db:
            if db:
                data = add_outfit_db(data, outfit)
                json.dump(data, db, indent=4)
