# coding: utf-8

from datetime import datetime
import requests
from cloudbot import hook


@hook.command("scores", "tennis", "game", "match")
def scores(text):

    special_people = {'dave':'novak djokovic','delpo': 'del potro','rba':'roberto bautista','arv':'albert ramos','ddr':'kei nishikori','shoulders': 'sakkari'}

    now = datetime.now()
    if now.month < 10:
        month = f'0{now.month}'
    else:
        month = f'{now.month}'
    if now.day < 10:
        day = f'0{now.day}'
    else:
        day = f'{now.day}'
    date_string = f'{now.year}-{month}-{day}'
    time_string = f'{now.hour}{now.minute}{now.second}'

    url = f'http://ace.tennis.com/pulse/{date_string}_livescores_new.json?v={time_string}'
    scores_json = requests.get(url).json()

    tournaments = scores_json['tournaments']
    results = []
    bold = '\x02'
    color = '\x0313'
    colorend = '\x03'
    final_string = ''

    for tournament in tournaments:
        tournament_data = {}
        name = tournament['name']
        if 'Boys' in name:
            continue
        elif 'Girls' in name:
            continue
        elif 'Qualification' in name:
            continue
        matches = tournament['events']
        city = tournament['location']
        country = tournament['country']
        gender = tournament['gender']
        match_names = []
        for match in matches:
            if match['status'] == 'Cancelled':
                continue
            match_data = {}
            teams = []
            round_title = match['round']
            players = match['players']

            for player in players:
                team_data = {}

                player_name = player['name']
                if player['is_serving'] == True:
                    player_name = f'{color}{player_name}{colorend}'
                team_data['player_name'] = player_name

                set_score_list = player['set_games']
                team_data['set_score_list'] = set_score_list
                team_data['winner'] = player['is_winner']
                team_data['seed'] = player['seed']
                teams.append(team_data)

            match_data['status'] = match['status']
            match_data['team_data'] = teams
            match_data['round'] = round_title
            match_names.append(match_data)

        tournament_data['name'] = name
        tournament_data['city'] = city
        tournament_data['country'] = country
        tournament_data['gender'] = gender
        tournament_data['match_data'] = match_names
        results.append(tournament_data)

    if results:
        final_mstring = []
        final_wstring = []
        final_cmstring = []
        final_cwstring = []
        for tourney in results:
            tourney_type = ''
            if tourney['gender'] == 'male' and 'Challenger' not in tourney['name']:
                final_m = f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                nsm = ''
                om = ''
                fm = ''
                tourney_type = 'a'
            elif tourney['gender'] == 'female' and 'Challenger' not in tourney['name']:
                final_w = f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                nsw = ''
                ow = ''
                fw = ''
                tourney_type = 'w'
            elif tourney['gender'] == 'male' and 'Challenger' in tourney['name']:
                final_cm = f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                nscm = ''
                ocm = ''
                fcm = ''
                tourney_type = 'cm'
            elif tourney['gender'] == 'female' and 'Challenger' in tourney['name']:
                final_cw = f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                nscw = ''
                ocw = ''
                fcw = ''
                tourney_type = 'cw'
            for match in tourney['match_data']:
                if match['team_data'][0]['seed']:
                    seed1 = match['team_data'][0]['seed']
                    first_name= f'({seed1.upper()}){match["team_data"][0]["player_name"]}'
                else:
                    first_name = match['team_data'][0]['player_name']
                first_set_num = match['team_data'][0]['set_score_list']
                if match['team_data'][1]['seed']:
                    seed2 = match['team_data'][1]['seed']
                    second_name= f'({seed2.upper()}){match["team_data"][1]["player_name"]}'
                else:
                    second_name = match['team_data'][1]['player_name']
                second_set_num = match['team_data'][1]['set_score_list']
                if match['status'] == 'Not started':
                    s = f'| {first_name} vs. {second_name} '
                    if tourney_type == 'a':
                        nsm = nsm + s
                    elif tourney_type == 'w':
                        nsw = nsw + s
                    elif tourney_type == 'cm':
                        nscm = nscm + s
                    elif tourney_type == 'cw':
                        nscw = nscw + s
                elif match['status'] == 'Finished':
                    if match['team_data'][0]['winner'] == True:
                        try:
                            s = f'| {bold}{first_name}{bold} d. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                        except IndexError:
                            s = f'| {bold}{first_name}{bold} d. {second_name}: w/o'
                        try:
                            s = s + f', {first_set_num[1]}-{second_set_num[1]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {first_set_num[2]}-{second_set_num[2]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {first_set_num[3]}-{second_set_num[3]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {first_set_num[4]}-{second_set_num[4]}'
                        except IndexError:
                            pass
                        try:
                            if int(first_set_num[-1]) <= 5:
                                s = s + '(ret.)'
                        except IndexError:
                            pass
                    else:
                        try:
                            s = f'| {bold}{second_name}{bold} d. {first_name}: {second_set_num[0]}-{first_set_num[0]}'
                        except IndexError:
                            s = f'| {bold}{second_name}{bold} d. {first_name}: w/o'
                        try:
                            s = s + f', {second_set_num[1]}-{first_set_num[1]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {second_set_num[2]}-{first_set_num[2]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {second_set_num[3]}-{first_set_num[3]}'
                        except IndexError:
                            pass
                        try:
                            s = s + f', {second_set_num[4]}-{first_set_num[4]}'
                        except IndexError:
                            pass
                        try:
                            if int(second_set_num[-1]) <= 5:
                                s = s + '(ret.)'
                        except IndexError:
                            pass
                    s = s + ' '
                    if tourney_type == 'a':
                        fm = fm + s
                    elif tourney_type == 'w':
                        fw = fw + s
                    elif tourney_type == 'cm':
                        fcm = fcm + s
                    elif tourney_type == 'cw':
                        fcw = fcw + s
                else:
                    try:
                        s = f'| {first_name} vs. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                    except IndexError:
                        s = f'| {first_name} vs. {second_name}: 0-0'
                    try:
                        s = s + f', {first_set_num[1]}-{second_set_num[1]}'
                    except IndexError:
                        pass
                    try:
                        s = s + f', {first_set_num[2]}-{second_set_num[2]}'
                    except IndexError:
                        pass
                    try:
                        s = s + f', {first_set_num[3]}-{second_set_num[3]}'
                    except IndexError:
                        pass
                    try:
                        s = s + f', {first_set_num[4]}-{second_set_num[4]}'
                    except IndexError:
                        pass
                    # m = m + f' {first_game_score}-{second_game_score} '
                    s = s + ' '
                    if tourney_type == 'a':
                        om = om + s
                    elif tourney_type == 'w':
                        ow = ow + s
                    elif tourney_type == 'cm':
                        ocm = ocm + s
                    elif tourney_type == 'cw':
                        ocw = ocw + s

            if tourney_type == 'a':
                final_m = final_m + om + nsm + fm
                final_mstring.append(final_m)
            elif tourney_type == 'w':
                final_w = final_w + ow + nsw + fw
                final_wstring.append(final_w)
            elif tourney_type == 'cm':
                final_cm = final_cm + ocm + nscm + fcm
                final_cmstring.append(final_cm)
            elif tourney_type == 'cw':
                final_cw = final_cw + ocw + nscw + fcw
                final_cwstring.append(final_cw)

        league_list = ['atp','wta','cm','cw']
        tourney_list = []
        for i in range(len(results)):
            if len(results[i]['city'].split(' ')) > 1:
                temp_city = results[i]['city'].lower().split(' ')
                city = '-'.join(temp_city)
            else:
                city = results[i]["city"].lower()
            tourney_list.append(f'{city}')
        
        if text.lower().split()[-1] in league_list:
            if text.lower().split()[-1] == 'atp':
                if not final_mstring:
                    return('No ATP matches today.')
                else:
                    for i in range(len(final_mstring)):
                        final_string = final_string + final_mstring[i] + '\n'
                    return(final_string)
            elif text.lower().split()[-1] == 'wta':
                if not final_wstring:
                    return('No WTA matches today.')
                else:
                    for i in range(len(final_wstring)):
                        final_string = final_string + final_wstring[i] + '\n'
                    return(final_string)
            elif text.lower().split()[-1] == 'cm':
                if not final_cmstring:
                    return("No ATP Challenger matches today.")
                else:
                    for i in range(len(final_cmstring)):
                        final_string = final_string + final_cmstring[i] + '\n'
                    return(final_string)
            elif text.lower().split()[-1] == 'cw':
                if not final_cwstring:
                    return("No WTA Challenger/125k matches today.")
                else:
                    for i in range(len(final_cwstring)):
                        final_string = final_string + final_cwstring[i] + '\n'
                    return(final_cwstring[i])
        elif text.lower().split()[-1] in tourney_list:
            final_tstring = []
            for i in range(len(results)):
                final_t = ''
                tourney = results[i]
                temp_input = text.lower().split('-')
                fix_input = ' '.join(temp_input)
                if fix_input in tourney['city'].lower():
                    final_t = final_t + f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                    ot = ''
                    nst = ''
                    ft = ''
                    for match in tourney['match_data']:
                        if match['team_data'][0]['seed']:
                            seed1 = match['team_data'][0]['seed']
                            first_name= f'({seed1.upper()}){match["team_data"][0]["player_name"]}'
                        else:
                            first_name = match['team_data'][0]['player_name']
                        first_set_num = match['team_data'][0]['set_score_list']
                        if match['team_data'][1]['seed']:
                            seed2 = match['team_data'][1]['seed']
                            second_name= f'({seed2.upper()}){match["team_data"][1]["player_name"]}'
                        else:
                            second_name = match['team_data'][1]['player_name']
                        second_set_num = match['team_data'][1]['set_score_list']
                        if match['status'] == 'Not started':
                            s = f'| {first_name} vs. {second_name} '
                            ot = ot + s
                        elif match['status'] == 'Finished':
                            if match['team_data'][0]['winner'] == True:
                                try:
                                    s = f'| {bold}{first_name}{bold} d. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                                except IndexError:
                                    s = f'| {bold}{first_name}{bold} d. {second_name}: w/o'
                                try:
                                    s = s + f', {first_set_num[1]}-{second_set_num[1]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {first_set_num[2]}-{second_set_num[2]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {first_set_num[3]}-{second_set_num[3]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {first_set_num[4]}-{second_set_num[4]}'
                                except IndexError:
                                    pass
                                try:
                                    if int(first_set_num[-1]) <= 5:
                                        s = s + '(ret.)'
                                except IndexError:
                                    pass
                            else:
                                try:
                                    s = f'| {bold}{second_name}{bold} d. {first_name}: {second_set_num[0]}-{first_set_num[0]}'
                                except IndexError:
                                    s = f'| {bold}{second_name}{bold} d. {first_name}: w/o'
                                try:
                                    s = s + f', {second_set_num[1]}-{first_set_num[1]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {second_set_num[2]}-{first_set_num[2]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {second_set_num[3]}-{first_set_num[3]}'
                                except IndexError:
                                    pass
                                try:
                                    s = s + f', {second_set_num[4]}-{first_set_num[4]}'
                                except IndexError:
                                    pass
                                try:
                                    if int(second_set_num[-1]) <= 5:
                                        s = s + '(ret.)'
                                except IndexError:
                                    pass
                            ft = ft + s + ' '
                        else:
                            try:
                                s = f'| {first_name} vs. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                            except IndexError:
                                s = f'| {first_name} vs. {second_name}: 0-0'
                            try:
                                s = s + f', {first_set_num[1]}-{second_set_num[1]}'
                            except IndexError:
                                pass
                            try:
                                s = s + f', {first_set_num[2]}-{second_set_num[2]}'
                            except IndexError:
                                pass
                            try:
                                s = s + f', {first_set_num[3]}-{second_set_num[3]}'
                            except IndexError:
                                pass
                            try:
                                s = s + f', {first_set_num[4]}-{second_set_num[4]}'
                            except IndexError:
                                pass
                            nst = nst + s + ' '
                    final_t = final_t + ot + nst + ft
                    final_tstring.append(final_t)
            if not final_tstring or len(text.lower().split()[-1]) < 3:
                return("Please pick a valid tour (ATP, WTA, CM (Men's Challenger), or CW (Women's Challenger), a player that has been/is in/will be in a match today.), or a current tournament (city name, use a dash if there are two words). Player name/tournament input must be at least 3 characters (sorry Li Na).")
            else:
                final_string = ''
                for i in range(len(final_tstring)):
                    final_string = final_string + final_tstring[i] + '\n'
                return(final_string)
        else:
            final_pstring = []
            for tourney in results:
                final_p = ''
                for j in range(len(tourney['match_data'])):
                    player1 = tourney['match_data'][j]['team_data'][0]['player_name']
                    player2 = tourney['match_data'][j]['team_data'][1]['player_name']
                    pn = text.lower().split()[-1]
                    try:
                        sp = special_people[pn]
                    except KeyError:
                        sp = pn
                        pass
                    if (pn in player1.lower() or pn in player2.lower()) or (sp in player1.lower() or sp in player2.lower()):
                        match = tourney['match_data'][j]
                        final_p = final_p + f'{bold}{tourney["name"]} ({tourney["city"]}, {tourney["country"]}){bold}: '
                        if match['team_data'][0]['seed']:
                            seed1 = match['team_data'][0]['seed']
                            first_name= f'({seed1.upper()}){match["team_data"][0]["player_name"]}'
                        else:
                            first_name = match['team_data'][0]['player_name']
                        first_set_num = match['team_data'][0]['set_score_list']
                        if match['team_data'][1]['seed']:
                            seed2 = match['team_data'][1]['seed']
                            second_name= f'({seed2.upper()}){match["team_data"][1]["player_name"]}'
                        else:
                            second_name = match['team_data'][1]['player_name']
                        second_set_num = match['team_data'][1]['set_score_list']
                        round_name = match['round']
                        if match['status'] == 'Not started':
                            final_p = final_p + f'| {round_name}: {first_name} vs. {second_name} '
                        elif match['status'] == 'Finished':
                            if match['team_data'][0]['winner'] == True:
                                try:
                                    final_p = final_p + f'| {round_name}: {bold}{first_name}{bold} d. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                                except IndexError:
                                    final_p = final_p + f'| {round_name}: {bold}{first_name}{bold} d. {second_name}: w/o'
                                try:
                                    final_p = final_p + f', {first_set_num[1]}-{second_set_num[1]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {first_set_num[2]}-{second_set_num[2]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {first_set_num[3]}-{second_set_num[3]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {first_set_num[4]}-{second_set_num[4]}'
                                except IndexError:
                                    pass
                                try:
                                    if int(first_set_num[-1]) <= 5:
                                        final_p = final_p + '(ret.)'
                                except IndexError:
                                    pass
                            else:
                                try:
                                    final_p = final_p + f'| {round_name}: {bold}{second_name}{bold} d. {first_name}: {second_set_num[0]}-{first_set_num[0]}'
                                except IndexError:
                                    final_p = final_p + f'| {round_name}: {bold}{second_name}{bold} d. {first_name}: w/o'
                                try:
                                    final_p = final_p + f', {second_set_num[1]}-{first_set_num[1]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {second_set_num[2]}-{first_set_num[2]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {second_set_num[3]}-{first_set_num[3]}'
                                except IndexError:
                                    pass
                                try:
                                    final_p = final_p + f', {second_set_num[4]}-{first_set_num[4]}'
                                except IndexError:
                                    pass
                                try:
                                    if int(second_set_num[-1]) <= 5:
                                        final_p = final_p + '(ret.)'
                                except IndexError:
                                    pass
                        else:
                            try:
                                final_p = final_p + f'| {round_name}: {first_name} vs. {second_name}: {first_set_num[0]}-{second_set_num[0]}'
                            except IndexError:
                                final_p = final_p + f'| {round_name}: {first_name} vs. {second_name}: 0-0'
                            try:
                                final_p = final_p + f', {first_set_num[1]}-{second_set_num[1]}'
                            except IndexError:
                                pass
                            try:
                                final_p = final_p + f', {first_set_num[2]}-{second_set_num[2]}'
                            except IndexError:
                                pass
                            try:
                                final_p = final_p + f', {first_set_num[3]}-{second_set_num[3]}'
                            except IndexError:
                                pass
                            try:
                                final_p = final_p + f', {first_set_num[4]}-{second_set_num[4]}'
                            except IndexError:
                                pass
                        final_pstring.append(final_p)
            if not final_pstring or len(text.lower().split()[-1]) < 3:
                return("Please pick a valid tour (ATP, WTA, CM (Men's Challenger), or CW (Women's Challenger), a player that has been/is in/will be in a match today.), or a current tournament (city name, use a dash if there are two words). Player name/tournament input must be at least 3 characters (sorry Li Na).")
            else:
                final_string = ''
                for i in range(len(final_pstring)):
                    final_string = final_string + final_pstring[i] + '\n'
                return(final_string)