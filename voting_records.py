import os
import sys
import getopt
import csv
import json
import requests

#TODO: PSR bill tags

# HOUSE REP districts: 2,7,8,9,10,14,18,22,29,36
housereps = {'tx2': {'id': 'P000592',
                     'first_name': 'Ted',
                     'last_name': 'Poe',
                     'congress': [109, 110, 111, 112, 113, 114, 115]},
             'tx7': {'id': 'C001048',
                     'first_name': 'John',
                     'last_name': 'Culberson',
                     'congress': [107, 108, 109, 110, 111, 112, 113, 114, 115]},
             'tx8': {'id': 'B000755',
                     'first_name': 'Kevin',
                     'last_name': 'Brady',
                     'congress': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]},
             'tx9': {'id': 'G000553',
                     'first_name': 'Al',
                     'last_name': 'Green',
                     'congress': [109, 110, 111, 112, 113, 114, 115]},
             'tx10': {'id': 'M001157',
                      'first_name': 'Michael',
                      'last_name': 'McCaul',
                      'congress': [109, 110, 111, 112, 113, 114, 115]},
             'tx14': {'id': 'W000814',
                      'first_name': 'Randy',
                      'last_name': 'Weber',
                      'congress': [113, 114, 115]},
             'tx18': {'id': 'J000032',
                      'first_name': 'Sheila',
                      'last_name': 'Jackson Lee',
                      'congress': [104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]},
             'tx22': {'id': 'O000168',
                      'first_name': 'Pete',
                      'last_name': 'Olson',
                      'congress': [111, 112, 113, 114, 115]},
             'tx29': {'id': 'G000410',
                      'first_name': 'Gene',
                      'last_name': 'Green',
                      'congress': [103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]},
             'tx36': {'id': 'B001291',
                      'first_name': 'Brian',
                      'last_name': 'Babin',
                      'congress': [114, 115]}
             }


def usage():
    # TODO: i don't remember unix standards right now
    # print("you did it wrong")  # at least it's not this anymore
    print("Indivisible HTX Congressional Vote Records depends on the ProPublica Congress API")
    print("Required parameters: ")
    print("-d [district number] OR -i [representative ID] OR -n [representative name]")
    print("-c [congress number] OR -y [year]")
    print("-k [ProPublica API key]")
    print("-u [update existing file]")

# TODO: associate names and IDs of reps from the relevant districts
def get_member_id(name):
    return ''


def get_member_name(id):
    return ''


def years_of_congress(congress):
    return 2 * (congress - 1) + 1789


# TODO: just house reps for now, link up to directory later
def get_chamber(id):
    return 'house'


def get_votes_by_month(chamber, year, month):
    # chamber: 'house' or 'senate'
    # year, month: YYYY, MM
    votes_by_month_url = lambda chamber, year, month: "https://api.propublica.org/congress/v1/" + chamber + "/votes/" + str(year) + "/" + str(month) + ".json"
    r = requests.get(votes_by_month_url(chamber, year, month), headers=headers)
    data = r.json()
    return data


def get_specific_vote(congress, chamber, session_number, roll_call_number):
    # congress: house 102-115, senate 101-115; from above data
    # chamber: 'house' or 'senate'; same as above call
    # session_number: 1 odd-numbered year, 2 even-numbered year; from above data
    # roll_call_number: from above data
    specific_vote_url = lambda congress, chamber, session_number, roll_call_number: "https://api.propublica.org/congress/v1/" + str(congress) + "/" + chamber + "/sessions/" + session_number + "/votes/" + roll_call_number + ".json"
    r = requests.get(specific_vote_url(congress, chamber, session_number, roll_call_number), headers=headers)
    data = r.json()
    return data


congress_number = 0
member_name = ''
member_id = ''
_congress = False
_update = False
years = []
months = []
full_year = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

