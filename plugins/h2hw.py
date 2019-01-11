import requests
from lxml import html

from cloudbot import hook


@hook.command('h2hw')
def h2hw(text):
    """<name/name> will bring up the head2head record of two WTA players."""
    rq = text
    if not rq:
        return('Format: .h2hw sharapova/serena')

    nick_dict = {'shoulders':'Maria_Sakkari','muguruza':'Garbine_Muguruza','azarenka':'Victoria_Azarenka'}

    rq = rq.strip()
    rq = rq.split('/')

    if rq[0] in nick_dict:
        p1 = nick_dict[rq[0]]
        disp1 = ' '.join(p1.split('_'))
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={rq[0]}')
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[4]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        p1 = '_'.join([p1text[1][1:].replace(' ','_'),p1text[0].replace(' ','_')])
        disp1 = ' '.join([p1text[1][1:],p1text[0]])

    if rq[1] in nick_dict:
        p2 = nick_dict[rq[1]]
        disp2 = ' '.join(p2.split('_'))
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={rq[1]}')
        tree = html.fromstring(page.text)
        try:
            p2text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[4]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        p2 = '_'.join([p2text[1][1:].replace(' ','_'),p2text[0].replace(' ','_')])
        disp2 = ' '.join([p2text[1][1:],p2text[0]])

    page = requests.get(f'http://www.stevegtennis.com/head-to-head/women/{p1}/{p2}/')
    tree = html.fromstring(page.text)

    try:
        w1 = tree.xpath('//table[@id="player_info"]/tr[1]/td[1]/div/text()')[0]
        w2 = tree.xpath('//table[@id="player_info"]/tr[1]/td[3]/div/text()')[0]
        lyear = tree.xpath('//tr[@class="row1"]/td[1]/text()')[0]
        ltourney = tree.xpath('//tr[@class="row1"]/td[2]/a/text()')[0]
        lround = tree.xpath('//tr[@class="row1"]/td[3]/text()')[0]
        lwinner = tree.xpath('//tr[@class="row1"]/td[5]/a/text()')[0]
        lloser = tree.xpath('//tr[@class="row1"]/td[6]/a/text()')[0]
        lscore = tree.xpath('//tr[@class="row1"]/td[7]/text()')[0].replace(' ',', ')
        h2h = f'{disp1} {w1} - {w2} {disp2}. Last: {lyear} {ltourney} {lround} {lwinner} d. {lloser} {lscore}'
    except IndexError:
        h2h = 'Names were chosen, but this doesn\'t work on stevegtennis for some reason.'
    return(h2h)
