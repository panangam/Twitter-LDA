# -*- coding: utf-8 -*-
__metaclass__ = type

import codecs
import ujson
from itertools import izip_longest

def filter_tweets(fin, fout):
    """
    Filters tweets from fin and writes selected tweets to fout. Selected tweets fulfill:
    - English
    - geo and place are enabled
    - in California

    :param fin: filename of input file containing
    :type fin: str
    :param fout: filename of output file
    :type fout: str
    :return: None
    :rtype: None
    """
    with codecs.open(fin, 'r', encoding='utf-8') as input_file, codecs.open(fout, 'a', encoding='utf-8') as output_file:
        count = 0
        filter_count = 0
        for line in input_file:
            line = line.strip()
            if not line:
                continue
            try:
                twt = ujson.loads(line)
                count += 1
                if (twt['lang'] != 'en') or (twt['text'].startswith("I'm at")):
                    continue
                # elif (twt['geo'] is None) or (twt['place'] is None):
                elif (twt['place'] is None):
                    continue
                elif twt['place']['country_code'] != 'US':
                    continue
                elif twt['place']['full_name'][-2:].lower() != 'ca':
                    continue
                else:
                    output_file.write(line + '\n')
                    filter_count += 1
            except ValueError, e:
                print 'ValueError:', e
            except KeyError, e:
                print 'KeyError:', e
            except TypeError, e:
                print 'TypeError:', e
        print("Read {0} tweets. Filter found {1}".format(count, filter_count))


def grouper(chunk_size, iterable, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks.

    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx

    :param chunk_size: chunk size
    :type chunk_size: int
    :param iterable: item to be grouped
    :type iterable: iterable
    :param fillvalue: value used to fill incomplete groups
    :type fillvalue: anything

    """
    args = [iter(iterable)] * chunk_size
    return izip_longest(fillvalue=fillvalue, *args)


if __name__ == '__main__':

    f_out = '../data/CA_filtered_twitData_26-27.dat'
    data_fname_prefix = '../data/twitData'
    for i in range(26, 28):
        data_fname = '{0}{1}.dat'.format(data_fname_prefix, i)
        try:
            print 'Filtering file: ' + data_fname
            filter_tweets(data_fname, f_out)
        except IOError, e:
            print IOError.message
            print 'Skipping file ' + data_fname

    n = 500
    split_fname_prefix = '../data/CA_split/{0}_'.format(f_out[11:-4])
    with codecs.open(f_out, 'r', encoding='utf-8') as f:
        for i, g in enumerate(grouper(n, f, fillvalue=''), 1):
            with codecs.open('{0}{1}.dat'.format(split_fname_prefix, i*n), 'w', encoding='utf-8') as split_fout:
                split_fout.writelines(g)
