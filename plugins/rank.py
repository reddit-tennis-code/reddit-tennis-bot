import requests
from cloudbot import hook
from lxml import html
import unicodedata
import math

@hook.command("rank")
def rank(text,reply):
    """.rank <atp/wta> <rank/player name> returns the official ranking information for the rank or player chosen."""

    text = text.strip()
    text = text.split(' ')

    try:
        if text[0].lower() == 'atp':
            page = requests.get('https://live-tennis.eu/en/official-atp-ranking')
        elif text[0].lower() == 'wta':
            page = requests.get('https://live-tennis.eu/en/official-wta-ranking')
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

    try:
        if text[2].isdigit():
            num = int(text[2])
            if num >= 11 and num < 51:
                num = num+1
            elif num >= 51 and num < 250:
                num = num+(math.floor(num/50)+1)
            else:
                num = num+5
            row = rank_rows[num-1]
            try:
                rank = row.xpath('td[1]/text()')[0].strip()
            except IndexError:
                rank = row.xpath('td[1]/span/text()')[0].strip()
            try:
                prev_rank = row.xpath('td[8]/text()')[0]
            except IndexError:
                prev_rank = row.xpath('td[8]/span/text()')[0]
            if '+' in prev_rank:
                rank_flux = green+prev_rank+colorend
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = red+prev_rank+colorend
            try:
                player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                try:
                    player = row.xpath('td[4]/*/text()')[0].encode('raw_unicode_escape')
                except IndexError:
                    reply("Can't find ranking.")
            points = row.xpath('td[7]/text()')[0]
            tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
            max_points = row.xpath('td[14]/text()')[0]
            if tournament.decode('utf-8') == '-':
                tournament = 'Not playing'.encode('raw_unicode_escape')
            if str(max_points) == '-':
                max_points = points
            reply(rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')

        elif text[2].isalpha():
            intxt = ' '.join(text[2:]).upper()
            input_form = unicodedata.normalize('NFKD', intxt)
            new_input = ''.join([c for c in input_form if not unicodedata.combining(c)])
            for row in rank_rows:
                try:
                    try:
                        check_player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                        nfkd_form = unicodedata.normalize('NFKD', check_player)
                        player_check = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
                        in_check = new_input in player_check.upper()
                    except IndexError:
                        check_player1 = row.xpath('td[4]/*[1]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                        check_player2 = row.xpath('td[4]/*[2]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                        nfkd_form1 = unicodedata.normalize('NFKD', check_player1)
                        nfkd_form2 = unicodedata.normalize('NFKD', check_player2)
                        player_check1 = ''.join([c for c in nfkd_form1 if not unicodedata.combining(c)])
                        player_check2 = ''.join([c for c in nfkd_form2 if not unicodedata.combining(c)])
                        in_check = new_input in player_check1.upper() or new_input in player_check2.upper()
                    if in_check:
                        rank = row.xpath('td[1]/text()')[0].strip()
                        if not rank:
                            rank = row.xpath('td[1]/span/text()')[0].strip()
                        prev_rank = row.xpath('td[8]/text()')[0]
                        if '+' in prev_rank:
                            rank_flux = green+prev_rank+colorend
                        elif prev_rank == '-':
                            rank_flux = prev_rank
                        else:
                            rank_flux = red+prev_rank+colorend
                        try:
                            player = row.xpath('td[4]/text()')[0].encode('raw_unicode_escape')
                        except IndexError:
                            try:
                                if new_input in player_check1.upper():
                                    player = row.xpath('td[4]/*[1]/text()')[0].encode('raw_unicode_escape')
                                if new_input in player_check2.upper():
                                    player = row.xpath('td[4]/*[2]/text()')[0].encode('raw_unicode_escape')
                            except IndexError:
                                reply("Can't find player.")
                        points = row.xpath('td[7]/text()')[0]
                        tournament = row.xpath('td[10]/text()')[0].encode('raw_unicode_escape')
                        max_points = row.xpath('td[14]/text()')[0]
                        if tournament.decode('utf-8') == '-':
                            tournament = 'Not playing'.encode('raw_unicode_escape')
                        if str(max_points) == '-':
                            max_points = points
                        reply(rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + '. Current tournament: ' + tournament.decode('utf-8') + ', max points possible = ' + max_points + '\n')
                        break
                except IndexError:
                    continue
        else:
            reply('Could not find ranking.')
    except IndexError:
        top_ten = ''
        plist = []
        for i in range(0,10,1):
            rank = rank_rows[i].xpath('td[1]/text()')[0].strip()
            prev_rank = rank_rows[i].xpath('td[8]/text()')[0]
            if '+' in prev_rank:
                rank_flux = green+prev_rank+colorend
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = red+prev_rank+colorend
            try:
                player = rank_rows[i].xpath('td[4]/text()')[0].encode('raw_unicode_escape')
            except IndexError:
                try:
                    player = rank_rows[i].xpath('td[4]/span/text()')[0].encode('raw_unicode_escape')
                except IndexError:
                    player = rank_rows[i].xpath('td[4]/*[1]/text()')[0].encode('raw_unicode_escape')
                    if player in plist:
                        player = rank_rows[i].xpath('td[4]/*[2]/text()')[0].encode('raw_unicode_escape')
            plist.append(player)
            top_ten = top_ten + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + '), '
        reply(top_ten[0:-2])