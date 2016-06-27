"""General data import tasks.
"""
import csv
import os

from scripts import PATH
from scripts.utils import pbar
from astropy.time import Time as astrotime
from ..funcs import (make_date_string)

from .. import Events


def do_psst(events, stubs, args, tasks, task_obj, log):
    current_task = task_obj.current_task(args)
    # 2016arXiv160204156S
    file_path = os.path.join(
        PATH.REPO_EXTERNAL, '2016arXiv160204156S-tab1.tsv')
    with open(file_path, 'r') as f:
        data = list(csv.reader(f, delimiter='\t',
                               quotechar='"', skipinitialspace=True))
        for r, row in enumerate(pbar(data, current_task)):
            if row[0][0] == '#':
                continue
            (events,
             name,
             source) = Events.new_event(tasks, args, events, row[0], log,
                                        bibcode='2016arXiv160204156S')
            events[name].add_quantity(
                'claimedtype', row[3].replace('SN', '').strip('() '), source)
            events[name].add_quantity('redshift', row[5].strip(
                '() '), source, kind='spectroscopic')

    file_path = os.path.join(
        PATH.REPO_EXTERNAL, '2016arXiv160204156S-tab2.tsv')
    with open(file_path, 'r') as f:
        data = list(csv.reader(f, delimiter='\t',
                               quotechar='"', skipinitialspace=True))
        for r, row in enumerate(pbar(data, current_task)):
            if row[0][0] == '#':
                continue
            (events,
             name,
             source) = Events.new_event(tasks, args, events, row[0], log,
                                        bibcode='2016arXiv160204156S')
            events[name].add_quantity('ra', row[1], source)
            events[name].add_quantity('dec', row[2], source)
            mldt = astrotime(float(row[4]), format='mjd').datetime
            discoverdate = make_date_string(mldt.year, mldt.month, mldt.day)
            events[name].add_quantity('discoverdate', discoverdate, source)

    events, stubs = Events.journal_events(tasks, args, events, stubs, log)

    # 1606.04795
    file_path = os.path.join(PATH.REPO_EXTERNAL, '1606.04795.tsv')
    with open(file_path, 'r') as f:
        data = list(csv.reader(f, delimiter='\t',
                               quotechar='"', skipinitialspace=True))
        for r, row in enumerate(pbar(data, current_task)):
            if row[0][0] == '#':
                continue
            (events,
             name,
             source) = Events.new_event(tasks, args, events, row[0], log,
                                        srcname='Smartt et al. 2016',
                                        url='http://arxiv.org/abs/1606.04795')
            events[name].add_quantity('ra', row[1], source)
            events[name].add_quantity('dec', row[2], source)
            mldt = astrotime(float(row[3]), format='mjd').datetime
            discoverdate = make_date_string(mldt.year, mldt.month, mldt.day)
            events[name].add_quantity('discoverdate', discoverdate, source)
            events[name].add_quantity('claimedtype', row[6], source)
            events[name].add_quantity(
                'redshift', row[7], source, kind='spectroscopic')
            for alias in [x.strip() for x in row[8].split(',')]:
                events[name].add_quantity('alias', alias, source)

    events, stubs = Events.journal_events(tasks, args, events, stubs, log)

    return events