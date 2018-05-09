import requests
from lxml import html

from cloudbot import hook


@hook.command('h2h', 'h2hm')
def h2ha(text):
    """<name/name> - gets a head 2 head stat of two specified names"""
    gender = 0
    rq = text
    if not rq:
        return 'Find a head to head with h2h or h2hw'

    try:
        gender = 2
        if gender == 1 or 2:
            rq = rq.strip()
            rq = rq.split('/')
            p1 = rq[0]
            p2 = rq[1]
            if p1.find(' '):
                p1 = p1.replace(" ", "+")

            if p2.find(' '):
                p2 = p2.replace(" ", "+")

            page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl='+p1)
            tree = html.fromstring(page.text)

            p1link = tree.xpath('//tbody[@class="flags"]/tr[1]/td['+str(gender)+']/a/@href')
            p1link = ''.join(p1link)
            p1link = p1link.strip('/')
            p1link = p1link.split('/')
            p1link = p1link[1]

            page = requests.get('http://www.tennisexplorer.com/list-players/?search-text-pl='+p2)
            tree = html.fromstring(page.text)

            p2link = tree.xpath('//tbody[@class="flags"]/tr[1]/td['+str(gender)+']/a/@href')
            p2link = ''.join(p2link)
            p2link = p2link.strip('/')
            p2link = p2link.split('/')
            p2link = p2link[1]

            page = requests.get('http://www.tennisexplorer.com/mutual/' + p1link +'/' + p2link +'/')
            tree = html.fromstring(page.text)

            pNames = tree.xpath('//th[@class="plName"]/a/text()')
            p1name = pNames[0]
            p2name = pNames[1]

            p1name = p1name.split()
            p1name = p1name[1] + ' ' + p1name[0]

            p2name = p2name.split()
            p2name = p2name[1] + ' ' + p2name[0]

            score = tree.xpath('//td[@class="gScore"]/text()')
            score = ''.join(score)

            h2h = p1name + ' ' + score + ' ' + p2name
            return h2h

    except IndexError:
            return'No Head to Head found.'
