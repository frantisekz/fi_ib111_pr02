#!/usr/bin/python3
# -*- coding: utf-8 -*-

from operator import itemgetter

"""
IB111 Project02
================
Analýza hlasování poslanců
Author: František Zatloukal


deputies[[deputy_id, person_id, "name", party_id]]
deputies_presence[[deputy_id, presence]]

parties[party_id["party_name", deputies[id]]]
votings[voting_id[deputy_id["deputy_voted"]]]
"""

# FILE NAMES
VOTINGS_FILE = "hl2013h1.unl_redxl"
DEPUTIES_FILE = "poslanec.unl"
PERSONS_FILE = "osoby.unl"
PARTIES_FILE = "organy_utf8.unl"

def load_deputies(deputies_file, persons_file):
    """
    returns deputies[[deputy_id, person_id, "name", party_id]]
    """
    deputies = []
    deputies_full = []
    with open(deputies_file) as fp:
        for line in fp:
            line_split = line.split("|")
            if line_split[4] == "171": # 171 is actual time range id
                append_blank = [int(line_split[0]), int(line_split[1]), "", int(line_split[3])]
                deputies.append(append_blank)

    with open(persons_file) as fp:
        for line in fp:
            line_split = line.split("|")
            for deputy in deputies:
                line_split[0] = int(line_split[0])
                if line_split[0] in deputy:
                    deputy[2] = line_split[1] + " " + line_split[3] + " " + line_split[2]
                    deputies_full.append(append_blank)
    return deputies

def load_votings(votings_file):
    """
    returns votings[[voting_id, [deputy_id, "deputy_voted"]]]
    """
    num_lines = sum(1 for line in open(votings_file))
    votings = []
    i = 0
    j = -1
    with open(votings_file) as fp:
        for line in fp:
            line_split = line.split("|")
            #print("Processing line " + str(i) + " out of " + str(num_lines))
            append_blank = [int(line_split[1]), [int(line_split[0]), line_split[2]]]
            votings.append(append_blank)
            j += 1
            i += 1
    return votings

def load_parties(parties_file):
    """
    returns parties[[party_id, party_name]]
    """
    parties = []
    with open(parties_file) as fp:
        for line in fp:
            line_split = line.split("|")
            append_blank = [int(line_split[0]), line_split[4]]
            parties.append(append_blank)
    return parties

def load_deputies_presence():
    """
    Returns deputies_presence[deputy_id, present_percentage[deputy_id, votings[]]]
    """
    deputies_presence = []
    for deputy in deputies:
        deputies_presence.append([deputy[0], deputy_present_percentage(deputy[0], votings)])
    return deputies_presence

def deputy_present_percentage(deputy_id, votings):
    """
    returns present percentage
    """
    missed = 0
    total = 0
    i = 0
    voting = []
    for voting in votings:
        if voting[1][0] == deputy_id:
            if voting[1][1] == "M" or voting[1][1] == "@":
                missed += 1
                total += 1
            else:
                total += 1
        i += 1

    if missed != 0:
        return (total-missed)/total
    else:
        return 1

def lowest_deputies_present(deputies, deputies_presence):
    sorted_presence = sorted(deputies_presence, key=itemgetter(1), reverse=False)
    outputlist = []
    for single in sorted_presence:
        for deputy in deputies:
            if single[0] == deputy[0]:
                full_item = [deputy[2], single[1]]
                print("Deputy " + deputy[2] + ", with id " + str(deputy[0]) + ", was present " + str(round(single[1]*100)) + "% of the time")
                outputlist.append(full_item)
    return outputlist

def party_present_percentage(party_id, deputies_presence, deputies):
    """
    returns present percentage of party
    """
    i = 0
    presence = 0
    for deputy in deputies_presence:
        if get_deputy_party(deputy[0]) == party_id:
            presence += deputy[1]
            i += 1
    return presence/i

def parties_present_percentages(deputies, deputies_presence):
    """
    returns present percentages of all parties
    """
    i = 0
    presence = []
    parties = []
    parties_clean = []
    parties_full = []
    for deputy in deputies:
        parties.append(deputy[3])

    # remove duplicates
    for party in parties:
        if party not in parties_clean:
            parties_full.append([party, 1])
            parties_clean.append(party)

    for party in parties_clean:
        index = parties_clean.index(party)
        print("Party ' " + str(party_to_name(party)) + "', id " + str(party) + ", was present " + str(round(100*party_present_percentage(party, deputies_presence, deputies))) + "% of the time.")
        parties_full[index] = party_present_percentage(party, deputies_presence, deputies)
    return parties_full

def party_to_name(party_id):
    """
    returns party name from give party_id
    """
    for party in parties:
        if party[0] == party_id:
            return party[1]
    return -1

def get_deputy_party(deputy_id):
    """
    returns party_id for given deputy_id
    """
    for deputy in deputies:
        if deputy[0] == deputy_id:
            return deputy[3]

def single_dominant_voting(voting_id, party_id):
    """
    finds dominant result for one voting/party combination
    """
    dominance_result = [0, 0]
    result = "UNK"
    for deputy in deputies:
        if deputy[3] == party_id:
            for voting in votings:
                if voting[0] == voting_id:
                    if deputy[0] == voting[1][0]:
                        if voting[1][1] == "A":
                            dominance_result[0] += 1
                        if voting[1][1] == "B":
                            dominance_result[1] += 1
    if dominance_result[0] > dominance_result[1]:
        result = "A"
    if dominance_result[0] < dominance_result[1]:
        result = "B"
    return result

def single_party_voting_difference(voting_id, dominant, party_id):
    voted_dominant = 0
    total = 0
    for voting in votings:
        if voting[0] == voting_id:
            for deputy in deputies:
                if deputy[3] == party_id:
                    #print("Comparing deputy id: " + str(deputy[0]) + " with deputy id: " + str(voting[1][0]))
                    if deputy[0] == voting[1][0]:
                        if voting[1][1] == dominant:
                            voted_dominant += 1
                            total += 1
                        elif voting[1][1] == "B":
                            total += 1
    if total != 0:
        #print("Voted dominantly: " + str(voted_dominant) + "; out of total: " + str(total))
        return voted_dominant/total
    else:
        return 0

def dominant_votings():
    i = 1
    differences = {}
    for party in parties:
        for voting in votings:
            actual_dominance = single_dominant_voting(voting[0], party[0])
            if actual_dominance != "UNK":
                try:
                    differences[party[0]] = differences[party[0]] + single_party_voting_difference(voting[0], actual_dominance, party[0])
                    i += 1
                except:
                    differences[party[0]] = single_party_voting_difference(voting[0], actual_dominance, party[0])
        try:
            differences[party[0]] = differences[party[0]] / i
        except:
            i = i
        i = 1
    return differences

votings = load_votings(VOTINGS_FILE)
deputies = load_deputies(DEPUTIES_FILE, PERSONS_FILE)
parties = load_parties(PARTIES_FILE)
deputies_presence = load_deputies_presence()

print("==================================")
print("Deputies presence: ")
lowest_deputies_present(deputies, deputies_presence)

print("==================================")
print("Parties presence: ")
parties_present_percentages(deputies, deputies_presence)

print("==================================")
print("Parties unity: ")
print(dominant_votings())
