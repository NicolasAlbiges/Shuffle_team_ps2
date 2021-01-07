from database import db


class Pseudo:
    def __init__(self):
        self.outfit_members = []
        data = db.get_data()
        if data != "error":
            self.outfit_members = data['outfits']

    def add_outfits(self, outfit):
        for i in range(0, len(outfit)):
            self.add_outfit(outfit[i])

    def add_outfit(self, outfit_members):
        for i in range(0, len(self.outfit_members)):
            if self.outfit_members[i]['tag'] == outfit_members['tag']:
                self.outfit_members[i] = outfit_members
                return
        self.outfit_members.append(outfit_members)
        db.insert_outfit(outfit_members)

    def remove_faction_names(self, pseudo_tested):
        max_len = len(pseudo_tested)
        if (pseudo_tested[max_len - 1] == 'c' and pseudo_tested[max_len - 2] == 'n') or (pseudo_tested[max_len - 1] == 'r' and pseudo_tested[max_len - 2] == 't') or (pseudo_tested[max_len - 1] == 's' and pseudo_tested[max_len - 2] == 'v'):
            pseudo_tested = pseudo_tested[:-2]
        return pseudo_tested

    def find_best_occurrence(self, original_pseudo, pseudo_tested):
        i_max = 0
        i_max_temp = 0
        occ = 0
        percentages = 0
        while i_max != len(pseudo_tested):
            i = 0
            i_max_temp = i_max
            while i != len(original_pseudo):
                if i_max_temp <= (len(pseudo_tested) - 1) and original_pseudo[i] == pseudo_tested[i_max_temp]:
                    occ = 1 + occ
                i = i + 1
                i_max_temp = i_max_temp + 1
            if (occ / len(pseudo_tested)) * 100 > percentages:
                percentages = (occ / len(original_pseudo)) * 100
            occ = 0
            i_max = i_max + 1
        return percentages

    def find_occurrence(self, original_pseudo, pseudo_tested):
        pseudo_tested = pseudo_tested.split()[0]
        original_pseudo = original_pseudo.split()[0]
        if original_pseudo == pseudo_tested:
            return 100
        pseudo_tested = self.remove_faction_names(pseudo_tested)
        percentages = self.find_best_occurrence(original_pseudo, pseudo_tested)
        return percentages

    def find_pseudo(self, pseudo):
        for outfit in self.outfit_members:
            for element in outfit['members']:
                if self.find_occurrence(pseudo.lower(), element['name'].lower()) > 70:
                    return element['name']
        return "error 404"

    def replace_pseudos(self, pseudo_list):
        i = 0
        while i != len(pseudo_list):
            print("This is the orignal pseudo %s"% pseudo_list[i])
            current_pseudo = self.find_pseudo(pseudo_list[i])
            print("This is the current pseudo %s\n"% current_pseudo)
            if current_pseudo != "error 404":
                pseudo_list[i] = current_pseudo
            i = 1 + i
        return pseudo_list