try:
    opts, args = getopt.getopt(sys.argv[1:], 'n:i:y:c:d:k:u')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-n':  # Member name given
        member_name = arg
        member_id = get_member_id(arg)
    elif opt == '-i':  # Member ID given
        member_name = get_member_name(arg)
        member_id = arg
    elif opt == '-y':  # Year given
        # Assign/store year, all months
        years = [arg]
        months = [full_year]
    elif opt == '-c':  # Congress number given
        _congress = True
        congress_number = arg
        y = years_of_congress(int(arg))  # Get start year of congress
        years = [y, y + 1, y + 2]
        months = [full_year, full_year, ['01']]
        # TODO: check for future dates to avoid null results
    elif opt == '-d':  # District number given
        # Get member name, ID
        member_name = housereps['tx' + arg]['last_name']
        member_id = housereps['tx' + arg]['id']
    elif opt == '-k':  # API key provided
        API_KEY = arg
        headers = {'X-API-Key': API_KEY}
    elif opt == '-u':
        # Update instead of creating new file
        _update = True

chamber = get_chamber(member_id)

if _congress:
    s = congress_number
else:
    s = years[0]

file_out = member_name + "_votes_" + s + ".csv"

if _update:
    if os.path.isfile(file_out):  # if file_out exists
        f_o = open(file_out, 'a')
        # TODO: get date of last vote in file (cutoff date)
    else:
        print("File "+file_out+" not found for update")
        exit()
else:
    f_o = open(file_out, 'w')

writer = csv.writer(f_o)
# TODO: vote type?
file_header = ['Chamber', 'Congress', 'Session', 'Roll Call', 'Bill', 'Title', 'Latest Action', 'Question', 'Result',
               'Date', 'Time', 'Position']
writer.writerow(file_header)

year_index = 0
for year in years:

    for month in months[year_index]:

        month_data = get_votes_by_month(chamber, year, month)
        results = month_data["results"]
        votes = results["votes"]

        for vote in votes:
            # print(json.dumps(vote, indent=4))

            # get congress, session number, roll call number from vote
            congress = vote["congress"]

            # If congress number was given, ignore votes from the wrong congress
            if _congress and congress != congress_number:
                break
            # If vote belongs to correct congress or we don't care, carry on

            session_number = vote["session"]
            roll_call_number = vote["roll_call"]

            # TODO: vote type
            # TODO: compare date to cutoff date

            vote_data = get_specific_vote(congress, chamber, session_number, roll_call_number)

            results = vote_data.get("results", {})

            if not results:
                # TODO: this happens on first 2 votes of congress (quorum call, election of speaker)
                # not sure why, the URIs work
                # TODO: use info from other call to fill in row, not skip
                print('congress: ' + congress + ', session number: ' + session_number + ', roll call: ' + roll_call_number)
                break

            vote_details = results["votes"]["vote"]
            positions = vote_details["positions"]
            # print(json.dumps(positions, indent=4))

            # look through voting members for given member ID
            member_position = ""
            for member in positions:
                # if member voted, record position and write out vote info
                if member["member_id"] == member_id:
                    member_position = member["vote_position"]

            # write everything
            list_to_write = []
            list_to_write.append(chamber)
            list_to_write.append(congress)
            list_to_write.append(session_number)
            list_to_write.append(roll_call_number)

            nom = vote.get("nomination", {})
            bill1 = vote.get("bill", {})
            if bill1:
                list_to_write.append(bill1["number"])
            elif nom:
                list_to_write.append("Nomination " + nom["nomination_id"])
            else:
                list_to_write.append("")

            bill2 = vote_details.get("bill", {})
            if bill2:
                list_to_write.append(bill2["title"])
                list_to_write.append(bill2["latest_action"])
            elif nom:
                list_to_write.append(nom["agency"] + ", " + nom["name"])
                list_to_write.append("")
            else:
                list_to_write.append("")
                list_to_write.append("")

            list_to_write.append(vote["question"])
            list_to_write.append(vote["result"])
            list_to_write.append(vote["date"])
            list_to_write.append(vote["time"])
            list_to_write.append(member_position)
            writer.writerow(list_to_write)

    year_index += 1
