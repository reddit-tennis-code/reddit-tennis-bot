import requests
from cloudbot import hook
from lxml import html
import unicodedata

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
        if text[1].isdigit():
            for row in rank_rows:
                try:
                    check_num = row.xpath('td[1]/text()')[0].strip()
                    if not check_num:
                        check_num = row.xpath('td[1]/span/text()')[0].strip()
                    if text[1] == check_num:
                        rank = row.xpath('td[1]/text()')[0].strip()
                        if not rank:
                            rank = row.xpath('td[1]/span/text()')[0].strip()
                        prev_rank = row.xpath('td[7]/text()')[0]
                        if '+' in prev_rank:
                            rank_flux = f'{green}{prev_rank}{colorend}'
                        elif prev_rank == '-':
                            rank_flux = prev_rank
                        else:
                            rank_flux = f'{red}{prev_rank}{colorend}'
                        player = row.xpath('td[3]/text()')[0].encode('raw_unicode_escape')
                        points = row.xpath('td[6]/text()')[0]
                        reply(rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + '\n')
                        return
                except IndexError:
                    continue
        elif text[1].isalpha():
            intxt = ' '.join(text[1:]).upper()
            input_form = unicodedata.normalize('NFKD', intxt)
            new_input = ''.join([c for c in input_form if not unicodedata.combining(c)])
            for row in rank_rows:
                try:
                    check_player = row.xpath('td[3]/text()')[0].encode('raw_unicode_escape').decode('utf-8')
                    nfkd_form = unicodedata.normalize('NFKD', check_player)
                    player_check = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
                    if new_input in player_check.upper():
                        rank = row.xpath('td[1]/text()')[0].strip()
                        if not rank:
                            rank = row.xpath('td[1]/span/text()')[0].strip()
                        prev_rank = row.xpath('td[7]/text()')[0]
                        if '+' in prev_rank:
                            rank_flux = f'{green}{prev_rank}{colorend}'
                        elif prev_rank == '-':
                            rank_flux = prev_rank
                        else:
                            rank_flux = f'{red}{prev_rank}{colorend}'
                        player = row.xpath('td[3]/text()')[0].encode('raw_unicode_escape')
                        points = row.xpath('td[6]/text()')[0]
                        reply(rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + ') ' + points + '\n')
                        return
                except IndexError:
                    continue
        else:
            reply('Could not find ranking.')
            return
    except IndexError:
        top_ten = ''
        for i in range(0,20,2):
            rank = rank_rows[i].xpath('td[1]/text()')[0].strip()
            prev_rank = rank_rows[i].xpath('td[7]/text()')[0]
            if '+' in prev_rank:
                rank_flux = f'{green}{prev_rank}{colorend}'
            elif prev_rank == '-':
                rank_flux = prev_rank
            else:
                rank_flux = f'{red}{prev_rank}{colorend}'
            player = rank_rows[i].xpath('td[3]/text()')[0].encode('raw_unicode_escape')
            top_ten = top_ten + rank + '. ' + player.decode('utf-8') + ' (' + rank_flux + '), '
        reply(top_ten[0:-2])
        return