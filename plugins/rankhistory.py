import requests
from cloudbot import hook
from lxml import html
import json
import datetime

@hook.command("rankhistory")
def rankhistory(text,reply):
    "<atp/wta> <player name> <YYYY-MM-DD> returns the official singles ranking of the player that week."

    headers = {'GET': '/posts/35306761/ivc/15ce?_=1630535997785 HTTP/1.1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'prov=a10aab95-0270-115d-b275-c5d684dde609'}

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
        page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl={}'.format(search_text))
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[{}]/a/text()'.format(num))[0].split(',')
        except IndexError:
            reply('Could not find player.')
            return
        name_lookup = '%20'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])

    if num == '2':
        url = 'https://www.atptour.com/en/-/ajax/playersearch/PlayerUrlSearch?searchTerm={}'.format(name_lookup)
        player_json = requests.get(url,headers=headers).json()
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

        hist_url = 'https://www.atptour.com{}'.format(new_url)
        page = requests.get(hist_url,headers=headers)
        tree = html.fromstring(page.text)
        rank_rows = tree.xpath('//table[@class="mega-table"]/tbody/tr')
        monday1 = date_obj - datetime.timedelta(days=date_obj.weekday())
        monday2 = (monday1 - datetime.timedelta(days=1)) - datetime.timedelta(days=(monday1 - datetime.timedelta(days=1)).weekday())
        wednesday1 = monday2 + datetime.timedelta(days=2)
        datestr1 = '{}.{}.{}'.format(monday1.strftime("%Y"),monday1.strftime("%m"),monday1.strftime("%d"))
        datestr2 = '{}.{}.{}'.format(monday2.strftime("%Y"),monday2.strftime("%m"),monday2.strftime("%d"))
        datestr3 = '{}.{}.{}'.format(wednesday1.strftime("%Y"),wednesday1.strftime("%m"),wednesday1.strftime("%d"))

        for row in rank_rows:
            site_date = row.xpath('td[1]/text()')[0].strip()
            if site_date == datestr1:
                rank = row.xpath('td[2]/text()')[0].strip()
                reply('{}: #{} on {} {}, {}'.format(pname,rank,date_obj.strftime("%B"),date_obj.strftime("%d"),date_obj.strftime("%Y")))
                return
            elif site_date == datestr2:
                rank = row.xpath('td[2]/text()')[0].strip()
                reply('{}: #{} on {} {}, {}'.format(pname,rank,date_obj.strftime("%B"),date_obj.strftime("%d"),date_obj.strftime("%Y")))
                return
            elif site_date == datestr3:
                rank = row.xpath('td[2]/text()')[0].strip()
                reply('{}: #{} on {} {}, {}'.format(pname,rank,date_obj.strftime("%B"),date_obj.strftime("%d"),date_obj.strftime("%Y")))
                return
    else:
        url = 'https://api.wtatennis.com/tennis/players/?page=0&pageSize=20&name={}&nationality='.format(name_lookup)
        player_json = requests.get(url,headers=headers).json()

        player_url = 'https://api.wtatennis.com/tennis/players/{}/ranking?from={}-01-01&to={}-12-31&aggregation-method=weekly'.format(str(player_json['content'][0]['id']),date[0:4],date[0:4])
        pname = player_json['content'][0]['fullName']

        rank_json = requests.get(player_url,headers=headers).json()
        for wranking in rank_json['weeklyRankings']:
            week_rank = wranking['rankedAt'][0:10]
            rank_date = datetime.datetime.strptime(week_rank,'%Y-%m-%d')
            if date_obj > rank_date:
                rank = str(wranking['singlesRanking'])
                reply('{}: #{} on {} {}, {}'.format(pname,rank,date_obj.strftime("%B"),date_obj.strftime("%d"),date_obj.strftime("%Y")))
                return

    reply('Valid date, but no ranking found for {} for that week.'.format(pname))
