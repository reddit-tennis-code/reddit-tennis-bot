import requests
from lxml import html

from cloudbot import hook


@hook.command('h2hm')
def h2hm(text):
    """<name/name> will bring up the head2head record of two ATP players."""
    rq = ' '.join(text[1:])
    if not rq:
        return('Format: .h2hm federer/nadal')

    nick_dict = {'delpo': 'Juan_Martin_Del_Potro','ddr': 'Kei_Nishikori','dave': 'Novak_Djokovic','goat': 'Tommy_Robredo',
    'diegoat': 'Diego_Sebastian_Schwartzman'}

    rq = rq.strip()
    rq = rq.split('/')

    if rq[0] in nick_dict:
        p1 = nick_dict[rq[0]]
        disp1 = ' '.join(p1.split('_'))
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={rq[0]}')
        tree = html.fromstring(page.text)
        try:
            p1text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[2]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        p1 = '_'.join([p1text[1][1:].replace(' ','_').replace('-','_'),p1text[0].replace(' ','_').replace('-','_')])
        disp1 = ' '.join([p1text[1][1:].replace('-',' '),p1text[0].replace('-',' ')])

    if rq[1] in nick_dict:
        p2 = nick_dict[rq[1]]
        disp2 = ' '.join(p2.split('_'))
    else:
        page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={rq[1]}')
        tree = html.fromstring(page.text)
        try:
            p2text = tree.xpath('//table[@class="result"]/tbody/tr[1]/td[2]/a/text()')[0].split(',')
        except IndexError:
            return('Invalid name, probably.')
        p2 = '_'.join([p2text[1][1:].replace(' ','_').replace('-','_'),p2text[0].replace(' ','_').replace('-','_')])
        disp2 = ' '.join([p2text[1][1:].replace('-',' '),p2text[0].replace('-',' ')])

    page = requests.get(f'http://www.stevegtennis.com/head-to-head/men/{p1}/{p2}/')
    tree = html.fromstring(page.text)

    try:
        w1 = tree.xpath('//table[@id="player_info"]/tr[1]/td[1]/div/text()')[0]
        w2 = tree.xpath('//table[@id="player_info"]/tr[1]/td[3]/div/text()')[0]
        h2h = disp1 + ' ' + w1 + ' - ' + w2 + ' ' + disp2
    except IndexError:
        h2h = 'Names were chosen, but this doesn\'t work on stevegtennis for some reason.'
    return(h2h)
