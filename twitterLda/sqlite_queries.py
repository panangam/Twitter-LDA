# -*- coding: utf-8 -*-

# sqlite_queries.py

from twitterLda.sqlite_models import User, Venue, Checkin, UserVenue, db
from twitterLda.projectPath import datadir

import codecs
import peewee as pw
import os
import datetime
import json

vendir = os.path.join(datadir, 'ven')

def connect():
    db.connect()

def close():
    db.close()

def readShoutJson(jsonStr):
    """
    Read a raw checkin json fro only the fields we need.

    :param ch_json: raw checkin json
    :type ch_json: dict{}
    :return: parsed object with necessary fields
    :rtype: json str
    """
    ch_json = json.loads(jsonStr)
    result = {}
    try:
        result['id'] = ch_json['id']
        result['userid'] = ch_json['user']['id']
        result['userLast'] = ch_json['user'].get('lastName', None)
        result['userFirst'] = ch_json['user'].get('firstName', None)
        result['venue'] = ch_json['venue']['id']
        result['venueName'] = ch_json['venue'].get('name', None)
        result['venueCity'] = ch_json['venue']['location'].get('city', None)
        result['venueState'] = ch_json['venue']['location'].get('state', None)
        result['venueZip'] = ch_json['venue']['location'].get('postalCode', None)
        venCat = ch_json['venue'].get('categories', None)
        if not venCat:
            result['venueCatID'] = None
            result['venueCatName'] = None
        else:
            result['venueCatID'] = venCat[0]['id']
            result['venueCatName'] = venCat[0]['name']
        result['shout'] = ch_json['shout']
        when = datetime.datetime.utcfromtimestamp(int(ch_json['createdAt']) + 60*int(ch_json['timeZoneOffset']))
        result['date'] = when.date().strftime("%Y-%m-%d")
        result['time'] = when.time().strftime("%H:%M:%S")
        result['weekday'] = when.isoweekday()              # Monday = 1, Sunday = 7
    except KeyError, e:
        print 'KeyError:', e, 'while on checkin:', ch_json['id']
        return False
    except IndexError, e:
        print 'IndexError:', e, 'while on checkin:', ch_json['id']
        return False
    return result


def insertShoutsFromJson(fin):
    """
    Create entries into the tables from data in json file.

    :param ch_json_file: transformed checkin json filename
    :type ch_json_file: str
    :return: 2-tuple of num_processed, num_loaded
    :rtype: 2-tuple of ints
    """
    db.create_tables([Checkin, User, Venue, UserVenue], safe=True)

    num_loaded = 0
    num_processed = 0
    with db.atomic():
        for (num, line) in enumerate(fin):
            try:
                ch = readShoutJson(line)
                if not ch:
                    # print 'shout json incomplete or wrong format on line %d' % num
                    continue

                curr_user, created = User.get_or_create(
                    id=ch['userid'],
                    defaults={'lastname': ch['userLast'],
                              'firstname': ch['userFirst'],
                              'shout_count': 0})

                curr_user, createdAt = User.get_or_create(
                    id=1,
                    defaults={
                        'lastname': 'testlast',
                        'firstname': 'testfirst',
                        'shout_count': 0
                    })

                curr_venue, created = Venue.get_or_create(
                    id=ch['venue'],
                    defaults={'name': ch['venueName'],
                              'city': ch['venueCity'],
                              'state': ch['venueState'],
                              'zip': ch['venueZip'],
                              'cat_id': ch['venueCatID'],
                              'cat_name': ch['venueCatName'],
                              'shout_count': 0})

                UserVenue.get_or_create(
                    user=curr_user,
                    venue=curr_venue)

                Checkin.create(
                    id=ch['id'],
                    user=curr_user,
                    venue=curr_venue,
                    date=ch['date'],
                    time=ch['time'],
                    weekday=ch['weekday'],
                    shout=ch['shout'])

                num_loaded += 1

            except pw.IntegrityError, e:
                print 'tried to load duplicate'
                continue
            finally:
                num_processed += 1

    update_shout_counts()

    print 'Processed {} checkins. Created {} new rows in checkin table.'.format(num_processed, num_loaded)
    return num_processed, num_loaded

def update_shout_counts():
    """
    Counts total # of shouts for each user and each venue.

    :return: None
    :rtype: None
    """
    venue_subquery = Checkin.select(pw.fn.COUNT(Checkin.id)).where(Checkin.venue == Venue.id)
    venue_update = Venue.update(shout_count=venue_subquery)
    venue_update.execute()

    user_subquery = Checkin.select(pw.fn.COUNT(Checkin.id)).where(Checkin.user == User.id)
    user_update = User.update(shout_count=user_subquery)
    user_update.execute()

def venues_to_docs():
    """
    For each venue, creates a file of all related shouts, one shout per line.

    :return: None
    :rtype: None
    """
    for ven in Venue.select():
        with codecs.open(os.path.join(vendir, '{}.txt'.format(ven.id)), 'w', encoding='utf-8') as ven_f:
            for checkin in ven.checkins:
                ven_f.write(checkin.shout)
                ven_f.write('\n')


def venues_to_doc(fname=os.path.join(datadir, 'allVenues.txt')):
    """
    Writes all venues to one file.

    :param fname: filename of output file
    :return:
    :rtype:
    """
    with codecs.open(fname, 'w', encoding='utf-8') as fout:
        for ven in Venue.select():
            fout.write(ven.id + ' ')
            checkin_str = u' '.join(ven.checkins)
            fout.write(checkin_str)
            fout.write('\n')

def topn_venues(n=30):
    """
    Finds the n venues with the most shouts.

    :param n: how many venues to find
    :type n: int
    :return: list of n venues (id, name)
    :rtype: []
    """
    venues_by_shoutcount = (Venue
                            .select(Venue.id, Venue.name)
                            .order_by(Venue.shout_count.desc())
                            .limit(n))
    return venues_by_shoutcount

def split_weekdays(ven_id):
    """
    Divides a venue's shouts into bins by day of the week.

    :param ven_id: venue id to be split
    :type ven_id: str
    :return: a dict where key=weekday, value=list of words from all shouts on that weekday
    :rtype: dict{}
    """
    ven_by_weekday = (Checkin
                      .select(Checkin.weekday, Checkin.shout)
                      .where(Checkin.venue == ven_id)
                      .order_by(Checkin.weekday))
    weekday_dict = {}
    for checkin in ven_by_weekday.execute():
        shouts_temp = weekday_dict.get(checkin.weekday, [])
        shouts_temp.extend(checkin.shout.split())
        weekday_dict[checkin.weekday] = shouts_temp
    return weekday_dict

def make_ven_index():
    """
    Create a file that links venue.ID with the offset in MmCorpus.docbyoffset.

    :return: None
    :rtype: None
    """
    with codecs.open(os.path.join(datadir, 'ven_id2i.txt'), 'w', encoding='utf-8') as ven_id2i:
        for i, doc in enumerate(sorted(os.listdir(vendir))):
            ven_id2i.write('{0}\t{1}\n'.format(doc[:-4], i))

if __name__ == '__main__':
    db.connect()
    venues_to_docs()
    update_shout_counts()
    topn = topn_venues(50)
    topnIDs = ['{}'.format(n.id) for n in topn]
    print topnIDs
    db.close()
