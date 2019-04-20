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
        'dave':'Novak%20Djokovic','delpo':'delpo','evert':r'Chris%20Evert','bjk':r'Billie%20Jean%20King'}

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
        link_div = f'{link_div}#ranking'
        player_name = player_div[0].xpath('div[1]/div[2]/h2/a/text()')[0].strip()
        ptree = html.fromstring(requests.get(link_div).text)

        rank = ptree.xpath('//div[@class="rankings-container career-high"]/div[1]/p[1]/text()')[0].strip()
        date_raw = ptree.xpath('//div[@class="rankings-container career-high"]/div[1]/p[2]/text()')[0].strip()
        date_obj = datetime.datetime.strptime(date_raw,'%Y/%m/%d')

        reply(f'{player_name}: Singles Career High = #{rank} (first reached on {date_obj.strftime("%B")} {date_obj.strftime("%d")}, {date_obj.strftime("%Y")})')
