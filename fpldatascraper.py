# Standard Library Modules
import sys
import csv
import time
import os
import json
import urllib.request
import asyncio as async
import pandas as pd
from aiohttp import ClientSession
from unidecode import unidecode

#Initializing empty dictionaries that will converted to csv files later
TOTAL_PAST_STATS = {}
CURR_SEASON_STATS = {}
PLAYERS = {}
RESULTS = {}
PLAYER_RESULTS_STATS = {}

# Global Values
numOfPlayers = 0
playerNames = []


def get_curr_stats():
    """
    Use FPL API bootstrap endpoint for eventual Player.csv and CurrentSeasonStats.csv
    Also used to define number of players (to avoid unnecessary HTTP requests)
    
    :return: None
    """

    position_dictionary = {
        1: 'GKP',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }

    r = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static')
    bootstrap_data = r.json()
    global numOfPlayers
    
    #Getting the number of players so as to avoid unnecessary http calls
    
    numOfPlayers = len(bootstrap_data['elements'])

    # Getting All Players' Info
    i=1

    while i<numOfPlayers:

        # unidecode replaces accented letters in player names with ascii characters
        
        playerNames.append(unidecode(bootstrap_data['elements'][i]['first_name'])
                            + ' '
                            + unidecode(bootstrap_data['elements'][i]['second_name']))

        # # Get Player's Team
        # team_code = bootstrap_data['elements'][i]['team_code']
        # team_name = TEAM_DICT[team_code]

        # Getting Player's Position

        position_code = bootstrap_data['elements'][i]['element_type']
        position = position_dictionary[position_code]

        # Getting Player's Current Season Stats
        
        curr_season_data = {
            'total_points':     bootstrap_data['elements'][i]['total_points'],
            'mins_played':      bootstrap_data['elements'][i]['minutes'],
            'goals_scored':     bootstrap_data['elements'][i]['goals_scored'],
            'assists':          bootstrap_data['elements'][i]['assists'],
            'clean_sheets':     bootstrap_data['elements'][i]['clean_sheets'],
            'goals_conceded':   bootstrap_data['elements'][i]['goals_conceded'],
            'own_goals':        bootstrap_data['elements'][i]['own_goals'],
            'penalties_saved':  bootstrap_data['elements'][i]['penalties_saved'],
            'penalties_missed': bootstrap_data['elements'][i]['penalties_missed'],
            'yellow_cards':     bootstrap_data['elements'][i]['yellow_cards'],
            'red_cards':        bootstrap_data['elements'][i]['red_cards'],
            'saves':            bootstrap_data['elements'][i]['saves'],
            'ea_index':         bootstrap_data['elements'][i]['ea_index'],
            'influence':        float(bootstrap_data['elements'][i]['influence']),
            'creativity':       float(bootstrap_data['elements'][i]['creativity']),
            'threat':           float(bootstrap_data['elements'][i]['threat']),
            'ict_index':        float(bootstrap_data['elements'][i]['ict_index']),
            'Player_pid':       bootstrap_data['elements'][i]['id']
        }

        # Creating Player Table

        PLAYERS[playerNames[i]] = {
            'pid':  bootstrap_data['elements'][i]['id'],
            'name': playerNames[i],
            'nationality': '',
            'position': position
        }

        # Creating CurrentSeasonStats Table
        
        CURR_SEASON_STATS[playerNames[i]] = curr_season_data

        i+=1


def get_fixture_results():
    """
    Use FPL API fixtures endpoint for eventual Result.csv
    
    :return: None
    """

    team_dictionary = {
        1: 'Arsenal', 2: 'Bournemouth', 3: 'Brighton and Hove Albion', 4: 'Burnley',
        5: 'Chelsea', 6: 'Crystal Palace', 7: 'Everton',
        8: 'Huddersfield Town', 9: 'Leicester City', 10: 'Liverpool',
        11: 'Manchester City', 12: 'Manchester United', 13: 'New Castle United',
        14: 'Southampton', 15: 'Stoke City',
        16: 'Swansea City', 17: 'Tottenham Hotspur', 18: 'Watford',
        19: 'West Bromwich Albion', 20: 'West Ham United'
    }

    manager_dictionary = {
        1: 'Arsene Wenger', 2: 'Eddie Howe', 3: 'Chris Hughton', 4: 'Sean Dyche', 5: 'Antonio Conte',
        6: 'Roy Hodgson', 7: 'Ronald Koeman', 8: 'David Wagner', 9: 'Craig Shakespeare',
        10: 'Jurgen Klopp', 11: 'Pep Guardiola', 12: 'Jose Mourinho', 13: 'Rafael Benitez',
        14: 'Mauricio Pellegrino', 15: 'Mark Hughes', 16: 'Paul Clement',
        17: 'Mauricio Pochettino', 18: 'Marco Silva', 19: 'Tony Pulis', 20: 'Slaven Bilic'
    }

    r = requests.get('https://fantasy.premierleague.com/drf/fixtures')
    fixtures_data = r.json()

    for fixture in fixtures_data:
        home_team = team_dictionary[fixture['team_h']]
        away_team = team_dictionary[fixture['team_a']]
        RESULTS[home_team + ' VS. ' + away_team] = {
            'id': fixture['id'],
            'gameweek': fixture['event'],
            'home_score': fixture['team_h_score'],
            'away_score': fixture['team_a_score'],
            'home_team': home_team,
            'away_team': away_team,
            'home_mgr': manager_dictionary[fixture['team_h']],
            'away_mgr': manager_dictionary[fixture['team_a']]
        }


