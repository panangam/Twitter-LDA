# -*- coding: utf-8 -*-
__metaclass__ = type

import codecs
import ujson
import requests
import pickle
import datetime
import os
import time

class Twitter2foursquare(object):
    """
    This class handles conversion of tweets into foursquare checkins.
    """

    def __init__(self):
        self.a_token = "DTZ5HFUFJFV11VP2INOSGME3J02L0GFGBIA00V4K1PZEXSQO"

    def file_chunk(self, iterable, n):
        '''
        yield array of consecutive n elements in iter each time

        :param iterable:iterable
        :param n:       number of elements in each chunk
        '''
        for i in xrange(0, len(iterable), n):
            yield iterable[i:i+n]

    def tweets_to_checkins(self, fin, fout):
        """
        Processes tweets.
        Uses swampapp reference to query foursquare's API for full checkin info. Foursquare API has a max 500 requests
        per hour.
        Checkins come in json format and are output to file.

        :param fin: Filename containing raw tweets.
        :param fout: Output filename of foursquare json checkins.
        """
        with codecs.open(fin, 'r', encoding='utf-8') as tweets_file, codecs.open(fout, 'a', encoding='utf-8') as ch_file:
            count = 0
            for line in tweets_file:
                count += 1 
                try:
                    twt = ujson.loads(line)
                    temp_url = twt['entities']['urls'][0]['expanded_url']
                    # find index of last '/' in the url, use index to get shortID substring
                    truncate_at = temp_url.rfind('/')
                    shortID = temp_url[truncate_at+1:]
                    print('    shout: ' + shortID)

                    # try max 30 attempts to get a reponse from foursquare API.
                    for i in range(30):
                        try:
                            r = requests.get('https://api.foursquare.com/v2/checkins/resolve?shortId=' +
                                             '{sid}&oauth_token={at}'.format(sid=shortID, at=self.a_token) + '&v=20150603')
                        except requests.exceptions.ConnectionError, e:
                            print 'ConnectionError:', e
                            time.sleep(3)
                        else:
                            break

                    rJson = r.json()
                    ch_file.write(ujson.dumps(rJson['response']['checkin']) + '\n')

                except IndexError, e:
                    print 'IndexError', e
                    if rJson['meta']['code'] == 403:
                        self.display_403(rJson['meta']['errorType'], count)
                    continue

                except KeyError, e:
                    print 'KeyError', e
                    if rJson['meta']['code'] == 403:
                        self.display_403(rJson['meta']['errorType'], count)
                    continue

                except ValueError, e:
                    print 'ValueError', e
                    pass

                if count % 500 == 0:
                    print 'processed %d tweets' % count
                    time.sleep(3600)

    def get_categories(self):
        r = requests.get('https://api.foursquare.com/v2/venues/categories?oauth_token={at}'
                         .format(at=self.a_token) + '&v=20150603')
        rJson = r.json()
        categories = rJson['response']['categories']
        with codecs.open('data/categories.json', 'w', encoding='utf-8') as fout:
            fout.write(ujson.dumps(categories))


    @staticmethod
    def display_403(error_type, count):
        """
        Outputs info about server response 403.
        :param error_type: details about the error
        :type error_type: str
        :param count: how many shouts were processed until error
        :type count: int
        :return: None
        :rtype: None
        """
        print error_type
        print datetime.datetime.now().time().isoformat()
        print('max # requests for this hour')
        print('processed ' + str(count) + ' shouts')
        time.sleep(3600)


    # def loadCheckins(self, fin):
    #     """
    #     add check_ins to checkins
    #     :param fin: file containing shouts
    #     """
    #     with codecs.open(fin, 'r', encoding = "utf-8", errors = 'replace') as cfile:
    #         for line in cfile:
    #             check_in_json = ujson.loads(line)
    #             if MyCheckin.checkins.has_key(check_in_json['id']):
    #                 # print("key already exists")
    #                 continue
    #             else:
    #                 try:
    #                     check_in = MyCheckin(check_in_json)
    #                 except KeyError:
    #                     pass


    # def addToVenDocs(self, check_in):
    #     """
    #     add check_in to venDocs
    #     :param check_in:
    #     :return:
    #     """
    #     print('adding to venDocs')
    #     shout = check_in['shout']
    #     shout_tokens = twokenize.tokenizeRawTweetText(shout)
    #     new_shout = ' '.join(shout_tokens)
    #     try:
    #         venShoutList = self.venDocs[check_in['venueID']]
    #         venShoutList.append(new_shout)
    #         self.venDocs[check_in['venueID']] = venShoutList
    #     # if not venDocs.has_key(check_in['venueID']):
    #     #     venDocs[check_in['venueID']] = [new_shout]
    #     # else:
    #     #     venDocs[check_in['venueID']].append(new_shout)
    #     except KeyError:
    #         self.venDocs[check_in['venueID']] = [new_shout]
    #     self.venNameIndex[check_in['venueID']] = check_in['venueName']
    #     return


    # def loadCheckinsToVenDocs(self, fin):
    #     with open(fin, 'r') as f:
    #         for line in f:
    #             try:
    #                 cn = ujson.loads(line)
    #                 self.checkins[cn['id']] = cn
    #                 addToVenDocs(cn)
    #             except KeyError:
    #                 print('KeyError!!!!!!!!!!!!!!\n')
    #                 # pprint.pprint(cn)
    #             except ValueError:
    #                 pass

    # def outputVenDocs(self):
    #     """
    #     for each venue, write a file containing the shouts
    #     :return:
    #     """
    #     for ven in self.venDocs.keys():
    #         venName = self.venNameIndex[ven]
    #         # chars_to_remove = ['/', '\\', '!', '?', '@']
    #         # venName = ''.join(re.split(r'\/\\?!@', venName))
    #         venName = re.sub(r'/\?!@', '', venName)
    #
    #         try:
    #             with codecs.open('.\\data\\venues\\' + venName + '-' + ven[:5] + '.txt', 'w', 'utf-8') as venOut:
    #                 shoutList = self.venDocs[ven]
    #                 for shout in shoutList:
    #                     venOut.write(shout + '\n')
    #         except IOError:
    #             with codecs.open('.\\data\\venues\\' + ven[:5] + '.txt', 'w', 'utf-8') as venOut:
    #                 shoutList = self.venDocs[ven]
    #                 for shout in shoutList:
    #                     venOut.write(shout + '\n')

    def countUniqueUsers(self):
        return len(set([self.checkins[c]['userID'] for c in self.checkins]))


    def saveState(self):
        with open('.\\data\\state\\t2f.dat', 'w') as f:
            pickle.dump(self, f)

    def loadState(self):
        with open('.\\data\\state\\t2f.dat', 'r') as f:
            t2f = pickle.load(f)
            return t2f

