import requests
from cloudbot import hook
from lxml import html
import json
import datetime

@hook.command("rankhistory")
def rankhistory(text,reply):
    "<atp/wta> <player name> <YYYY-MM-DD> returns the official singles ranking of the player that week."

    rq = text.split(' ')
    if not rq:
        reply('Format: .rankhistory atp federer')

    nick_dict = {'shoulders':'Maria%20Sakkari','muguruza':'Garbine%20Muguruza','azarenka':'Victoria%20Azarenka', \
	'dave':'Novak%20Djokovic','delpo':'delpo','evert':r'Chris%20Evert','bjk':r'Billie%20Jean%20King', \
        'faa':r'Felix%20Auger%20Aliassime'}

    if rq[0] == 'atp':
        num = '2'
    elif rq[0] == 'wta':
        num = '4'
    else:
        reply('Invalid tour. Please type "atp" or "wta" after the command.')
        return

    if len(rq[1:-1]) > 1:
        search_text = '+'.join(rq[1:-1])
    else:
        search_text = rq[1:-1][0]

    date = rq[-1]
    try:
        date_obj = datetime.datetime.strptime(date,'%Y-%m-%d')
    except ValueError:
        reply('Invalid date/date format. Must be YYYY-MM-DD.')
        return

    if search_text in nick_dict:
        name_lookup = nick_dict[search_text]
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={search_text}')
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath(f'//table[@class="result"]/tbody/tr[1]/td[{num}]/a/text()')[0].split(',')
        except IndexError:
            reply('Could not find player.')
            return
        name_lookup = '%20'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])

    if num == '2':
        url = f'https://www.atptour.com/en/-/ajax/playersearch/PlayerUrlSearch?searchTerm={name_lookup}'
        player_json = requests.get(url).json()
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
    else:
        url = f'https://www.wtatennis.com/search/players/{name_lookup}'
        search_tree = html.fromstring(requests.get(url).text)
        player_div = search_tree.xpath('//div[@id="block-luxbox-search-luxbox-search-block-players"]/div[1]/div')
        if len(player_div) > 1:
            reply('Multiple players returned. Please refine your search.')
            return
        elif len(player_div) == 0:
            reply('No players found.')
            return
        
        link_div = player_div[0].xpath('div[1]/div[2]/h2/a/@href')[0]
        pname = player_div[0].xpath('div[1]/div[2]/h2/a/text()')[0].strip()
        split_link = link_div.split('/')
        monday1 = date_obj - datetime.timedelta(days=date_obj.weekday())
        monday2 = (monday1 - datetime.timedelta(days=1)) - datetime.timedelta(days=(monday1 - datetime.timedelta(days=1)).weekday())
        datestr1 = f'{monday1.strftime("%m")}-{monday1.strftime("%d")}-{monday1.strftime("%Y")}'
        datestr2 = f'{monday2.strftime("%m")}-{monday2.strftime("%d")}-{monday2.strftime("%Y")}'
        hist_url = f'https://www.wtatennis.com/player/{split_link[-3]}/print/rankings-history/{monday1.strftime("%Y")}'

        page = requests.get(hist_url)
        tree = html.fromstring(page.text)
        rank_rows = tree.xpath('//table[@id="weekly-rankings-table"]/tbody/tr')

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

    reply(f'Valid date, but no ranking found for {pname} for that week.')