def get_past_seasons(pid, data, psc):
    """
    Return stats from previous seasons if player is a veteran.
    
    :param pid: Int - Player ID# 
    :param data: Dictionary - JSON
    :param psc: Int - Past Season Count
    :return: Dictionary - JSON
    """

    # Variable declarations for summed past statistic headers
    total_points, minutes, goals_scored, assists, clean_sheets = 0, 0, 0, 0, 0
    goals_conceded, own_goals, penalties_saved, penalties_missed = 0, 0, 0, 0
    yellow_cards, red_cards, saves, ea_index = 0, 0, 0, 0

    # For all previous PL seasons...
    for s in range(psc):
        total_points += data['history_past'][s]['total_points']
        minutes += data['history_past'][s]['minutes']
        goals_scored += data['history_past'][s]['goals_scored']
        assists += data['history_past'][s]['assists']
        clean_sheets += data['history_past'][s]['clean_sheets']
        goals_conceded += data['history_past'][s]['goals_conceded']
        own_goals += data['history_past'][s]['own_goals']
        penalties_saved += data['history_past'][s]['penalties_saved']
        penalties_missed += data['history_past'][s]['penalties_missed']
        yellow_cards += data['history_past'][s]['yellow_cards']
        red_cards += data['history_past'][s]['red_cards']
        saves += data['history_past'][s]['saves']
        ea_index += data['history_past'][s]['ea_index']

    # Create JSON of overall past season stats
    past_season_data = {
        'total_points': total_points,
        'mins_played': minutes,
        'goals_scored': goals_scored,
        'assists': assists,
        'clean_sheets': clean_sheets,
        'goals_conceded': goals_conceded,
        'own_goals': own_goals,
        'penalties_saved': penalties_saved,
        'penalties_missed': penalties_missed,
        'yellow_cards': yellow_cards,
        'red_cards': red_cards,
        'saves': saves,
        'ea_index': ea_index,
        'previous_pl_seasons': psc,
        'Player_pid': pid
    }

    return past_season_data


def get_history():
    """
    Use FPL API element-summary endpoint for eventual TotalPastStats.csv and PlayerResultStats.csv
    
    :return: None
    """

    misses = 0
    player_url = 'https://fantasy.premierleague.com/drf/element-summary/{}'

    for pid in range(1, numOfPlayers + 1):
        player_name = playerNames[pid - 1]
        r = requests.get(player_url.format(pid))
        print('Grabbing ' + player_name)

        # Skip broken URLs
        if r.status_code != 200:
            misses += 1
            print('BROKEN URL @ PLAYER #: ' + str(pid) + '\n')
            print(player_name + ' should be here!\n')
            # More than one miss in a row - end of requests!
            if misses > 1:
                print('Two broken URLs in a row...')
                print('Something is wrong with your connection or the API.\n')
                sys.exit()
            continue

        # Reset 'missing' counter to continue loop through entire API endpoint.
        misses = 0

        player_data = r.json()

        # Number of seasons previously played in the PL
        past_season_count = len(player_data['history_past'])

        # If player has played in PL before...
        if past_season_count > 0:
            # Sum up past season statistics for overall past table
            TOTAL_PAST_STATS[player_name] = get_past_seasons(pid, player_data, past_season_count)

        # Get Player's stats for each game played so far
        games_played = player_data['history']
        for game in games_played:
            # key looks like this: 'Hector Bellerin Fixture 8: {stats}
            key = (player_name + ' Fixture ' + str(game['fixture']))
            PLAYER_RESULTS_STATS[key] = {
                'pmid': game['id'],
                'points': game['total_points'],
                'mins_played': game['minutes'],
                'goals_scored': game['goals_scored'],
                'assists': game['assists'],
                'clean_sheets': game['clean_sheets'],
                'goals_conceded': game['goals_conceded'],
                'own_goals': game['own_goals'],
                'penalties_saved': game['penalties_saved'],
                'penalties_missed': game['penalties_missed'],
                'yellow_cards': game['yellow_cards'],
                'red_cards': game['red_cards'],
                'saves': game['saves'],
                'influence': float(game['influence']),
                'creativity': float(game['creativity']),
                'threat': float(game['threat']),
                'ict_index': float(game['ict_index']),
                'Result_id': game['fixture'],
                'Player_pid': pid
            }

        # Next player...
        pid += 1


