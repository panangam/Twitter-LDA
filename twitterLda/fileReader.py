'''
fileReader.py

Provide several utilities function to read some file formats. Most functions get a file (or string iterable) as an input and output an iterable of texts.
'''
from twitterLda.projectPath import datadir

import json
import csv
import os

def tweetIterFuncGen(filename):
  def tweetIterFunc():
    with open(filename) as fin:
      for text in twitterFileReader(fin):
        yield text.decode('utf8', 'ignore')

  return tweetIterFunc

def twitterFileReader(fin):
  '''
  Read a file with each line containing a json of a Tweet's data raw output from Twitter API. Return an iterable yielding only the Tweet text

  :param fin: text file containing Tweet jsons
  :return: iterable yielding each Tweet text
  '''
  for (num, line) in enumerate(fin):
    # print line
    try:
      tweet = json.loads(line)
    except ValueError:
      print 'JSON format error at entry %d' % num

    try:
      yield tweet['text'].encode('utf-8', 'ignore')
    except AttributeError:
      print 'missing text field at entry %d' % num

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
  '''
  Wrapper function of csv.reader() to read a unicode file. Will encode file into UTF-8 format

  :param unicode_csv_data:  csv file to read
  :param dialect:           dialect of csv file
  :param **kwargs:          other parameters for csv.reader()

  :return: a csv.reader() instance reading unicode file
  '''
  # csv.py doesn't do Unicode; encode temporarily as UTF-8:
  csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                          dialect=dialect, **kwargs)
  for row in csv_reader:
      # decode UTF-8 back to Unicode, cell by cell:
      yield [cell for cell in row]

def utf_8_encoder(unicode_csv_data):
  '''
  Helper function for unicode_csv_reader(). Receive a text iterable and encode it into UTF-8 format

  :param unicode_csv_data: file to encode
  
  :return: UTF-8 encoded iterable
  '''
  for (num, line) in enumerate(unicode_csv_data):
    try:
      line = line.decode('utf-8', 'ignore')
      yield line.encode('utf-8', 'ignore')
    except UnicodeDecodeError:
      print 'codec error on entry %d' % num

from projectPath import datadir
import os

if __name__ == '__main__':
  
  with open(os.path.join(datadir, 'disaster.csv'), 'r') as fin:
    docIter = unicode_csv_reader(fin, delimiter='\t')
    lineIter = (line[4] for line in docIter)
    i = 0
    j = 0
    for text in lineIter:
      i += 1
    for text in lineIter:
      j += 1
    print i, j

def venIterFunc():
  vendir = os.path.join(datadir, 'ven')
  venDocList = os.listdir(vendir)
  venDocPathList = [os.path.join(vendir, venDoc) for venDoc in venDocList]
  for venDocPath in venDocPathList:
    with open(venDocPath, 'r') as venDocFile:
      for shout in venDocFile:
        yield shout.decode('utf8', 'ignore')
  
  '''
  with open(os.path.join(datadir, 'twitData31.dat'), 'r') as fin:
    tweetIter = twitterFileReader(fin)
    for text in tweetIter:
      print text
      raw_input()
  '''