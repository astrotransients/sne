#!/usr/local/bin/python2.7

import csv
import glob
import sys
import os
import re
import bz2
import operator
from collections import OrderedDict
from datetime import datetime
from bokeh.io import hplot, vplot
from bokeh.plotting import figure, show, save
from bokeh.resources import CDN
from bokeh.embed import file_html

indir = "../data/"
outdir = "../"

header = [
	"Names",
	"Year",
	"Month",
	"Day",
	"Date",
	"Host Names",
	"Publications",
	"Instruments/Surveys",
	"<em>z</em>",
	r"<em>v</em><sub>Helio</sub>",
	"$N_{\\rm h}$",
	"Claimed Type",
	"Notes",
	"Plots",
	"Data"
]

columnkey = [
	"name",
	"year",
	"discovermonth",
	"discoverday",
	"date",
	"host",
	"citations",
	"instruments",
	"redshift",
	"hvel",
	"nh",
	"claimedtype",
	"notes",
	"plot",
	"data"
]

footer = [
	"Note: IAU name preferred",
	"",
	"",
	"",
	"",
	"*&nbsp;Uncertain",
	"* discovery\n&Dagger; sne type first proposed",
	"",
	"",
	"",
	"Line of sight H column",
	"",
	"",
	"",
	""
]

showcols = [
	True,
	False,
	False,
	False,
	False,
	True,
	False,
	True,
	True,
	True,
	False,
	True,
	False,
	True,
	True,
]

photokeys = [
	'timeunit',
	'time',
	'band',
	'instrument',
	'abmag',
	'aberr',
	'upperlimit',
	'source'
]

if (len(columnkey) != len(header) or len(columnkey) != len(footer)):
	print 'Error: Header and/or footer not same length as key list.'
	sys.exit(0)

dataavaillink = "<a href='https://bitbucket.org/Guillochon/sne'>Y</a>";

header = dict(zip(columnkey,header))

bandcolors = [
	"indigo",
	"firebrick",
	"forestgreen",
	"red",
	"crimson",
	"indigo",
	"darkblue",
	"mediumvioletred",
	"pink",
	"#d82930",
	"orangered",
	"mediumvioletred",
	"mediumspringgreen",
	"orange",
	"chocolate",
	"darkorange",
]

bandcodes = [
	"u",
	"g",
	"r",
	"i",
	"z",
	"U",
	"B",
	"V",
	"R",
	"I",
	"G",
	"Y",
	"J",
	"H",
	"K"
]

bandnames = [
	"u",
	"g",
	"r",
	"i",
	"z",
	"U",
	"B",
	"V",
	"R",
	"I",
	"G",
	"Y",
	"J",
	"H",
	"K"
]

bandcolordict = dict(zip(bandcodes,bandcolors))
bandnamedict = dict(zip(bandcodes,bandnames))

coldict = dict(zip(range(len(columnkey)),columnkey))

def bandcolorf(color):
	if (color in bandcolordict):
		return bandcolordict[color]
	else:
		return 'black'

def bandnamef(code):
	if (code in bandnamedict):
		return bandnamedict[code]
	else:
		return code