def dict_to_csv(json_data, filename, headers, tablename):
    """
    Export dictionary collection to CSV
    
    :param json_data: Dictionary - JSON
    :param filename: String - Name of .csv output
    :param headers: String - CSV column headers
    :param tablename: String - Related database table
    :return: None 
    """

    with open(filename, 'w') as csvfile:
        try:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for i in json_data:
                writer.writerow(json_data[i])
        finally:
            print(tablename, ' written to CSV successfully.')


def sort_csv(csv_filename, sorting_key):
    """
    Use pandas to sort CSVs and delete unsorted arguments in .csv
    
    :param csv_filename: String - Name of .csv output
    :param sorting_key: String - Refers to CSV column header
    :return: None
    """

    df = pd.read_csv(csv_filename)
    df = df.sort_values(by=sorting_key)
    os.remove(csv_filename)
    df.to_csv(csv_filename, index=False)


# Collection function for relevant exporting functions
# TODO: Implement OrderedDict instead of manually plugging in headers
def export_data():
    """
    Function to call all related export functions.
    
    :return: None
    """

    # Headers for CSV creation functions
    player_table_headers = ['pid', 'name', 'nationality', 'position']
    curr_table_headers = ['total_points', 'mins_played', 'goals_scored', 'assists', 'clean_sheets',
                          'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
                          'yellow_cards', 'red_cards', 'saves', 'ea_index', 'influence',
                          'creativity', 'threat', 'ict_index', 'Player_pid']
    past_table_headers = ['total_points', 'mins_played', 'goals_scored', 'assists', 'clean_sheets',
                          'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
                          'yellow_cards', 'red_cards', 'saves', 'ea_index', 'previous_pl_seasons',
                          'Player_pid']
    result_table_headers = ['id', 'gameweek', 'home_score', 'away_score', 'home_team', 'away_team',
                            'home_mgr', 'away_mgr']
    prs_table_headers = ['pid', 'points', 'mins_played', 'goals_scored', 'assists', 'clean_sheets',
                         'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
                         'yellow_cards', 'red_cards', 'saves', 'influence', 'creativity', 'threat',
                         'ict_index', 'Result_id', 'Player_pid']

    dict_to_csv(PLAYERS, 'Player.csv', player_table_headers, 'PLAYERS')
    dict_to_csv(CURR_SEASON_STATS, 'CurrentSeasonStats.csv', curr_table_headers, 'CURRENT_SEASON_STATS')
    dict_to_csv(TOTAL_PAST_STATS, 'TotalPastStats.csv', past_table_headers, 'TOTAL_PAST_STATS')
    dict_to_csv(RESULTS, 'Result.csv', result_table_headers, 'RESULTS')
    dict_to_csv(PLAYER_RESULTS_STATS, 'PlayerResultStats.csv', prs_table_headers, 'PLAYER_RESULTS_STATS')

    print('...Sorting CSV Files...\n')
    time.sleep(1)
    sort_csv('Player.csv', 'pid')
    print('......\n')
    sort_csv('CurrentSeasonStats.csv', 'Player_pid')
    print('......\n')
    sort_csv('TotalPastStats.csv', 'Player_pid')
    print('......\n')
    sort_csv('Result.csv', 'id')
    print('......\n')
    sort_csv('PlayerResultStats.csv', 'pmid')
    print('DONE!')


if __name__ == '__main__':
    print('...Getting player names and current season stats...\n')
    get_curr_stats()
    print('...Getting players past season stats (if any)...\n')
    get_history()
    print('...Getting scorelines from games played thus far this season...\n')
    get_fixture_results()
    print('...Writing CSV Files...\n')
    export_data()
