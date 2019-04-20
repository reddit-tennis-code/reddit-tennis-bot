import requests
from cloudbot import hook
from lxml import html
import json
import datetime

@hook.command("rankhistory")
def rankhistory(text,reply):
    "<player name> <YYYY-MM-DD> returns the official ATP ranking of the player that week"

    text = text.split(' ')
    player = '%20'.join(text[0:-1])
    date = text[-1]
    atp_url = f'https://www.atptour.com/en/-/ajax/playersearch/PlayerUrlSearch?searchTerm={player}'

    player_json = requests.get(atp_url).json()

    if len(player_json['items']) > 1:
        reply('Multiple players returned. Please refine your search.')
        return
    elif len(player_json['items']) == 0:
        reply('No players found.')
        return

    split_end = player_json['items'][0]['Value'].split('/')
    split_end[-1] = 'rankings-history'
    new_url = '/'.join(split_end)
    pname = player_json['items'][0]['Key']

    hist_url = f'https://www.atptour.com{new_url}'
    page = requests.get(hist_url)
    tree = html.fromstring(page.text)
    rank_rows = tree.xpath('//table[@class="mega-table"]/tbody/tr')
    try:
        date_obj = datetime.datetime.strptime(date,'%Y-%m-%d')
    except ValueError:
        reply('Invalid date format. Must be YYYY-MM-DD.')
        return
    monday1 = date_obj - datetime.timedelta(days=date_obj.weekday())
    monday2 = (monday1 - datetime.timedelta(days=1)) - datetime.timedelta(days=(monday1 - datetime.timedelta(days=1)).weekday())
    wednesday1 = monday2 + datetime.timedelta(days=2)
    datestr1 = f'{monday1.strftime("%Y")}.{monday1.strftime("%m")}.{monday1.strftime("%d")}'
    datestr2 = f'{monday2.strftime("%Y")}.{monday2.strftime("%m")}.{monday2.strftime("%d")}'
    datestr3 = f'{wednesday1.strftime("%Y")}.{wednesday1.strftime("%m")}.{wednesday1.strftime("%d")}'

    for row in rank_rows:
        site_date = row.xpath('td[1]/text()')[0].strip()
        if site_date == datestr1:
            rank = row.xpath('td[2]/text()')[0].strip()
            reply(f'{pname}: #{rank} on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")}')
            return
        elif site_date == datestr2:
            rank = row.xpath('td[2]/text()')[0].strip()
            reply(f'{pname}: #{rank} on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")}')
            return
        elif site_date == datestr3:
            rank = row.xpath('td[2]/text()')[0].strip()
            reply(f'{pname}: #{rank} on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")}')
            return

    reply('Valid date, but no ranking found.')
    return
    
