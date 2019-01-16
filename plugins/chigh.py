import requests
from lxml import html

from cloudbot import hook


@hook.command('chigh')
def chigh(text):
    """.chigh atp/wta <player> will return the career high ranking of the player."""
    rq = text
    if not rq:
        return('Format: .chigh atp djokovic')

    # nick_dict = {'shoulders':'Maria%20Sakkari','csn':'Carla%20Suarez%20Navarro','muguruza':'Garbine%20Muguruza'}

    rq = rq.strip()
    rq = rq.split(' ')

    if rq[0] == 'atp':
        num = '2'
    elif rq[0] == 'wta':
        num = '4'
    else:
        return('Invalid tour. Please type "atp" or "wta" after the command.')
	
    if len(rq[1:]) > 1:
        search_text = ' '.join(rq[1:])
    else:
        search_text = rq[1]

    page = requests.get(f'http://www.tennisexplorer.com/list-players/?search-text-pl={search_text}')
    tree = html.fromstring(page.text)
    try:
        plink_end = tree.xpath(f'//table[@class="result"]/tbody/tr[1]/td[{num}]/a/@href')
        plink = f'http://www.tennisexplorer.com{plink_end[0]}'
    except IndexError:
        return('Could not find player.')

    ppage = requests.get(plink)
    ptree = html.fromstring(ppage.text)

    try:
        pname = ptree.xpath('//div[@id="center"]/div/table/tbody/tr/td[2]/h3/text()')[0].split(' ')
        prank = ptree.xpath('//div[@id="center"]/div/table/tbody/tr/td[2]/div[3]/text()')[0].split(' ')
        if ')' in prank[-1]:
            prank = ptree.xpath('//div[@id="center"]/div/table/tbody/tr/td[2]/div[4]/text()')[0].split(' ')
    except IndexError:
        print('Valid player page, but could not find rank information.')
    
    if 'man' in prank[-1]:
        chigh_string = f'{pname[-1]} ' + ' '.join(pname[0:-1]) + ' has no ranking information before 1995.'
    else:
        chigh_string = f'{pname[-1]} ' + ' '.join(pname[0:-1]) + f': Singles career high = #{prank[-1][0:-1]}'

    return(chigh_string)