catalogrows = []
for file in (sorted(glob.glob(indir + "*.bz2"), key=lambda s: s.lower()) + sorted(glob.glob(indir + "*.dat"), key=lambda s: s.lower())):
	print file
	filehead, ext = os.path.splitext(file)
	if ext == ".dat":
		tsvin = open(file,'rb')
	elif ext == ".bz2":
		tsvin = bz2.BZ2File(file,'rb')
	else:
		print "illegal file extension"
	tsvin = csv.reader(tsvin, delimiter='\t')

	catalog = dict(zip(columnkey,['' for _ in xrange(len(columnkey))]))

	table = []

	photometry = []

	eventname = os.path.basename(file).split('.')[0]

	plotavail = False;
	for row in tsvin:
		photorow = OrderedDict.fromkeys(photokeys, '')
		if row[0] == 'photometry':
			plotavail = True;
			plotlink = "<a href='https://sne.space/sne/" + eventname + ".html' target='_blank'><img alt='plot' width='32' height='32' src='https://sne.space/light-curve-icon.png'></a>";
			catalog['plot'] = plotlink

			photodict = dict(zip(row[1:], row[2:]))

			for key in photorow:
				if key in photodict:
					photorow[key] = photodict[key]

			photometry.append(photorow)

		elif row[0] in columnkey:
			table.append(row)
			catalog[row[0]] = row[1]

	catalog['data'] = r'<a href="https://sne.space/sne/data/' + eventname + r'.dat.bz2">Download</a>'
	
	prange = xrange(len(photometry))
	instrulist = sorted(filter(None, list(set([photometry[x]['instrument'] for x in prange]))))
	instruments = ", ".join(instrulist)
	if len(instrulist) > 0:
		catalog['instruments'] = instruments

	catalogrows.append(catalog)

	tools = "pan,wheel_zoom,box_zoom,save,crosshair,hover,reset,resize"

	if plotavail:
		phototime = [float(photometry[x]['time']) for x in prange]
		photoAB = [float(photometry[x]['abmag']) for x in prange]
		photoerrs = [float(photometry[x]['aberr'] if photometry[x]['aberr'] else 0.) for x in prange]

		x_buffer = 0.1*(max(phototime) - min(phototime))
		x_range = [-x_buffer + min(phototime), x_buffer + max(phototime)]

		p1 = figure(title='Photometry for ' + eventname, x_axis_label='Time (' + photometry[0]['timeunit'] + ')',
			y_axis_label='AB Magnitude', x_range = x_range, tools = tools,
			y_range = (0.5 + max([x + y for x, y in zip(photoAB, photoerrs)]), -0.5 + min([x - y for x, y in zip(photoAB, photoerrs)])))

		err_xs = []
		err_ys = []

		for x, y, yerr in zip(phototime, photoAB, photoerrs):
			err_xs.append((x, x))
			err_ys.append((y - yerr, y + yerr))

		photoband = [photometry[x]['band'] for x in prange]
		phototype = [int(photometry[x]['upperlimit']) if photometry[x]['upperlimit'] else 0 for x in prange]
		bandset = set(photoband)
		bandset = [i for (j, i) in sorted(zip(map(bandnamef, bandset), bandset))]

		for band in bandset:
			bandname = bandnamef(band)
			indb = [i for i, j in enumerate(photoband) if j == band]
			indt = [i for i, j in enumerate(phototype) if j == 0]
			ind = set(indb).intersection(indt)

			p1.circle([phototime[x] for x in ind], [photoAB[x] for x in ind],
				color=bandcolorf(band), legend=bandname, size=5)
			p1.multi_line([err_xs[x] for x in ind], [err_ys[x] for x in ind], color=bandcolorf(band))

			upplimlegend = bandname if len(ind) == 0 else ''

			indt = [i for i, j in enumerate(phototype) if j == 1]
			ind = set(indb).intersection(indt)
			p1.inverted_triangle([phototime[x] for x in ind], [photoAB[x] for x in ind],
				color=bandcolorf(band), legend=upplimlegend, size=8)

		p = p1

		#save(p)
		html = file_html(p, CDN, eventname)
		returnlink = r'    <a href="https://sne.space"><< Return to supernova catalog</a>';
		html = re.sub(r'(\<body\>)', r'\1\n    '+returnlink, html)
		html = re.sub(r'(\<\/body\>)', r'<a href="https://sne.space/sne/data/' + eventname + r'.dat.bz2">Download datafile</a><br><br>\n	  \1', html)
		html = re.sub(r'(\<\/body\>)', returnlink+r'\n	  \1', html)
		print outdir + eventname + ".html"
		with open(outdir + eventname + ".html", "w") as f:
			f.write(html)

# Construct the date
for r, row in enumerate(catalogrows):
	if not row['year']:
		year = 1
	else:
		year = int(row['year'])

	if not row['discovermonth']:
		month = 1
	else:
		month = int(row['discovermonth'])

	if not row['discoverday']:
		day = 1
	else:
		day = int(row['discoverday'])
	
	catalogrows[r]['date'] = datetime(year=year, month=month, day=day)

# Write it all out at the end
csvout = open(outdir + 'sne-catalog.csv', 'wb')
csvout = csv.writer(csvout, quotechar='"', quoting=csv.QUOTE_ALL)

prunedheader = [header[coldict[i]] for (i, j) in enumerate(showcols) if j]
csvout.writerow(prunedheader)

catalogrows.sort(key=operator.itemgetter('date'), reverse=True)
for row in catalogrows:
	prunedrow = [row[coldict[i]] for (i, j) in enumerate(showcols) if j]
	csvout.writerow(prunedrow)

prunedfooter = [header[coldict[i]] for (i, j) in enumerate(showcols) if j]
csvout.writerow(prunedfooter)
