import requests
from lxml import html
import datetime
from cloudbot import hook


@hook.command('chigh')
def chigh(text,reply):
    """<atp/wta> <player> will return the career high ranking of the player."""
    rq = text
    if not rq:
        reply('Format: .chigh wta evert')

    nick_dict = {'shoulders':'Maria%20Sakkari','muguruza':'Garbine%20Muguruza','azarenka':'Victoria%20Azarenka', \
        'dave':'Novak%20Djokovic','delpo':'delpo','evert':r'Chris%20Evert','bjk':r'Billie%20Jean%20King', \
            'faa':r'Felix%20Auger%20Aliassime'}

    rq = rq.strip()
    rq = rq.split(' ')

    if rq[0] == 'atp':
        num = '2'
    elif rq[0] == 'wta':
        num = '4'
    else:
        reply('Invalid tour. Please type "atp" or "wta" after the command.')

    if len(rq[1:]) > 1:
        search_text = '+'.join(rq[1:])
    else:
        search_text = rq[1]

    if search_text in nick_dict:
        name_lookup = nick_dict[search_text]
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={search_text}')
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath(f'//table[@class="result"]/tbody/tr[1]/td[{num}]/a/text()')[0].split(',')
        except IndexError:
            reply('Could not find player.')
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
        
        player_url = f'https://www.atptour.com{player_json["items"][0]["Value"]}'
        player_name = player_json['items'][0]['Key']

        ppage = requests.get(player_url)
        ptree = html.fromstring(ppage.text)
        rank = ptree.xpath('//table[@id="playersStatsTable"]/tbody/tr[2]/td[2]/div[1]')[0].get('data-singles').strip()
        date_raw = ptree.xpath('//table[@id="playersStatsTable"]/tbody/tr[2]/td[2]/div[2]')[0].get('data-singles-label').strip().split(' ')[-1]
        date_obj = datetime.datetime.strptime(date_raw,'%Y.%m.%d')

        reply(f'{player_name}: Singles Career High = #{rank} (first reached on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")})')
    else:
        url = 'https://api.wtatennis.com/tennis/players/?page=0&pageSize=20&name={}&nationality='.format(name_lookup)
        player_json = requests.get(url).json()

        player_url = 'https://www.wtatennis.com/players/{}/{}/rankings-history'.format(str(player_json['content'][0]['id']),url_name)
        player_name = player_json['content'][0]['fullName']

        ppage = requests.get(player_url)
        ptree = html.fromstring(ppage.text)
        check_rank = ptree.xpath('//div[@class="rankings-overview-item"]')
        if len(check_rank) == 4:
            rank = ptree.xpath('//div[@class="rankings-overview-item"][2]/div[3]/text()')[0].strip()
            date_raw = ptree.xpath('//div[@class="rankings-overview-item"][2]/div[4]/text()')[0].strip()
            date_obj = datetime.datetime.strptime(date_raw,'%b %d, %Y')
        else:
            rank = ptree.xpath('//div[@class="rankings-overview-item"]/div[3]/text()')[0].strip()
            date_raw = ptree.xpath('//div[@class="rankings-overview-item"]/div[4]/text()')[0].strip()
            date_obj = datetime.datetime.strptime(date_raw,'%b %d, %Y')

        reply(f'{player_name}: Singles Career High = #{rank} (first reached on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")})')
