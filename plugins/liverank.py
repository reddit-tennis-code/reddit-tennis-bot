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

    if len(text) > 1:
        if text[1].isdigit():
            for row in rank_rows:
                try:
                    check_num = row.xpath('td[1]/text()')[0].strip()
                except IndexError:
                    try:
                        check_num = row.xpath('td[1]/span/text()')[0].strip()
                    except IndexError:
                        continue
                else:
                    if text[1] == check_num:
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
                            player = row.xpath('td[4]/span/text()')[0].encode('raw_unicode_escape')
                        points = row.xpath('td[7]/text()')[0]
                        tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
                        max_points = row.xpath('td[14]/text()')[0]
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
            for row in rank_rows:
                try:
                    check_player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                except IndexError:
                    try:
                        check_player = row.xpath('td[4]/span/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                    except IndexError:
                        continue
                else:
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
                            player = row.xpath('td[4]/span/text()')[0].encode('raw_unicode_escape')
                        points = row.xpath('td[7]/text()')[0]
                        tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
                        max_points = row.xpath('td[14]/text()')[0]
                        if tournament.decode('utf-8') == '-':
                            tournament = 'Not playing'.encode('raw_unicode_escape')
                        if str(max_points) == '-':
                            max_points = points
                        reply('#' + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + 'pts' + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')
                        return
        else:
            reply('Could not find ranking.')
            return
    else:
        top_ten = ''
        for i in range(0,20,2):
            try:
                rank = rank_rows[i].xpath('td[1]/text()')[0].strip()
            except IndexError:
                rank = rank_rows[i].xpath('td[1]/span/text()')[0].strip()
            try:
                prev_rank = rank_rows[i].xpath('td[8]/text()')[0].strip()
            except IndexError:
                prev_rank = rank_rows[i].xpath('td[8]/span/text()')[0].strip()
            if '+' in prev_rank:
                rank_flux = f'{green}{prev_rank}{colorend}'
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = f'{red}{prev_rank}{colorend}'
            try:
                player = rank_rows[i].xpath('td[4]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                player = rank_rows[i].xpath('td[4]/span/text()')[0].encode('raw_unicode_escape')
            top_ten = top_ten + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + '), '
        reply(top_ten[0:-2])
        return