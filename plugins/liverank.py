import requests
from cloudbot import hook
from lxml import html
import unicodedata

@hook.command("liverank")
def liverank(text,reply):
    """.liverank <atp/wta> <rank/player name> returns the live ranking information for the rank or player chosen."""

    text = text.strip()
    text = text.split(' ')

    try:
        if text[0].lower() == 'atp':
            page = requests.get('https://live-tennis.eu/en/atp-live-ranking')
        elif text[0].lower() == 'wta':
            page = requests.get('https://live-tennis.eu/en/wta-live-ranking')
        else:
            reply('Please enter ATP or WTA, optionally followed by name or ranking.')
            return
    except IndexError:
        reply('Please enter ATP or WTA, optionally followed by name or ranking.')
        return
    tree = html.fromstring(page.text)
    rank_rows = tree.xpath('//table[@id="u868"]/tbody/tr')
    green = '\x0309'
    red = '\x0304'
    colorend = '\x03'

    plist = []
    flux_list = []
    point_list = []
    mp_list = []
    tourn_list = []

    for i in range(0,62,2):
        if i <= 18:
            try:
                rank = rank_rows[i].xpath('td[1]/text()')[0].strip()
            except IndexError:
                rank = rank_rows[i].xpath('td[1]/*/text()')[0].strip()
            try:
                prev_rank = rank_rows[i].xpath('td[8]/text()')[0].strip()
            except IndexError:
                prev_rank = rank_rows[i].xpath('td[8]/*/text()')[0].strip()
            if '+' in prev_rank:
                rank_flux = f'{green}{prev_rank}{colorend}'
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = f'{red}{prev_rank}{colorend}'
            try:
                player = rank_rows[i].xpath('td[4]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                player = rank_rows[i].xpath('td[4]/*[1]/text()')[0].encode('raw_unicode_escape')
                if player in plist:
                    player = rank_rows[i].xpath('td[4]/*[2]/text()')[0].encode('raw_unicode_escape')
            try:
                points = rank_rows[i].xpath('td[7]/text()')[0]
            except IndexError:
                points = rank_rows[i].xpath('td[7]/*/text()')[0]
            try:
                tournament = rank_rows[i].xpath('td[10]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                tournament = rank_rows[i].xpath('td[10]/*/text()')[0].encode('raw_unicode_escape')
            try:
                max_points = rank_rows[i].xpath('td[14]/text()')[0]
            except IndexError:
                max_points = rank_rows[i].xpath('td[14]/*/text()')[0]
            if tournament.decode('utf-8') == '-':
                tournament = 'Not playing'.encode('raw_unicode_escape')
            if str(max_points) == '-':
                max_points = points
            plist.append(player)
            flux_list.append(rank_flux)
            point_list.append(points)
            mp_list.append(max_points)
            tourn_list.append(tournament)
        else:
            try:
                rank = rank_rows[i+2].xpath('td[1]/text()')[0].strip()
            except IndexError:
                rank = rank_rows[i+2].xpath('td[1]/span/text()')[0].strip()
            try:
                prev_rank = rank_rows[i+2].xpath('td[8]/text()')[0].strip()
            except IndexError:
                prev_rank = rank_rows[i+2].xpath('td[8]/span/text()')[0].strip()
            if '+' in prev_rank:
                rank_flux = f'{green}{prev_rank}{colorend}'
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = f'{red}{prev_rank}{colorend}'
            try:
                player = rank_rows[i+2].xpath('td[4]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                player = rank_rows[i+2].xpath('td[4]/*[1]/text()')[0].encode('raw_unicode_escape')
                if player in plist:
                    player = rank_rows[i+2].xpath('td[4]/*[2]/text()')[0].encode('raw_unicode_escape')
            try:
                points = rank_rows[i+2].xpath('td[7]/text()')[0]
            except IndexError:
                points = rank_rows[i+2].xpath('td[7]/*/text()')[0]
            try:
                tournament = rank_rows[i+2].xpath('td[10]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                tournament = rank_rows[i+2].xpath('td[10]/*/text()')[0].encode('raw_unicode_escape')
            try:
                max_points = rank_rows[i+2].xpath('td[14]/text()')[0]
            except IndexError:
                max_points = rank_rows[i+2].xpath('td[14]/*/text()')[0]
            if tournament.decode('utf-8') == '-':
                tournament = 'Not playing'.encode('raw_unicode_escape')
            if str(max_points) == '-':
                max_points = points
            plist.append(player)
            flux_list.append(rank_flux)
            point_list.append(points)
            mp_list.append(max_points)
            tourn_list.append(tournament)

    if len(text) > 1:
        if text[1].isdigit():
            num = int(text[1])
            if num < 31:
                rank = str(num)
                player = plist[num-1]
                rank_flux = flux_list[num-1]
                points = point_list[num-1]
                max_points = mp_list[num-1]
                tournament = tourn_list[num-1]
            else:
                num = num + int(num/50) + 1
                row = rank_rows[(num+(num-1))-1]
                try:
                    rank = row.xpath('td[1]/text()')[0].strip()
                except IndexError:
                    rank = row.xpath('td[1]/span/text()')[0].strip()
                try:
                    prev_rank = row.xpath('td[8]/text()')[0].strip()
                except IndexError:
                    prev_rank = row.xpath('td[8]/span/text()')[0].strip()
                if '+' in prev_rank:
                    rank_flux = f'{green}{prev_rank}{colorend}'
                elif prev_rank == '-':
                    rank_flux = prev_rank
                else:
                    rank_flux = f'{red}{prev_rank}{colorend}'
                try:
                    player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape')
                except IndexError:
                    try:
                        player = row.xpath('td[4]/*/text()')[0].encode('raw_unicode_escape')
                    except IndexError:
                        reply("Can't find ranking.")
                        return
                try:
                    points = row.xpath('td[7]/text()')[0]
                except IndexError:
                    points = row.xpath('td[7]/*/text()')[0]
                try:
                    tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
                except IndexError:
                    tournament = row.xpath('td[10]/*/text()')[0].encode('raw_unicode_escape')
                try:
                    max_points = row.xpath('td[14]/text()')[0]
                except IndexError:
                    max_points = row.xpath('td[14]/*/text()')[0]
                if tournament.decode('utf-8') == '-':
                    tournament = 'Not playing'.encode('raw_unicode_escape')
                if str(max_points) == '-':
                    max_points = points
            reply('#' + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + 'pts' + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')
            return
        elif text[1].isalpha():
            intxt = ' '.join(text[1:]).upper()
            input_form = unicodedata.normalize('NFKD', intxt)
            new_input = ''.join([c for c in input_form if not unicodedata.combining(c)])
            for name in plist:
                # print(name.decode('utf-8'))
                nfkd_form = unicodedata.normalize('NFKD', name.decode('utf-8'))
                player_check = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
                if new_input in player_check.upper():
                    rank = plist.index(name)+1
                    player = name
                    rank_flux = flux_list[rank-1]
                    points = point_list[rank-1]
                    max_points = mp_list[rank-1]
                    tournament = tourn_list[rank-1]
                    reply('#' + str(rank) + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + 'pts' + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')
                    break
                    return
            for row in rank_rows[62:]:
                try:
                    check_player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                except IndexError:
                    continue
                nfkd_form = unicodedata.normalize('NFKD', check_player)
                player_check = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
                if new_input in player_check.upper():
                    try:
                        rank = row.xpath('td[1]/text()')[0].strip()
                    except IndexError:
                        rank = row.xpath('td[1]/span/text()')[0].strip()
                    try:
                        prev_rank = row.xpath('td[8]/text()')[0].strip()
                    except IndexError:
                        prev_rank = row.xpath('td[8]/span/text()')[0].strip()
                    if '+' in prev_rank:
                        rank_flux = f'{green}{prev_rank}{colorend}'
                    elif prev_rank == '-':
                        rank_flux = prev_rank
                    else:
                        rank_flux = f'{red}{prev_rank}{colorend}'
                    try:
                        player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape')
                    except IndexError:
                        try:
                            player = row.xpath('td[4]/*/text()')[0].encode('raw_unicode_escape')
                        except IndexError:
                            reply("Can't find player.")
                    try:
                        points = row.xpath('td[7]/text()')[0]
                    except IndexError:
                        points = row.xpath('td[7]/*/text()')[0]
                    try:
                        tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
                    except IndexError:
                        tournament = row.xpath('td[10]/*/text()')[0].encode('raw_unicode_escape')
                    try:
                        max_points = row.xpath('td[14]/text()')[0]
                    except IndexError:
                        max_points = row.xpath('td[14]/*/text()')[0]
                    if tournament.decode('utf-8') == '-':
                        tournament = 'Not playing'.encode('raw_unicode_escape')
                    if str(max_points) == '-':
                        max_points = points
                    reply('#' + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + 'pts' + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')
                    break
                    return
        else:
            reply('Could not find ranking.')
            return
    else:
        top_ten = ''
        for i in range(10):  
            top_ten = top_ten + str(i+1) + '. ' + plist[i].decode('utf-8') + ' (' + flux_list[i] + '), '
        reply(top_ten[0:-2])
        return