if __name__ == '__main__':
    t2f = Twitter2foursquare()
    t2f.get_categories()

    '''
    os.chdir('data/CA_split/')
    split_file_list = sorted(os.listdir(os.getcwd()), key=lambda filename: int(filename[27:-4]))
    for i, fname in enumerate(split_file_list):
        print i, '\t', fname
    print '\n'
    
    fout = '../CA_shouts_30-34.dat'
    for f in split_file_list:
        print('processing ' + f)
        t2f.tweets_to_checkins(f, fout)
        print('done with ' + f + '\n')
        time.sleep(3600)
    '''

    outFileName = 'data/shouts/test_shouts.txt'
    t2f.tweets_to_checkins('data/tweets/twitData31.dat', outFileName)


'''
    t2f.tweets_to_checkins('.\\data\\twitData4_LA_imAt.dat', '.\\data\\4sq_shouts4_LA_imAt.dat')
    outputVenDocs()
    loadCheckinsToVenDocs('.\\data\\LA_4sq_shouts.dat')
    loadCheckinsToVenDocs('.\\data\\LA_4sq_shouts_test_200.dat')
    MyCheckin.loadCheckins('.\\data\\LA_4sq_shoutsT.dat')
    print("# of Checkins: " + str(len(MyCheckin.checkins)))
    t2f.outputVenDocs()
    t2f = t2f.loadState()
    t2f.saveState()
    print(str(t2f.countUniqueUsers()) + ' users')
    print(str(len(t2f.checkins)))
    t2f2 = t2f.loadState()
    t2f2.outputVenDocs()
'''
#