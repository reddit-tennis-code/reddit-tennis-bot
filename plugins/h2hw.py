import requests
from lxml import html
from cloudbot import hook

@hook.command('h2hw')
def h2hw(text,reply):
    """<name/name> will bring up the head2head record of two WTA players."""

    headers = {'GET': '/posts/35306761/ivc/15ce?_=1630535997785 HTTP/1.1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'prov=a10aab95-0270-115d-b275-c5d684dde609'}
    
    round_dict = {'R128': 'Round of 128', 'R64': 'Round of 64', 'R32': 'Round of 32', 'R16': 'Round of 16',
              'Q': 'Quarterfinal', 'S': 'Semfinal', 'F': 'Final'}
        
    rq = text
    if not rq:
        return('Format: .h2hw sharapova/serena')

    nick_dict = {'shoulders':'Maria_Sakkari','muguruza':'Garbine_Muguruza','azarenka':'Victoria_Azarenka'}

    rq = rq.strip()
    rq = rq.split('/')

    if rq[0] in nick_dict:
        name_lookup1 = nick_dict[rq[0]]
        # url_name1 = '-'.join(name_lookup1.split('_'))
    else:
        page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl={}'.format(rq[0]))
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[4]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        name_lookup1 = '%20'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])
        # url_name1 = '-'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])

    if rq[1] in nick_dict:
        name_lookup2 = nick_dict[rq[0]]
        # url_name2 = '-'.join(name_lookup2.split('_'))
    else:
        page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl={}'.format(rq[1]))
        tree = html.fromstring(page.text)
        try:
            p2text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[4]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        name_lookup2 = '%20'.join([p2text[1][1:].replace(' ','_'),p2text[0].replace(' ','_')])
        # url_name2 = '-'.join([p2text[1][1:].replace(' ','_'),p2text[0].replace(' ','_')])

    url1 = 'https://api.wtatennis.com/tennis/players/?page=0&pageSize=20&name={}&nationality='.format(name_lookup1)
    player_json1 = requests.get(url1).json()
    if player_json1['pageInfo']['numEntries'] > 1:
        reply('Multiple players returned. Please refine your search.')
        return
    elif player_json1['pageInfo']['numEntries'] == 0:
        reply('No players found.')
        return
    player1_id = str(player_json1['content'][0]['id'])

    url2 = 'https://api.wtatennis.com/tennis/players/?page=0&pageSize=20&name={}&nationality='.format(name_lookup2)
    player_json2 = requests.get(url2).json()
    if player_json2['pageInfo']['numEntries'] > 1:
        reply('Multiple players returned. Please refine your search.')
        return
    elif player_json2['pageInfo']['numEntries'] == 0:
        reply('No players found.')
        return
    player2_id =str(player_json2['content'][0]['id'])

    h2h_url = 'https://api.wtatennis.com/tennis/players/{}/headtohead/{}?sort=desc'.format(player1_id,player2_id)
    h2h_json = requests.get(h2h_url,headers=headers).json()

    disp1 = '{} {}'.format(h2h_json['bio'][0]['firstname'],h2h_json['bio'][0]['lastname'])
    disp2 = '{} {}'.format(h2h_json['bio'][1]['firstname'],h2h_json['bio'][1]['lastname'])

    try:
        w1 = str(h2h_json['headToHeadSummary'][0]['wins'])
        w2 = str(h2h_json['headToHeadSummary'][0]['losses'])
        ltourney = h2h_json['matchEncounterResults'][0]['TournamentName'].lower().capitalize()
        lyear = h2h_json['matchEncounterResults'][0]['StartDate'][0:4]
        lround = round_dict[h2h_json['matchEncounterResults'][0]['round_name']]
        lscore = h2h_json['matchEncounterResults'][0]['scores']
        reason_code = h2h_json['matchEncounterResults'][0]['reason_code']
        if h2h_json['matchEncounterResults'][0]['winner'] == 1:
            lwinner = disp1
            lloser = disp2
        else:
            lwinner = disp2
            lloser = disp1
            
        if lscore == '':
            lscore_str = 'w/o'
        else:
            lscore_str = ', '.join(lscore.split('  '))
        
        if reason_code == 'R':
            reason_str = 'ret.'
        else:
            reason_str = ''

        result_string = '{} {} - {} {}. Last: {} {} {}, {} d. {} {} {}'.format(disp1,w1,w2,disp2,lyear,ltourney,lround,lwinner,lloser,lscore_str,reason_str)
    except IndexError:
        w1 = '0'
        w2 = '0'
        result_string = '{} {} - {} {}'.format(disp1,w1,w2,disp2)

    reply(result_string)