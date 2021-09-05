import requests
from lxml import html
from cloudbot import hook
import json

@hook.command('h2hm')
def h2hm(text,reply):
    """<name/name> will bring up the head2head record of two ATP players."""

    headers = {'GET': '/posts/35306761/ivc/15ce?_=1630535997785 HTTP/1.1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'prov=a10aab95-0270-115d-b275-c5d684dde609'}
        
    rq = text
    if not rq:
        return('Format: .h2hm federer/nadal')

    nick_dict = {'delpo': 'Juan_Martin_Del_Potro','ddr': 'Kei_Nishikori','dave': 'Novak_Djokovic','goat': 'Tommy_Robredo',
    'diegoat': 'Diego_Sebastian_Schwartzman'}

    rq = rq.strip()
    rq = rq.split('/')

    if rq[0] in nick_dict:
        name_lookup1 = nick_dict[rq[0]]
        url_name1 = '-'.join(name_lookup1.split('_'))
    else:
        page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl={}'.format(rq[0]))
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[2]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        name_lookup1 = '%20'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])
        url_name1 = '-'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])

    if rq[1] in nick_dict:
        name_lookup2 = nick_dict[rq[0]]
        url_name2 = '-'.join(name_lookup2.split('_'))
    else:
        page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl={}'.format(rq[1]))
        tree = html.fromstring(page.text)
        try:
            p2text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[2]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        name_lookup2 = '%20'.join([p2text[1][1:].replace(' ','_'),p2text[0].replace(' ','_')])
        url_name2 = '-'.join([p2text[1][1:].replace(' ','_'),p2text[0].replace(' ','_')])

    url1 = 'https://www.atptour.com/en/-/ajax/playersearch/PlayerUrlSearch?searchTerm={}'.format(name_lookup1)
    player_json1 = requests.get(url1).json()
    if len(player_json1['items']) > 1:
        reply('Multiple players returned. Please refine your search.')
        return
    elif len(player_json1['items']) == 0:
        reply('No players found.')
        return
    player1_id = player_json1['items'][0]['Value'].split('/')[-2]

    url2 = 'https://www.atptour.com/en/-/ajax/playersearch/PlayerUrlSearch?searchTerm={}'.format(name_lookup2)
    player_json2 = requests.get(url2).json()
    if len(player_json2['items']) > 1:
        reply('Multiple players returned. Please refine your search.')
        return
    elif len(player_json2['items']) == 0:
        reply('No players found.')
        return
    player2_id = player_json2['items'][0]['Value'].split('/')[-2]

    h2h_url = 'https://www.atptour.com/en/players/atp-head-2-head/{}-vs-{}/{}/{}'.format(url_name1,url_name2,player1_id,player2_id)
    h2h_page = requests.get(h2h_url,headers=headers)
    h2h_tree = html.fromstring(h2h_page.text)
    h2h_json = json.loads(h2h_tree.xpath('//script[contains(., "playerLeft")]/text()')[0])

    disp1 = '{} {}'.format(h2h_json['playerLeft']['firstName'],h2h_json['playerLeft']['lastName'])
    w1 = h2h_json['playerLeft']['winCount']

    disp2 = '{} {}'.format(h2h_json['playerRight']['firstName'],h2h_json['playerRight']['lastName'])
    w2 = h2h_json['playerRight']['winCount']

    try:
        ltourney = h2h_json['Tournaments'][0]['TournamentName']
        lyear = h2h_json['Tournaments'][0]['EventYear']
        lround = h2h_json['Tournaments'][0]['MatchResults'][0]['Round']['LongName']
        sets1 = h2h_json['Tournaments'][0]['MatchResults'][0]['PlayerTeam']['Sets']
        sets2 = h2h_json['Tournaments'][0]['MatchResults'][0]['OpponentTeam']['Sets']
        reason = h2h_json['Tournaments'][0]['MatchResults'][0]['Reason']
        lscore = []
        if h2h_json['Tournaments'][0]['MatchResults'][0]['Winner'][0] == h2h_json['playerLeft']['lastName'][0]:
            lwinner = disp1
            lloser = disp2
            for i in range(len(sets1)):
                lscore.append('{}-{}'.format(sets1[i]['SetScore'],sets2[i]['SetScore']))

        else:
            lwinner = disp2
            lloser = disp1
            for i in range(len(sets1)):
                lscore.append('{}-{}'.format(sets2[i]['SetScore'],sets1[i]['SetScore']))
            
        lscore_str = ', '.join(lscore)
        if reason:
            if reason == "RET":
                reason_str = '{}.'.format(reason.lower())
            else:
                reason_str = '{}'.format(reason.lower())
        else:
            reason_str = '' 

        if lscore_str == '':
            result_string = '{} {} - {} {}. Last: {} {} {}, {} d. {}{} {}'.format(disp1,w1,w2,disp2,lyear,ltourney,lround,lwinner,lloser,lscore_str,reason_str)
        else:
            result_string = '{} {} - {} {}. Last: {} {} {}, {} d. {} {} {}'.format(disp1,w1,w2,disp2,lyear,ltourney,lround,lwinner,lloser,lscore_str,reason_str)
    except IndexError:
        result_string = '{} {} - {} {}'.format(disp1,w1,w2,disp2)

    reply(result_string)
