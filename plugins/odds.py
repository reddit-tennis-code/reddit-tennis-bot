import requests
from cloudbot import hook
from xml.etree import ElementTree
from operator import itemgetter
from itertools import groupby, count

def batch(iterable, size):
	""" Batch generator for output."""

	c = count()
	for k, g in groupby(iterable, lambda x:next(c)//size):
		yield g

def fml(string):
	"""Format and color moneyline based on value (-/+)."""

	if string == "":  # empty.
		return "-"
	elif float(str(string).replace('.0','')) > 0:  # positive
		return f'\x0309+{str(string)}\x03'
		# return ircutils.mircColor("+"+(str(string)), 'green')
	elif float(str(string).replace('.0','')) < 0:  # negative
		return f'\x0304{str(string)}\x03'
		# return ircutils.mircColor((str(string)), 'red')
	else:  # no clue what to do so just bold.
		return f'\x02{str(string)}\x02'
		# return ircutils.bold(string)

def processgame(game):
	"""Process a single XML line for a game/event."""

	tmp = {}  # dict container.
	tmp['gpd'] = game.get('gpd')  # gameplayed? helpful for soccer.
	tmp['gametype'] = game.get('idgmtyp')  # gametype. used to detect props.
	tmp['date'] = game.get('gmdt')  # game date.
	tmp['time'] = game.get('gmtm')  # game time.
	tmp['vpt'] = game.get('vpt')  # visiting pitcher. (mlb)
	tmp['hpt'] = game.get('hpt')  # home pitcher. (mlb)
	# tmp['newdt'] = "{0} {1}".format(tmp['date'], tmp['time'])  # fixed date.
	tmp['away'] = game.get('vtm')  # visiting/away team.
	tmp['home'] = game.get('htm')  # home team.
	tmp['haschild'] = game.find('line').get('haschild')  # odd XML var. checks for games.
	# handle odds. we check for one field then another.
	tmp['awayodds'] = game.find('line').get('voddst')  # find visitor odds.
	if tmp['awayodds'] == '':  # empty/blank or not there.
		tmp['awayodds'] = game.find('line').get('vsprdoddst')  # alt. visitor odds.
	tmp['homeodds'] = game.find('line').get('hoddst')  # home odds.
	if tmp['homeodds'] == '':  # empty/blank or not there.
		tmp['homeodds'] = game.find('line').get('hsprdoddst')  # alternate home odds.
	# get the over/under total here.
	if game.find('line').attrib['ovt']:  # abs/fix so its ###.#
		tmp['over'] = "%.12g" % abs(float(game.find('line').get('ovt')))
	else:  # sometimes no o/u.
		tmp['over'] = None
	# find the spread and fix it if we have it.
	tmp['spread'] = game.find('line').get('hsprdt')  # find the spread and fix.
	if tmp['spread'] != '0' and not tmp['spread'].startswith('-') and tmp['spread'] != '':
		tmp['spread'] = "+{0}".format(tmp['spread'])  # hackey to get + infront of non - spread.
	# some matches like soccer have a draw line.
	tmp['vspoddst'] = game.find('line').get('vspoddst')
	# do something here to bold the favorite. this is tricky since odds can be in different fields.
	if tmp['spread'] and tmp['spread'] != '' and tmp['spread'] != "0":  # first try to use the spread if it's there. then turn to odds.
		if tmp['spread'].startswith('-'):  # if the spread is -, the hometeam is favored.
			tmp['home'] = f'\x02{tmp["home"]}\x02'
		else:  # we bold the away team because it's + or regular number.
			tmp['away'] = f'\x02{tmp["away"]}\x02'
	elif tmp['awayodds'] != "-" and tmp['homeodds'] != "-" and tmp['awayodds'] != '' and tmp['homeodds'] != '':
		if tmp['awayodds'] < tmp['homeodds']:
			tmp['away'] = f'\x02{tmp["away"]}\x02'
		elif tmp['homeodds'] < tmp['awayodds']:
			tmp['home'] = f'\x02{tmp["home"]}\x02'
	# now that we're done, return.
	return tmp

def processprop(prop):
	"""Process prop lines where it's a team/name and line. Returns a dict for sorting."""

	tmp = {}
	tmp['tmname'] = prop.get('tmname')
	tmp['line'] = int(prop.get('odds'))  # to sort.
	return tmp

@hook.command("odds")
def odds(text, reply):
	""".odds <sport> [team]. Displays various odds/lines for sporting events. Ex: .odds EPL Manch or .odds NBA LA"""

	# validate input/sports.
	optsport = text.split()[0]
	optinput = ' '.join(text.split()[1:])
	optsport, optprop = optsport.upper(), False  # upper to match. False on the prop.
	validsports = {'NFL':'1', 'NBA':'3', 'NCB':'4','NHL':'7', 'MLB':'5', 'INTL-FRIENDLY':'10090',
					'EPL':'10003', 'LALIGA':'12159', 'UFC-MMA':'206', 'UFC-BELLATOR':'12636',
					'MLS':'10007', 'UEFA-CL':'10016', 'LIGUE1':'10005','BUNDESLIGA':'10004',
					'SERIEA':'10002', 'UEFA-EUROPA':'12613', 'BOXING':'12064', 'TENNIS-M':'12331',
					'TENNIS-W':'12332', 'AUSSIERULES':'12118', 'GOLF':'12003', 'WCQ-UEFA':'12321',
					'WCQ-CONMEBOL':'12451', 'WCQ-CAF':'12461', 'WCQ-CONCACAF':'12484', 'NASCAR':'12015',
					'CFL':'12145', 'CFB':['2', '12734'], 'CONCACAF-CL':'12442' }

	if not optsport in validsports:  # error if not in above.
		validprops = { 'NFL-SUPERBOWL':'1561335', 'NFL-MVP':'1583283', 'BCS':'1609313'}
		if optsport in validprops:
			optprop = optsport
			optsport = "PROP"
		else:  # prop not found. so we display only the sports.
			reply("ERROR: '{0}' is invalid. Valid sports: {1}".format(optsport, " | ".join(sorted(validsports.keys()))))
			return

	# now try and parse/open XML.
	try:
		response = requests.get('http://lines.bookmaker.eu/')
		tree = ElementTree.fromstring(response.content)
	except Exception:
		reply("ERROR: Something broke trying to parse the XML.")
		return

	# now that we have XML, it must be processed differently depending on props/games.
	if optsport in ("GOLF", "NASCAR"):  # specific handler for golf. we label sport but handle as prop.
		line = tree.findall('./Leagues/league[@IdLeague="%s"]/game' % validsports[optsport])
		if not line:
			reply("ERROR: I did not find any {0} prop/future odds.".format(optsport))
			return
		# we only grab the first [0]. we could do more than one.
		propname = line[0].attrib['htm']  # tournament here.
		props = []  # list to dump out in for processing.
		for l in (line[0].findall('line')):  # we enumerate over all "line" in the entry.
			try:
				props.append(processprop(l))  # send to prop handler and append.
			except:
				continue
		# now sort (lowest first) before we prep the output. (creates a list w/dict in it.)
		props = sorted(props, key=itemgetter('line'))
	elif optsport == "PROP":  # processing PROPS/futures here.
		line = tree.find(".//game[@idgm='%s']" % validprops[optprop])
		if not line:  # prop or no items found inside the prop.
			reply("ERROR: I did not find {0} prop/future or any odds in it.".format(optprop))
			return
		# we did find prop+lines, so lets grab the name and the lines.
		propname = line.attrib['htm']  # htm contains the "name" of the prop/future.
		props = []  # everything goes into props dict so we can sort.
		for l in (line.findall('line')):  # we enumerate over all "line" in the entry.
			props.append(processprop(l))  # send to prop handler and append.
		# now sort (lowest first) before we prep the output. (creates a list w/dict in it.)
		props = sorted(props, key=itemgetter('line'))
	else:  # processing GAMES here not props.
		# first, we must check if sportid from the dict is a string or list (list for CFB)
		catids = validsports[optsport]
		if isinstance(catids, list):  # we do have a list, not a string (CFB)
			l = []  # tmp container.
			for catid in catids:  # iterate through the category ids in the list.
				l.append(tree.findall('./Leagues/league[@IdLeague="%s"]/game' % (catid)))  # find like normal and append to tmp container.
			# we're done iterating over the ids. now merge these into one (flatten).
			leagues = [x for sublist in l for x in sublist]
		else:  # catids = string (single)
			leagues = tree.findall('./Leagues/league[@IdLeague="%s"]/game' % (validsports[optsport]))
		# now, lets check if what we got back looking for games in leagues is empty (no games, wrong time of year, etc).
		#self.log.info("WW: {1} LEAGUES: {0}".format(leagues, validsports[optsport]))
		if len(leagues) == 0:
			reply("ERROR: I did not find any events in the {0} category.".format(optsport))
			return
		
		# we must process each "game" or match.
		games = []  # list to store dicts of processed games.
		for game in leagues:  # each entry is a game/match.
			games.append(processgame(game))  # add processesed xml list.
		# now, we should sort by dt (epoch seconds) with output (earliest first).
		games = sorted(games, key=itemgetter('date', 'time'))

	# now, we must preprocess the output in the dicts.
	# each sport is different and we append into a list for output.
	output = []
	# first, handle props and prop-like sports (GOLF ONLY).
	if optsport == "PROP" or optsport in ("GOLF", "NASCAR"):  # we join all of the props/lines into one entry. title.
		proplist = " | ".join([q['tmname'].title().strip() + " (" + fml(q['line']) + ")" for q in props])
		output.append(f'\x0309{propname}\x03 :: {proplist}')
		#output.append("{0} :: {1}".format(ircutils.mircColor(propname, 'red'), proplist))
	# REST ARE NON-PROP. EACH HANDLES A SPORT DIFFERENTLY.
	# handle NFL football.
	elif optsport in ("NFL", "CFL", "CFB"):
		for (v) in games:
			if v['spread'] != "" and v['homeodds'] != '':
				output.append("{0} @ {1}[{2}]  o/u: {3}  {4}/{5}".format(v['away'], v['home'],\
					v['spread'], v['over'], fml(v['awayodds']), fml(v['homeodds'])))
	# handle tennis.
	elif optsport in ('TENNIS-M', 'TENNIS-W'):
		for v in games:
			if v['homeodds'] != '' and not v['away'].endswith('SET'):  # haschild="True" related="False"
				output.append("{0} vs. {1}  {2}/{3}".format(v['away'], v['home'],\
					fml(v['awayodds']), fml(v['homeodds'])))
	# handle aussie rules.
	elif optsport == "AUSSIERULES":
		for (v) in games:
			if v['homeodds'] != '':
				output.append("{0} @ {1}  {2}/{3}".format(v['away'], v['home'],\
					fml(v['awayodds']), fml(v['homeodds'])))
	# handle baseball.
	elif optsport == "MLB":
		for (v) in games:
			if v['haschild'] == "True" and v['homeodds'] != '':
				output.append("{0} @ {1}  {2}/{3}".format(v['away'], v['home'],\
					fml(v['awayodds']), fml(v['homeodds'])))
	# handle hockey.
	elif optsport == "NHL":
		for (v) in games:
			if v['haschild'] == "True" and v['homeodds'] != '':
				output.append("{0} @ {1}  o/u: {2}  {3}/{4}".format(v['away'], v['home'],\
					v['over'], fml(v['awayodds']), fml(v['homeodds'])))
	# handle college basketball output.
	elif optsport == "NCB":
		for (v) in games:
			if v['haschild'] == "True" and v['homeodds'] != '':
				output.append("{0} @ {1}[{2}]  o/u: {3}  {4}/{5}".format(v['away'], v['home'],\
					v['spread'], v['over'], fml(v['awayodds']), fml(v['homeodds'])))
	# handle NBA output.
	elif optsport == "NBA":
		for (v) in games:
			if ((v['haschild'] == "True") and (v['spread'] != "" and v['over'] != "")):
				output.append("{0} @ {1}[{2}]  o/u: {3}  {4}/{5}".format(v['away'], v['home'],\
					v['spread'], v['over'], fml(v['awayodds']), fml(v['homeodds'])))
	# handle soccer output.
	elif optsport in ('EPL', 'LALIGA', 'BUNDESLIGA', 'SERIEA', 'LIGUE1', 'MLS', 'UEFA-EUROPA', 'UEFA-CL',
						'WCQ-UEFA', 'WCQ-CONMEBOL', 'WCQ-CAF', 'WCQ-CONCACAF', 'INTL-FRIENDLY', 'CONCACAF-CL'):
		for (v) in games:  # we check for Game below because it blocks out 1H/2H lines.
			if v['haschild'] == "True" and v['homeodds'] != '' and v['awayodds'] != '' and v['gpd'] == 'Game':
					output.append("{0} @ {1}  o/u: {2}  {3}/{4} (Draw: {5})".format(v['away'], v['home'],\
					v['over'], fml(v['awayodds']), fml(v['homeodds']), fml(v['vspoddst'])))
	# handle UFC output.
	elif optsport in ('UFC-MMA', 'UFC-BELLATOR'):
		for (v) in games:
			if v['homeodds'] != '' and v['awayodds'] != '':
				output.append("{0} vs. {1}  {2}/{3}".format(v['away'], v['home'],\
					fml(v['awayodds']), fml(v['homeodds'])))
	# handle boxing output.
	elif optsport == "BOXING":
		for (v) in games:
			if v['homeodds'] != '' and v['awayodds'] != '':
				output.append("{0} vs. {1}  {2}/{3}".format(v['away'], v['home'],\
					fml(v['awayodds']), fml(v['homeodds'])))

	# before we do anything, check if we should strip ansi.
	# if self.registryValue('disableANSI', msg.args[0]):
	# 	output = [i.strip() for i in output]
		#output = [ircutils.stripFormatting(i) for i in output]

	# OUTPUT TIME.
	# checks if optinput (looking for something)
	if not optinput or optsport == "PROP":  # just display the games.
		outlength = len(output)  # calc once.
		# determine how to output based on outlength.
		if outlength == 0:  # nothing.
			reply("Sorry, I did not find any active odds in {0}.".format(optsport))
		elif outlength <= 6:  # 7 or under
			for each in output:  # one per line.
				reply(each)
		else:  # more than 9, we batch 4 per line. we also cap the # of lines.
			count = 0
			for N in batch(output, 4):
				if count < 6:  # 5 and under.
					reply(" | ".join([item for item in N]))
					count += 1  # ++
				else:  # 6 and up.
					reply("I found too many results in the {0} category. Please specify a string to search for.".format(optsport))
					break
	else:  # we do want to limit output to only matching items.
		count = 0  # to handle a max # of 5.
		for each in output:  # iterate through output list.
			if optinput.lower() in each.lower():  # match.
				if count < 5:  # output matching items.
					reply(each)
					count += 1  # ++
				else:  # too many to output after 5. breaks,
					reply("I found too many results for '{0}'. Please specify something more specific".format(optinput))
					break
		# last check for if we outputted NOTHING.
		if count == 0:  # nothing came out.
			reply("Sorry, I did not find any odds matching '{0}' in {1} category.".format(optinput, optsport))
